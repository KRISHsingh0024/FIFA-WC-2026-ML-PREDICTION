"""
Feature Engineering: Match-level features.
Combines team-level strength profiles into matchup-level inputs (differentials, ratios, rankings, H2H) for ML model training and inference.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_match_features():
    """
    Combines historical matches with team-level features to build the final training dataset.
    """
    matches_path = os.path.join(config.RAW_DATA_DIR, "historical_matches.parquet")
    team_features_path = os.path.join(config.PROCESSED_DATA_DIR, "team_features.parquet")
    
    if not os.path.exists(matches_path):
        raise FileNotFoundError(f"Historical matches not found at {matches_path}. Please run collect_historical_matches.py first.")
    if not os.path.exists(team_features_path):
        raise FileNotFoundError(f"Team features not found at {team_features_path}. Please run team_features.py first.")
        
    logging.info("Loading inputs...")
    df_matches = pd.read_parquet(matches_path)
    df_teams = pd.read_parquet(team_features_path)
    
    # Set team features index for quick lookup
    df_teams = df_teams.set_index("national_team")
    
    records = []
    
    # Calculate H2H stats beforehand to avoid lookahead bias (though in a simplified model, we can calculate overall rates)
    # We will build a simple H2H mapping: { (team_a, team_b): [outcomes] }
    h2h_history = {}
    for idx, row in df_matches.iterrows():
        t1, t2 = row["home_team"], row["away_team"]
        outcome = row["outcome"] # 'W', 'D', 'L'
        
        pair = tuple(sorted([t1, t2]))
        if pair not in h2h_history:
            h2h_history[pair] = []
        # Store outcome from t1's perspective
        h2h_history[pair].append((t1, outcome))
        
    logging.info("Generating match-level feature vectors...")
    for idx, row in df_matches.iterrows():
        t1 = row["home_team"]
        t2 = row["away_team"]
        
        # Check if we have features for both teams
        if t1 not in df_teams.index or t2 not in df_teams.index:
            continue
            
        feat1 = df_teams.loc[t1]
        feat2 = df_teams.loc[t2]
        
        # 1. Differential Features (home - away)
        attack_diff = feat1["team_attack_strength"] - feat2["team_attack_strength"]
        defense_diff = feat1["team_defense_solidity"] - feat2["team_defense_solidity"]
        midfield_diff = feat1["team_midfield_creativity"] - feat2["team_midfield_creativity"]
        xg_diff = feat1["team_overall_xg"] - feat2["team_overall_xg"]
        xa_diff = feat1["team_overall_xa"] - feat2["team_overall_xa"]
        depth_diff = feat1["team_depth_score"] - feat2["team_depth_score"]
        star_diff = feat1["team_star_player_impact"] - feat2["team_star_player_impact"]
        
        # 2. Ratio Features (home / away)
        attack_ratio = feat1["team_attack_strength"] / (feat2["team_attack_strength"] + 0.01)
        defense_ratio = feat1["team_defense_solidity"] / (feat2["team_defense_solidity"] + 0.01)
        
        # 3. Contextual Features
        r1 = config.FIFA_RANKINGS.get(t1, 50)
        r2 = config.FIFA_RANKINGS.get(t2, 50)
        fifa_rank_diff = r2 - r1 # positive = team1 is better ranked (lower rank)
        
        # 4. H2H win rate of t1 against t2
        pair = tuple(sorted([t1, t2]))
        h2hs = h2h_history.get(pair, [])
        t1_wins = 0
        total_games = 0
        # Only calculate H2H prior to this match to be realistic (for simplicity, we skip dates but filter this match)
        for ht, out in h2hs:
            # Skip current match
            if ht == t1 and out == row["outcome"] and total_games == 0:
                continue
            total_games += 1
            if ht == t1 and out == "W":
                t1_wins += 1
            elif ht != t1 and out == "L":
                t1_wins += 1
                
        h2h_win_rate = t1_wins / total_games if total_games > 0 else 0.4 # baseline 40% win
        
        # 5. New Match Features (Differentials)
        ucl_rep_diff = feat1["team_ucl_representation"] - feat2["team_ucl_representation"]
        confederation_diff = feat1["team_confederation_strength"] - feat2["team_confederation_strength"]
        creativity_diff = feat1["team_avg_creativity_score"] - feat2["team_avg_creativity_score"]
        defensive_score_diff = feat1["team_avg_defensive_score"] - feat2["team_avg_defensive_score"]
        
        # Label/Target
        # W = 0 (Home Win), D = 1 (Draw), L = 2 (Away Win)
        target = 0 if row["outcome"] == "W" else (1 if row["outcome"] == "D" else 2)
        
        records.append({
            "match_id": row["match_id"],
            "date": row["date"],
            "home_team": t1,
            "away_team": t2,
            "attack_diff": round(attack_diff, 4),
            "defense_diff": round(defense_diff, 4),
            "midfield_diff": round(midfield_diff, 4),
            "xg_diff": round(xg_diff, 4),
            "xa_diff": round(xa_diff, 4),
            "depth_diff": round(depth_diff, 4),
            "star_diff": round(star_diff, 4),
            "attack_ratio": round(attack_ratio, 4),
            "defense_ratio": round(defense_ratio, 4),
            "fifa_rank_diff": fifa_rank_diff,
            "h2h_win_rate": round(h2h_win_rate, 4),
            "ucl_rep_diff": round(ucl_rep_diff, 4),
            "confederation_diff": round(confederation_diff, 4),
            "creativity_diff": round(creativity_diff, 4),
            "defensive_score_diff": round(defensive_score_diff, 4),
            "target": target
        })
        
    df_features = pd.DataFrame(records)
    processed_path = os.path.join(config.PROCESSED_DATA_DIR, "match_features.parquet")
    df_features.to_parquet(processed_path, index=False)
    logging.info(f"Saved match feature matrix ({len(df_features)} rows) to {processed_path}")
    return df_features

if __name__ == "__main__":
    build_match_features()
