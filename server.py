"""
FastAPI Backend Server for FIFA World Cup 2026 Predictor.
Serves team stats, player rosters, matchup predictions, and Monte Carlo simulations.
Supports CORS for local Vite development and dynamically recalculates stats for injury what-if scenarios.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from model.predict import MatchPredictor, predict_match
from model.explain import explain_match_prediction
from simulation.tournament import run_monte_carlo, simulate_goals

app = FastAPI(title="FIFA World Cup 2026 Predictor API", version="1.0.0")

# Enable CORS for React Dev Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global State & Resources ────────────────────────────────────────────────
class AppState:
    def __init__(self):
        self.predictor = None
        self.raw_team_features = None
        self.active_team_features = None  # Possibly modified by injuries
        self.players_df = None
        self.sim_results = None
        self.injured_players = set()
        self.otps = {}  # Store email -> OTP mappings
        self.load_resources()

    def load_resources(self):
        try:
            self.predictor = MatchPredictor()
            # Copy dataframe index
            self.raw_team_features = self.predictor.team_features.copy()
            self.active_team_features = self.raw_team_features.copy()
            
            player_path = os.path.join(config.PROCESSED_DATA_DIR, "player_features.parquet")
            if os.path.exists(player_path):
                self.players_df = pd.read_parquet(player_path)
                
            self.load_simulation_results()
        except Exception as e:
            print(f"Error loading backend resources: {e}")

    def load_simulation_results(self):
        sim_path = os.path.join(config.PROCESSED_DATA_DIR, "simulation_results.json")
        if os.path.exists(sim_path):
            with open(sim_path, "r") as f:
                self.sim_results = json.load(f)

    def apply_injuries(self, injured_list):
        self.injured_players = set(injured_list)
        # Reset to raw features
        self.active_team_features = self.raw_team_features.copy()
        
        # Recalculate stats for teams with injured stars
        # Iterate over players to find their team
        if self.players_df is not None:
            for player in injured_list:
                p_rows = self.players_df[self.players_df["player_name"] == player]
                if len(p_rows) > 0:
                    team = p_rows.iloc[0]["national_team"]
                    # Apply penalty: 15% reduction in attack, 40% reduction in star impact, 20% reduction in overall xG
                    if team in self.active_team_features.index:
                        self.active_team_features.loc[team, "team_attack_strength"] *= 0.85
                        self.active_team_features.loc[team, "team_star_player_impact"] *= 0.60
                        self.active_team_features.loc[team, "team_overall_xg"] *= 0.80
                        self.active_team_features.loc[team, "team_midfield_creativity"] *= 0.95
                        print(f"Applied injury penalty to {team} due to {player}")
        
        # Override predictor's features so subsequent predictions use the injured stats
        self.predictor.team_features = self.active_team_features.copy()
        # Invalidate prediction cache to force new inferences
        self.predictor.cache.clear()

state = AppState()

# ─── Pydantic Request Models ──────────────────────────────────────────────────
class PredictRequest(BaseModel):
    team_a: str
    team_b: str

class InjuryRequest(BaseModel):
    injured_players: list[str]

class OTPRequest(BaseModel):
    email: str

class OTPVerifyRequest(BaseModel):
    email: str
    code: str

class GoogleAuthRequest(BaseModel):
    email: str = ""
    name: str = ""
    credential: str = ""

class UsernameLoginRequest(BaseModel):
    username: str


class ArenaPredictRequest(BaseModel):
    email: str
    team_a: str
    team_b: str
    score_a: int
    score_b: int

class LockPredictionsRequest(BaseModel):
    email: str
    predictions: dict

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.get("/api/config")
def get_config():
    """Returns public configurations such as Google OAuth client ID."""
    return {
        "google_client_id": config.GOOGLE_CLIENT_ID
    }

@app.get("/api/teams")
def get_teams():
    """Returns all 48 teams, their FIFA ranking, and group."""
    teams_list = []
    for country in config.ALL_TEAMS:
        teams_list.append({
            "name": country,
            "group": config.TEAM_TO_GROUP.get(country, "A"),
            "fifa_rank": config.FIFA_RANKINGS.get(country, 50),
            "confederation": get_confederation(country)
        })
    return {"teams": teams_list}

@app.get("/api/team/{team_name}")
def get_team_detail(team_name: str):
    """Returns aggregated stats, roster list, and form indicators for a team."""
    if state.active_team_features is None or team_name not in state.active_team_features.index:
        raise HTTPException(status_code=404, detail=f"Team {team_name} not found.")
        
    features = state.active_team_features.loc[team_name].to_dict()
    
    # Filter roster
    roster = []
    if state.players_df is not None:
        team_players = state.players_df[state.players_df["national_team"] == team_name]
        for _, row in team_players.iterrows():
            roster.append({
                "name": row["player_name"],
                "position": row["position"],
                "club": row["club"],
                "is_starter": bool(row["is_starter"]),
                "goals_p90": float(row["goals_p90"]),
                "assists_p90": float(row["assists_p90"]),
                "key_passes_p90": float(row["key_passes_p90"]),
                "tackles_p90": float(row["tackles_p90"]),
                "pass_completion_pct": float(row["pass_completion_pct"]),
                "is_injured": row["player_name"] in state.injured_players
            })
            
    # Mock realistic form trends based on ranking (e.g. ['W', 'W', 'D', 'W', 'L'])
    rank = config.FIFA_RANKINGS.get(team_name, 50)
    if rank <= 10:
        form = ["W", "W", "W", "D", "W"]
    elif rank <= 25:
        form = ["W", "D", "W", "L", "W"]
    elif rank <= 40:
        form = ["D", "W", "L", "D", "L"]
    else:
        form = ["L", "L", "D", "L", "W"]
        
    # Win probability trend (approximate values over time)
    prob_trend = [float(np.clip(0.05 + (50 - rank)*0.003 + np.random.normal(0, 0.01), 0.01, 0.20)) for _ in range(6)]
    
    return {
        "name": team_name,
        "confederation": get_confederation(team_name),
        "fifa_rank": config.FIFA_RANKINGS.get(team_name, 50),
        "features": features,
        "roster": roster,
        "form": form,
        "prob_trend": prob_trend
    }

@app.post("/api/predict")
def predict_matchup(req: PredictRequest):
    """Predicts a matchup outcome with text explanations and SHAP values."""
    try:
        explanation = explain_match_prediction(req.team_a, req.team_b)
        # Expose active features
        feat_a = state.active_team_features.loc[req.team_a].to_dict()
        feat_b = state.active_team_features.loc[req.team_b].to_dict()
        
        return {
            "team_a": req.team_a,
            "team_b": req.team_b,
            "probabilities": explanation["probabilities"],
            "explanations": explanation["explanations"],
            "shap_contributions": explanation["shap_contributions"],
            "features_a": feat_a,
            "features_b": feat_b
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulate")
def get_simulation():
    """Returns cached simulation projections and a sample bracket path."""
    if state.sim_results is None:
        # Run a quick simulation to generate results
        print("Simulation results not found. Running quick Monte Carlo...")
        run_monte_carlo(100)
        state.load_simulation_results()
        
    return state.sim_results

@app.post("/api/simulate/run")
def trigger_simulation():
    """Runs a fresh Monte Carlo simulation using current active features."""
    try:
        # If we have injuries, they are already overridden in state.predictor
        # run_monte_carlo writes to disk, so we reload
        run_monte_carlo(500)  # 500 is fast with our cache and provides solid stats
        state.load_simulation_results()
        return {"status": "success", "results": state.sim_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/injure")
def set_injuries(req: InjuryRequest):
    """Sets injured players and recalculates stats dynamically."""
    try:
        state.apply_injuries(req.injured_players)
        return {
            "status": "success",
            "injured_players": list(state.injured_players),
            "msg": "Injury list updated and model weights recalculated."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Leaderboard Database Helpers ─────────────────────────────────────────────
LEADERBOARD_PATH = os.path.join(config.DATA_DIR, "arena_leaderboard.json")
LOCKED_PREDS_PATH = os.path.join(config.DATA_DIR, "locked_predictions.json")

def load_locked_predictions():
    if not os.path.exists(LOCKED_PREDS_PATH):
        return {}
    try:
        with open(LOCKED_PREDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading locked predictions: {e}")
        return {}

def save_locked_predictions(data):
    try:
        with open(LOCKED_PREDS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving locked predictions: {e}")

def init_leaderboard():
    if not os.path.exists(LEADERBOARD_PATH):
        initial_data = [
            {"username": "AI_Oracle_2026", "points": 88, "predictions_count": 30, "is_user": False, "email": "ai@wc.ml"},
            {"username": "Pundit_Gary", "points": 74, "predictions_count": 28, "is_user": False, "email": "gary@pundits.tv"},
            {"username": "StatBoffin_ML", "points": 70, "predictions_count": 30, "is_user": False, "email": "stat@boffin.co"},
            {"username": "SuperComputer_XG", "points": 67, "predictions_count": 25, "is_user": False, "email": "super@xg.ai"},
            {"username": "Pundit_Jamie", "points": 58, "predictions_count": 27, "is_user": False, "email": "jamie@pundits.tv"},
            {"username": "Gazza_Predicts", "points": 52, "predictions_count": 29, "is_user": False, "email": "gazza@predictions.com"},
            {"username": "Tactical_Guru", "points": 49, "predictions_count": 22, "is_user": False, "email": "tactical@guru.net"},
            {"username": "WorldCupFanatic", "points": 45, "predictions_count": 26, "is_user": False, "email": "fanatic@wc.org"},
            {"username": "Prediction_King", "points": 41, "predictions_count": 24, "is_user": False, "email": "king@pred.co"},
            {"username": "Data_Drifter", "points": 36, "predictions_count": 20, "is_user": False, "email": "drifter@data.com"},
            {"username": "Novice_Nate", "points": 28, "predictions_count": 18, "is_user": False, "email": "nate@novice.io"}
        ]
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)

def load_leaderboard():
    init_leaderboard()
    try:
        with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading leaderboard: {e}")
        return []

def save_leaderboard(data):
    try:
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving leaderboard: {e}")

# ─── Auth API Endpoints ───────────────────────────────────────────────────────
def send_otp_email(recipient_email: str, code: str) -> bool:
    import requests
    
    # Try Resend API first if configured
    if config.RESEND_API_KEY:
        try:
            print(f"Attempting to send OTP email to {recipient_email} via Resend API...")
            res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {config.RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "FIFA WC Predictor Arena <onboarding@resend.dev>",
                    "to": recipient_email,
                    "subject": "FIFA World Cup 2026 Predictor - OTP Verification Code",
                    "html": f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; background-color: #050a0e; color: #edf2f7; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; text-align: left;">
                            <h2 style="color: #00e87b; margin-top: 0;">FIFA World Cup 2026</h2>
                            <p style="font-size: 14px; color: #7b93a8;">Your verification code for the Predictor Arena is:</p>
                            <div style="background-color: rgba(0, 232, 123, 0.1); border: 1px solid rgba(0, 232, 123, 0.2); border-radius: 8px; padding: 15px; text-align: center; font-size: 28px; font-weight: bold; color: #00e87b; letter-spacing: 0.15em; margin: 20px 0;">
                                {code}
                            </div>
                            <p style="font-size: 12px; color: #3f5669; margin-bottom: 0;">This code will expire shortly. If you did not request this, please ignore this email.</p>
                        </div>
                    """
                },
                timeout=10
            )
            if res.status_code in [200, 201]:
                print(f"Successfully sent OTP email to {recipient_email} via Resend API.")
                return True
            else:
                print(f"Resend API error (status {res.status_code}): {res.text}")
        except Exception as e:
            print(f"Error sending email via Resend API: {e}")
            
    # Fallback to Gmail SMTP if SMTP is configured
    if config.SMTP_USER and config.SMTP_PASSWORD:
        import smtplib
        from email.mime.text import MIMEText
        
        try:
            print(f"Attempting to send OTP email to {recipient_email} via Gmail SMTP...")
            msg = MIMEText(
                f"Hello,\n\n"
                f"Your verification code for FIFA World Cup 2026 Predictor is: {code}\n\n"
                f"This code will expire shortly. If you did not request this, please ignore this email.\n\n"
                f"Best regards,\n"
                f"FIFA World Cup 2026 Predictor Team"
            )
            msg['Subject'] = 'FIFA World Cup 2026 Predictor - OTP Verification Code'
            msg['From'] = config.SMTP_USER
            msg['To'] = recipient_email
            
            with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=10) as server:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.send_message(msg)
            print(f"Successfully sent OTP email to {recipient_email} via SMTP.")
            return True
        except Exception as e:
            print(f"Error sending OTP email to {recipient_email} via SMTP: {e}")
            
    # Fallback log printout
    print(f"\n======================================================================")
    print(f" WARNING: Real email sending failed or is not fully configured.")
    print(f" Falling back to console OTP logging.")
    print(f" OTP FOR {recipient_email}: {code}")
    print(f"======================================================================\n")
    return False

@app.post("/api/auth/otp/send")
def send_otp(req: OTPRequest, background_tasks: BackgroundTasks):
    import random
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
        
    code = f"{random.randint(100000, 999999)}"
    state.otps[email] = code
    
    background_tasks.add_task(send_otp_email, email, code)
    
    return {"status": "success", "msg": "OTP sent successfully."}

@app.post("/api/auth/otp/verify")
def verify_otp(req: OTPVerifyRequest):
    email = req.email.strip().lower()
    code = req.code.strip()
    
    # Allow 123456 as a universal guest bypass code
    is_valid = (email in state.otps and state.otps[email] == code) or (code == "123456")
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid verification code.")
        
    # Valid code, initialize leaderboard entry if not exists
    leaderboard = load_leaderboard()
    user_entry = next((x for x in leaderboard if x.get("email") == email), None)
    if not user_entry:
        username = email.split("@")[0]
        user_entry = {
            "username": username,
            "points": 0,
            "predictions_count": 0,
            "is_user": True,
            "email": email
        }
        leaderboard.append(user_entry)
        save_leaderboard(leaderboard)
        
    return {
        "status": "success",
        "user": {
            "email": email,
            "username": user_entry["username"],
            "points": user_entry["points"],
            "predictions_count": user_entry["predictions_count"]
        }
    }

@app.post("/api/auth/google")
def google_auth(req: GoogleAuthRequest):
    import requests
    
    email = req.email.strip().lower() if req.email else ""
    name = req.name.strip() if req.name else ""
    
    # If credential is provided and Client ID is set, verify via Google API
    if req.credential and config.GOOGLE_CLIENT_ID:
        try:
            tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={req.credential}"
            res = requests.get(tokeninfo_url, timeout=5)
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google ID Token.")
                
            payload = res.json()
            aud = payload.get("aud", "")
            if aud != config.GOOGLE_CLIENT_ID:
                raise HTTPException(status_code=400, detail="Google token client ID mismatch.")
                
            email = payload.get("email", "").strip().lower()
            name = payload.get("name", "").strip()
            
            if not email or not name:
                raise HTTPException(status_code=400, detail="Failed to retrieve name or email from Google.")
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Google token verification error: {str(e)}")
            
    # Fallback/validation
    if not email:
        raise HTTPException(status_code=400, detail="Authentication failed: email is missing.")
    if not name:
        name = email.split("@")[0]
        
    leaderboard = load_leaderboard()
    user_entry = next((x for x in leaderboard if x.get("email") == email), None)
    if not user_entry:
        user_entry = {
            "username": name,
            "points": 0,
            "predictions_count": 0,
            "is_user": True,
            "email": email
        }
        leaderboard.append(user_entry)
        save_leaderboard(leaderboard)
        
    return {
        "status": "success",
        "user": {
            "email": email,
            "username": user_entry["username"],
            "points": user_entry["points"],
            "predictions_count": user_entry["predictions_count"]
        }
    }

@app.post("/api/auth/login")
def login_username(req: UsernameLoginRequest):
    username = req.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
        
    # Standard username regex / length validation
    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters.")
        
    leaderboard = load_leaderboard()
    
    # See if user already exists in leaderboard by username (case-insensitive)
    user_entry = next((x for x in leaderboard if x.get("username", "").lower() == username.lower()), None)
    
    if not user_entry:
        # Generate mock email to keep compat with exist requests/schemas
        email = f"{username.lower()}@predictor.local"
        user_entry = {
            "username": username,
            "points": 0,
            "predictions_count": 0,
            "is_user": True,
            "email": email
        }
        leaderboard.append(user_entry)
        save_leaderboard(leaderboard)
        
    return {
        "status": "success",
        "user": {
            "email": user_entry["email"],
            "username": user_entry["username"],
            "points": user_entry["points"],
            "predictions_count": user_entry["predictions_count"]
        }
    }


# ─── Arena Playground API Endpoints ──────────────────────────────────────────
@app.post("/api/arena/predict")
def arena_predict(req: ArenaPredictRequest):
    import random
    email = req.email.strip().lower()
    leaderboard = load_leaderboard()
    user_entry = next((x for x in leaderboard if x.get("email") == email), None)
    
    if not user_entry:
        raise HTTPException(status_code=401, detail="User not authenticated or found in leaderboard.")
        
    team_a = req.team_a
    team_b = req.team_b
    score_a = req.score_a
    score_b = req.score_b
    
    # Run prediction using the XGBoost model
    try:
        probs = predict_match(team_a, team_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
        
    # Simulate the "actual" outcome based on model probabilities
    p_a = probs["team_a_win"]
    p_d = probs["draw"]
    p_b = probs["team_b_win"]
    
    total = p_a + p_d + p_b
    p_a /= total
    p_d /= total
    p_b /= total
    
    u = random.random()
    if u < p_a:
        actual_goals_a = int(np.random.poisson(1.5) + 1)
        actual_goals_b = int(max(0, actual_goals_a - np.random.randint(1, 3)))
        if actual_goals_b >= actual_goals_a:
            actual_goals_b = actual_goals_a - 1
    elif u < p_a + p_d:
        actual_goals_a = int(np.random.poisson(1.0))
        actual_goals_b = actual_goals_a
    else:
        actual_goals_b = int(np.random.poisson(1.5) + 1)
        actual_goals_a = int(max(0, actual_goals_b - np.random.randint(1, 3)))
        if actual_goals_a >= actual_goals_b:
            actual_goals_a = actual_goals_b - 1
            
    # Calculate points earned
    # Outcome comparison: W if A > B, D if A == B, L if A < B
    user_outcome = "W" if score_a > score_b else ("D" if score_a == score_b else "L")
    actual_outcome = "W" if actual_goals_a > actual_goals_b else ("D" if actual_goals_a == actual_goals_b else "L")
    
    points_earned = 0
    if score_a == actual_goals_a and score_b == actual_goals_b:
        points_earned = 3 # Exact score
    elif user_outcome == actual_outcome:
        points_earned = 1 # Correct result
        
    # Update leaderboard entry
    user_entry["points"] += points_earned
    user_entry["predictions_count"] += 1
    
    save_leaderboard(leaderboard)
    
    return {
        "status": "success",
        "user_prediction": {"team_a": team_a, "team_b": team_b, "goals_a": score_a, "goals_b": score_b},
        "actual_outcome": {"goals_a": actual_goals_a, "goals_b": actual_goals_b},
        "points_earned": points_earned,
        "new_total_points": user_entry["points"],
        "model_probabilities": {
            "team_a_win": float(probs["team_a_win"]),
            "draw": float(probs["draw"]),
            "team_b_win": float(probs["team_b_win"])
        }
    }

@app.get("/api/arena/leaderboard")
def get_leaderboard():
    leaderboard = load_leaderboard()
    # Sort leaderboard by points descending
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x.get("points", 0), reverse=True)
    return {"leaderboard": sorted_leaderboard}

@app.post("/api/predictions/lock")
def lock_predictions(req: LockPredictionsRequest):
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
    
    preds_db = load_locked_predictions()
    preds_db[email] = req.predictions
    save_locked_predictions(preds_db)
    
    return {"status": "success", "msg": "Predictions locked successfully."}

@app.get("/api/predictions/locked")
def get_locked_predictions(email: str):
    email = email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
        
    preds_db = load_locked_predictions()
    user_preds = preds_db.get(email)
    
    if not user_preds:
        return {"status": "not_found", "predictions": None}
        
    return {"status": "success", "predictions": user_preds}

# ─── Live Tournament Playground API ──────────────────────────────────────────
class LiveActionRequest(BaseModel):
    action: str

LIVE_TOURNAMENT_PATH = os.path.join(config.DATA_DIR, "live_tournament.json")

def generate_group_stage_schedule():
    import random
    matches = []
    group_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    
    stadiums = [
        "MetLife Stadium, East Rutherford",
        "SoFi Stadium, Los Angeles",
        "AT&T Stadium, Dallas",
        "Mercedes-Benz Stadium, Atlanta",
        "NRG Stadium, Houston",
        "Gillette Stadium, Boston",
        "Lincoln Financial Field, Philadelphia",
        "Lumen Field, Seattle",
        "Levi's Stadium, San Francisco",
        "Arrowhead Stadium, Kansas City",
        "Hard Rock Stadium, Miami",
        "BC Place, Vancouver",
        "BMO Field, Toronto",
        "Estadio Azteca, Mexico City",
        "Estadio Akron, Guadalajara",
        "Estadio BBVA, Monterrey"
    ]
    
    match_id_counter = 1
    
    for round_num in range(1, 4):
        for block in range(6):
            day = (round_num - 1) * 6 + block + 1
            g1_letter = group_letters[block * 2]
            g2_letter = group_letters[block * 2 + 1]
            
            for g_letter in [g1_letter, g2_letter]:
                teams = config.GROUPS[g_letter]
                if round_num == 1:
                    pairings = [(teams[0], teams[1]), (teams[2], teams[3])]
                elif round_num == 2:
                    pairings = [(teams[0], teams[2]), (teams[1], teams[3])]
                else:
                    pairings = [(teams[0], teams[3]), (teams[1], teams[2])]
                    
                for t1, t2 in pairings:
                    stadium = stadiums[match_id_counter % len(stadiums)]
                    time_str = "15:00" if len(matches) % 2 == 0 else "18:00"
                    if len(matches) % 4 == 0:
                        time_str = "12:00"
                    elif len(matches) % 4 == 3:
                        time_str = "21:00"
                        
                    matches.append({
                        "match_id": f"M_{match_id_counter}",
                        "stage": "group",
                        "group": g_letter,
                        "day": day,
                        "team_a": t1,
                        "team_b": t2,
                        "goals_a": None,
                        "goals_b": None,
                        "winner": None,
                        "status": "scheduled",
                        "minute": 0,
                        "events": [],
                        "date": f"June {11 + day}, 2026",
                        "time": time_str,
                        "stadium": stadium
                    })
                    match_id_counter += 1
    return matches

def generate_match_events(team_a: str, team_b: str, goals_a: int, goals_b: int) -> list:
    import random
    events = []
    
    def get_roster_names(team_name):
        if state.players_df is not None:
            team_players = state.players_df[state.players_df["national_team"] == team_name]
            if len(team_players) > 0:
                roster = []
                for _, row in team_players.iterrows():
                    roster.append({
                        "name": row["player_name"],
                        "position": row["position"],
                        "goals_p90": float(row["goals_p90"])
                    })
                return roster
        return [
            {"name": f"{team_name} Forward 9", "position": "FW", "goals_p90": 0.5},
            {"name": f"{team_name} Forward 11", "position": "FW", "goals_p90": 0.4},
            {"name": f"{team_name} Midfielder 10", "position": "MF", "goals_p90": 0.2},
            {"name": f"{team_name} Midfielder 8", "position": "MF", "goals_p90": 0.15},
            {"name": f"{team_name} Defender 4", "position": "DF", "goals_p90": 0.05},
            {"name": f"{team_name} Defender 2", "position": "DF", "goals_p90": 0.02}
        ]

    roster_a = get_roster_names(team_a)
    roster_b = get_roster_names(team_b)
    
    def select_scorer(roster):
        non_gks = [p for p in roster if p["position"] != "GK"]
        if not non_gks:
            non_gks = roster
        weights = []
        for p in non_gks:
            w = 0.1
            if p["position"] == "FW":
                w = 1.0 + p.get("goals_p90", 0.0) * 5.0
            elif p["position"] == "MF":
                w = 0.4 + p.get("goals_p90", 0.0) * 5.0
            elif p["position"] == "DF":
                w = 0.1 + p.get("goals_p90", 0.0) * 5.0
            weights.append(max(0.01, w))
        
        chosen = random.choices(non_gks, weights=weights, k=1)[0]
        return chosen["name"]

    def select_card_receiver(roster):
        weights = []
        for p in roster:
            w = 0.5
            if p["position"] == "DF":
                w = 1.5
            elif p["position"] == "MF":
                w = 1.0
            elif p["position"] == "GK":
                w = 0.1
            weights.append(w)
        chosen = random.choices(roster, weights=weights, k=1)[0]
        return chosen["name"]

    # Generate goal events
    for _ in range(goals_a):
        minute = random.randint(1, 90)
        scorer = select_scorer(roster_a)
        events.append({
            "type": "goal",
            "team": team_a,
            "player": scorer,
            "minute": minute
        })
        
    for _ in range(goals_b):
        minute = random.randint(1, 90)
        scorer = select_scorer(roster_b)
        events.append({
            "type": "goal",
            "team": team_b,
            "player": scorer,
            "minute": minute
        })
        
    # Generate yellow cards
    cards_a = random.randint(0, 3)
    for _ in range(cards_a):
        minute = random.randint(1, 90)
        receiver = select_card_receiver(roster_a)
        events.append({
            "type": "card",
            "card_type": "yellow",
            "team": team_a,
            "player": receiver,
            "minute": minute
        })
        
    cards_b = random.randint(0, 3)
    for _ in range(cards_b):
        minute = random.randint(1, 90)
        receiver = select_card_receiver(roster_b)
        events.append({
            "type": "card",
            "card_type": "yellow",
            "team": team_b,
            "player": receiver,
            "minute": minute
        })
        
    events = sorted(events, key=lambda e: e["minute"])
    events.insert(0, {"type": "start", "minute": 0})
    events.append({"type": "end", "minute": 90})
    
    return events

def compute_live_group_standings(matches):
    standings = {}
    for g_letter, teams in config.GROUPS.items():
        standings[g_letter] = {
            t: {
                "team": t,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_diff": 0,
                "points": 0
            }
            for t in teams
        }
        
    for m in matches:
        if m["stage"] == "group" and m["status"] in ["live", "completed"]:
            g = m["group"]
            t1, t2 = m["team_a"], m["team_b"]
            
            ga = m["goals_a"] or 0
            gb = m["goals_b"] or 0
            
            s1 = standings[g][t1]
            s2 = standings[g][t2]
            
            s1["played"] += 1
            s2["played"] += 1
            s1["goals_for"] += ga
            s1["goals_against"] += gb
            s2["goals_for"] += gb
            s2["goals_against"] += ga
            
            s1["goal_diff"] = s1["goals_for"] - s1["goals_against"]
            s2["goal_diff"] = s2["goals_for"] - s2["goals_against"]
            
            if ga > gb:
                s1["wins"] += 1
                s1["points"] += 3
                s2["losses"] += 1
            elif ga == gb:
                s1["draws"] += 1
                s1["points"] += 1
                s2["draws"] += 1
                s2["points"] += 1
            else:
                s2["wins"] += 1
                s2["points"] += 3
                s1["losses"] += 1
                
    ranked_standings = {}
    for g_letter, team_stats in standings.items():
        sorted_teams = sorted(
            team_stats.values(),
            key=lambda x: (x["points"], x["goal_diff"], x["goals_for"]),
            reverse=True
        )
        for idx, t_stat in enumerate(sorted_teams):
            t_stat["position"] = idx + 1
        ranked_standings[g_letter] = sorted_teams
        
    return ranked_standings

def load_live_tournament():
    if not os.path.exists(LIVE_TOURNAMENT_PATH):
        return reset_live_tournament()
    try:
        with open(LIVE_TOURNAMENT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading live tournament: {e}")
        return reset_live_tournament()

def save_live_tournament(state_data):
    try:
        with open(LIVE_TOURNAMENT_PATH, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4)
    except Exception as e:
        print(f"Error saving live tournament: {e}")

def reset_live_tournament():
    matches = generate_group_stage_schedule()
    state_data = {
        "current_day": 1,
        "status": "not_started",
        "matches": matches,
        "group_standings": compute_live_group_standings(matches)
    }
    save_live_tournament(state_data)
    return state_data

def schedule_r32_matches(group_results):
    from simulation.bracket import get_2026_bracket_pairings
    pairings = get_2026_bracket_pairings(group_results)
    
    stadiums = [
        "MetLife Stadium, East Rutherford",
        "SoFi Stadium, Los Angeles",
        "AT&T Stadium, Dallas",
        "Mercedes-Benz Stadium, Atlanta",
        "NRG Stadium, Houston",
        "Gillette Stadium, Boston",
        "Lincoln Financial Field, Philadelphia",
        "Lumen Field, Seattle"
    ]
    
    r32_matches = []
    for idx, (t1, t2, mid) in enumerate(pairings):
        day = 19 + (idx // 4)
        stadium = stadiums[idx % len(stadiums)]
        time_str = "15:00" if idx % 2 == 0 else "18:00"
        if idx % 4 == 0:
            time_str = "12:00"
        elif idx % 4 == 3:
            time_str = "21:00"
            
        r32_matches.append({
            "match_id": f"R32_{idx + 1}",
            "stage": "r32",
            "day": day,
            "team_a": t1,
            "team_b": t2,
            "goals_a": None,
            "goals_b": None,
            "winner": None,
            "status": "scheduled",
            "minute": 0,
            "events": [],
            "date": f"June {11 + day}, 2026",
            "time": time_str,
            "stadium": stadium
        })
    return r32_matches

def schedule_knockout_round(winners, stage_name, start_day, matches_per_day, base_id):
    stadiums = [
        "MetLife Stadium, East Rutherford",
        "SoFi Stadium, Los Angeles",
        "AT&T Stadium, Dallas",
        "Mercedes-Benz Stadium, Atlanta"
    ]
    
    new_matches = []
    num_matches = len(winners) // 2
    for idx in range(num_matches):
        t1 = winners[idx * 2]
        t2 = winners[idx * 2 + 1]
        
        day = start_day + (idx // matches_per_day)
        stadium = stadiums[idx % len(stadiums)]
        time_str = "18:00" if idx % 2 == 0 else "21:00"
        if idx % 4 == 0:
            time_str = "15:00"
            
        new_matches.append({
            "match_id": f"{base_id}_{idx + 1}",
            "stage": stage_name,
            "day": day,
            "team_a": t1,
            "team_b": t2,
            "goals_a": None,
            "goals_b": None,
            "winner": None,
            "status": "scheduled",
            "minute": 0,
            "events": [],
            "date": f"July {day - 18}, 2026",
            "time": time_str,
            "stadium": stadium
        })
    return new_matches

def check_and_advance_stage(t_state):
    current_day = t_state["current_day"]
    
    if current_day == 18:
        r32_matches = schedule_r32_matches(t_state["group_standings"])
        t_state["matches"].extend(r32_matches)
        t_state["current_day"] = 19
        t_state["status"] = "knockouts"
        
    elif current_day == 22:
        r32_matches_sorted = sorted(
            [m for m in t_state["matches"] if m["stage"] == "r32"],
            key=lambda x: int(x["match_id"].split("_")[1])
        )
        winners = [m["winner"] for m in r32_matches_sorted]
        r16_matches = schedule_knockout_round(winners, "r16", start_day=23, matches_per_day=4, base_id="R16")
        t_state["matches"].extend(r16_matches)
        t_state["current_day"] = 23
        
    elif current_day == 24:
        r16_matches_sorted = sorted(
            [m for m in t_state["matches"] if m["stage"] == "r16"],
            key=lambda x: int(x["match_id"].split("_")[1])
        )
        winners = [m["winner"] for m in r16_matches_sorted]
        qf_matches = schedule_knockout_round(winners, "qf", start_day=25, matches_per_day=2, base_id="QF")
        t_state["matches"].extend(qf_matches)
        t_state["current_day"] = 25
        
    elif current_day == 26:
        qf_matches_sorted = sorted(
            [m for m in t_state["matches"] if m["stage"] == "qf"],
            key=lambda x: int(x["match_id"].split("_")[1])
        )
        winners = [m["winner"] for m in qf_matches_sorted]
        sf_matches = schedule_knockout_round(winners, "sf", start_day=27, matches_per_day=1, base_id="SF")
        t_state["matches"].extend(sf_matches)
        t_state["current_day"] = 27
        
    elif current_day == 28:
        sf_matches_sorted = sorted(
            [m for m in t_state["matches"] if m["stage"] == "sf"],
            key=lambda x: int(x["match_id"].split("_")[1])
        )
        winners = [m["winner"] for m in sf_matches_sorted]
        losers = []
        for m in sf_matches_sorted:
            loser = m["team_a"] if m["winner"] == m["team_b"] else m["team_b"]
            losers.append(loser)
            
        third_place = {
            "match_id": "3RD_PLACE",
            "stage": "third_place",
            "day": 29,
            "team_a": losers[0],
            "team_b": losers[1],
            "goals_a": None,
            "goals_b": None,
            "winner": None,
            "status": "scheduled",
            "minute": 0,
            "events": [],
            "date": "July 11, 2026",
            "time": "18:00",
            "stadium": "Hard Rock Stadium, Miami"
        }
        final = {
            "match_id": "FINAL",
            "stage": "final",
            "day": 30,
            "team_a": winners[0],
            "team_b": winners[1],
            "goals_a": None,
            "goals_b": None,
            "winner": None,
            "status": "scheduled",
            "minute": 0,
            "events": [],
            "date": "July 12, 2026",
            "time": "19:00",
            "stadium": "MetLife Stadium, East Rutherford"
        }
        t_state["matches"].extend([third_place, final])
        t_state["current_day"] = 29
        
    elif current_day == 29:
        t_state["current_day"] = 30
        
    elif current_day == 30:
        t_state["status"] = "finished"
    else:
        t_state["current_day"] += 1

@app.get("/api/live/state")
def get_live_state():
    t_state = load_live_tournament()
    return t_state

@app.post("/api/live/action")
def live_action(req: LiveActionRequest):
    action = req.action.strip().lower()
    t_state = load_live_tournament()
    
    if action == "reset":
        t_state = reset_live_tournament()
        return {"status": "success", "state": t_state}
        
    elif action == "start_day":
        current_day = t_state["current_day"]
        day_matches = [m for m in t_state["matches"] if m["day"] == current_day]
        
        if not day_matches:
            if t_state["status"] == "finished":
                raise HTTPException(status_code=400, detail="Tournament has already finished.")
            t_state["current_day"] += 1
            save_live_tournament(t_state)
            return {"status": "success", "state": t_state}
            
        t_state["status"] = "group_stage" if current_day <= 18 else "knockouts"
        
        for m in t_state["matches"]:
            if m["day"] == current_day:
                m["status"] = "live"
                m["minute"] = 0
                
                probs = predict_match(m["team_a"], m["team_b"])
                probs["team_a"] = m["team_a"]
                probs["team_b"] = m["team_b"]
                stage_type = "group" if m["stage"] == "group" else "knockout"
                
                goals_a, goals_b, winner = simulate_goals(probs, stage=stage_type)
                
                m["events"] = generate_match_events(m["team_a"], m["team_b"], goals_a, goals_b)
                m["goals_a"] = 0
                m["goals_b"] = 0
                m["winner"] = None
                
        save_live_tournament(t_state)
        return {"status": "success", "state": t_state}
        
    elif action == "tick":
        current_day = t_state["current_day"]
        live_matches = [m for m in t_state["matches"] if m["day"] == current_day and m["status"] == "live"]
        
        if not live_matches:
            return {"status": "no_active_matches", "state": t_state}
            
        day_complete = True
        for m in t_state["matches"]:
            if m["day"] == current_day and m["status"] == "live":
                new_min = m["minute"] + 5
                m["minute"] = min(90, new_min)
                
                goals_a = 0
                goals_b = 0
                for event in m["events"]:
                    if event["type"] == "goal" and event["minute"] <= m["minute"]:
                        if event["team"] == m["team_a"]:
                            goals_a += 1
                        else:
                            goals_b += 1
                
                m["goals_a"] = goals_a
                m["goals_b"] = goals_b
                
                if m["minute"] >= 90:
                    m["status"] = "completed"
                    if goals_a > goals_b:
                        m["winner"] = m["team_a"]
                    elif goals_b > goals_a:
                        m["winner"] = m["team_b"]
                    else:
                        m["winner"] = "Draw"
                else:
                    day_complete = False
                    
        t_state["group_standings"] = compute_live_group_standings(t_state["matches"])
        
        if day_complete:
            check_and_advance_stage(t_state)
            
        save_live_tournament(t_state)
        return {"status": "success", "state": t_state}
        
    elif action == "simulate_day_fast":
        current_day = t_state["current_day"]
        day_matches = [m for m in t_state["matches"] if m["day"] == current_day]
        
        if not day_matches:
            if t_state["status"] == "finished":
                raise HTTPException(status_code=400, detail="Tournament has already finished.")
            t_state["current_day"] += 1
            save_live_tournament(t_state)
            return {"status": "success", "state": t_state}
            
        t_state["status"] = "group_stage" if current_day <= 18 else "knockouts"
        
        for m in t_state["matches"]:
            if m["day"] == current_day and m["status"] != "completed":
                probs = predict_match(m["team_a"], m["team_b"])
                probs["team_a"] = m["team_a"]
                probs["team_b"] = m["team_b"]
                stage_type = "group" if m["stage"] == "group" else "knockout"
                
                goals_a, goals_b, winner = simulate_goals(probs, stage=stage_type)
                
                m["events"] = generate_match_events(m["team_a"], m["team_b"], goals_a, goals_b)
                m["goals_a"] = goals_a
                m["goals_b"] = goals_b
                m["winner"] = winner
                m["minute"] = 90
                m["status"] = "completed"
                
        t_state["group_standings"] = compute_live_group_standings(t_state["matches"])
        check_and_advance_stage(t_state)
        save_live_tournament(t_state)
        return {"status": "success", "state": t_state}
        
    elif action == "simulate_tournament_fast":
        if t_state["status"] == "finished":
            raise HTTPException(status_code=400, detail="Tournament has already finished.")
            
        while t_state["status"] != "finished":
            current_day = t_state["current_day"]
            day_matches = [m for m in t_state["matches"] if m["day"] == current_day]
            
            if not day_matches:
                t_state["current_day"] += 1
                if t_state["current_day"] > 35:
                    t_state["status"] = "finished"
                continue
                
            t_state["status"] = "group_stage" if current_day <= 18 else "knockouts"
            
            for m in t_state["matches"]:
                if m["day"] == current_day and m["status"] != "completed":
                    probs = predict_match(m["team_a"], m["team_b"])
                    probs["team_a"] = m["team_a"]
                    probs["team_b"] = m["team_b"]
                    stage_type = "group" if m["stage"] == "group" else "knockout"
                    
                    goals_a, goals_b, winner = simulate_goals(probs, stage=stage_type)
                    
                    m["events"] = generate_match_events(m["team_a"], m["team_b"], goals_a, goals_b)
                    m["goals_a"] = goals_a
                    m["goals_b"] = goals_b
                    m["winner"] = winner
                    m["minute"] = 90
                    m["status"] = "completed"
                    
            t_state["group_standings"] = compute_live_group_standings(t_state["matches"])
            check_and_advance_stage(t_state)
            
        save_live_tournament(t_state)
        return {"status": "success", "state": t_state}

# ─── Helper Functions ─────────────────────────────────────────────────────────
def get_confederation(team_name: str) -> str:
    """Returns the football confederation for a team."""
    return config.CONFEDERATION_MAP.get(team_name, "OFC")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
