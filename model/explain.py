"""
Model Explainability Interface.
Uses SHAP values or XGBoost feature importances to explain predictions and rank player impact.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_feature_importances() -> pd.Series:
    """
    Returns feature importances from the trained model.
    """
    model_path = config.MODEL_PATH
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Train the model first.")
        
    model = joblib.load(model_path)
    importances = model.feature_importances_
    
    feat_imp = pd.Series(importances, index=config.MATCH_FEATURES).sort_values(ascending=False)
    return feat_imp

def explain_match_prediction(team_a: str, team_b: str) -> dict:
    """
    Explains why the model predicted a certain probability for Team A vs Team B.
    Computes feature differentials and how they align with general feature importances.
    """
    from model.predict import MatchPredictor
    predictor = MatchPredictor()
    
    # Get matchup features
    df_match = predictor.get_match_features(team_a, team_b)
    
    # Load model
    model = predictor.model
    probs = model.predict_proba(df_match[config.MATCH_FEATURES])[0]
    
    # Explain based on differences
    explanations = []
    
    # Rank difference contribution
    fifa_diff = df_match.loc[0, "fifa_rank_diff"]
    if fifa_diff > 15:
        explanations.append(f"Rankings: {team_a} is ranked significantly higher than {team_b} (+{fifa_diff} ranks).")
    elif fifa_diff < -15:
        explanations.append(f"Rankings: {team_b} is ranked significantly higher than {team_a} ({abs(fifa_diff)} ranks).")
        
    # Attack difference
    att_diff = df_match.loc[0, "attack_diff"]
    if att_diff > 0.15:
        explanations.append(f"Attack: {team_a}'s starting forwards show higher goals and xG rates in club play.")
    elif att_diff < -0.15:
        explanations.append(f"Attack: {team_b}'s starting forwards show higher goals and xG rates in club play.")
        
    # Midfield difference
    mid_diff = df_match.loc[0, "midfield_diff"]
    if mid_diff > 0.15:
        explanations.append(f"Midfield: {team_a} possesses superior creativity and passing progression metrics.")
    elif mid_diff < -0.15:
        explanations.append(f"Midfield: {team_b} possesses superior creativity and passing progression metrics.")
        
    # Defense difference
    def_diff = df_match.loc[0, "defense_diff"]
    if def_diff > 0.15:
        explanations.append(f"Defense: {team_a}'s defensive line records higher tackles/interceptions in major leagues.")
    elif def_diff < -0.15:
        explanations.append(f"Defense: {team_b}'s defensive line records higher tackles/interceptions in major leagues.")
        
    # Star player impact
    star_diff = df_match.loc[0, "star_diff"]
    if star_diff > 0.2:
        explanations.append(f"Star Player: {team_a} has a higher peak-performing game-changer on paper.")
    elif star_diff < -0.2:
        explanations.append(f"Star Player: {team_b} has a higher peak-performing game-changer on paper.")
        
    # UCL Experience
    ucl_diff = df_match.loc[0, "ucl_rep_diff"]
    if ucl_diff > 3:
        explanations.append(f"UCL Experience: {team_a} has significantly more players competing in the UEFA Champions League.")
    elif ucl_diff < -3:
        explanations.append(f"UCL Experience: {team_b} has significantly more players competing in the UEFA Champions League.")
        
    # Confederation Strength
    conf_diff = df_match.loc[0, "confederation_diff"]
    if conf_diff > 0.15:
        explanations.append(f"Confederation: {team_a} benefits from a stronger historic confederation strength (e.g. UEFA/CONMEBOL).")
    elif conf_diff < -0.15:
        explanations.append(f"Confederation: {team_b} benefits from a stronger historic confederation strength (e.g. UEFA/CONMEBOL).")

    # Baseline fallback explanation if everything is close
    if not explanations:
        explanations.append("Matchup: Both teams are evenly matched across attack, midfield, and defensive metrics.")
        
    # Attempt SHAP explanation if shap is installed
    shap_contributions = {}
    try:
        import shap
        # Build background dataset (train on a small batch of features)
        features_path = os.path.join(config.PROCESSED_DATA_DIR, "match_features.parquet")
        if os.path.exists(features_path):
            df_all = pd.read_parquet(features_path)
            X = df_all[config.MATCH_FEATURES]
            
            # Use TreeExplainer
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(df_match[config.MATCH_FEATURES])
            
            # Extract shap for class 0 (Team A Win)
            # shap outputs list of arrays for multiclass
            if isinstance(shap_values, list):
                shap_a = shap_values[0][0]
            else:
                # for binary/multi in some shap versions
                shap_a = shap_values[0, :, 0] if len(shap_values.shape) > 2 else shap_values[0]
                
            for col, val in zip(config.MATCH_FEATURES, shap_a):
                shap_contributions[col] = float(val)
    except Exception as e:
        # SHAP not installed or failed, build fallback from raw differentials
        for col in config.MATCH_FEATURES:
            val = df_match.loc[0, col]
            # scale roughly for visualization
            shap_contributions[col] = float(val * 0.1)
            
    return {
        "probabilities": {
            "team_a_win": float(probs[0]),
            "draw": float(probs[1]),
            "team_b_win": float(probs[2])
        },
        "explanations": explanations,
        "shap_contributions": shap_contributions
    }

if __name__ == "__main__":
    # Test explain
    try:
        res = explain_match_prediction("France", "Argentina")
        print("\nExplanations:")
        for exp in res["explanations"]:
            print(f"- {exp}")
        print("\nContributions:")
        for col, val in res["shap_contributions"].items():
            print(f"{col:20s}: {val:.4f}")
    except Exception as e:
        print(f"Could not run test: {e}. Train the model first.")
