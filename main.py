"""
Main pipeline orchestrator CLI.
Allows running individual steps (collect, features, train, simulate) or the full end-to-end pipeline.
"""

import os
import sys
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_step(step_name: str):
    """Imports and runs the main function of the specified step."""
    logging.info(f"========== STARTING STEP: {step_name.upper()} ==========")
    
    if step_name == "collect":
        # Run player stats collection
        from data.collect_player_stats import main as collect_players
        collect_players()
        
        # Run historical matches collection
        from data.collect_historical_matches import main as collect_matches
        collect_matches()
        
    elif step_name == "features":
        # Run player features
        from features.player_features import process_player_features
        process_player_features()
        
        # Run team features
        from features.team_features import aggregate_team_features
        aggregate_team_features()
        
        # Run match features
        from features.match_features import build_match_features
        build_match_features()
        
    elif step_name == "train":
        # Run model training
        from model.train import train_model
        train_model()
        
    elif step_name == "simulate":
        # Run tournament simulation
        from simulation.tournament import run_monte_carlo
        run_monte_carlo()
        
    logging.info(f"========== COMPLETED STEP: {step_name.upper()} ==========\n")

def main():
    parser = argparse.ArgumentParser(description="FIFA World Cup 2026 Prediction Model Pipeline Orchestrator")
    parser.add_argument(
        "--step",
        choices=["collect", "features", "train", "simulate", "all"],
        default="all",
        help="Pipeline step to run (default: all)"
    )
    args = parser.parse_args()
    
    if args.step == "all":
        steps = ["collect", "features", "train", "simulate"]
        for step in steps:
            run_step(step)
    else:
        run_step(args.step)
        
    logging.info("Pipeline Execution Finished Successfully!")

if __name__ == "__main__":
    main()
