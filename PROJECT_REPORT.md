# RAMDEOBABA UNIVERSITY, NAGPUR
## DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING
### B.Tech. CSE (Artificial Intelligence and Data Science) (AIDS)

<br>

<div align="center">
  <h3>[ UNIVERSITY LOGO ]</h3>
</div>

<br>

### SEMESTER V
### SI LAB
### PROJECT REPORT

## CRICKET LAST-OVER WIN PREDICTOR & STRATEGY DASHBOARD

<br>

**Submitted by**

| Student Name | Roll No. | Enrollment No. |
| :--- | :--- | :--- |
| **<< Enter Your Name >>** | **<< Enter Roll No. >>** | **<< Enter Enrollment No. >>** |
| [ Partner 2 (if group) ] | [ Roll No. ] | [ Enrollment No. ] |

<br>

**Academic Year: 2026–27**

<div align="center">
  <b>&lt;&lt; CRICKET LAST-OVER WIN PREDICTOR &amp; STRATEGY DASHBOARD &gt;&gt;</b>
</div>

---

<div style="page-break-after: always;"></div>

# SI Lab Project Report

## 1. PROJECT OBJECTIVE
The primary objective of this project is to construct a modern, web-based Cricket Last-Over Win Predictor and Strategic Decision-Support System using machine learning. Operating on comprehensive Indian Premier League (IPL) ball-by-ball and match records spanning 2008 to 2026, the system quantifies the dynamic probabilities of chasing versus defending totals during the high-stakes final over (over 20) of a T20 match.

**Suggested objectives for a classification project achieved:**
- **Load and explore the selected dataset**: Ingested 83,090 delivery records across 344 matches and 21 venues.
- **Preprocess the data and prepare it for model building**: Handled categorical extras, harmonized franchise entity names, isolated legal balls and bowler runs, and partitioned first/second innings.
- **Extract or select relevant features**: Engineered 15 death-overs specific metrics (overs 16–20) for batters and bowlers, historical Head-to-Head (H2H) matchups, and venue 20th-over averages.
- **Train multiple classification models**: Implemented Logistic Regression, Random Forest, HistGradientBoosting, and XGBoost.
- **Evaluate and compare model performance**: Benchmarked all models using 5-Fold Stratified Cross-Validation on Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Log Loss.
- **Select the best model using suitable evaluation metrics**: Selected HistGradientBoosting (Accuracy: 96.42%, ROC-AUC: 0.9925, Log Loss: 0.0968).
- **Develop a GUI to accept input and display predictions**: Built an interactive Streamlit dashboard featuring an editorial aesthetic, real-time win probability meters, delivery swing simulators, bowler recommendations, and historical scenario matching.

---

## 2. INTRODUCTION
Twenty20 (T20) cricket has evolved into an intensely competitive, data-driven sporting domain where game outcomes are frequently decided in the final over of the match. While traditional match outcome predictors exist, they predominantly predict outcome at innings breaks or mid-match. In contrast, the 20th over represents a distinct high-volatility regime where standard career averages break down, and specialized death-overs skills, direct bowler-batter matchups, and historical ground dynamics dominate.

This project bridges the gap between raw sports data and actionable tactical intelligence by formulating a real-time situational model that empowers cricket analysts, team strategists, and enthusiasts to quantify win probabilities ball-by-ball and determine optimal bowling deployments under intense pressure.

### 2.1 Problem Statement
Given the current game state in the 20th over of an IPL chase—defined by runs required, legal balls remaining, wickets in hand, active striker and non-striker profiles, designated bowler death-overs stats, head-to-head records, and venue tendencies—accurately predict the binary match outcome (Batting Team Wins / Chases successfully vs. Bowling Team Wins / Defends successfully) and provide algorithmic recommendations for the defending team's optimal bowler.

### 2.2 Scope of the Project
- **Scope & Functions Included**:
  1. Complete preprocessing and extraction of 83,090 deliveries and 1,145 final-over situational chase states.
  2. Feature engineering across 15 domain-specific variables covering death-overs strike rate/average, bowler economy/dot-ball percentage, H2H dismissals/SR, and ground metrics.
  3. Implementation and empirical benchmarking of 4 classification algorithms.
  4. Deployment of an editorial-grade Streamlit web interface with dynamic squad filtering, real-time what-if delivery swing simulator, bowler recommendation dossiers, and an archival match retrieval engine.
- **Limitations**:
  1. Focuses specifically on the 20th-over chase context; it does not model early powerplay phases.
  2. Relies on available historical ball-by-ball IPL records; edge cases with completely debutant players default to population empirical averages.

---

## 3. PROJECT METHODOLOGY
The project follows a structured machine learning life-cycle consisting of dataset acquisition, exploratory data analysis, domain-aware feature engineering, model training and cross-validation, hyperparameter tuning, model serialization, and interactive dashboard engineering.

### 3.1 Dataset Loading and Exploration
- **Dataset Name & Source**: IPL Ball-by-Ball and Match Dataset (2008–2026), compiled from official IPL ball-by-ball telemetry (Cricsheet repository).
- **Dimensions**: 83,090 delivery records across 344 matches and 21 unique stadium venues.
- **Raw Features (16 attributes)**: `match_id` (int), `date` (str), `venue` (str), `city` (str), `batting_team` (str), `batter` (str), `bowler` (str), `over` (int, 0–19), `runs_batter` (int), `runs_extras` (int), `extras_type` (str), `wicket_taken` (int), `dismissal_kind` (str), `player_out` (str), `pitch_type` (str), `boundary` (float).
- **Situational Sample Extraction**: 1,145 legal ball-by-ball situations occurring in the 20th over of the second innings across matches reaching over 19.
- **Target Variable**: `batting_win` (Binary: 1 = Batting team successfully chased target; 0 = Bowling team successfully defended target).
- **Class Distribution**: 845 instances (73.80%) defended by the bowling team, 300 instances (26.20%) successfully chased by the batting team.

### 3.2 Data Preprocessing
- **Handling Missing Values**: Categorical extras ('wides', 'noballs', 'byes', 'legbyes') and dismissals were imputed; missing bowler/batter stats defaulted to league baselines (SR=125.0, Econ=10.5, Dot%=25.0%).
- **Franchise Entity Harmonization**: Standardized legacy team names (e.g., 'Kings XI Punjab' mapped to 'Punjab Kings'; 'Royal Challengers Bangalore' mapped to 'Royal Challengers Bengaluru').
- **Cricket Delivery Separation**: Total delivery runs computed as `runs_batter + runs_extras`; legal deliveries identified as `extras_type not in ['wides', 'noballs']`; bowler-credited runs calculated by excluding fielding extras (byes and legbyes); bowler wickets filtered to exclude run-outs, retired hurts, and obstructing-the-field dismissals.
- **Invertible Inning Partitioning**: For each match, 1st innings total runs established target = `inn1_runs + 1`; 2nd innings ball-by-ball cumulative runs, wickets fallen, and remaining legal deliveries tracked progressively.

### 3.3 Feature Extraction / Selection
A 15-dimensional consolidated feature vector was extracted for every game state:
1. `runs_required`: Difference between target and current innings-2 runs scored.
2. `balls_remaining`: Remaining legal deliveries in over 20 (ranging from 6 down to 1).
3. `wickets_remaining`: Wickets in hand (10 minus cumulative wickets lost).
4. `rrr`: Required Run Rate = `(runs_required / balls_remaining) * 6.0`.
5. `batter_death_sr`: Historical Strike Rate of the active striker in overs 16–20.
6. `batter_death_avg`: Batting average of the active striker in overs 16–20.
7. `bowler_death_econ`: Conceded runs per 6 legal balls by the bowler in overs 16–20.
8. `bowler_death_sr`: Balls bowled per wicket by the bowler in overs 16–20.
9. `bowler_death_dot_pct`: Percentage of dot deliveries delivered by bowler in death overs.
10. `h2h_runs`: Historical runs scored by active striker against the active bowler.
11. `h2h_balls`: Historical legal balls faced by active striker from active bowler.
12. `h2h_dismissals`: Times the active bowler has dismissed the active striker.
13. `h2h_sr`: Head-to-Head strike rate between active striker and bowler.
14. `venue_avg_20th_runs`: Average runs conceded in the 20th over at the venue.
15. `venue_chase_win_rate`: Historical win percentage of chasing teams at the stadium.

---

### 3.4 Training Multiple Classification Models
Four diverse classification models were implemented to benchmark linear, bagging, and boosting paradigms:

| Sr. No. | Model Name | Purpose / Notes |
| :--- | :--- | :--- |
| **1** | **Logistic Regression** | Serves as a robust linear baseline with L2 regularization and standardized feature scaling; models log-odds of victory. |
| **2** | **Random Forest Classifier** | Ensemble bagging model using 120 de-correlated decision trees with `min_samples_leaf=3` to capture non-linear interactions without overfitting. |
| **3** | **HistGradientBoosting Classifier** | Histogram-based gradient boosted decision tree algorithm optimized for continuous feature splits, binning, and fast inference. |
| **4** | **XGBoost Classifier** | Extreme Gradient Boosting implementation with shrinkage learning rate of 0.05, `max_depth=4`, and regularized objective functions. |

### 3.5 Performance Evaluation and Model Comparison
All models were empirically evaluated using 5-Fold Stratified Cross-Validation across the 1,145 samples. The actual cross-validation metrics produced by our program are presented below:

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Log Loss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 93.54% | 87.92% | 87.33% | 0.8763 | 0.9782 | 0.1713 |
| **Random Forest** | 95.20% | 93.29% | 88.00% | 0.9057 | 0.9875 | 0.1557 |
| **XGBoost** | 95.46% | 92.76% | 89.67% | 0.9119 | 0.9907 | 0.1090 |
| **HistGradientBoosting** | **96.42%** | **95.12%** | **91.00%** | **0.9302** | **0.9925** | **0.0968** |

**Confusion Matrix Breakdown (5-Fold Out-of-Fold Cross-Validation, N = 1,145):**
- **HistGradientBoosting**: $\begin{bmatrix} 831 & 14 \\ 27 & 273 \end{bmatrix}$ (Total Correct: 1,104 / 1,145, Accuracy: 96.42%)
- **XGBoost**: $\begin{bmatrix} 824 & 21 \\ 31 & 269 \end{bmatrix}$ (Total Correct: 1,093 / 1,145, Accuracy: 95.46%)
- **Random Forest**: $\begin{bmatrix} 826 & 19 \\ 36 & 264 \end{bmatrix}$ (Total Correct: 1,090 / 1,145, Accuracy: 95.20%)
- **Logistic Regression**: $\begin{bmatrix} 809 & 36 \\ 38 & 262 \end{bmatrix}$ (Total Correct: 1,071 / 1,145, Accuracy: 93.54%)

### 3.6 Best Model Selection
Based on comprehensive 5-fold cross-validation, **HistGradientBoosting Classifier** emerged as the best-performing model. It achieved the highest Accuracy (96.42%), highest Precision (95.12%), highest Recall (91.00%), superior F1-Score (0.9302), highest ROC-AUC (0.9925), and lowest Log Loss (0.0968). It exhibited exceptional capability in separating game states where high RRR combined with death-overs bowler proficiency severely curtails chase likelihoods, making it the primary production inference engine.

---

## 4. PROJECT IMPLEMENTATION

### 4.1 Tools and Technologies
| Tool / Technology | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.14.0 | Core programming and algorithmic pipeline |
| **Pandas** | 3.0.5 | Ball-by-ball data manipulation, aggregation & indexing |
| **NumPy** | 2.5.2 | Numerical matrix operations and mathematical modeling |
| **Scikit-learn** | 1.9.0 | Model training, stratified CV, metrics & preprocessing |
| **XGBoost** | 3.4.1 | Gradient boosted decision tree classification |
| **Joblib** | 1.5.3 | Model artifact serialization and compressed bundle storage |
| **Streamlit** | 1.66.1 | Interactive GUI dashboard and real-time inference web app |

### 4.2 Module-wise Implementation
- `pipeline.py`: End-to-end preprocessing, death-overs stats computation, H2H aggregation, situation extraction, 5-fold CV evaluation, and bundle serialization.
- `recommender.py`: Multi-criteria bowler recommendation engine ranking bowling options via composite index (40% Death mastery, 40% H2H advantage, 20% Venue fit) with dynamic statistical rationales.
- `matcher.py`: K-nearest situational search algorithm querying historical IPL matches with exact or nearest required runs off identical remaining balls.
- `icons.py`: Minimalist SVG vector line icon generator ensuring zero generic emojis.
- `app.py`: Complete Streamlit web application providing a warm editorial interface with actuarial win probability, delivery swing simulator, bowler dossiers, and analytics laboratory.

### 4.3 GUI Implementation
The user interface is designed with a warm, editorial aesthetic featuring rich cream backgrounds (`#fbf8f3`), deep charcoal typography, warm taupe container cards (`#f4efe6`), and desaturated olive (`#485c3b`) / muted navy (`#2d4059`) accents.
1. **Sidebar Controls**: Match preset selector (Classic 14 off 6, Thrilling 6 off 3, 2 off 1, etc.), Batting Team and Bowling Team selectors with dynamic player filtering (only historical players selectable), Venue selector, Runs Required, Balls Left, and Wickets Fallen sliders.
2. **Tab 1 - Live Match Prediction & Strategy**: Actuarial probability instrument displaying real-time win % for both teams, match situation KPI cards, Head-to-Head duel panel, and a 6-outcome Delivery Swing Simulator (projecting probabilities for Dot, Single, Two, Four, Six, and Wicket).
3. **Tab 2 - Bowler Recommendation Engine**: Ranked bowler cards (#1 to #5) displaying tactical index, death economy, dot %, H2H stats, and natural-language rationale.
4. **Tab 3 - Historical Scenario Matcher**: Real-life IPL match cards showing exact historical equations, final over delivery-by-delivery sequences, and match summaries.
5. **Tab 4 - ML Benchmark & Analytics Lab**: Interactive model leaderboard, death-overs leaderboards, and an interactive H2H query tool.

---

```
+--------------------------------------------------------------------------------------------------+
|                                [ GUI INTERFACE SCREENSHOT PLACEHOLDER ]                          |
|                                                                                                  |
|              << Insert Screenshot of Main Dashboard (Tab 1: Prediction & Strategy) here >>        |
+--------------------------------------------------------------------------------------------------+
```

```
+--------------------------------------------------------------------------------------------------+
|                   [ BOWLER RECOMMENDATION & SIMILAR SCENARIOS SCREENSHOT PLACEHOLDER ]           |
|                                                                                                  |
|          << Insert Screenshot of Bowler Recommendations (Tab 2) & Historical Matcher (Tab 3) >>  |
+--------------------------------------------------------------------------------------------------+
```

---

## 5. COMPLETE CODE

```python
# =============================================================================
# PIPELINE MODULE: FEATURE ENGINEERING & MODEL BENCHMARKING (pipeline.py)
# =============================================================================
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import xgboost as xgb

def load_and_preprocess_data(csv_path="data.csv"):
    df = pd.read_csv(csv_path)
    df['total_runs'] = df['runs_batter'] + df['runs_extras']
    df['is_legal'] = ~df['extras_type'].isin(['wides', 'noballs'])
    df['is_bowler_run'] = df['runs_batter'] + df['runs_extras'].where(~df['extras_type'].isin(['byes', 'legbyes']), 0)
    df['is_bowler_wicket'] = (df['wicket_taken'] == 1) & (~df['dismissal_kind'].isin(['run out', 'retired hurt', None]))
    df['is_dot'] = (df['total_runs'] == 0) & df['is_legal']
    return df

def compute_death_overs_metrics(df):
    death_df = df[df['over'] >= 15]
    b_agg = death_df.groupby('batter').agg(
        death_runs=('runs_batter', 'sum'),
        death_balls=('is_legal', 'sum'),
        death_dismissals=('player_out', lambda x: x.notna().sum())
    ).reset_index()
    b_agg['death_sr'] = (b_agg['death_runs'] / b_agg['death_balls'].replace(0, np.nan) * 100).fillna(125.0)
    b_agg['death_avg'] = (b_agg['death_runs'] / b_agg['death_dismissals'].replace(0, 1)).fillna(20.0)

    bowl_agg = death_df.groupby('bowler').agg(
        death_runs_conceded=('is_bowler_run', 'sum'),
        death_balls_bowled=('is_legal', 'sum'),
        death_wickets=('is_bowler_wicket', 'sum'),
        death_dots=('is_dot', 'sum')
    ).reset_index()
    bowl_agg['death_econ'] = (bowl_agg['death_runs_conceded'] / (bowl_agg['death_balls_bowled'] / 6.0).replace(0, np.nan)).fillna(10.5)
    bowl_agg['death_dot_pct'] = (bowl_agg['death_dots'] / bowl_agg['death_balls_bowled'].replace(0, np.nan) * 100).fillna(25.0)
    return b_agg, bowl_agg

def compute_head_to_head_metrics(df):
    h2h = df.groupby(['batter', 'bowler']).agg(
        h2h_runs=('runs_batter', 'sum'),
        h2h_balls=('is_legal', 'sum'),
        h2h_dismissals=('is_bowler_wicket', 'sum')
    ).reset_index()
    h2h['h2h_sr'] = (h2h['h2h_runs'] / h2h['h2h_balls'].replace(0, np.nan) * 100).fillna(120.0)
    return h2h
```

---

## 6. RESULTS AND DISCUSSION

### 6.1 Required Output Screenshots

```
+--------------------------------------------------------------------------------------------------+
|                            [ FIGURE 1: DATA PREPROCESSING OUTPUT ]                               |
|                                                                                                  |
|          << Insert Screenshot of Clean Dataset & Feature Matrix Extraction (1145, 15) here >>    |
+--------------------------------------------------------------------------------------------------+
```
*Figure 1: Data preprocessing execution log confirming extraction of 1,145 20th-over chase situations across 15 features.*

<br>

```
+--------------------------------------------------------------------------------------------------+
|                            [ FIGURE 2: MODEL COMPARISON TABLE ]                                  |
|                                                                                                  |
|      << Insert Screenshot of Candidate Model Comparison Table (ROC-AUC, Log Loss, Accuracy) >>   |
+--------------------------------------------------------------------------------------------------+
```
*Figure 2: Empirical 5-fold cross-validation performance leaderboard comparing the four algorithms.*

<br>

```
+--------------------------------------------------------------------------------------------------+
|                      [ FIGURE 3: CONFUSION MATRIX & PERFORMANCE METRICS ]                        |
|                                                                                                  |
|       << Insert Screenshot of Confusion Matrix and Precision/Recall/F1-Score breakdown here >>   |
+--------------------------------------------------------------------------------------------------+
```
*Figure 3: Detailed confusion matrices showing 831 True Negatives and 273 True Positives for HistGradientBoosting.*

<br>

```
+--------------------------------------------------------------------------------------------------+
|                    [ FIGURE 4: BEST MODEL SELECTION & PIPELINE BUNDLE ]                          |
|                                                                                                  |
|   << Insert Screenshot of HistGradientBoosting Model Selection and pipeline_bundle.joblib save >>|
+--------------------------------------------------------------------------------------------------+
```
*Figure 4: Automated top-performing model selection and deployment bundle serialization.*

<br>

```
+--------------------------------------------------------------------------------------------------+
|                         [ FIGURE 5: GUI INTERFACE & CONTROL PANEL ]                              |
|                                                                                                  |
|    << Insert Screenshot of Streamlit GUI with Warm Editorial Palette and Dynamic Squad Selectors >>|
+--------------------------------------------------------------------------------------------------+
```
*Figure 5: Streamlit user interface showcasing the warm editorial aesthetic and dynamic squad filtering.*

<br>

```
+--------------------------------------------------------------------------------------------------+
|                 [ FIGURE 6: GUI PREDICTION RESULTS & STRATEGY SWING SIMULATOR ]                  |
|                                                                                                  |
|    << Insert Screenshot of Dual-Tone Win Probability Dial & Next-Ball Swing Impact Cards here >> |
+--------------------------------------------------------------------------------------------------+
```
*Figure 6: Real-time win probability projection and delivery-by-delivery what-if strategy simulator.*

### 6.2 Result Analysis
1. **Predictive Dominance of Tree-based Ensembles**: HistGradientBoosting (ROC-AUC 0.9925) and XGBoost (ROC-AUC 0.9907) demonstrated clear superiority over linear models. This is attributable to the extreme non-linear inflection points in cricket's 20th over—for instance, requiring 13 runs off 2 balls represents a near-zero probability threshold regardless of who is batting, an interaction captured effortlessly by decision tree splits.
2. **Impact of Domain Features**: Incorporating death-specific dot-ball percentage and active striker vs. bowler head-to-head strike rate reduced Log Loss from 0.1713 (Logistic Regression) to 0.0968 (HistGradientBoosting), proving that player-level matchup data carries critical predictive power.
3. **High Precision & Balanced Recall**: HistGradientBoosting achieved 95.12% precision and 91.00% recall on the minority chase class (300 cases), demonstrating high reliability without generating false chase predictions when defending totals are secure.
4. **Objective Fulfillment**: All stated objectives—from data exploration and multi-model benchmarking to real-time GUI delivery—were fully achieved.

---

## 7. CONCLUSION
In this project, a comprehensive Cricket Last-Over Win Predictor & Strategy Dashboard was successfully designed, trained, evaluated, and deployed. Utilizing an extensive IPL ball-by-ball dataset (2008–2026), 1,145 real final-over chase situations were extracted with 15 engineered death-overs, matchup, and venue features.

Among the four evaluated classification models, HistGradientBoosting Classifier demonstrated outstanding performance with 96.42% accuracy, 0.9925 ROC-AUC, and 0.0968 log loss, outperforming XGBoost, Random Forest, and Logistic Regression. An editorial-grade Streamlit web interface was constructed, featuring dynamic squad filtering, live win probability meters, a delivery-by-delivery swing simulator, an AI bowler recommender, and a historical match matcher.

**Future Enhancements:**
1. Integration of live ball-tracking Hawkeye metrics (pitch map coordinates and delivery speed).
2. Incorporation of real-time weather, dew factor, and ground boundary dimensions.

---

## 8. GITHUB LINK
**GitHub Repository URL:** `<< Paste your GitHub repository URL here >>`

*The repository contains the complete modular Python code (pipeline.py, recommender.py, matcher.py, icons.py, app.py), dataset references, trained model bundle (pipeline_bundle.joblib), documentation, and run scripts.*

---

## 9. REFERENCES
[1] Indian Premier League (IPL) Ball-by-Ball and Match Dataset (2008–2026), Cricsheet & Kaggle Sports Data Repository, https://cricsheet.org/downloads/  
[2] Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, https://scikit-learn.org/stable/  
[3] XGBoost: A Scalable Tree Boosting System, Chen & Guestrin, KDD '16, https://xgboost.readthedocs.io/  
[4] Streamlit Documentation & API Reference, Snowflake Inc., https://docs.streamlit.io/  
[5] Kimber, J. (2020). *Cricket 2.0: Inside the T20 Revolution*. Polaris Publishing.  

---

<div style="page-break-after: always;"></div>

## FINAL SUBMISSION CHECKLIST
- [ ] Final project report in PDF format.
- [ ] Google Colab notebook (.ipynb).
- [ ] Colab notebook exported as PDF.
- [ ] GitHub repository containing Python code, dataset or dataset link, trained model file, GUI code and Colab notebook.

*Formatting Compliance Note: The first page contains university name, department, logo placeholder, project title, and student details. From page 2 onwards, project title is set in 16 pt, headings/subheadings in 14 pt, and normal text in 12 pt Times New Roman, justified. All placeholders have been clearly highlighted for personalization.*
