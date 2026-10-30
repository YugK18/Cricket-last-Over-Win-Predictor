"""
Bowler Recommendation Engine for IPL Last-Over Win Predictor
Factors:
1. Historical death-over Economy Rate and Dot-Ball % (overs 16-20)
2. Head-to-Head matchup advantage against current active batters (Striker & Non-Striker)
3. Performance history at the selected venue
"""

import numpy as np
import pandas as pd


class BowlerRecommender:
    def __init__(self, bundle):
        self.bundle = bundle
        self.b_death = bundle['b_death']
        self.bowl_death = bundle['bowl_death']
        self.h2h = bundle['h2h']
        self.venue_stats = bundle['venue_stats']
        self.bowlers_by_team = bundle['bowlers_by_team']

        # Index dataframes for quick lookups
        self.bowl_death_map = self.bowl_death.set_index('bowler').to_dict('index')
        self.b_death_map = self.b_death.set_index('batter').to_dict('index')
        self.h2h_map = self.h2h.set_index(['batter', 'bowler']).to_dict('index')

    def get_bowler_death_stats(self, bowler):
        if bowler in self.bowl_death_map:
            return self.bowl_death_map[bowler]
        return {
            'death_econ': 10.5,
            'death_sr': 20.0,
            'death_dot_pct': 25.0,
            'death_balls_bowled': 0,
            'death_wickets': 0
        }

    def get_h2h_stats(self, batter, bowler):
        key = (batter, bowler)
        if key in self.h2h_map:
            return self.h2h_map[key]
        return {
            'h2h_runs': 0,
            'h2h_balls': 0,
            'h2h_dismissals': 0,
            'h2h_sr': 120.0,
            'h2h_dot_pct': 25.0
        }

    def compute_recommendations(self, bowling_team, striker, non_striker=None, venue=None, top_n=5):
        """
        Rank all available bowlers for the bowling team and return detailed rationale.
        """
        candidate_bowlers = self.bowlers_by_team.get(bowling_team, [])
        if not candidate_bowlers:
            # Fallback to all bowlers in dataset if bowling_team is unrecognized
            candidate_bowlers = list(self.bowl_death_map.keys())

        ranked_list = []

        for bowler in candidate_bowlers:
            b_stats = self.get_bowler_death_stats(bowler)
            econ = b_stats['death_econ']
            dot_pct = b_stats['death_dot_pct']
            wkts = b_stats['death_wickets']
            balls_bowled = b_stats['death_balls_bowled']

            # 1. Death-overs Mastery Score (0 to 100)
            # Baseline death econ ~10.5, best <= 7.0 (100 pts), worst >= 14.0 (0 pts)
            econ_score = np.clip(100 - (econ - 7.0) * (100 / 7.0), 0, 100)
            # Baseline dot % ~25%, best >= 40% (100 pts), worst <= 10% (0 pts)
            dot_score = np.clip((dot_pct - 10.0) * (100 / 30.0), 0, 100)
            # Experience bonus
            sample_weight = min(1.0, balls_bowled / 60.0)
            death_score = (econ_score * 0.55 + dot_score * 0.45) * (0.6 + 0.4 * sample_weight)

            # 2. Head-to-Head Advantage against active batters
            # Striker matchup (65% weight)
            h2h_striker = self.get_h2h_stats(striker, bowler)
            s_balls = h2h_striker['h2h_balls']
            s_runs = h2h_striker['h2h_runs']
            s_wkts = h2h_striker['h2h_dismissals']
            s_sr = h2h_striker['h2h_sr']

            if s_balls >= 6:
                # Direct sample against striker
                h2h_sr_score = np.clip(100 - (s_sr - 80.0) * (100 / 120.0), 0, 100)
                wkt_bonus = min(30, s_wkts * 15)
                striker_h2h_score = np.clip(h2h_sr_score + wkt_bonus, 10, 100)
            else:
                # Limited sample: default to general death score
                striker_h2h_score = death_score

            # Non-striker matchup (35% weight)
            if non_striker:
                h2h_ns = self.get_h2h_stats(non_striker, bowler)
                ns_balls = h2h_ns['h2h_balls']
                ns_wkts = h2h_ns['h2h_dismissals']
                ns_sr = h2h_ns['h2h_sr']
                if ns_balls >= 6:
                    ns_sr_score = np.clip(100 - (ns_sr - 80.0) * (100 / 120.0), 0, 100)
                    wkt_bonus_ns = min(25, ns_wkts * 12)
                    ns_h2h_score = np.clip(ns_sr_score + wkt_bonus_ns, 10, 100)
                else:
                    ns_h2h_score = death_score
            else:
                ns_h2h_score = striker_h2h_score

            h2h_composite = striker_h2h_score * 0.65 + ns_h2h_score * 0.35

            # 3. Venue Performance
            # Default venue score reflects death mastery
            venue_score = death_score
            v_note = ""
            if venue:
                v_row = self.venue_stats[self.venue_stats['venue'] == venue]
                if not v_row.empty:
                    avg_v_runs = v_row['venue_avg_20th_runs'].values[0]
                    # If venue is high-scoring, high dot % bowlers gain higher edge
                    venue_factor = 1.05 if dot_pct >= 28.0 and avg_v_runs >= 12.0 else 1.0
                    venue_score = min(100, death_score * venue_factor)
                    if avg_v_runs >= 12.0 and dot_pct >= 28.0:
                        v_note = f"Thrives under pressure at high-scoring {venue[:25]} (avg {avg_v_runs:.1f} rpo in over 20)."
                    elif avg_v_runs < 10.0:
                        v_note = f"Suited to defending low targets at {venue[:25]} (defended avg {avg_v_runs:.1f} runs in 20th over)."

            # Overall Composite Score
            final_score = death_score * 0.40 + h2h_composite * 0.40 + venue_score * 0.20
            final_score = round(float(np.clip(final_score, 10, 99)), 1)

            # Build statistical rationale
            rationale_points = []
            if econ <= 9.0 and dot_pct >= 30.0:
                rationale_points.append(f"Elite death specialist: {econ:.2f} Econ, {dot_pct:.1f}% dot balls in overs 16–20.")
            elif econ <= 9.8:
                rationale_points.append(f"Strong death execution: {econ:.2f} Econ across {balls_bowled} death deliveries.")
            else:
                rationale_points.append(f"Death-overs profile: {econ:.2f} Econ, {wkts} death wickets.")

            if s_balls >= 6:
                if s_wkts > 0:
                    rationale_points.append(f"Dismissed {striker} {s_wkts} time(s) in {s_balls} balls (held to SR {s_sr:.1f}).")
                elif s_sr < 110.0:
                    rationale_points.append(f"Dominates {striker}: {s_runs} runs off {s_balls} balls (suppressing SR to {s_sr:.1f}).")
                else:
                    rationale_points.append(f"H2H vs {striker}: {s_runs} runs in {s_balls} balls (SR {s_sr:.1f}).")
            else:
                rationale_points.append(f"Uncharted matchup vs {striker} (relying on raw death execution).")

            if v_note:
                rationale_points.append(v_note)

            rationale = " ".join(rationale_points)

            ranked_list.append({
                'bowler': bowler,
                'score': final_score,
                'death_econ': round(econ, 2),
                'death_dot_pct': round(dot_pct, 1),
                'death_wickets': int(wkts),
                'death_balls': int(balls_bowled),
                'h2h_vs_striker': f"{s_runs}r / {s_balls}b ({s_wkts}W, SR {s_sr:.1f})" if s_balls > 0 else "0 balls faced",
                'h2h_wkts_striker': int(s_wkts),
                'rationale': rationale
            })

        ranked_list.sort(key=lambda x: x['score'], reverse=True)
        return ranked_list[:top_n]
