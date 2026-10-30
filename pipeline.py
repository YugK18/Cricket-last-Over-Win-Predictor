"""
IPL Last-Over Win Predictor & Strategy Dashboard
Data Preprocessing, Feature Engineering, and Model Training Pipeline
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, log_loss, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import xgboost as xgb

# Silence loky core counting warning in restricted environments
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data.csv')
ARTIFACT_DIR = os.path.join(BASE_DIR, 'artifacts')

os.makedirs(ARTIFACT_DIR, exist_ok=True)


def load_and_preprocess_data(csv_path=DATA_PATH):
    print("Loading raw ball-by-ball dataset...")
    df = pd.read_csv(csv_path)

    # Clean team names
    team_mapping = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
    }
    df['batting_team'] = df['batting_team'].replace(team_mapping)

    # Delivery-level calculations
    df['total_runs'] = df['runs_batter'] + df['runs_extras']
    df['is_legal'] = ~df['extras_type'].isin(['wides', 'noballs'])
    # Bowler runs: exclude fielding extras (byes, legbyes)
    df['is_bowler_run'] = df['runs_batter'] + df['runs_extras'].where(
        ~df['extras_type'].isin(['byes', 'legbyes']), 0
    )
    # Bowler wickets: exclude run-outs and non-bowler dismissals
    non_bowler_dismissals = ['run out', 'retired hurt', 'retired out', 'obstructing the field', None]
    df['is_bowler_wicket'] = (df['wicket_taken'] == 1) & (~df['dismissal_kind'].isin(non_bowler_dismissals))
    df['is_dot'] = (df['total_runs'] == 0) & df['is_legal']
    df['year'] = pd.to_datetime(df['date'], format='mixed').dt.year

    return df


def compute_team_player_mappings(df):
    """
    Build dynamic mapping:
    - Which batters have played for which batting team
    - Which bowlers have bowled for which bowling team
    """
    print("Computing team and player relationships...")
    # Batters per team
    batters_by_team = {}
    for team, grp in df.groupby('batting_team'):
        # Sort by total runs scored for that team
        p_stats = grp.groupby('batter').agg(
            runs=('runs_batter', 'sum'),
            balls=('is_legal', 'sum')
        ).reset_index()
        p_stats = p_stats[p_stats['balls'] >= 10].sort_values('runs', ascending=False)
        batters_by_team[team] = p_stats['batter'].tolist()

    # Determine bowling team per match & innings
    # For each match and innings, bowling team is the other team
    match_innings_bowler = []
    for mid, m in df.groupby('match_id', sort=False):
        teams = m['batting_team'].unique()
        if len(teams) < 2:
            continue
        inn_idx = (m['batting_team'] != m['batting_team'].shift()).cumsum()
        for inn in inn_idx.unique()[:2]:
            sub = m[inn_idx == inn]
            bat_team = sub['batting_team'].iloc[0]
            bowl_team = teams[1] if bat_team == teams[0] else teams[0]
            for bowler, bgrp in sub.groupby('bowler'):
                match_innings_bowler.append({
                    'bowling_team': bowl_team,
                    'bowler': bowler,
                    'balls': bgrp['is_legal'].sum(),
                    'wickets': bgrp['is_bowler_wicket'].sum()
                })

    bowlers_df = pd.DataFrame(match_innings_bowler)
    bowlers_by_team = {}
    for team, grp in bowlers_df.groupby('bowling_team'):
        b_stats = grp.groupby('bowler').agg(
            balls=('balls', 'sum'),
            wickets=('wickets', 'sum')
        ).reset_index()
        b_stats = b_stats[b_stats['balls'] >= 12].sort_values(['wickets', 'balls'], ascending=[False, False])
        bowlers_by_team[team] = b_stats['bowler'].tolist()

    return batters_by_team, bowlers_by_team


def compute_death_overs_metrics(df):
    """
    Feature engineering for overs 16-20 (over index 15-19):
    - Batter SR & Avg
    - Bowler Economy, Strike Rate, Dot-ball %
    """
    print("Computing death-overs (16-20) metrics...")
    death_df = df[df['over'] >= 15].copy()

    # Batters in death overs
    b_agg = death_df.groupby('batter').agg(
        death_runs=('runs_batter', 'sum'),
        death_balls=('is_legal', 'sum'),
        death_dismissals=('player_out', lambda x: x.notna().sum()),
        death_fours=('runs_batter', lambda x: (x == 4).sum()),
        death_sixes=('runs_batter', lambda x: (x == 6).sum())
    ).reset_index()

    b_agg['death_sr'] = (b_agg['death_runs'] / b_agg['death_balls'].replace(0, np.nan) * 100).fillna(125.0)
    b_agg['death_avg'] = (b_agg['death_runs'] / b_agg['death_dismissals'].replace(0, 1)).fillna(20.0)

    # Bowlers in death overs
    bowl_agg = death_df.groupby('bowler').agg(
        death_runs_conceded=('is_bowler_run', 'sum'),
        death_balls_bowled=('is_legal', 'sum'),
        death_wickets=('is_bowler_wicket', 'sum'),
        death_dots=('is_dot', 'sum')
    ).reset_index()

    bowl_agg['death_econ'] = (
        bowl_agg['death_runs_conceded'] / (bowl_agg['death_balls_bowled'] / 6.0).replace(0, np.nan)
    ).fillna(10.5)
    bowl_agg['death_sr'] = (
        bowl_agg['death_balls_bowled'] / bowl_agg['death_wickets'].replace(0, np.nan)
    ).fillna(22.0)
    bowl_agg['death_dot_pct'] = (
        bowl_agg['death_dots'] / bowl_agg['death_balls_bowled'].replace(0, np.nan) * 100
    ).fillna(25.0)

    return b_agg, bowl_agg


def compute_head_to_head_metrics(df):
    """
    Batter vs Bowler Head-to-Head historical stats:
    runs scored, dismissals, strike rate, balls faced, dots
    """
    print("Computing Head-to-Head (H2H) metrics...")
    h2h = df.groupby(['batter', 'bowler']).agg(
        h2h_runs=('runs_batter', 'sum'),
        h2h_balls=('is_legal', 'sum'),
        h2h_dismissals=('is_bowler_wicket', 'sum'),
        h2h_dots=('is_dot', 'sum')
    ).reset_index()

    h2h['h2h_sr'] = (h2h['h2h_runs'] / h2h['h2h_balls'].replace(0, np.nan) * 100).fillna(120.0)
    h2h['h2h_dot_pct'] = (h2h['h2h_dots'] / h2h['h2h_balls'].replace(0, np.nan) * 100).fillna(25.0)

    return h2h


def compute_venue_metrics(df):
    """
    Venue metrics:
    - Average 20th-over runs conceded/scored
    - Historical chase success rate at the venue
    """
    print("Computing venue-specific metrics...")
    # Chase success rate
    match_chase = []
    for mid, m in df.groupby('match_id', sort=False):
        inn_idx = (m['batting_team'] != m['batting_team'].shift()).cumsum()
        inn1 = m[inn_idx == 1]
        inn2 = m[inn_idx == 2]
        if len(inn1) == 0 or len(inn2) == 0:
            continue
        target = inn1['total_runs'].sum() + 1
        inn2_runs = inn2['total_runs'].sum()
        chased = 1 if inn2_runs >= target else 0
        match_chase.append({
            'match_id': mid,
            'venue': m['venue'].iloc[0],
            'chased': chased
        })

    chase_df = pd.DataFrame(match_chase)
    venue_chase = chase_df.groupby('venue').agg(
        venue_total_matches=('match_id', 'count'),
        venue_chase_win_rate=('chased', 'mean')
    ).reset_index()

    # 20th-over runs at venue
    over19 = df[df['over'] == 19].groupby(['match_id', 'venue'])['total_runs'].sum().reset_index()
    venue_over19 = over19.groupby('venue').agg(
        venue_avg_20th_runs=('total_runs', 'mean'),
        venue_over19_matches=('total_runs', 'count')
    ).reset_index()

    venue_stats = pd.merge(venue_chase, venue_over19, on='venue', how='outer')
    venue_stats['venue_chase_win_rate'] = venue_stats['venue_chase_win_rate'].fillna(0.50)
    venue_stats['venue_avg_20th_runs'] = venue_stats['venue_avg_20th_runs'].fillna(11.2)
    venue_stats['venue_total_matches'] = venue_stats['venue_total_matches'].fillna(0).astype(int)

    return venue_stats


def extract_situations_and_history(df):
    """
    Extract:
    1. Ball-by-ball 20th over situations for ML training
    2. Historical match database for the 'Similar Scenarios' matcher
    """
    print("Extracting last-over situations and historical match instances...")
    situations = []
    historical_matches = []

    for mid, m in df.groupby('match_id', sort=False):
        inn_idx = (m['batting_team'] != m['batting_team'].shift()).cumsum()
        inn1 = m[inn_idx == 1]
        inn2 = m[inn_idx == 2].copy()

        if len(inn1) == 0 or len(inn2) == 0:
            continue

        target = inn1['total_runs'].sum() + 1
        inn2_final_runs = inn2['total_runs'].sum()
        inn2_final_wickets = inn2['wicket_taken'].sum()
        batting_win = 1 if inn2_final_runs >= target else 0
        is_tied = (inn2_final_runs == target - 1)

        venue = m['venue'].iloc[0]
        date_str = str(m['date'].iloc[0])
        year = str(m['year'].iloc[0])
        bat_team = inn2['batting_team'].iloc[0]
        bowl_team = inn1['batting_team'].iloc[0]

        inn2_over19 = inn2[inn2['over'] == 19].copy()
        if len(inn2_over19) == 0:
            continue

        inn2_before19 = inn2[inn2['over'] < 19]
        runs_before19 = inn2_before19['total_runs'].sum()
        wickets_before19 = inn2_before19['wicket_taken'].sum()

        legal_balls_bowled = 0
        curr_runs = runs_before19
        curr_wickets = wickets_before19

        ball_events = []
        for _, brow in inn2_over19.iterrows():
            ball_desc = f"{brow['total_runs']}r"
            if brow['wicket_taken'] == 1:
                ball_desc = f"W ({brow['dismissal_kind']})"
            elif brow['runs_extras'] > 0:
                ball_desc = f"{brow['total_runs']} ({brow['extras_type']})"
            ball_events.append(ball_desc)

        # Store historical match summary
        hist_entry = {
            'match_id': mid,
            'year': year,
            'date': date_str,
            'venue': venue,
            'batting_team': bat_team,
            'bowling_team': bowl_team,
            'target': target,
            'inn1_total': target - 1,
            'inn2_total': inn2_final_runs,
            'inn2_wickets': inn2_final_wickets,
            'runs_needed_start_over': target - runs_before19,
            'wickets_in_hand_start_over': 10 - wickets_before19,
            'outcome': 'Chased' if batting_win else ('Tied' if is_tied else 'Defended'),
            'margin': abs(inn2_final_runs - (target - 1)),
            'over_events': ball_events
        }
        historical_matches.append(hist_entry)

        # Ball-by-ball situational states
        for _, row in inn2_over19.iterrows():
            balls_remaining = 6 - legal_balls_bowled
            if balls_remaining <= 0:
                break
            runs_required = target - curr_runs
            wickets_remaining = 10 - curr_wickets

            if runs_required <= 0 or wickets_remaining <= 0:
                break

            rrr = (runs_required / balls_remaining) * 6.0

            situations.append({
                'match_id': mid,
                'year': year,
                'date': date_str,
                'venue': venue,
                'batting_team': bat_team,
                'bowling_team': bowl_team,
                'striker': row['batter'],
                'bowler': row['bowler'],
                'runs_required': runs_required,
                'balls_remaining': balls_remaining,
                'wickets_remaining': wickets_remaining,
                'rrr': rrr,
                'batting_win': batting_win,
                'outcome': 'Chased' if batting_win else 'Defended',
                'final_runs_needed': target - runs_before19
            })

            curr_runs += row['total_runs']
            curr_wickets += row['wicket_taken']
            if row['is_legal']:
                legal_balls_bowled += 1

    sit_df = pd.DataFrame(situations)
    hist_df = pd.DataFrame(historical_matches)
    return sit_df, hist_df


def build_feature_dataset(sit_df, b_death, bowl_death, h2h, venue_stats):
    """
    Merge all engineered features into the situational dataset
    """
    print("Building consolidated feature matrix...")
    df_merged = sit_df.copy()

    df_merged = df_merged.merge(
        b_death[['batter', 'death_sr', 'death_avg']],
        left_on='striker', right_on='batter', how='left'
    ).rename(columns={'death_sr': 'batter_death_sr', 'death_avg': 'batter_death_avg'})

    df_merged = df_merged.merge(
        bowl_death[['bowler', 'death_econ', 'death_sr', 'death_dot_pct']],
        left_on='bowler', right_on='bowler', how='left'
    ).rename(columns={
        'death_econ': 'bowler_death_econ',
        'death_sr': 'bowler_death_sr',
        'death_dot_pct': 'bowler_death_dot_pct'
    })

    df_merged = df_merged.merge(
        h2h[['batter', 'bowler', 'h2h_runs', 'h2h_balls', 'h2h_dismissals', 'h2h_sr']],
        left_on=['striker', 'bowler'], right_on=['batter', 'bowler'], how='left'
    )

    df_merged = df_merged.merge(
        venue_stats[['venue', 'venue_avg_20th_runs', 'venue_chase_win_rate']],
        on='venue', how='left'
    )

    # Impute defaults for unseen pairs / edge cases
    df_merged['batter_death_sr'] = df_merged['batter_death_sr'].fillna(130.0)
    df_merged['batter_death_avg'] = df_merged['batter_death_avg'].fillna(22.0)
    df_merged['bowler_death_econ'] = df_merged['bowler_death_econ'].fillna(10.5)
    df_merged['bowler_death_sr'] = df_merged['bowler_death_sr'].fillna(20.0)
    df_merged['bowler_death_dot_pct'] = df_merged['bowler_death_dot_pct'].fillna(25.0)

    df_merged['h2h_runs'] = df_merged['h2h_runs'].fillna(0.0)
    df_merged['h2h_balls'] = df_merged['h2h_balls'].fillna(0.0)
    df_merged['h2h_dismissals'] = df_merged['h2h_dismissals'].fillna(0.0)
    df_merged['h2h_sr'] = df_merged['h2h_sr'].fillna(120.0)

    df_merged['venue_avg_20th_runs'] = df_merged['venue_avg_20th_runs'].fillna(11.2)
    df_merged['venue_chase_win_rate'] = df_merged['venue_chase_win_rate'].fillna(0.50)

    feature_cols = [
        'runs_required', 'balls_remaining', 'wickets_remaining', 'rrr',
        'batter_death_sr', 'batter_death_avg',
        'bowler_death_econ', 'bowler_death_sr', 'bowler_death_dot_pct',
        'h2h_runs', 'h2h_balls', 'h2h_dismissals', 'h2h_sr',
        'venue_avg_20th_runs', 'venue_chase_win_rate'
    ]

    return df_merged, feature_cols


def train_and_evaluate_models(df_features, feature_cols):
    """
    Train multiple classification models:
    - XGBoost
    - Random Forest
    - HistGradientBoosting
    - Logistic Regression

    Evaluate using:
    - ROC-AUC
    - Log Loss
    - Accuracy

    Selects top-performing model and fits on full data for deployment.
    """
    print("Training and evaluating candidate ML models...")
    X = df_features[feature_cols].copy()
    y = df_features['batting_win'].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    candidate_models = {
        'Logistic Regression': (LogisticRegression(max_iter=1000, C=1.0, random_state=42), True),
        'Random Forest': (RandomForestClassifier(n_estimators=120, max_depth=6, min_samples_leaf=3, random_state=42), False),
        'HistGradientBoosting': (HistGradientBoostingClassifier(max_iter=120, max_depth=4, learning_rate=0.06, random_state=42), False),
        'XGBoost': (xgb.XGBClassifier(n_estimators=120, max_depth=4, learning_rate=0.05, eval_metric='logloss', random_state=42), False)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    metrics_summary = []
    fitted_models = {}

    for name, (model, requires_scale) in candidate_models.items():
        X_used = X_scaled if requires_scale else X.values

        # 5-fold cross-validated out-of-fold predictions
        proba = cross_val_predict(model, X_used, y, cv=cv, method='predict_proba')[:, 1]
        preds = (proba >= 0.5).astype(int)

        auc = roc_auc_score(y, proba)
        loss = log_loss(y, proba)
        acc = accuracy_score(y, preds)

        metrics_summary.append({
            'Model': name,
            'ROC_AUC': float(auc),
            'Log_Loss': float(loss),
            'Accuracy': float(acc),
            'Composite_Score': float(auc - loss * 0.5)  # Higher is better
        })

        # Fit on full dataset for production inference
        model.fit(X_used, y)
        fitted_models[name] = model

    metrics_df = pd.DataFrame(metrics_summary).sort_values('ROC_AUC', ascending=False)
    print("\nCandidate Model Performance Leaderboard:")
    print(metrics_df.to_string(index=False))

    best_model_name = metrics_df.iloc[0]['Model']
    print(f"\nTop-performing model selected: {best_model_name}")

    return {
        'best_model_name': best_model_name,
        'metrics_df': metrics_df,
        'models': fitted_models,
        'scaler': scaler,
        'feature_cols': feature_cols
    }


def run_full_pipeline():
    df = load_and_preprocess_data()
    batters_by_team, bowlers_by_team = compute_team_player_mappings(df)
    b_death, bowl_death = compute_death_overs_metrics(df)
    h2h = compute_head_to_head_metrics(df)
    venue_stats = compute_venue_metrics(df)
    sit_df, hist_df = extract_situations_and_history(df)
    df_features, feature_cols = build_feature_dataset(sit_df, b_death, bowl_death, h2h, venue_stats)

    model_bundle = train_and_evaluate_models(df_features, feature_cols)

    # Save package to artifacts
    package = {
        'model_bundle': model_bundle,
        'batters_by_team': batters_by_team,
        'bowlers_by_team': bowlers_by_team,
        'b_death': b_death,
        'bowl_death': bowl_death,
        'h2h': h2h,
        'venue_stats': venue_stats,
        'historical_matches': hist_df,
        'situations_dataset': sit_df,
        'feature_cols': feature_cols,
        'all_teams': sorted(list(set(list(batters_by_team.keys()) + list(bowlers_by_team.keys())))),
        'venues': sorted(venue_stats['venue'].tolist())
    }

    save_path = os.path.join(ARTIFACT_DIR, 'pipeline_bundle.joblib')
    joblib.dump(package, save_path, compress=3)
    print(f"\nPipeline successfully saved to {save_path} (Size: {os.path.getsize(save_path):,} bytes)")

    return package


if __name__ == '__main__':
    run_full_pipeline()
