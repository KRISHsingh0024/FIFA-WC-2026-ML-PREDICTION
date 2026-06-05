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
        
        # H2H win rate (For manual predictions, we use a calculated baseline or default)
        # We can approximate based on rankings or static history
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
        
        result = {
            "team_a": team_a,
            "team_b": team_b,
            "team_a_win": float(probs[0]),
            "draw": float(probs[1]),
            "team_b_win": float(probs[2])
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
