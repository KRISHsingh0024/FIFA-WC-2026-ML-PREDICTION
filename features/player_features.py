"""
Feature Engineering: Player-level features.
Normalizes player stats, handles league weighting, and saves processed player features.
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

def process_player_features():
    """
    Loads raw player stats, applies league weighting, and processes features.
    """
    raw_path = os.path.join(config.RAW_DATA_DIR, "player_stats_2024_2025.parquet")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw player stats file not found at {raw_path}. Please run collect_player_stats.py first.")
        
    logging.info(f"Loading raw player stats from {raw_path}...")
    df = pd.read_parquet(raw_path)
    
    # 1. Apply League Weighting to performance metrics
    # Metrics to weight (all stats that indicate performance)
    metrics_to_scale = [
        "goals_p90", "xg_p90", "npxg_p90", "assists_p90", "xa_p90",
        "key_passes_p90", "tackles_p90", "interceptions_p90", "blocks_p90",
        "clearances_p90", "progressive_passes_p90", "progressive_carries_p90",
        "successful_dribbles_p90", "shot_creating_actions_p90", "goal_creating_actions_p90"
    ]
    
    logging.info("Applying competition difficulty weights...")
    for col in metrics_to_scale:
        if col in df.columns:
            # Multiply raw stats by league_weight (e.g. UCL gets 1.3x)
            df[col] = df[col] * df["league_weight"]
            
    # 2. Handle missing values
    df[metrics_to_scale] = df[metrics_to_scale].fillna(0.0)
    df["pass_completion_pct"] = df["pass_completion_pct"].fillna(70.0) # baseline pass completion
    
    # 3. Create composite metrics
    # E.g., Attacking efficiency = goals_p90 / (xg_p90 + 0.01)
    df["attacking_efficiency"] = df["goals_p90"] / (df["xg_p90"] + 0.01)
    # Clip extreme values from divide-by-zero or tiny xG
    df["attacking_efficiency"] = df["attacking_efficiency"].clip(0.0, 3.0)
    
    # Midfield creativity = key_passes_p90 + progressive_passes_p90 * 0.5 + xa_p90 * 2.0
    df["creativity_score"] = df["key_passes_p90"] + (df["progressive_passes_p90"] * 0.5) + (df["xa_p90"] * 2.0)
    
    # Defensive workrate = tackles_p90 + interceptions_p90 + blocks_p90 * 0.5 + clearances_p90 * 0.3
    df["defensive_score"] = df["tackles_p90"] + df["interceptions_p90"] + (df["blocks_p90"] * 0.5) + (df["clearances_p90"] * 0.3)
    
    # Save processed player features
    processed_path = os.path.join(config.PROCESSED_DATA_DIR, "player_features.parquet")
    df.to_parquet(processed_path, index=False)
    logging.info(f"Saved processed player features to {processed_path}")
    return df

if __name__ == "__main__":
    process_player_features()
