"""
Match Predictor Interface.
Loads the trained model and team features, compiles matchup features on the fly, and predicts outcomes between any two teams.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

class MatchPredictor:
    def __init__(self):
        self.model = None
        self.team_features = None
        self.h2h_history = {} # Cache historical H2H matches
        self.cache = {} # Cache predicted matchup probabilities
        self.load_resources()
        
    def load_resources(self):
        """Loads trained XGBoost model and team feature database."""
        model_path = config.MODEL_PATH
        team_path = os.path.join(config.PROCESSED_DATA_DIR, "team_features.parquet")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
        if not os.path.exists(team_path):
            raise FileNotFoundError(f"Team features file not found at {team_path}. Please run aggregation first.")
            
        self.model = joblib.load(model_path)
        # Force CPU for inference to prevent CUDA multi-threading deadlocks in web server
        if hasattr(self.model, "set_params"):
            try:
                self.model.set_params(device="cpu")
            except Exception as e:
                pass
        self.team_features = pd.read_parquet(team_path).set_index("national_team")
        
        # Load historical matches for H2H lookup
        hist_path = os.path.join(config.RAW_DATA_DIR, "historical_matches.parquet")
        if os.path.exists(hist_path):
            try:
                df_hist = pd.read_parquet(hist_path)
                for _, row in df_hist.iterrows():
                    t1, t2 = row["home_team"], row["away_team"]
                    outcome = row["outcome"]
                    pair = tuple(sorted([t1, t2]))
                    if pair not in self.h2h_history:
                        self.h2h_history[pair] = []
                    self.h2h_history[pair].append((t1, outcome))
            except Exception as e:
                logging.warning(f"Could not load historical matches for H2H lookup: {e}")
        
    def get_match_features(self, team_a: str, team_b: str) -> pd.DataFrame:
        """
        Creates match feature vector for Team A vs Team B.
        Matches features structured during training:
        ['attack_diff', 'defense_diff', 'midfield_diff', 'xg_diff', 'xa_diff', 'depth_diff', 'star_diff',
         'attack_ratio', 'defense_ratio', 'fifa_rank_diff', 'h2h_win_rate']
        """
        if team_a not in self.team_features.index:
            raise ValueError(f"Team {team_a} not found in database.")
        if team_b not in self.team_features.index:
            raise ValueError(f"Team {team_b} not found in database.")
            
        feat1 = self.team_features.loc[team_a]
        feat2 = self.team_features.loc[team_b]
        
        # Differential Features (A - B)
        attack_diff = feat1["team_attack_strength"] - feat2["team_attack_strength"]
        defense_diff = feat1["team_defense_solidity"] - feat2["team_defense_solidity"]
        midfield_diff = feat1["team_midfield_creativity"] - feat2["team_midfield_creativity"]
        xg_diff = feat1["team_overall_xg"] - feat2["team_overall_xg"]
        xa_diff = feat1["team_overall_xa"] - feat2["team_overall_xa"]
        depth_diff = feat1["team_depth_score"] - feat2["team_depth_score"]
        star_diff = feat1["team_star_player_impact"] - feat2["team_star_player_impact"]
        
        # Ratio Features (A / B)
        attack_ratio = feat1["team_attack_strength"] / (feat2["team_attack_strength"] + 0.01)
        defense_ratio = feat1["team_defense_solidity"] / (feat2["team_defense_solidity"] + 0.01)
        
        # Contextual Features
        r1 = config.FIFA_RANKINGS.get(team_a, 50)
        r2 = config.FIFA_RANKINGS.get(team_b, 50)
        fifa_rank_diff = r2 - r1 # positive = team A is better ranked (lower rank)
        
        # H2H win rate from historical matches
        pair = tuple(sorted([team_a, team_b]))
        h2hs = self.h2h_history.get(pair, [])
        t1_wins = 0
        total_games = 0
        for ht, out in h2hs:
            total_games += 1
            if ht == team_a and out == "W":
                t1_wins += 1
            elif ht != team_a and out == "L":
                t1_wins += 1
                
        if total_games > 0:
            h2h_win_rate = t1_wins / total_games
        else:
            # Fallback to rank diff baseline
            h2h_win_rate = 0.5 + (fifa_rank_diff * 0.005)
            h2h_win_rate = np.clip(h2h_win_rate, 0.2, 0.8)
        
        # 5. New Match Features (Differentials)
        ucl_rep_diff = feat1["team_ucl_representation"] - feat2["team_ucl_representation"]
        confederation_diff = feat1["team_confederation_strength"] - feat2["team_confederation_strength"]
        creativity_diff = feat1["team_avg_creativity_score"] - feat2["team_avg_creativity_score"]
        defensive_score_diff = feat1["team_avg_defensive_score"] - feat2["team_avg_defensive_score"]

        match_dict = {
            "attack_diff": attack_diff,
            "defense_diff": defense_diff,
            "midfield_diff": midfield_diff,
            "xg_diff": xg_diff,
            "xa_diff": xa_diff,
            "depth_diff": depth_diff,
            "star_diff": star_diff,
            "attack_ratio": attack_ratio,
            "defense_ratio": defense_ratio,
            "fifa_rank_diff": fifa_rank_diff,
            "h2h_win_rate": h2h_win_rate,
            "ucl_rep_diff": ucl_rep_diff,
            "confederation_diff": confederation_diff,
            "creativity_diff": creativity_diff,
            "defensive_score_diff": defensive_score_diff
        }
        
        return pd.DataFrame([match_dict])
        
    def predict(self, team_a: str, team_b: str) -> dict:
        """
        Predicts match probabilities.
        Returns:
            {
                "team_a": team_a,
                "team_b": team_b,
                "team_a_win": prob,
                "draw": prob,
                "team_b_win": prob
            }
        """
        # Check cache
        cache_key = (team_a, team_b)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Compile features
        X_match = self.get_match_features(team_a, team_b)
        X_match = X_match[config.MATCH_FEATURES] # Ensure column order
        
        # Predict probabilities
        # model outputs class order: 0 (Team A Win), 1 (Draw), 2 (Team B Win)
        probs = self.model.predict_proba(X_match)[0]
        
        # Apply 2026 pre-tournament calibration
        s_a = getattr(config, "TEAM_CALIBRATION", {}).get(team_a, 0.0)
        s_b = getattr(config, "TEAM_CALIBRATION", {}).get(team_b, 0.0)
        diff = s_a - s_b
        
        if diff != 0:
            p_a = float(probs[0]) * np.exp(diff)
            p_draw = float(probs[1])
            p_b = float(probs[2]) * np.exp(-diff)
            total = p_a + p_draw + p_b
            if total > 0:
                p_a /= total
                p_draw /= total
                p_b /= total
            else:
                p_a, p_draw, p_b = float(probs[0]), float(probs[1]), float(probs[2])
        else:
            p_a, p_draw, p_b = float(probs[0]), float(probs[1]), float(probs[2])
            
        result = {
            "team_a": team_a,
            "team_b": team_b,
            "team_a_win": p_a,
            "draw": p_draw,
            "team_b_win": p_b
        }
        
        # Store in cache
        self.cache[cache_key] = result
        return result

_predictor = None

def predict_match(team_a: str, team_b: str) -> dict:
    """Convenience functional interface."""
    global _predictor
    if _predictor is None:
        _predictor = MatchPredictor()
    return _predictor.predict(team_a, team_b)


if __name__ == "__main__":
    # Test prediction
    try:
        res = predict_match("France", "Argentina")
        print(f"Prediction: {res['team_a']} vs {res['team_b']}")
        print(f"  {res['team_a']} Win: {res['team_a_win']:.2%}")
        print(f"  Draw: {res['draw']:.2%}")
        print(f"  {res['team_b']} Win: {res['team_b_win']:.2%}")
    except Exception as e:
        print(f"Could not run test prediction: {e}. Train the model first.")
