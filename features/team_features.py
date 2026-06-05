"""
Feature Engineering: Team-level features.
Aggregates individual player features into team-level strength scores using position-based aggregation and depth logic.
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

def aggregate_team_features():
    """
    Aggregates player-level features into team-level strength metrics for all 48 qualified teams.
    """
    player_path = os.path.join(config.PROCESSED_DATA_DIR, "player_features.parquet")
    if not os.path.exists(player_path):
        raise FileNotFoundError(f"Processed player features file not found at {player_path}. Please run player_features.py first.")
        
    logging.info(f"Loading processed player features from {player_path}...")
    df_players = pd.read_parquet(player_path)
    
    team_records = []
    
    for team in config.ALL_TEAMS:
        # Filter players for this team
        df_team = df_players[df_players["national_team"] == team]
        
        if len(df_team) == 0:
            logging.warning(f"No player data found for team: {team}. Generating default team profile...")
            # Create a blank record or fallback
            default_record = {col: 0.5 for col in config.TEAM_FEATURES}
            default_record["national_team"] = team
            team_records.append(default_record)
            continue
            
        # Separate Starters vs Bench
        df_starters = df_team[df_team["is_starter"] == True]
        df_bench = df_team[df_team["is_starter"] == False]
        
        # If no starters defined, take top 11 by minutes
        if len(df_starters) == 0:
            df_starters = df_team.nlargest(11, "minutes_played")
            df_bench = df_team[~df_team["player_name"].isin(df_starters["player_name"])]
            
        # Position breakdowns for starters
        starters_fw = df_starters[df_starters["position"] == "FW"]
        starters_mf = df_starters[df_starters["position"] == "MF"]
        starters_df = df_starters[df_starters["position"] == "DF"]
        starters_gk = df_starters[df_starters["position"] == "GK"]
        
        # 1. Team Attack Strength
        # Weighted average of FW and MF attacking statistics
        fw_attack = starters_fw["goals_p90"].mean() if len(starters_fw) > 0 else 0.1
        mf_attack = starters_mf["goals_p90"].mean() if len(starters_mf) > 0 else 0.05
        fw_xg = starters_fw["xg_p90"].mean() if len(starters_fw) > 0 else 0.1
        team_attack_strength = (fw_attack * 0.6 + mf_attack * 0.2 + fw_xg * 0.2)
        
        # 2. Team Midfield Creativity
        # Midfielders' key passes, progressive passes, and assists
        mf_key_passes = starters_mf["key_passes_p90"].mean() if len(starters_mf) > 0 else 0.5
        mf_xa = starters_mf["xa_p90"].mean() if len(starters_mf) > 0 else 0.05
        mf_prog = starters_mf["progressive_passes_p90"].mean() if len(starters_mf) > 0 else 1.5
        team_midfield_creativity = (mf_key_passes * 0.4 + mf_xa * 0.4 + mf_prog * 0.02)
        
        # 3. Team Defense Solidity
        # Defenders' and GK defensive metrics
        df_tackles = starters_df["tackles_p90"].mean() if len(starters_df) > 0 else 1.0
        df_interceptions = starters_df["interceptions_p90"].mean() if len(starters_df) > 0 else 0.8
        df_clearances = starters_df["clearances_p90"].mean() if len(starters_df) > 0 else 1.5
        # Scale defense solidity to match a 0-1 scale approx
        team_defense_solidity = (df_tackles * 0.3 + df_interceptions * 0.3 + df_clearances * 0.1)
        
        # 4. Overall xG / xA sums
        team_overall_xg = df_starters["xg_p90"].sum()
        team_overall_xa = df_starters["xa_p90"].sum()
        
        # 5. Depth Score
        # Average quality ratio of bench vs starters
        starter_avg_metric = df_starters["goals_p90"].mean() + df_starters["key_passes_p90"].mean() + df_starters["tackles_p90"].mean()
        bench_avg_metric = df_bench["goals_p90"].mean() + df_bench["key_passes_p90"].mean() + df_bench["tackles_p90"].mean()
        team_depth_score = bench_avg_metric / (starter_avg_metric + 0.01)
        
        # 6. Star Player Impact
        # The Mbappé effect: maximum individual player contribution (composite of goals + creativity + progressive actions)
        df_team_copy = df_team.copy()
        df_team_copy["star_score"] = df_team_copy["goals_p90"] + df_team_copy["assists_p90"] + (df_team_copy["key_passes_p90"] * 0.5) + (df_team_copy["successful_dribbles_p90"] * 0.3)
        team_star_player_impact = df_team_copy["star_score"].max()
        
        # 7. General averages
        team_avg_goals_p90 = df_starters["goals_p90"].mean()
        team_avg_assists_p90 = df_starters["assists_p90"].mean()
        team_avg_key_passes_p90 = df_starters["key_passes_p90"].mean()
        team_avg_tackles_p90 = df_starters["tackles_p90"].mean()
        team_avg_interceptions_p90 = df_starters["interceptions_p90"].mean()
        team_avg_pass_completion = df_starters["pass_completion_pct"].mean()
        team_avg_progressive_carries_p90 = df_starters["progressive_carries_p90"].mean()
        team_avg_dribbles_p90 = df_starters["successful_dribbles_p90"].mean()
        
        # 8. New Features
        team_ucl_representation = sum(1 for _, p in df_team.iterrows() if p["league_weight"] > 1.0)
        
        confederation = config.CONFEDERATION_MAP.get(team, "UEFA")
        team_confederation_strength = config.CONFEDERATION_STRENGTH.get(confederation, 1.0)
        
        team_avg_creativity_score = df_starters["creativity_score"].mean() if len(df_starters) > 0 else 0.0
        team_avg_defensive_score = df_starters["defensive_score"].mean() if len(df_starters) > 0 else 0.0

        team_records.append({
            "national_team": team,
            "team_attack_strength": round(team_attack_strength, 4),
            "team_midfield_creativity": round(team_midfield_creativity, 4),
            "team_defense_solidity": round(team_defense_solidity, 4),
            "team_overall_xg": round(team_overall_xg, 4),
            "team_overall_xa": round(team_overall_xa, 4),
            "team_depth_score": round(team_depth_score, 4),
            "team_star_player_impact": round(team_star_player_impact, 4),
            "team_avg_goals_p90": round(team_avg_goals_p90, 4),
            "team_avg_assists_p90": round(team_avg_assists_p90, 4),
            "team_avg_key_passes_p90": round(team_avg_key_passes_p90, 4),
            "team_avg_tackles_p90": round(team_avg_tackles_p90, 4),
            "team_avg_interceptions_p90": round(team_avg_interceptions_p90, 4),
            "team_avg_pass_completion": round(team_avg_pass_completion, 4),
            "team_avg_progressive_carries_p90": round(team_avg_progressive_carries_p90, 4),
            "team_avg_dribbles_p90": round(team_avg_dribbles_p90, 4),
            "team_ucl_representation": float(team_ucl_representation),
            "team_confederation_strength": round(team_confederation_strength, 4),
            "team_avg_creativity_score": round(team_avg_creativity_score, 4),
            "team_avg_defensive_score": round(team_avg_defensive_score, 4),
        })
        
    df_teams = pd.DataFrame(team_records)
    
    # Save processed team features
    processed_path = os.path.join(config.PROCESSED_DATA_DIR, "team_features.parquet")
    df_teams.to_parquet(processed_path, index=False)
    logging.info(f"Saved aggregated team features to {processed_path}")
    return df_teams

if __name__ == "__main__":
    aggregate_team_features()
