"""
Model Training Script.
Loads match-level features, performs hyperparameter optimization using Optuna on GPU,
evaluates via 10-Fold Stratified Cross-Validation with early stopping,
saves the trained model, and writes the best parameters back to config.py.
"""

import os
import sys
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, log_loss, classification_report
import joblib
import logging
import optuna
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def train_model():
    """
    Trains the match outcome model and saves the trained classifier.
    """
    features_path = os.path.join(config.PROCESSED_DATA_DIR, "match_features.parquet")
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Match features not found at {features_path}. Please run match_features.py first.")
        
    logging.info(f"Loading match features from {features_path}...")
    df = pd.read_parquet(features_path)
    
    # Feature columns
    feature_cols = config.MATCH_FEATURES
    X = df[feature_cols]
    y = df["target"] # 0 = Win, 1 = Draw, 2 = Loss
    
    logging.info(f"Features: {feature_cols}")
    logging.info(f"Dataset shape: {X.shape}")
    
    # Optuna Objective Function
    def objective(trial):
        params = {
            "objective": "multi:softprob",
            "num_class": 3,
            "eval_metric": "mlogloss",
            "random_state": config.RANDOM_SEED,
            "device": "cuda",
            "tree_method": "hist",
            
            # Hyperparameter Search Space
            "max_depth": trial.suggest_int("max_depth", 4, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 200, 1000),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "gamma": trial.suggest_float("gamma", 0.0, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 2.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.5, 3.0),
        }
        
        # Fast Stratified CV evaluation within each trial (using 5 folds for speed in search)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_SEED)
        log_losses = []
        
        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Early stopping setup
            model = xgb.XGBClassifier(**params, early_stopping_rounds=25)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
            
            probs = model.predict_proba(X_val)
            loss = log_loss(y_val, probs)
            log_losses.append(loss)
            
        return np.mean(log_losses)
        
    # Run Optuna Hyperparameter Optimization
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    logging.info("Running Optuna hyperparameter optimization (100 trials) on GPU...")
    study.optimize(objective, n_trials=100)
    
    best_params = study.best_params
    logging.info(f"Optuna Optimization Complete!")
    logging.info(f"Best Log Loss: {study.best_value:.4f}")
    logging.info(f"Best Hyperparameters: {best_params}")
    
    # 10-Fold Stratified Cross Validation on the best hyperparameters
    logging.info("Starting robust 10-Fold Stratified Cross Validation with Best Params...")
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=config.RANDOM_SEED)
    
    acc_scores = []
    log_losses = []
    
    final_params = {
        "objective": "multi:softprob",
        "num_class": 3,
        "eval_metric": "mlogloss",
        "random_state": config.RANDOM_SEED,
        "device": "cuda",
        "tree_method": "hist",
        **best_params
    }
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        # Train XGBoost with best params and early stopping
        model = xgb.XGBClassifier(**final_params, early_stopping_rounds=30)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Predict
        preds = model.predict(X_val)
        probs = model.predict_proba(X_val)
        
        acc = accuracy_score(y_val, preds)
        loss = log_loss(y_val, probs)
        
        acc_scores.append(acc)
        log_losses.append(loss)
        
        logging.info(f"Fold {fold+1:2d} - Accuracy: {acc:.4f}, Log Loss: {loss:.4f}")
        
    mean_acc = np.mean(acc_scores)
    mean_loss = np.mean(log_losses)
    logging.info(f"CV Mean Accuracy: {mean_acc:.4f}")
    logging.info(f"CV Mean Log Loss: {mean_loss:.4f}")
    
    # Train final model on all data
    logging.info("Training final model on full dataset...")
    final_model = xgb.XGBClassifier(**final_params)
    final_model.fit(X, y)
    
    # Save the trained model
    joblib.dump(final_model, config.MODEL_PATH)
    logging.info(f"Successfully saved final model to {config.MODEL_PATH}")
    
    # Write the best params back to config.py
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        new_params_str = "MODEL_PARAMS = {\n"
        new_params_str += '    "objective": "multi:softprob",\n'
        new_params_str += '    "num_class": 3,\n'
        for k, v in best_params.items():
            if isinstance(v, str):
                new_params_str += f'    "{k}": "{v}",\n'
            else:
                new_params_str += f'    "{k}": {v},\n'
        new_params_str += '    "eval_metric": "mlogloss",\n'
        new_params_str += '    "random_state": 42,\n'
        new_params_str += '    "use_label_encoder": False,\n'
        new_params_str += '    "device": "cuda",\n'
        new_params_str += '    "tree_method": "hist",\n'
        new_params_str += "}"
        
        config_content = re.sub(r"MODEL_PARAMS = \{.*?\}", new_params_str, config_content, flags=re.DOTALL)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        logging.info("Successfully updated config.py with best hyperparameter values.")
    except Exception as e:
        logging.warning(f"Could not automatically update config.py: {e}")
        
    # Evaluate on full training set to print classification report
    full_preds = final_model.predict(X)
    print("\n--- Final Model Training Performance ---")
    print(classification_report(y, full_preds, target_names=["Home Win (0)", "Draw (1)", "Away Win (2)"]))
    
    # Feature Importances
    importances = final_model.feature_importances_
    feat_imp = pd.Series(importances, index=feature_cols).sort_values(ascending=False)
    print("\nFeature Importances:")
    for feat, imp in feat_imp.items():
        print(f"{feat:25s}: {imp:.4f}")

if __name__ == "__main__":
    train_model()
