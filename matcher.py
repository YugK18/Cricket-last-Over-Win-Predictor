"""
Historical Match Matcher for IPL Last-Over Situations
Queries the IPL dataset for real-life matches with identical or nearest
runs required and balls remaining in the 20th over.
"""

import pandas as pd
import numpy as np


class HistoricalMatcher:
    def __init__(self, bundle):
        self.bundle = bundle
        self.situations = bundle['situations_dataset']
        self.historical_matches = bundle['historical_matches']

        # Pre-group matches by match_id for rapid retrieval of full over logs
        self.hist_matches_map = self.historical_matches.set_index('match_id').to_dict('index')

    def find_similar_scenarios(self, runs_required, balls_remaining, top_n=6):
        """
        Query for exact or nearest real-life IPL instances where a team needed
        `runs_required` off `balls_remaining` in the 20th over.
        """
        # Filter for situations matching the exact number of remaining balls
        subset = self.situations[self.situations['balls_remaining'] == balls_remaining].copy()

        if subset.empty:
            # Fallback if no exact balls remaining (should not happen for 1..6)
            subset = self.situations.copy()

        # Compute difference in required runs
        subset['run_diff'] = (subset['runs_required'] - runs_required).abs()

        # Sort by closest run difference, then by most recent year
        subset = subset.sort_values(by=['run_diff', 'year'], ascending=[True, False])

        # Deduplicate by match_id so each real match appears at most once
        dedup_matches = []
        seen_mids = set()

        for _, row in subset.iterrows():
            mid = row['match_id']
            if mid in seen_mids:
                continue
            seen_mids.add(mid)

            hist_info = self.hist_matches_map.get(mid, {})
            over_events = hist_info.get('over_events', [])
            outcome = hist_info.get('outcome', row['outcome'])

            # Generate narrative highlight summary
            events_str = " • ".join(over_events) if over_events else "N/A"
            margin = hist_info.get('margin', 0)
            target = hist_info.get('target', 0)
            inn2_total = hist_info.get('inn2_total', 0)

            if outcome == 'Chased':
                highlight = f"Chased successfully! Reached {inn2_total} (target {target}). Final over events: [{events_str}]."
            elif outcome == 'Defended':
                highlight = f"Defended successfully! Kept batting team to {inn2_total} (won by {margin} run{'s' if margin != 1 else ''}). Over events: [{events_str}]."
            else:
                highlight = f"Scores tied ({inn2_total} vs {target-1})! Match headed into a dramatic Super Over. Events: [{events_str}]."

            dedup_matches.append({
                'match_id': mid,
                'year': str(row['year']),
                'date': str(row['date']),
                'batting_team': row['batting_team'],
                'bowling_team': row['bowling_team'],
                'venue': row['venue'],
                'striker': row['striker'],
                'bowler': row['bowler'],
                'hist_runs_required': int(row['runs_required']),
                'hist_balls_remaining': int(row['balls_remaining']),
                'hist_wickets_remaining': int(row['wickets_remaining']),
                'run_diff': int(row['run_diff']),
                'is_exact_match': bool(row['run_diff'] == 0),
                'outcome': outcome,
                'target': target,
                'inn2_total': inn2_total,
                'over_events': over_events,
                'highlight_summary': highlight
            })

            if len(dedup_matches) >= top_n:
                break

        return dedup_matches
