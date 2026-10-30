# Cricket Last-Over Win Predictor & Strategy Dashboard

A modern, web-based sports analytics platform and decision-support engine built with Python and Streamlit. The system trains and deploys state-of-the-art machine learning models on IPL ball-by-ball match data (2008–2026) to deliver real-time last-over win probabilities, an AI-powered bowler recommendation engine, and historical match scenario matching.

---

## 1. Editorial Aesthetic & Design System

The application features a warm, editorial design inspired by classic sports monographs and publications (Wisden, The Athletic, NYT Sports Analytics):

- **Palette**:
  - **Background**: Rich cream parchment (`#fbf8f3` main app background, `#f4eee4` sidebar).
  - **Body Typography**: Deep charcoal (`#24282f` / `#1a1e24`) for optimal contrast and readability.
  - **Container Cards**: Warm taupe panels (`#f4efe6`) with tactile 1px borders (`#dfd8cb`).
  - **Primary Accents**:
    - **Desaturated Olive** (`#485c3b` / `#3b5030`): Used for batting team metrics, chase victories, and positive tactical indicators.
    - **Muted Navy** (`#2d4059` / `#2c3f56`): Used for bowling team metrics, defense indicators, and secondary badges.
  - **Functional Accents**:
    - **Muted Terracotta** (`#9c4132`): High pressure indicators and defended match badges.
    - **Warm Antique Bronze** (`#8c6d31`): Tied/Super Over matches and balanced pressure markers.
- **Typography Pairing**:
  - **Headings**: Elegant serif typography (`Newsreader`, Georgia, serif) with refined proportions.
  - **Body Text**: Clean, modern sans-serif (`Inter`, sans-serif) engineered for digital legibility.
  - **Actuarial / Numeric Data**: Monospace figures (`JetBrains Mono`, monospace).
- **Tactile UI & Subtle Dividers**:
  - Natural contrast, grounded borders (`1px solid #dfd8cb`), and subtle hairline dividers (`#2d2a24` masthead rule).
  - **No bright neon highlights**, **no artificial glowing buttons**, **no futuristic sci-fi gradients**, and **no over-designed floating cards**.
  - **Architectural Stadium Watermark**: Hand-crafted architectural cricket ground line engraving set to **exactly 20% opacity** behind the cream background.
  - **Iconography**: Clean, minimalist SVG vector line icons (stroke-based vector paths) and analytical badges.

---

## 2. Machine Learning Pipeline & Empirical Benchmark

### Feature Engineering
- **Death-Overs Performance (Overs 16–20)**: Batter Strike Rate & Average; Bowler Economy Rate, Strike Rate, and Dot-Ball % (excluding fielding extras and non-bowler dismissals).
- **Head-to-Head (H2H) Matchup Intelligence**: Direct batter vs. bowler historical encounters: balls faced, runs scored, bowler dismissals, and H2H strike rate.
- **Venue-Specific Historical Profiles**: Average 20th-over runs conceded/defended and historical chase success rate at the venue.
- **Match Situational Context**: Runs required, balls remaining (1 to 6), wickets remaining (1 to 10), and Required Run Rate ($RRR$).

### Candidate Model Evaluation (5-Fold Stratified Cross-Validation)
| Model Architecture | ROC-AUC | Log Loss | Accuracy | Deployment Status |
| :--- | :---: | :---: | :---: | :---: |
| **HistGradientBoosting** | **0.9925** | **0.0968** | **96.42%** | **Selected & Deployed (Top Performer)** |
| **XGBoost** | 0.9907 | 0.1090 | 95.46% | Integrated Candidate |
| **Random Forest** | 0.9875 | 0.1557 | 95.20% | Integrated Candidate |
| **Logistic Regression** | 0.9782 | 0.1713 | 93.54% | Integrated Candidate |

---

## 3. Core Dashboard Capabilities

1. **Dynamic Squad & Player Filtering**:
   - Batting and Bowling team selection with automated mutual exclusion.
   - Player dropdowns dynamically filter to strictly allow selection of players who have historically played for the selected franchise (Striker, Non-Striker, and Bowler).
2. **Match Scenario Inputs**:
   - Venue / Stadium selector (loads historical venue metrics).
   - Runs required (1 to 36) & Balls remaining in over 20 (1 to 6).
   - Wickets fallen / remaining in hand (0 to 9 fallen).
   - Quick presets for classic finishes (e.g. 14 off 6, 6 off 3, 2 off 1, 29 off 6).
3. **Actuarial Win Probability Projection**:
   - High-contrast digital percentage readouts.
   - Dual-tone progress instrument with desaturated olive (chasing) and muted navy (defending).
   - Pressure classification (*Low*, *Balanced*, *High*, *Extreme*).
4. **Delivery-by-Delivery Swing Simulator**:
   - Evaluates the immediate win probability shift for every possible outcome on the next delivery: **Dot (0r)**, **Single (1r)**, **Two (2r)**, **Four (4r)**, **Six (6r)**, and **Wicket**.
5. **Smart Bowler Recommendation Engine**:
   - Multi-factor recommendation index (0–100) combining Death-overs Economy & Dot % (40%), Head-to-Head matchup advantage (40%), and Venue adaptation (20%).
   - Displays ranked bowler dossiers (#1, #2, #3, ...) with a complete empirical rationale.
6. **Historical Match Matcher ("Similar Scenarios")**:
   - Queries the IPL dataset for real-life matches where a chasing team faced the identical or nearest target from the same remaining balls.
   - Displays match fixture, year, venue, final outcome (**CHASED**, **DEFENDED**, or **SUPER OVER**), and the exact ball-by-ball delivery log.
7. **Empirical Model Validation & Analytics Monograph**:
   - Candidate model comparison leaderboard across all 4 architectures.
   - Top death-overs batters and bowlers leaderboards.
   - Head-to-head archival lookup between any batter and bowler.

---

## 4. How to Run

Execute inside `c:\Users\AYUSHI\Downloads\SI`:

```bash
streamlit run app.py
```
