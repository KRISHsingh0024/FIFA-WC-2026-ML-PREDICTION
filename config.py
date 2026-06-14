"""
Central configuration for FIFA World Cup 2026 Prediction Model.
Contains all tournament data, league definitions, feature specs, and model params.
"""

import os

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env file manually if it exists to avoid requiring extra libraries
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                val_str = val.strip()
                if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
                    val_str = val_str[1:-1]
                os.environ[key.strip()] = val_str

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "xgb_wc_predictor.pkl")

# Create directories if they don't exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── Season ──────────────────────────────────────────────────────────────────
SEASON = "2024-2025"

# ─── Leagues & Weights ──────────────────────────────────────────────────────
# League identifiers for soccerdata/FBref
LEAGUES = {
    "ENG-Premier League": {"name": "Premier League", "weight": 1.0},
    "ESP-La Liga": {"name": "La Liga", "weight": 1.0},
    "ITA-Serie A": {"name": "Serie A", "weight": 1.0},
    "GER-Bundesliga": {"name": "Bundesliga", "weight": 1.0},
    "FRA-Ligue 1": {"name": "Ligue 1", "weight": 1.0},
}

# Champions League gets higher weight (cross-league competition, higher pressure)
UCL_WEIGHT = 1.3

# ─── Stat Types to Collect from FBref ────────────────────────────────────────
STAT_TYPES = ["standard", "shooting", "passing", "defense", "possession", "gca"]

# ─── Player Feature Columns (per-90 rates) ──────────────────────────────────
PLAYER_FEATURES = {
    "attacking": [
        "goals_p90", "xg_p90", "npxg_p90", "assists_p90", "xa_p90",
        "shot_creating_actions_p90", "goal_creating_actions_p90",
    ],
    "passing": [
        "key_passes_p90", "pass_completion_pct", "progressive_passes_p90",
    ],
    "defensive": [
        "tackles_p90", "interceptions_p90", "blocks_p90", "clearances_p90",
    ],
    "possession": [
        "progressive_carries_p90", "successful_dribbles_p90",
    ],
}

ALL_PLAYER_FEATURES = []
for group in PLAYER_FEATURES.values():
    ALL_PLAYER_FEATURES.extend(group)

# ─── Team Feature Columns ───────────────────────────────────────────────────
TEAM_FEATURES = [
    "team_attack_strength",
    "team_midfield_creativity",
    "team_defense_solidity",
    "team_overall_xg",
    "team_overall_xa",
    "team_depth_score",
    "team_star_player_impact",
    "team_avg_goals_p90",
    "team_avg_assists_p90",
    "team_avg_key_passes_p90",
    "team_avg_tackles_p90",
    "team_avg_interceptions_p90",
    "team_avg_pass_completion",
    "team_avg_progressive_carries_p90",
    "team_avg_dribbles_p90",
    "team_ucl_representation",
    "team_confederation_strength",
    "team_avg_creativity_score",
    "team_avg_defensive_score",
]

# ─── Match Feature Columns ──────────────────────────────────────────────────
MATCH_FEATURES = [
    # Differential features (team_a - team_b)
    "attack_diff", "defense_diff", "midfield_diff",
    "xg_diff", "xa_diff", "depth_diff", "star_diff",
    # Ratio features
    "attack_ratio", "defense_ratio",
    # Context
    "fifa_rank_diff", "h2h_win_rate",
    "ucl_rep_diff",
    "confederation_diff",
    "creativity_diff",
    "defensive_score_diff",
]

CONFEDERATION_MAP = {
    # UEFA
    "Czechia": "UEFA", "Bosnia and Herzegovina": "UEFA", "Switzerland": "UEFA",
    "Scotland": "UEFA", "Turkey": "UEFA", "Germany": "UEFA", "Netherlands": "UEFA",
    "Sweden": "UEFA", "Belgium": "UEFA", "Spain": "UEFA", "France": "UEFA",
    "Norway": "UEFA", "Austria": "UEFA", "Portugal": "UEFA", "England": "UEFA",
    "Croatia": "UEFA", "Italy": "UEFA", "Poland": "UEFA", "Denmark": "UEFA",
    "Wales": "UEFA",
    # CONMEBOL
    "Brazil": "CONMEBOL", "Paraguay": "CONMEBOL", "Ecuador": "CONMEBOL",
    "Uruguay": "CONMEBOL", "Argentina": "CONMEBOL", "Colombia": "CONMEBOL",
    "Chile": "CONMEBOL",
    # CONCACAF
    "Mexico": "CONCACAF", "Canada": "CONCACAF", "Haiti": "CONCACAF",
    "United States": "CONCACAF", "Curacao": "CONCACAF", "Panama": "CONCACAF",
    # CAF
    "South Africa": "CAF", "Morocco": "CAF", "Ivory Coast": "CAF",
    "Tunisia": "CAF", "Egypt": "CAF", "Cape Verde": "CAF", "Senegal": "CAF",
    "Algeria": "CAF", "DR Congo": "CAF", "Ghana": "CAF", "Cameroon": "CAF",
    "Nigeria": "CAF",
    # AFC
    "South Korea": "AFC", "Qatar": "AFC", "Australia": "AFC", "Japan": "AFC",
    "Iran": "AFC", "Saudi Arabia": "AFC", "Iraq": "AFC", "Jordan": "AFC",
    "Uzbekistan": "AFC",
    # OFC
    "New Zealand": "OFC"
}

CONFEDERATION_STRENGTH = {
    "UEFA": 1.0,
    "CONMEBOL": 0.95,
    "CONCACAF": 0.70,
    "CAF": 0.65,
    "AFC": 0.60,
    "OFC": 0.40
}

# ─── World Cup 2026 — Official Groups ───────────────────────────────────────
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# All 48 teams flattened
ALL_TEAMS = []
for teams in GROUPS.values():
    ALL_TEAMS.extend(teams)

# Team → Group lookup
TEAM_TO_GROUP = {}
for group, teams in GROUPS.items():
    for team in teams:
        TEAM_TO_GROUP[team] = group

# ─── FIFA Rankings (approximate, June 2026) ─────────────────────────────────
# Used as a feature — higher rank = stronger team (rank 1 is best)
FIFA_RANKINGS = {
    "Argentina": 1, "France": 2, "England": 3, "Brazil": 4,
    "Spain": 5, "Portugal": 6, "Netherlands": 7, "Belgium": 8,
    "Germany": 9, "Italy": 10, "Croatia": 11, "Colombia": 12,
    "Uruguay": 13, "Morocco": 14, "Japan": 15, "United States": 16,
    "Mexico": 17, "Switzerland": 18, "Denmark": 19, "Senegal": 20,
    "Iran": 21, "South Korea": 22, "Austria": 23, "Australia": 24,
    "Ecuador": 25, "Turkey": 26, "Nigeria": 27, "Sweden": 28,
    "Ivory Coast": 29, "Egypt": 30, "Tunisia": 31, "Poland": 32,
    "Algeria": 33, "Scotland": 34, "Canada": 35, "Saudi Arabia": 36,
    "Costa Rica": 37, "Qatar": 38, "Ghana": 39, "Cameroon": 40,
    "Chile": 41, "Paraguay": 42, "Iraq": 43, "Norway": 44,
    "Panama": 45, "DR Congo": 46, "New Zealand": 47,
    "Bosnia and Herzegovina": 48, "Jamaica": 49, "Jordan": 50,
    "South Africa": 51, "Czechia": 52, "Cape Verde": 53,
    "Haiti": 54, "Uzbekistan": 55, "Curacao": 56,
    "United Arab Emirates": 57, "Wales": 58,
}

# ─── Knockout Bracket Structure ─────────────────────────────────────────────
# Round of 32 pairings (group winners vs third-placed teams, runners-up vs runners-up)
# This follows the official FIFA pairing rules for the 2026 format
KNOCKOUT_PAIRINGS_R32 = [
    # Match 1-16: (Group Position, Group Letter) vs (Group Position, Group Letter)
    # These are determined after group stage based on finishing positions
    # We'll compute them dynamically in the simulation
]

# ─── XGBoost Hyperparameters (defaults, will be tuned) ──────────────────────
# Configured for GPU training on the user's RTX 4060
MODEL_PARAMS = {
    "objective": "multi:softprob",
    "num_class": 3,
    "max_depth": 6,
    "learning_rate": 0.07416113391178955,
    "n_estimators": 482,
    "subsample": 0.979957279496188,
    "colsample_bytree": 0.7905374660413975,
    "min_child_weight": 1,
    "gamma": 0.9540365190451945,
    "reg_alpha": 1.219313986348916,
    "reg_lambda": 1.5882474512201703,
    "eval_metric": "mlogloss",
    "random_state": 42,
    "use_label_encoder": False,
    "device": "cuda",
    "tree_method": "hist",
}

# ─── Monte Carlo Simulation ─────────────────────────────────────────────────
NUM_SIMULATIONS = 1000
RANDOM_SEED = 42

# ─── Position Mapping ───────────────────────────────────────────────────────
POSITIONS = {
    "GK": "Goalkeeper",
    "DF": "Defender",
    "MF": "Midfielder",
    "FW": "Forward",
}

POSITION_GROUPS = {
    "Goalkeeper": ["GK"],
    "Defender": ["DF", "CB", "LB", "RB", "LWB", "RWB"],
    "Midfielder": ["MF", "CM", "DM", "AM", "LM", "RM", "CDM", "CAM"],
    "Forward": ["FW", "LW", "RW", "CF", "ST", "SS"],
}
# ─── 2026 World Cup Outlook Calibration ─────────────────────────────────────
# Calibrates prediction probabilities to match the June 2026 pre-tournament context 
# (current squad strength, bookmaker odds, and Opta supercomputer favorites).
# Higher values boost a team's win probability, negative values decrease it.
TEAM_CALIBRATION = {
    "Spain": 0.2243,
    "France": 0.2980,
    "England": 0.3286,
    "Argentina": -0.1123,
    "Portugal": 0.1823,
    "Brazil": -0.1669,
    "Germany": 0.1566,
    "Netherlands": -0.0135,
    "Uruguay": -0.0218,
    "Colombia": 0.1066,
    "United States": -0.1336,
    "Mexico": -0.1897,
    "Morocco": -0.1084
}


# ─── SMTP Configuration ──────────────────────────────────────────────────────

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ─── Resend API Configuration ────────────────────────────────────────────────
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# ─── Google OAuth Configuration ──────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

# ─── BluesMinds AI Chat Configuration ────────────────────────────────────────
BLUESMINDS_API_KEY = os.getenv("BLUESMINDS_API_KEY", "")
BLUESMINDS_BASE_URL = os.getenv("BLUESMINDS_BASE_URL", "https://api.bluesminds.com/v1")
BLUESMINDS_MODEL = "grok-4.20-fast"

# ─── Chat Security Configuration ─────────────────────────────────────────────
CHAT_RATE_LIMIT_PER_MINUTE = 10  # Max chat requests per IP per minute
CHAT_MAX_MESSAGE_LENGTH = 1000   # Max characters per user message
CHAT_MAX_HISTORY_LENGTH = 20     # Max messages in conversation history
CHAT_ALLOWED_ORIGINS = [         # CORS allowlisting for production
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

