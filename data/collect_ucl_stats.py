"""
Champions League Stats Collection script.
Generates realistic UCL tournament stats for players competing at the top level,
which will be weighted and merged into the player feature pool.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.squad_lists import KEY_PLAYERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Top clubs that consistently play in the Champions League (2024-25 & 2025-26 seasons)
UCL_CLUBS = {
    "Real Madrid", "FC Barcelona", "Barcelona", "Manchester City", "Liverpool", "Arsenal",
    "Aston Villa", "Bayern München", "Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen",
    "Paris Saint-Germain", "PSG", "Atlético De Madrid", "Atletico Madrid", "Atlético Madrid",
    "Internazionale Milano", "Inter Milan", "AC Milan", "Juventus", "Atalanta", "Bologna",
    "Sporting CP", "SL Benfica", "Benfica", "FC Porto", "Porto", "Feyenoord", "Feyenoord Rotterdam",
    "PSV Eindhoven", "Celtic", "Girona", "Stuttgart", "Monaco", "Lille", "Brest", "Salzburg",
    "Shakhtar Donetsk", "Young Boys", "Club Brugge", "Dinamo Zagreb", "Slovan Bratislava",
    "Sparta Praha", "Sturm Graz"
}

def is_ucl_club(club_name):
    """Check if a club name matches any known UCL clubs."""
    if not club_name:
        return False
    club_lower = club_name.lower().strip()
    for uc in UCL_CLUBS:
        if uc.lower() in club_lower:
            return True
    return False

def generate_ucl_player_stats(league_records=None):
    """
    Generates UCL tournament performance data for players at UCL clubs.
    If league_records is provided, base stats are derived from league performance with a high-stakes,
    high-intensity tournament modulation (slightly lower goals/assists, higher defensive workrate).
    """
    logging.info("Generating UCL player statistics for the 2024-25 and 2025-26 campaigns...")
    np.random.seed(42)
    ucl_records = []
    
    if league_records:
        # Generate based on existing league stats
        for record in league_records:
            if not is_ucl_club(record["club"]):
                continue
                
            # UCL matches: typically 6 to 10 appearances for key players
            starter = record["is_starter"]
            minutes = np.random.randint(500, 900) if starter else np.random.randint(100, 450)
            matches = int(minutes / 80) + 1
            
            # Extract pos and modulate stats (high-stakes tournament: fewer goals/assists, more intense defending/passes)
            pos = record["position"]
            goals_p90 = record["goals_p90"] * np.random.uniform(0.8, 0.95)
            xg_p90 = record["xg_p90"] * np.random.uniform(0.8, 0.95)
            npxg_p90 = record["npxg_p90"] * np.random.uniform(0.8, 0.95)
            assists_p90 = record["assists_p90"] * np.random.uniform(0.75, 0.95)
            xa_p90 = record["xa_p90"] * np.random.uniform(0.8, 0.95)
            key_passes_p90 = record["key_passes_p90"] * np.random.uniform(0.85, 0.98)
            
            # Defense: increased pressure in UCL (higher tackles & interceptions)
            tackles_p90 = record["tackles_p90"] * np.random.uniform(1.05, 1.25)
            interceptions_p90 = record["interceptions_p90"] * np.random.uniform(1.05, 1.25)
            blocks_p90 = record["blocks_p90"] * np.random.uniform(1.05, 1.2)
            clearances_p90 = record["clearances_p90"] * np.random.uniform(1.0, 1.15)
            
            # Passing & Carrying: slightly lower completion/progressive due to tighter defenses
            progressive_passes_p90 = record["progressive_passes_p90"] * np.random.uniform(0.85, 0.95)
            progressive_carries_p90 = record["progressive_carries_p90"] * np.random.uniform(0.85, 0.95)
            successful_dribbles_p90 = record["successful_dribbles_p90"] * np.random.uniform(0.8, 0.95)
            pass_completion_pct = record["pass_completion_pct"] * np.random.uniform(0.96, 0.99)
            
            sca_p90 = record["shot_creating_actions_p90"] * np.random.uniform(0.85, 0.95)
            gca_p90 = record["goal_creating_actions_p90"] * np.random.uniform(0.8, 0.95)
            
            ucl_records.append({
                "player_name": record["player_name"],
                "position": pos,
                "club": record["club"],
                "national_team": record["national_team"],
                "is_starter": starter,
                "minutes_played": minutes,
                "matches_played": matches,
                "goals_p90": round(goals_p90, 3),
                "xg_p90": round(xg_p90, 3),
                "npxg_p90": round(npxg_p90, 3),
                "assists_p90": round(assists_p90, 3),
                "xa_p90": round(xa_p90, 3),
                "key_passes_p90": round(key_passes_p90, 3),
                "tackles_p90": round(tackles_p90, 3),
                "interceptions_p90": round(interceptions_p90, 3),
                "blocks_p90": round(blocks_p90, 3),
                "clearances_p90": round(clearances_p90, 3),
                "progressive_passes_p90": round(progressive_passes_p90, 3),
                "progressive_carries_p90": round(progressive_carries_p90, 3),
                "successful_dribbles_p90": round(successful_dribbles_p90, 3),
                "pass_completion_pct": round(pass_completion_pct, 2),
                "shot_creating_actions_p90": round(sca_p90, 3),
                "goal_creating_actions_p90": round(gca_p90, 3),
                "competition": "UCL"
            })
    else:
        # Generate standalone
        for country, players in KEY_PLAYERS.items():
            for name, pos, club, starter in players:
                if not is_ucl_club(club):
                    continue
                    
                minutes = np.random.randint(450, 950) if starter else np.random.randint(90, 360)
                matches = int(minutes / 85) + 1
                
                # Baseline position specific stats
                goals_p90 = 0.0
                xg_p90 = 0.0
                npxg_p90 = 0.0
                assists_p90 = 0.0
                xa_p90 = 0.0
                key_passes_p90 = 0.0
                tackles_p90 = 0.0
                interceptions_p90 = 0.0
                blocks_p90 = 0.0
                clearances_p90 = 0.0
                progressive_passes_p90 = 0.0
                progressive_carries_p90 = 0.0
                successful_dribbles_p90 = 0.0
                pass_completion_pct = np.random.uniform(73.0, 91.0)
                
                if pos == "FW":
                    goals_p90 = np.random.uniform(0.25, 0.7) if starter else np.random.uniform(0.05, 0.3)
                    xg_p90 = goals_p90 * np.random.uniform(0.9, 1.1)
                    npxg_p90 = xg_p90
                    assists_p90 = np.random.uniform(0.08, 0.25)
                    xa_p90 = assists_p90
                    key_passes_p90 = np.random.uniform(0.8, 2.2)
                    progressive_carries_p90 = np.random.uniform(2.0, 5.0)
                    successful_dribbles_p90 = np.random.uniform(1.2, 3.5)
                    tackles_p90 = np.random.uniform(0.1, 0.5)
                    interceptions_p90 = np.random.uniform(0.0, 0.2)
                elif pos == "MF":
                    goals_p90 = np.random.uniform(0.03, 0.2)
                    xg_p90 = goals_p90
                    assists_p90 = np.random.uniform(0.12, 0.38) if starter else np.random.uniform(0.05, 0.15)
                    xa_p90 = assists_p90
                    key_passes_p90 = np.random.uniform(1.5, 3.0)
                    progressive_passes_p90 = np.random.uniform(3.5, 7.5)
                    progressive_carries_p90 = np.random.uniform(1.2, 3.5)
                    successful_dribbles_p90 = np.random.uniform(0.6, 2.0)
                    tackles_p90 = np.random.uniform(1.4, 3.0)
                    interceptions_p90 = np.random.uniform(1.0, 2.2)
                elif pos == "DF":
                    goals_p90 = np.random.uniform(0.0, 0.05)
                    xg_p90 = goals_p90
                    assists_p90 = np.random.uniform(0.01, 0.1)
                    xa_p90 = assists_p90
                    key_passes_p90 = np.random.uniform(0.1, 0.8)
                    tackles_p90 = np.random.uniform(2.0, 4.2)
                    interceptions_p90 = np.random.uniform(1.4, 3.0)
                    blocks_p90 = np.random.uniform(1.0, 2.0)
                    clearances_p90 = np.random.uniform(3.0, 6.0)
                    progressive_passes_p90 = np.random.uniform(1.8, 4.5)
                    
                sca_p90 = key_passes_p90 * np.random.uniform(1.2, 1.8) + (goals_p90 + assists_p90) * 0.5
                gca_p90 = sca_p90 * np.random.uniform(0.1, 0.2)
                
                ucl_records.append({
                    "player_name": name,
                    "position": pos,
                    "club": club,
                    "national_team": country,
                    "is_starter": starter,
                    "minutes_played": minutes,
                    "matches_played": matches,
                    "goals_p90": round(goals_p90, 3),
                    "xg_p90": round(xg_p90, 3),
                    "npxg_p90": round(npxg_p90, 3),
                    "assists_p90": round(assists_p90, 3),
                    "xa_p90": round(xa_p90, 3),
                    "key_passes_p90": round(key_passes_p90, 3),
                    "tackles_p90": round(tackles_p90, 3),
                    "interceptions_p90": round(interceptions_p90, 3),
                    "blocks_p90": round(blocks_p90, 3),
                    "clearances_p90": round(clearances_p90, 3),
                    "progressive_passes_p90": round(progressive_passes_p90, 3),
                    "progressive_carries_p90": round(progressive_carries_p90, 3),
                    "successful_dribbles_p90": round(successful_dribbles_p90, 3),
                    "pass_completion_pct": round(pass_completion_pct, 2),
                    "shot_creating_actions_p90": round(sca_p90, 3),
                    "goal_creating_actions_p90": round(gca_p90, 3),
                    "competition": "UCL"
                })
                
    df = pd.DataFrame(ucl_records)
    output_path = os.path.join(config.RAW_DATA_DIR, "ucl_player_stats.parquet")
    df.to_parquet(output_path, index=False)
    logging.info(f"Saved {len(df)} UCL player records to {output_path}")
    return df

def main():
    df = generate_ucl_player_stats()
    print(f"UCL Stats Collection Complete. Total Rows: {len(df)}")

if __name__ == "__main__":
    main()
