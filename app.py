"""
Cricket Last-Over Win Predictor & Strategy Dashboard
Warm, Editorial Aesthetic (IPL 2008-2026 Dataset)
Rich cream background, deep charcoal typography, warm taupe container cards,
and desaturated olive / muted navy accent colors.
"""

import os
import warnings
os.environ['LOKY_MAX_CPU_COUNT'] = '4'
warnings.filterwarnings('ignore')

import base64
import textwrap
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Custom modules
from recommender import BowlerRecommender
from matcher import HistoricalMatcher
from icons import icon_svg

# Helper functions to reliably render raw HTML without markdown code block parsing issues
def render_html(html_str):
    st.html(textwrap.dedent(html_str).strip())

def render_sidebar_html(html_str):
    st.sidebar.html(textwrap.dedent(html_str).strip())

# Set Streamlit page configuration
st.set_page_config(
    page_title="Cricket Last-Over Win Predictor & Strategy Engine",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_PATH = os.path.join(BASE_DIR, 'artifacts', 'pipeline_bundle.joblib')
SVG_BG_PATH = os.path.join(BASE_DIR, 'stadium_bg.svg')


@st.cache_resource
def load_bundle():
    if not os.path.exists(BUNDLE_PATH):
        import pipeline
        return pipeline.run_full_pipeline()
    return joblib.load(BUNDLE_PATH)


bundle = load_bundle()
recommender = BowlerRecommender(bundle)
matcher = HistoricalMatcher(bundle)

# Load architectural SVG background and encode as base64
with open(SVG_BG_PATH, "r", encoding="utf-8") as f:
    svg_content = f.read()
svg_base64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")

# Warm Editorial Theme CSS
editorial_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Global Reset & Base Typography */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #24282f;
}}

/* Main Application Background: Rich Cream */
.stApp {{
    background-color: #fbf8f3 !important;
}}

/* Subtle Architectural Stadium Watermark (Exactly 20% Opacity) */
.stadium-bg-layer {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: url('data:image/svg+xml;base64,{svg_base64}');
    background-size: cover;
    background-position: center bottom;
    background-repeat: no-repeat;
    opacity: 0.20 !important; /* EXACTLY 20% OPACITY */
    pointer-events: none;
    z-index: 0;
}}

.main, .block-container {{
    position: relative;
    z-index: 1;
    max-width: 1320px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
}}

/* Streamlit Sidebar Overrides */
[data-testid="stSidebar"] {{
    background-color: #f4eee4 !important;
    border-right: 1px solid #dfd8cb !important;
}}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stSlider label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #3d434d !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Input widgets styling: crisp warm paper with grounded tactile border */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput div[data-baseweb="input"] > div,
.stTextInput div[data-baseweb="input"] > div {{
    background-color: #ffffff !important;
    border: 1px solid #d5ccbe !important;
    border-radius: 6px !important;
    color: #24282f !important;
    box-shadow: 0 1px 2px rgba(35, 30, 20, 0.03);
}}

/* Editorial Masthead / Header */
.editorial-masthead {{
    border-bottom: 2px solid #2d2a24;
    padding-bottom: 18px;
    margin-bottom: 24px;
}}

.masthead-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #5d6655;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.masthead-title {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 34px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #1a1e24;
    margin: 0;
    line-height: 1.15;
}}

.masthead-subtitle {{
    font-size: 14px;
    color: #555c66;
    margin-top: 8px;
    margin-bottom: 0;
    line-height: 1.5;
    max-width: 860px;
}}

/* Badges: Editorial tactile pills */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-family: 'JetBrains Mono', monospace;
}}

.badge-olive {{
    background: #ebf0e6;
    color: #3b5030;
    border: 1px solid #c2cfb8;
}}

.badge-navy {{
    background: #e7edf5;
    color: #2c3f56;
    border: 1px solid #bccbde;
}}

.badge-terracotta {{
    background: #f8ebe8;
    color: #9c4132;
    border: 1px solid #e5c0ba;
}}

.badge-bronze {{
    background: #f7f1e4;
    color: #8c6d31;
    border: 1px solid #dfd2bb;
}}

.badge-neutral {{
    background: #eae4d8;
    color: #4a515c;
    border: 1px solid #d4ccbf;
}}

/* Warm Taupe Container Panels */
.editorial-panel {{
    background: #f4efe6;
    border: 1px solid #dfd8cb;
    border-radius: 8px;
    padding: 20px 22px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(35, 30, 20, 0.04);
}}

.panel-header {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 19px;
    font-weight: 700;
    color: #1a1e24;
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #e4ddd1;
    padding-bottom: 10px;
}}

/* Tactile Stat Box */
.stat-box {{
    background: #ffffff;
    border: 1px solid #dfd8cc;
    border-radius: 6px;
    padding: 12px 14px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(35, 30, 20, 0.02);
}}

.stat-label {{
    font-size: 11px;
    text-transform: uppercase;
    color: #636b76;
    font-weight: 600;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}}

.stat-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 21px;
    font-weight: 700;
    color: #1a1e24;
}}

/* Win Probability Instrument */
.meter-card {{
    background: #f4eee4;
    border: 1px solid #ded6c7;
    border-radius: 8px;
    padding: 24px 26px;
    margin-bottom: 22px;
    box-shadow: 0 1px 4px rgba(35, 30, 20, 0.04);
}}

.team-win-display {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 12px;
}}

.team-win-name {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.2px;
}}

.team-win-pct {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
}}

.pct-batting {{
    color: #3b5030; /* Desaturated Olive */
}}

.pct-bowling {{
    color: #2c3f56; /* Muted Navy */
}}

.dual-bar-wrapper {{
    height: 16px;
    background: #e2dbce;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    border: 1px solid #d5ccbe;
    margin: 14px 0 14px 0;
}}

.bar-batting {{
    background: #485c3b; /* Desaturated Olive */
    height: 100%;
    transition: width 0.4s ease;
}}

.bar-bowling {{
    background: #2d4059; /* Muted Navy */
    height: 100%;
    transition: width 0.4s ease;
}}

/* Bowler Recommendation Card */
.bowler-card {{
    background: #f6f1e8;
    border: 1px solid #dfd8cb;
    border-radius: 6px;
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: 0 1px 2px rgba(35, 30, 20, 0.03);
}}

.rank-badge {{
    width: 28px;
    height: 28px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 13px;
}}

.rank-1 {{ background: #ebf0e6; color: #3b5030; border: 1px solid #c2cfb8; }}
.rank-2 {{ background: #e7edf5; color: #2c3f56; border: 1px solid #bccbde; }}
.rank-3 {{ background: #f7f1e4; color: #8c6d31; border: 1px solid #dfd2bb; }}
.rank-default {{ background: #eae4d8; color: #5a616d; border: 1px solid #d4ccbf; }}

/* Historical Match Card */
.match-card {{
    background: #f6f1e8;
    border: 1px solid #dfd8cb;
    border-radius: 6px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 2px rgba(35, 30, 20, 0.03);
}}

.match-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
}}

.match-card-meta {{
    font-size: 12.5px;
    color: #636b76;
    margin-bottom: 10px;
}}

.match-card-situation {{
    background: #ffffff;
    border: 1px solid #e2dbce;
    padding: 10px 14px;
    border-radius: 4px;
    margin-bottom: 10px;
    font-size: 12.5px;
    color: #24282f;
}}

.match-card-highlight {{
    font-size: 13px;
    color: #24282f;
    padding: 10px 14px;
    border-radius: 4px;
    line-height: 1.5;
}}

.highlight-chased {{
    background: #ebf0e6;
    border-left: 3px solid #485c3b;
}}

.highlight-defended {{
    background: #f8ebe8;
    border-left: 3px solid #9c4132;
}}

.highlight-tied {{
    background: #f7f1e4;
    border-left: 3px solid #8c6d31;
}}

/* Streamlit Tabs in Editorial Tone */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid #dfd8cb;
    margin-bottom: 18px;
}}

.stTabs [data-baseweb="tab"] {{
    padding: 9px 18px;
    background: transparent;
    border-radius: 4px 4px 0 0;
    color: #636b76;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: 0.3px;
}}

.stTabs [aria-selected="true"] {{
    background: #f4eee4 !important;
    color: #3b5030 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #485c3b !important;
}}
</style>
<div class="stadium-bg-layer"></div>
"""

st.html(editorial_css)

# Application Header & Model Metadata
model_bundle = bundle['model_bundle']
best_model_name = model_bundle['best_model_name']
metrics_df = model_bundle['metrics_df']

# Sidebar Configuration
render_sidebar_html(f"""
<div style="border-bottom: 1px solid #dfd8cb; padding-bottom: 12px; margin-bottom: 14px;">
    <div style="font-family:'JetBrains Mono',monospace; font-size:10.5px; color:#5d6655; font-weight:600; text-transform:uppercase; letter-spacing:1px;">
        CONTROL PANEL
    </div>
    <div style="font-family:'Newsreader',Georgia,serif; font-size:19px; font-weight:700; color:#1a1e24; margin-top:2px;">
        Match Scenario
    </div>
</div>
""")

all_teams = bundle['all_teams']
venues = bundle['venues']
batters_by_team = bundle['batters_by_team']
bowlers_by_team = bundle['bowlers_by_team']

# Model Switcher in Sidebar (Auto selects top performing model by default)
model_options = list(model_bundle['models'].keys())
selected_model_name = st.sidebar.selectbox(
    "Active Inference ML Model",
    model_options,
    index=model_options.index(best_model_name)
)

selected_model_roc = metrics_df.loc[metrics_df['Model'] == selected_model_name, 'ROC_AUC'].values[0]

# Application Top Masthead
render_html(f"""
<div class="editorial-masthead">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
        <div>
            <div class="masthead-eyebrow">
                {icon_svg("activity", size=14, color="#485c3b")}
                SPORTS ANALYTICS MONOGRAPH • IPL INTELLIGENCE ARCHIVE
            </div>
            <h1 class="masthead-title">
                The Cricket Last-Over Win Predictor & Strategy Engine
            </h1>
            <p class="masthead-subtitle">
                An empirical decision-support platform delivering real-time match outcome probabilities, algorithmic death-overs bowler selection, and historical scenario retrieval across IPL seasons (2008–2026).
            </p>
        </div>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:4px;">
            <div class="badge badge-olive">
                {icon_svg("award", size=13, color="#3b5030")} {selected_model_name.upper()}
            </div>
            <div class="badge badge-navy">
                {icon_svg("bar_chart", size=13, color="#2c3f56")} ROC-AUC: {selected_model_roc:.4f}
            </div>
            <div class="badge badge-bronze">
                {icon_svg("database", size=13, color="#8c6d31")} IPL 2008–2026
            </div>
        </div>
    </div>
</div>
""")

# Preset Scenarios Selector
st.sidebar.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
preset = st.sidebar.selectbox(
    "Scenario Preset",
    [
        "Custom Equation",
        "Classic 14 Needed off 6 Balls",
        "Thrilling 6 Needed off 3 Balls",
        "Nail-biter 2 Needed off 1 Ball",
        "High Pressure 20 Needed off 6 Balls",
        "Rinku Singh Miracle (29 off 6 Balls)"
    ]
)

# Preset Values
default_runs = 14
default_balls = 6
default_wkts = 5

if preset == "Classic 14 Needed off 6 Balls":
    default_runs, default_balls, default_wkts = 14, 6, 5
elif preset == "Thrilling 6 Needed off 3 Balls":
    default_runs, default_balls, default_wkts = 6, 3, 6
elif preset == "Nail-biter 2 Needed off 1 Ball":
    default_runs, default_balls, default_wkts = 2, 1, 7
elif preset == "High Pressure 20 Needed off 6 Balls":
    default_runs, default_balls, default_wkts = 20, 6, 6
elif preset == "Rinku Singh Miracle (29 off 6 Balls)":
    default_runs, default_balls, default_wkts = 29, 6, 7

# Team Selection
default_bat_team = "Chennai Super Kings" if "Chennai Super Kings" in all_teams else all_teams[0]
batting_team = st.sidebar.selectbox("Batting Team (Chasing)", all_teams, index=all_teams.index(default_bat_team))

bowling_teams_available = [t for t in all_teams if t != batting_team]
default_bowl_team = "Mumbai Indians" if "Mumbai Indians" in bowling_teams_available else bowling_teams_available[0]
bowling_team = st.sidebar.selectbox("Bowling Team (Defending)", bowling_teams_available, index=bowling_teams_available.index(default_bowl_team))

# Dynamic Player Filtering: strictly players who played for the chosen team
team_batters = batters_by_team.get(batting_team, [])
if not team_batters:
    team_batters = ["MS Dhoni", "RD Gaikwad", "RA Jadeja"]

striker = st.sidebar.selectbox("Active Striker", team_batters, index=0)

non_striker_options = [b for b in team_batters if b != striker]
if not non_striker_options:
    non_striker_options = team_batters
non_striker = st.sidebar.selectbox("Non-Striker Partner", non_striker_options, index=min(1, len(non_striker_options) - 1))

team_bowlers = bowlers_by_team.get(bowling_team, [])
if not team_bowlers:
    team_bowlers = ["JJ Bumrah", "TA Boult"]
active_bowler = st.sidebar.selectbox("Designated Bowler", team_bowlers, index=0)

# Venue & Equation Controls
st.sidebar.markdown("<hr style='border:none; border-top:1px solid #dfd8cb; margin:14px 0;'/>", unsafe_allow_html=True)
default_venue = "Wankhede Stadium, Mumbai" if "Wankhede Stadium, Mumbai" in venues else venues[0]
venue = st.sidebar.selectbox("Match Stadium / Venue", venues, index=venues.index(default_venue))

col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    runs_required = st.number_input("Runs Required", min_value=1, max_value=36, value=default_runs, step=1)
with col_sb2:
    balls_remaining = st.number_input("Balls Left", min_value=1, max_value=6, value=default_balls, step=1)

wickets_fallen = st.sidebar.slider("Wickets Fallen", min_value=0, max_value=9, value=default_wkts, step=1)
wickets_remaining = 10 - wickets_fallen

# Historical Venue Insights
venue_row = bundle['venue_stats'][bundle['venue_stats']['venue'] == venue]
venue_avg_runs = venue_row['venue_avg_20th_runs'].values[0] if not venue_row.empty else 11.2
venue_chase_rate = venue_row['venue_chase_win_rate'].values[0] if not venue_row.empty else 0.50

render_sidebar_html(f"""
<div style="background:#ffffff; padding:10px 12px; border-radius:6px; border:1px solid #dfd8cb; margin-top:10px; font-size:11.5px; color:#555c66; line-height:1.5;">
    <div><strong>Venue 20th Over Avg:</strong> <span style="color:#1a1e24; font-family:'JetBrains Mono'; font-weight:600;">{venue_avg_runs:.1f} runs</span></div>
    <div><strong>Historical Chase Win:</strong> <span style="color:#3b5030; font-family:'JetBrains Mono'; font-weight:600;">{venue_chase_rate * 100:.1f}%</span></div>
</div>
""")

# Required Run Rate
rrr = (runs_required / balls_remaining) * 6.0

# Extract death and H2H metrics for selected players
death_b_row = recommender.b_death_map.get(striker, {'death_sr': 130.0, 'death_avg': 22.0})
death_bowl_row = recommender.bowl_death_map.get(active_bowler, {'death_econ': 10.5, 'death_sr': 20.0, 'death_dot_pct': 25.0})
h2h_row = recommender.h2h_map.get((striker, active_bowler), {'h2h_runs': 0, 'h2h_balls': 0, 'h2h_dismissals': 0, 'h2h_sr': 120.0})

# Assemble Feature Vector
feature_dict = {
    'runs_required': runs_required,
    'balls_remaining': balls_remaining,
    'wickets_remaining': wickets_remaining,
    'rrr': rrr,
    'batter_death_sr': death_b_row.get('death_sr', 130.0),
    'batter_death_avg': death_b_row.get('death_avg', 22.0),
    'bowler_death_econ': death_bowl_row.get('death_econ', 10.5),
    'bowler_death_sr': death_bowl_row.get('death_sr', 20.0),
    'bowler_death_dot_pct': death_bowl_row.get('death_dot_pct', 25.0),
    'h2h_runs': h2h_row.get('h2h_runs', 0.0),
    'h2h_balls': h2h_row.get('h2h_balls', 0.0),
    'h2h_dismissals': h2h_row.get('h2h_dismissals', 0.0),
    'h2h_sr': h2h_row.get('h2h_sr', 120.0),
    'venue_avg_20th_runs': venue_avg_runs,
    'venue_chase_win_rate': venue_chase_rate
}

feature_order = bundle['feature_cols']
X_input = pd.DataFrame([feature_dict])[feature_order]

# Model Inference
active_model = model_bundle['models'][selected_model_name]
if selected_model_name == 'Logistic Regression':
    X_input_scaled = model_bundle['scaler'].transform(X_input)
    batting_win_prob = float(active_model.predict_proba(X_input_scaled)[0, 1])
else:
    batting_win_prob = float(active_model.predict_proba(X_input.values)[0, 1])

# Boundary adjustments for cricket realities
if runs_required <= 0:
    batting_win_prob = 1.0
elif wickets_remaining <= 0:
    batting_win_prob = 0.0
elif runs_required > (balls_remaining * 6):
    batting_win_prob = 0.0
else:
    batting_win_prob = float(np.clip(batting_win_prob, 0.01, 0.99))

bowling_win_prob = 1.0 - batting_win_prob
batting_pct = round(batting_win_prob * 100, 1)
bowling_pct = round(bowling_win_prob * 100, 1)

# Tab Navigation
tabs = st.tabs([
    "Live Match Prediction & Strategy",
    "Bowler Recommendation Engine",
    "Historical Scenario Matcher",
    "ML Benchmark & Analytics Lab"
])

# ==========================================
# TAB 1: Live Match Prediction & Strategy
# ==========================================
with tabs[0]:
    # Real-time Win Probability Instrument
    pressure_label = 'EXTREME' if rrr >= 15 else ('HIGH' if rrr >= 11 else ('BALANCED' if rrr >= 8 else 'LOW'))
    pressure_badge_class = 'badge-terracotta' if rrr >= 15 else ('badge-bronze' if rrr >= 11 else 'badge-olive')

    render_html(f"""
    <div class="meter-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:600; text-transform:uppercase; color:#5d6655; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                {icon_svg("gauge", size=15, color="#485c3b")} ACTUARIAL PROBABILITY PROJECTION
            </span>
            <div style="display:flex; gap:8px; align-items:center;">
                <span class="badge {pressure_badge_class}">PRESSURE: {pressure_label}</span>
                <span style="font-size:12px; color:#555c66; font-family:'JetBrains Mono',monospace;">
                    EQUATION: {runs_required} RUNS OFF {balls_remaining} BALLS ({wickets_remaining} WKTS)
                </span>
            </div>
        </div>
        <div class="team-win-display">
            <div>
                <div class="team-win-name" style="color:#2d3a27;">{batting_team}</div>
                <div style="font-size:11.5px; color:#636b76; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">Chasing Target</div>
            </div>
            <div class="team-win-pct pct-batting">{batting_pct}%</div>
            <div style="text-align:right;">
                <div class="team-win-pct pct-bowling">{bowling_pct}%</div>
                <div style="font-size:11.5px; color:#636b76; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">Defending Target</div>
            </div>
            <div style="text-align:right;">
                <div class="team-win-name" style="color:#213042;">{bowling_team}</div>
            </div>
        </div>
        <div class="dual-bar-wrapper">
            <div class="bar-batting" style="width: {batting_pct}%;"></div>
            <div class="bar-bowling" style="width: {bowling_pct}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:'JetBrains Mono',monospace; color:#636b76;">
            <span>BAT WIN PROBABILITY: {batting_pct}%</span>
            <span>MATCH GROUND: {venue[:32]}</span>
            <span>BOWL WIN PROBABILITY: {bowling_pct}%</span>
        </div>
    </div>
    """)

    # 4 Match Situation KPI Stat Boxes
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        render_html(f"""
        <div class="stat-box">
            <div class="stat-label">Required Run Rate (RRR)</div>
            <div class="stat-value" style="color:{'#9c4132' if rrr >= 16 else ('#8c6d31' if rrr >= 11 else '#3b5030')};">{rrr:.2f}</div>
        </div>
        """)
    with m_col2:
        render_html(f"""
        <div class="stat-box">
            <div class="stat-label">Striker Death SR (16–20)</div>
            <div class="stat-value" style="color:#3b5030;">{death_b_row.get('death_sr', 130.0):.1f}</div>
        </div>
        """)
    with m_col3:
        render_html(f"""
        <div class="stat-box">
            <div class="stat-label">Bowler Death Econ (16–20)</div>
            <div class="stat-value" style="color:#2c3f56;">{death_bowl_row.get('death_econ', 10.5):.2f}</div>
        </div>
        """)
    with m_col4:
        render_html(f"""
        <div class="stat-box">
            <div class="stat-label">Bowler Dot-Ball %</div>
            <div class="stat-value" style="color:#8c6d31;">{death_bowl_row.get('death_dot_pct', 25.0):.1f}%</div>
        </div>
        """)

    render_html("<div style='height: 14px;'></div>")

    # Active Matchup Grid & Strategy Simulator
    col_left, col_right = st.columns([1, 1])

    with col_left:
        render_html(f"""
        <div class="editorial-panel">
            <div class="panel-header">
                {icon_svg("users", size=18, color="#485c3b")} Head-to-Head Tactical Duel
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; background:#ffffff; border:1px solid #dfd8cc; padding:12px 16px; border-radius:6px; margin-bottom:12px;">
                <div>
                    <div style="font-size:10.5px; color:#636b76; text-transform:uppercase; font-weight:600;">Striker ({batting_team})</div>
                    <div style="font-family:'Newsreader',serif; font-weight:700; color:#3b5030; font-size:18px;">{striker}</div>
                </div>
                <div style="text-align:center;">
                    <div class="badge badge-neutral">VS</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10.5px; color:#636b76; text-transform:uppercase; font-weight:600;">Bowler ({bowling_team})</div>
                    <div style="font-family:'Newsreader',serif; font-weight:700; color:#2c3f56; font-size:18px;">{active_bowler}</div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; font-size:12px; text-align:center;">
                <div style="background:#ffffff; border:1px solid #dfd8cc; padding:10px; border-radius:6px;">
                    <div style="color:#636b76; font-size:11px; text-transform:uppercase; font-weight:600;">Runs / Balls</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:15px; margin-top:2px;">{int(h2h_row.get('h2h_runs', 0))}r / {int(h2h_row.get('h2h_balls', 0))}b</div>
                </div>
                <div style="background:#ffffff; border:1px solid #dfd8cc; padding:10px; border-radius:6px;">
                    <div style="color:#636b76; font-size:11px; text-transform:uppercase; font-weight:600;">Dismissals</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:15px; margin-top:2px; color:{'#9c4132' if h2h_row.get('h2h_dismissals', 0) > 0 else '#24282f'};">{int(h2h_row.get('h2h_dismissals', 0))}</div>
                </div>
                <div style="background:#ffffff; border:1px solid #dfd8cc; padding:10px; border-radius:6px;">
                    <div style="color:#636b76; font-size:11px; text-transform:uppercase; font-weight:600;">H2H Strike Rate</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:15px; margin-top:2px; color:{'#3b5030' if h2h_row.get('h2h_sr', 120) >= 150 else '#24282f'};">{h2h_row.get('h2h_sr', 120.0):.1f}</div>
                </div>
            </div>
            <div style="margin-top:12px; font-size:12.5px; color:#555c66; line-height:1.5;">
                <strong>Non-Striker Partner:</strong> <span style="color:#1a1e24;">{non_striker}</span> (Death SR: {recommender.b_death_map.get(non_striker, {}).get('death_sr', 125.0):.1f})
            </div>
        </div>
        """)

    with col_right:
        render_html(f"""
        <div class="editorial-panel">
            <div class="panel-header">
                {icon_svg("zap", size=18, color="#2c3f56")} Delivery-by-Delivery Swing Simulator
            </div>
            <p style="font-size:12.5px; color:#555c66; margin-bottom:12px; line-height:1.4;">
                Projected win probability shift based on the potential outcome of the very next ball:
            </p>
        </div>
        """)

        # Calculate outcomes on next ball
        sim_outcomes = [
            ("Dot (0r)", 0, False),
            ("Single (1r)", 1, False),
            ("Two (2r)", 2, False),
            ("Four (4r)", 4, False),
            ("Six (6r)", 6, False),
            ("Wicket", 0, True)
        ]

        sim_cols = st.columns(6)
        for i, (label, r_scored, is_wkt) in enumerate(sim_outcomes):
            next_runs_req = max(0, runs_required - r_scored)
            next_balls = max(0, balls_remaining - 1)
            next_wkts = max(0, wickets_remaining - (1 if is_wkt else 0))

            if next_balls == 0:
                next_bat_prob = 1.0 if next_runs_req <= 0 else 0.0
            elif next_runs_req <= 0:
                next_bat_prob = 1.0
            elif next_wkts <= 0:
                next_bat_prob = 0.0
            elif next_runs_req > (next_balls * 6):
                next_bat_prob = 0.0
            else:
                next_rrr = (next_runs_req / next_balls) * 6.0
                next_dict = feature_dict.copy()
                next_dict['runs_required'] = next_runs_req
                next_dict['balls_remaining'] = next_balls
                next_dict['wickets_remaining'] = next_wkts
                next_dict['rrr'] = next_rrr
                next_X = pd.DataFrame([next_dict])[feature_order]
                if selected_model_name == 'Logistic Regression':
                    next_X_scaled = model_bundle['scaler'].transform(next_X)
                    next_bat_prob = float(active_model.predict_proba(next_X_scaled)[0, 1])
                else:
                    next_bat_prob = float(active_model.predict_proba(next_X.values)[0, 1])
                next_bat_prob = float(np.clip(next_bat_prob, 0.01, 0.99))

            delta = round((next_bat_prob - batting_win_prob) * 100, 1)
            delta_str = f"+{delta}%" if delta > 0 else f"{delta}%"
            val_color = "#3b5030" if delta > 0 else ("#9c4132" if delta < 0 else "#636b76")
            bg_tint = "#ebf0e6" if delta > 0 else ("#f8ebe8" if delta < 0 else "#ffffff")

            with sim_cols[i]:
                render_html(f"""
                <div style="background:{bg_tint}; border:1px solid #dfd8cc; border-radius:6px; padding:10px 4px; text-align:center;">
                    <div style="font-size:11px; font-weight:600; color:#3d434d;">{label}</div>
                    <div style="font-size:14px; font-weight:700; font-family:'JetBrains Mono'; color:{val_color}; margin-top:4px;">{delta_str}</div>
                    <div style="font-size:10px; color:#636b76; margin-top:2px;">{round(next_bat_prob * 100, 1)}%</div>
                </div>
                """)

# ==========================================
# TAB 2: Bowler Recommendation Engine
# ==========================================
with tabs[1]:
    render_html(f"""
    <div style="margin-bottom:18px;">
        <h3 style="font-family:'Newsreader',Georgia,serif; color:#1a1e24; font-size:24px; margin:0; display:flex; align-items:center; gap:8px;">
            {icon_svg("shield", size=22, color="#2c3f56")} Smart Death-Overs Bowler Recommendation Engine
        </h3>
        <p style="font-size:13.5px; color:#555c66; margin-top:4px; line-height:1.5;">
            Algorithmic selection ranking the optimal bowler for <strong>{bowling_team}</strong> to deliver the 20th over against <strong>{striker}</strong> and <strong>{non_striker}</strong> at <strong>{venue}</strong>.
            Evaluation weights: Historical Death Economy & Dot % (40%), Head-to-Head Matchup Advantage (40%), and Venue Adaptation (20%).
        </p>
    </div>
    """)

    recommended_bowlers = recommender.compute_recommendations(
        bowling_team=bowling_team,
        striker=striker,
        non_striker=non_striker,
        venue=venue,
        top_n=5
    )

    for i, b in enumerate(recommended_bowlers):
        rank = i + 1
        rank_class = f"rank-{rank}" if rank <= 3 else "rank-default"
        is_current = (b['bowler'] == active_bowler)

        current_badge = f'<span class="badge badge-olive">{icon_svg("check_circle", size=11, color="#3b5030")} CURRENT SELECTION</span>' if is_current else ''
        border_color = '#485c3b' if rank == 1 else ('#2d4059' if rank == 2 else '#dfd8cb')
        score_color = '#3b5030' if rank == 1 else ('#2c3f56' if rank == 2 else '#1a1e24')

        render_html(f"""
        <div class="bowler-card" style="border-left: 4px solid {border_color};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div class="rank-badge {rank_class}">#{rank}</div>
                    <div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-family:'Newsreader',Georgia,serif; font-size:20px; font-weight:700; color:#1a1e24;">
                                {b['bowler']}
                            </span>
                            {current_badge}
                        </div>
                        <div style="font-size:12px; color:#636b76; margin-top:2px;">
                            Death Deliveries Bowled: {b['death_balls']} • Death Wickets: {b['death_wickets']}
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10.5px; text-transform:uppercase; color:#636b76; font-weight:600; letter-spacing:0.6px;">Tactical Score</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:700; color:{score_color};">
                        {b['score']}<span style="font-size:14px; color:#7e8794;">/100</span>
                    </div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:10px; margin:14px 0 10px 0; font-size:12px;">
                <div style="background:#ffffff; border:1px solid #dfd8cb; padding:8px 12px; border-radius:4px;">
                    <div style="color:#636b76; font-size:10.5px; text-transform:uppercase; font-weight:600;">Death Economy (16-20)</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:14px; color:#2c3f56; margin-top:2px;">{b['death_econ']:.2f} rpo</div>
                </div>
                <div style="background:#ffffff; border:1px solid #dfd8cb; padding:8px 12px; border-radius:4px;">
                    <div style="color:#636b76; font-size:10.5px; text-transform:uppercase; font-weight:600;">Death Dot-Ball %</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:14px; color:#8c6d31; margin-top:2px;">{b['death_dot_pct']:.1f}%</div>
                </div>
                <div style="background:#ffffff; border:1px solid #dfd8cb; padding:8px 12px; border-radius:4px;">
                    <div style="color:#636b76; font-size:10.5px; text-transform:uppercase; font-weight:600;">H2H vs {striker}</div>
                    <div style="font-weight:700; font-family:'JetBrains Mono'; font-size:13.5px; color:#3b5030; margin-top:2px;">{b['h2h_vs_striker']}</div>
                </div>
            </div>
            <div style="background:#fcfbf8; border:1px solid #dfd8cb; padding:10px 14px; border-radius:4px; font-size:12.5px; color:#3d434d; line-height:1.5; border-left:3px solid #2d4059;">
                <strong style="color:#2d4059;">Statistical Rationale:</strong> {b['rationale']}
            </div>
        </div>
        """)

# ==========================================
# TAB 3: Historical Scenario Matcher
# ==========================================
with tabs[2]:
    render_html(f"""
    <div style="margin-bottom:18px;">
        <h3 style="font-family:'Newsreader',Georgia,serif; color:#1a1e24; font-size:24px; margin:0; display:flex; align-items:center; gap:8px;">
            {icon_svg("clock", size=22, color="#8c6d31")} Historical Match Matcher ("Similar Scenarios")
        </h3>
        <p style="font-size:13.5px; color:#555c66; margin-top:4px; line-height:1.5;">
            Archival IPL encounters where a chasing team faced identical or nearest required runs ({runs_required}r) with {balls_remaining} ball(s) remaining in the 20th over.
        </p>
    </div>
    """)

    similar_matches = matcher.find_similar_scenarios(
        runs_required=runs_required,
        balls_remaining=balls_remaining,
        top_n=6
    )

    if not similar_matches:
        st.info("No matching historical instances found for this exact equation.")
    else:
        for m in similar_matches:
            outcome = m['outcome']
            if outcome == 'Chased':
                badge_html = f'<span class="badge badge-olive">{icon_svg("check_circle", size=11, color="#3b5030")} CHASED</span>'
                highlight_class = "highlight-chased"
            elif outcome == 'Defended':
                badge_html = f'<span class="badge badge-terracotta">{icon_svg("shield", size=11, color="#9c4132")} DEFENDED</span>'
                highlight_class = "highlight-defended"
            else:
                badge_html = f'<span class="badge badge-bronze">{icon_svg("alert_circle", size=11, color="#8c6d31")} TIED / SUPER OVER</span>'
                highlight_class = "highlight-tied"

            exact_html = f'<span class="badge badge-navy">EXACT RUNS MATCH</span>' if m['is_exact_match'] else f'<span class="badge badge-neutral">±{m["run_diff"]} RUNS</span>'

            events_html = " ".join([
                f'<span style="background:#ffffff; border:1px solid #d5ccbe; padding:2px 7px; border-radius:3px; font-family:\'JetBrains Mono\'; font-size:11px; margin-right:4px; color:#1a1e24;">{ev}</span>'
                for ev in m['over_events']
            ])

            render_html(f"""
            <div class="match-card">
                <div class="match-card-header">
                    <div>
                        <span style="font-family:'Newsreader',Georgia,serif; font-size:20px; font-weight:700; color:#1a1e24;">
                            {m['batting_team']} vs {m['bowling_team']}
                        </span>
                        <span style="font-size:12px; color:#636b76; font-family:'JetBrains Mono'; margin-left:8px;">({m['year']})</span>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center;">
                        {exact_html}
                        {badge_html}
                    </div>
                </div>
                <div class="match-card-meta">
                    {icon_svg("map_pin", size=13, color="#636b76")} {m['venue']} • Striker: <strong style="color:#1a1e24;">{m['striker']}</strong> • Bowler: <strong style="color:#1a1e24;">{m['bowler']}</strong>
                </div>
                <div class="match-card-situation">
                    <div style="margin-bottom:6px;">
                        <strong>Historical Equation:</strong> Needed <strong style="color:#8c6d31; font-family:'JetBrains Mono';">{m['hist_runs_required']} runs</strong> off <strong style="color:#8c6d31; font-family:'JetBrains Mono';">{m['hist_balls_remaining']} balls</strong> ({m['hist_wickets_remaining']} wickets in hand)
                    </div>
                    <div>
                        <span style="color:#636b76; font-size:11.5px; text-transform:uppercase; font-weight:600;">20th Over Sequence:</span> {events_html}
                    </div>
                </div>
                <div class="match-card-highlight {highlight_class}">
                    {m['highlight_summary']}
                </div>
            </div>
            """)

# ==========================================
# TAB 4: ML Benchmark & Analytics Lab
# ==========================================
with tabs[3]:
    render_html(f"""
    <div style="margin-bottom:18px;">
        <h3 style="font-family:'Newsreader',Georgia,serif; color:#1a1e24; font-size:24px; margin:0; display:flex; align-items:center; gap:8px;">
            {icon_svg("bar_chart", size=22, color="#485c3b")} Empirical Model Validation & Analytics Monograph
        </h3>
        <p style="font-size:13.5px; color:#555c66; margin-top:4px; line-height:1.5;">
            5-Fold Stratified Cross-Validation metrics across four candidate machine learning classification architectures evaluated on 20th-over IPL chase situations.
        </p>
    </div>
    """)

    # Leaderboard Table
    st.markdown("#### Candidate Model Performance Leaderboard")
    leaderboard_display = metrics_df.copy()
    leaderboard_display['ROC_AUC'] = leaderboard_display['ROC_AUC'].map(lambda x: f"{x:.4f}")
    leaderboard_display['Log_Loss'] = leaderboard_display['Log_Loss'].map(lambda x: f"{x:.4f}")
    leaderboard_display['Accuracy'] = leaderboard_display['Accuracy'].map(lambda x: f"{x * 100:.2f}%")
    leaderboard_display['Composite_Score'] = leaderboard_display['Composite_Score'].map(lambda x: f"{x:.4f}")

    st.dataframe(leaderboard_display, width='stretch', hide_index=True)

    col_ab1, col_ab2 = st.columns(2)

    with col_ab1:
        st.markdown("#### Top Death-Overs Batters (Min 60 balls in overs 16–20)")
        b_death_top = bundle['b_death'][bundle['b_death']['death_balls'] >= 60].sort_values('death_sr', ascending=False).head(8)
        b_disp = b_death_top[['batter', 'death_runs', 'death_balls', 'death_sr', 'death_avg']].copy()
        b_disp.columns = ['Batter', 'Runs', 'Balls', 'Strike Rate', 'Average']
        b_disp['Strike Rate'] = b_disp['Strike Rate'].map(lambda x: f"{x:.1f}")
        b_disp['Average'] = b_disp['Average'].map(lambda x: f"{x:.1f}")
        st.dataframe(b_disp, width='stretch', hide_index=True)

    with col_ab2:
        st.markdown("#### Top Death-Overs Bowlers (Min 60 balls in overs 16–20)")
        bowl_death_top = bundle['bowl_death'][bundle['bowl_death']['death_balls_bowled'] >= 60].sort_values('death_econ', ascending=True).head(8)
        bowl_disp = bowl_death_top[['bowler', 'death_runs_conceded', 'death_balls_bowled', 'death_econ', 'death_dot_pct']].copy()
        bowl_disp.columns = ['Bowler', 'Runs', 'Balls', 'Economy', 'Dot %']
        bowl_disp['Economy'] = bowl_disp['Economy'].map(lambda x: f"{x:.2f}")
        bowl_disp['Dot %'] = bowl_disp['Dot %'].map(lambda x: f"{x:.1f}%")
        st.dataframe(bowl_disp, width='stretch', hide_index=True)

    st.markdown("<hr style='border:none; border-top:1px solid #dfd8cb; margin:22px 0;'/>", unsafe_allow_html=True)
    st.markdown("#### Head-to-Head Archival Query")
    c_h1, c_h2 = st.columns(2)
    with c_h1:
        all_batters = sorted(bundle['b_death']['batter'].unique())
        selected_batter = st.selectbox("Select Batter", all_batters, index=all_batters.index(striker) if striker in all_batters else 0)
    with c_h2:
        all_bowlers = sorted(bundle['bowl_death']['bowler'].unique())
        selected_bowler = st.selectbox("Select Bowler", all_bowlers, index=all_bowlers.index(active_bowler) if active_bowler in all_bowlers else 0)

    h2h_lookup = recommender.get_h2h_stats(selected_batter, selected_bowler)
    render_html(f"""
    <div style="background:#f4efe6; border:1px solid #dfd8cb; border-radius:6px; padding:18px 20px; margin-top:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2dbce; padding-bottom:10px;">
            <span style="font-family:'Newsreader',Georgia,serif; font-size:19px; font-weight:700; color:#3b5030;">{selected_batter}</span>
            <span class="badge badge-neutral">HISTORICAL MATCHUP</span>
            <span style="font-family:'Newsreader',Georgia,serif; font-size:19px; font-weight:700; color:#2c3f56;">{selected_bowler}</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-top:14px; text-align:center;">
            <div class="stat-box">
                <div class="stat-label">Runs Scored</div>
                <div class="stat-value">{int(h2h_lookup.get('h2h_runs', 0))}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Balls Faced</div>
                <div class="stat-value">{int(h2h_lookup.get('h2h_balls', 0))}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Dismissals</div>
                <div class="stat-value" style="color:#9c4132;">{int(h2h_lookup.get('h2h_dismissals', 0))}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Strike Rate</div>
                <div class="stat-value" style="color:#3b5030;">{h2h_lookup.get('h2h_sr', 120.0):.1f}</div>
            </div>
        </div>
    </div>
    """)
