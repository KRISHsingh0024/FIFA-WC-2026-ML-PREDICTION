"""
Fetch real player statistics from api-football.com and update the model database.
Respects rate limits and handles daily API request quotas gracefully.
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
import time
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from data.squad_lists import KEY_PLAYERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_KEY = "9184ed3a59825bf5ecbadd05fe7a5f8d"
HEADERS = {
    'x-apisports-key': API_KEY
}

# API Football Team IDs for national teams
TEAM_IDS = {
    "Belgium": 1, "France": 2, "Croatia": 3, "Sweden": 5, "Brazil": 6, "Uruguay": 7, "Colombia": 8, "Spain": 9, "England": 10,
    "Panama": 11, "Japan": 12, "Senegal": 13, "Switzerland": 15, "Mexico": 16, "South Korea": 17, "Australia": 20, "Denmark": 21,
    "Iran": 22, "Saudi Arabia": 23, "Poland": 24, "Germany": 25, "Argentina": 26, "Portugal": 27, "Tunisia": 28, "Costa Rica": 29,
    "Morocco": 31, "Egypt": 32, "Czechia": 770, "Austria": 775, "Turkey": 777, "Scotland": 1108, "Bosnia and Herzegovina": 1113,
    "Netherlands": 1118, "Ivory Coast": 1501, "Algeria": 1532, "Cape Verde": 1533, "Uzbekistan": 1568, "Ghana": 1504,
    "DR Congo": 1508, "South Africa": 1531, "Iraq": 1567, "Jordan": 1548, "Qatar": 1569, "Ecuador": 2382, "USA": 2384, "United States": 2384,
    "Haiti": 2386, "Paraguay": 2380, "Canada": 5529, "Curacao": 5530, "New Zealand": 4673
}

def fetch_team_players_stats(team_id, team_name, season=2024):
    """Fetches players and stats for a given national team ID from api-football."""
    logging.info(f"Querying players for {team_name} (ID: {team_id}) for season {season}...")
    url = f'https://v3.football.api-sports.io/players?team={team_id}&season={season}'
    res = requests.get(url, headers=HEADERS)
    
    if res.status_code != 200:
        logging.warning(f"Failed to fetch {team_name}: HTTP status {res.status_code}")
        return []
        
    try:
        data = res.json()
        if "errors" in data and data["errors"]:
            logging.error(f"API Error: {data['errors']}")
            if "token" in str(data["errors"]).lower() or "limit" in str(data["errors"]).lower():
                # Quota exceeded or key error, raise exception to stop loop
                raise RuntimeError(f"API key quota limit reached: {data['errors']}")
            return []
            
        results = data.get("response", [])
        logging.info(f"Retrieved {len(results)} player profiles for {team_name}.")
        return results
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise e
        logging.error(f"Error parsing response for {team_name}: {e}")
        return []

def aggregate_player_stats(api_player_data, position):
    """Aggregates all stats blocks for a player (e.g. League + UCL) and converts to rates per 90."""
    player_info = api_player_data["player"]
    stats_list = api_player_data["statistics"]
    
    total_minutes = 0
    total_goals = 0
    total_assists = 0
    total_key_passes = 0
    total_tackles = 0
    total_interceptions = 0
    total_blocks = 0
    total_dribbles_succ = 0
    total_shots_on = 0
    total_passes = 0
    total_passes_acc_sum = 0.0
    
    for stats in stats_list:
        minutes = stats.get("games", {}).get("minutes") or 0
        if not minutes or minutes < 50:
            continue
            
        total_minutes += minutes
        total_goals += stats.get("goals", {}).get("total") or 0
        total_assists += stats.get("goals", {}).get("assists") or 0
        total_key_passes += stats.get("passes", {}).get("key") or 0
        total_tackles += stats.get("tackles", {}).get("total") or 0
        total_interceptions += stats.get("tackles", {}).get("interceptions") or 0
        total_blocks += stats.get("tackles", {}).get("blocks") or 0
        total_dribbles_succ += stats.get("dribbles", {}).get("success") or 0
        total_shots_on += stats.get("shots", {}).get("on") or 0
        
        passes_total = stats.get("passes", {}).get("total") or 0
        passes_acc = stats.get("passes", {}).get("accuracy") or 80.0
        # accuracy is returned as percentage integer
        total_passes += passes_total
        total_passes_acc_sum += (passes_total * (passes_acc / 100.0))
        
    if total_minutes < 150:
        return None # Not enough playing time to formulate stats
        
    # Per-90 calculation
    goals_p90 = (total_goals / total_minutes) * 90
    assists_p90 = (total_assists / total_minutes) * 90
    key_passes_p90 = (total_key_passes / total_minutes) * 90
    tackles_p90 = (total_tackles / total_minutes) * 90
    interceptions_p90 = (total_interceptions / total_minutes) * 90
    blocks_p90 = (total_blocks / total_minutes) * 90
    dribbles_p90 = (total_dribbles_succ / total_minutes) * 90
    shots_on_p90 = (total_shots_on / total_minutes) * 90
    
    pass_completion_pct = (total_passes_acc_sum / total_passes * 100.0) if total_passes > 0 else 80.0
    pass_completion_pct = min(100.0, max(50.0, pass_completion_pct))
    
    # Estimate advanced features
    xg_p90 = goals_p90 * 0.85 + shots_on_p90 * 0.1
    npxg_p90 = xg_p90
    xa_p90 = assists_p90 * 0.85 + key_passes_p90 * 0.1
    progressive_passes_p90 = key_passes_p90 * 2.5 + 0.5
    progressive_carries_p90 = dribbles_p90 * 1.8 + 0.5
    successful_dribbles_p90 = dribbles_p90
    shot_creating_actions_p90 = key_passes_p90 * 1.5 + goals_p90 * 0.5
    goal_creating_actions_p90 = assists_p90 * 1.2 + goals_p90 * 0.3
    clearances_p90 = tackles_p90 * 1.5 if position == "DF" else 0.2
    
    return {
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
        "shot_creating_actions_p90": round(shot_creating_actions_p90, 3),
        "goal_creating_actions_p90": round(goal_creating_actions_p90, 3)
    }

def main():
    player_path = os.path.join(config.RAW_DATA_DIR, "player_stats_2024_2025.parquet")
    if not os.path.exists(player_path):
        logging.error(f"Base player stats parquet file not found at {player_path}")
        return
        
    logging.info(f"Loading existing player stats database from {player_path}...")
    df_players = pd.read_parquet(player_path)
    
    # Priority national teams list (to fit easily within 100 requests limit)
    priority_teams = [
        "Argentina", "France", "Brazil", "England", "Spain", "Germany", "Mexico", "Canada", "Morocco",
        "Netherlands", "Portugal", "Belgium", "Uruguay", "United States", "Colombia", "Croatia", "Japan", "South Korea"
    ]
    
    updated_count = 0
    quota_reached = False
    
    for team in priority_teams:
        if quota_reached:
            break
            
        team_id = TEAM_IDS.get(team)
        if not team_id:
            logging.warning(f"No ID mapped for country {team}")
            continue
            
        try:
            # Query season 2024
            api_players = fetch_team_players_stats(team_id, team, season=2024)
            # Sleep 6 seconds to avoid exceeding the rate limit of 10 requests/minute
            time.sleep(6)
            
            if not api_players:
                # Fallback to season 2023 if 2024 is empty
                logging.info(f"Roster empty for {team} in 2024. Trying 2023...")
                api_players = fetch_team_players_stats(team_id, team, season=2023)
                time.sleep(6)
                
            if not api_players:
                continue
                
            # Filter rows of this team in parquet
            team_rows = df_players[df_players["national_team"] == team]
            if len(team_rows) == 0:
                logging.warning(f"No entries in local parquet for team {team}")
                continue
                
            # Build list of names in local parquet
            local_names = team_rows["player_name"].tolist()
            
            for p_data in api_players:
                api_name = p_data["player"]["name"]
                # Match to local list using fuzzy matching
                best_match, score = process.extractOne(api_name, local_names, scorer=fuzz.token_sort_ratio)
                
                if score >= 80:
                    # Retrieve matching row index
                    idx = df_players[(df_players["national_team"] == team) & (df_players["player_name"] == best_match)].index
                    if len(idx) > 0:
                        position = df_players.loc[idx[0], "position"]
                        stats_p90 = aggregate_player_stats(p_data, position)
                        
                        if stats_p90:
                            # Update statistics columns in DataFrame
                            for col, val in stats_p90.items():
                                df_players.loc[idx[0], col] = val
                            logging.info(f"Updated stats for {best_match} ({team}) from API. (Fuzzy Match: '{api_name}' -> '{best_match}', Score: {score})")
                            updated_count += 1
                            
        except RuntimeError as re:
            logging.error(f"Stopping API fetch: {re}")
            quota_reached = True
            break
        except Exception as e:
            logging.error(f"Unexpected error querying stats for {team}: {e}")
            
    # Save the updated stats parquet
    df_players.to_parquet(player_path, index=False)
    logging.info(f"Successfully updated stats for {updated_count} players from api-football.com API.")
    logging.info(f"Saved updated player stats database to {player_path}")

if __name__ == "__main__":
    main()
