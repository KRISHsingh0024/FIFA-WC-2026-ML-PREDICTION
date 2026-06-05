"""
Tournament Simulation Engine.
Simulates the entire FIFA World Cup 2026 (Group Stage + Knockout Stage) using Monte Carlo simulations.
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import logging
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from simulation.bracket import Group, Match, KnockoutRound, get_2026_bracket_pairings
from model.predict import predict_match

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def simulate_goals(probs: dict, stage: str = "group") -> tuple:
    """
    Simulates goals for Team A and Team B based on win/draw/loss probabilities.
    Returns: (goals_a, goals_b, winner)
    """
    p_a = probs["team_a_win"]
    p_d = probs["draw"]
    p_b = probs["team_b_win"]
    
    # Normalize if they don't sum to 1
    total = p_a + p_d + p_b
    p_a /= total
    p_d /= total
    p_b /= total
    
    u = np.random.rand()
    
    if stage == "group":
        if u < p_a:
            # A Wins
            goals_a = int(np.random.poisson(1.5) + 1)
            goals_b = int(max(0, goals_a - np.random.randint(1, 3)))
            if goals_b >= goals_a:
                goals_b = goals_a - 1
            return goals_a, goals_b, probs["team_a"]
        elif u < p_a + p_d:
            # Draw
            goals_a = int(np.random.poisson(1.0))
            goals_b = goals_a
            return goals_a, goals_b, "Draw"
        else:
            # B Wins
            goals_b = int(np.random.poisson(1.5) + 1)
            goals_a = int(max(0, goals_b - np.random.randint(1, 3)))
            if goals_a >= goals_b:
                goals_a = goals_b - 1
            return goals_a, goals_b, probs["team_b"]
    else:
        # Knockout: No draws allowed. If draw is selected, we resolve via extra time/penalties
        # We assign win based on relative probability
        relative_a = p_a / (p_a + p_b + 1e-6)
        
        if u < p_a or (p_a <= u < p_a + p_d and np.random.rand() < relative_a):
            # A Wins (possibly after penalties/ET)
            goals_a = int(np.random.poisson(1.5) + 1)
            goals_b = int(max(0, goals_a - np.random.randint(1, 3)))
            if goals_b >= goals_a:
                goals_b = goals_a - 1
            return goals_a, goals_b, probs["team_a"]
        else:
            # B Wins
            goals_b = int(np.random.poisson(1.5) + 1)
            goals_a = int(max(0, goals_b - np.random.randint(1, 3)))
            if goals_a >= goals_b:
                goals_a = goals_b - 1
            return goals_a, goals_b, probs["team_b"]

def run_single_tournament(verbose=False) -> dict:
    """
    Simulates a single run of the 104-match 2026 World Cup.
    Returns the teams advancing to each round and the ultimate champion.
    """
    # ─── Group Stage ─────────────────────────────────────────────────────────
    group_standings = {}
    group_matches_played = []
    
    for g_name, teams in config.GROUPS.items():
        g = Group(g_name, teams)
        
        # Schedule round-robin (6 matches per group)
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                t1, t2 = teams[i], teams[j]
                
                # Predict match probabilities
                probs = predict_match(t1, t2)
                goals1, goals2, winner = simulate_goals(probs, stage="group")
                
                g.record_match(t1, t2, goals1, goals2)
                group_matches_played.append({
                    "match_id": f"G_{g_name}_{t1}_{t2}",
                    "team_a": t1,
                    "team_b": t2,
                    "goals_a": goals1,
                    "goals_b": goals2,
                    "winner": winner
                })
                
        group_standings[g_name] = g.get_ranked_standings()
        
    # ─── Round of 32 ─────────────────────────────────────────────────────────
    r32_pairings = get_2026_bracket_pairings(group_standings)
    r32_winners = []
    r32_matches = []
    
    for t1, t2, mid in r32_pairings:
        probs = predict_match(t1, t2)
        goals1, goals2, winner = simulate_goals(probs, stage="knockout")
        r32_winners.append(winner)
        r32_matches.append({
            "match_id": mid,
            "team_a": t1,
            "team_b": t2,
            "goals_a": goals1,
            "goals_b": goals2,
            "winner": winner
        })
        
    # ─── Round of 16 ─────────────────────────────────────────────────────────
    r16_winners = []
    r16_matches = []
    # R32 Match 1 vs Match 2, 3 vs 4, etc.
    for i in range(0, 16, 2):
        t1 = r32_winners[i]
        t2 = r32_winners[i+1]
        probs = predict_match(t1, t2)
        goals1, goals2, winner = simulate_goals(probs, stage="knockout")
        r16_winners.append(winner)
        r16_matches.append({
            "match_id": f"R16_{i//2 + 1}",
            "team_a": t1,
            "team_b": t2,
            "goals_a": goals1,
            "goals_b": goals2,
            "winner": winner
        })
        
    # ─── Quarter Finals ──────────────────────────────────────────────────────
    qf_winners = []
    qf_matches = []
    for i in range(0, 8, 2):
        t1 = r16_winners[i]
        t2 = r16_winners[i+1]
        probs = predict_match(t1, t2)
        goals1, goals2, winner = simulate_goals(probs, stage="knockout")
        qf_winners.append(winner)
        qf_matches.append({
            "match_id": f"QF_{i//2 + 1}",
            "team_a": t1,
            "team_b": t2,
            "goals_a": goals1,
            "goals_b": goals2,
            "winner": winner
        })
        
    # ─── Semi Finals ─────────────────────────────────────────────────────────
    sf_winners = []
    sf_losers = []
    sf_matches = []
    for i in range(0, 4, 2):
        t1 = qf_winners[i]
        t2 = qf_winners[i+1]
        probs = predict_match(t1, t2)
        goals1, goals2, winner = simulate_goals(probs, stage="knockout")
        sf_winners.append(winner)
        sf_losers.append(t1 if winner == t2 else t2)
        sf_matches.append({
            "match_id": f"SF_{i//2 + 1}",
            "team_a": t1,
            "team_b": t2,
            "goals_a": goals1,
            "goals_b": goals2,
            "winner": winner
        })
        
    # ─── Third Place Match ───────────────────────────────────────────────────
    probs_3rd = predict_match(sf_losers[0], sf_losers[1])
    goals_3rd_a, goals_3rd_b, third_place_winner = simulate_goals(probs_3rd, stage="knockout")
    
    # ─── Final ───────────────────────────────────────────────────────────────
    probs_final = predict_match(sf_winners[0], sf_winners[1])
    goals_final_a, goals_final_b, champion = simulate_goals(probs_final, stage="knockout")
    runner_up = sf_winners[0] if champion == sf_winners[1] else sf_winners[1]
    
    final_match = {
        "match_id": "FINAL",
        "team_a": sf_winners[0],
        "team_b": sf_winners[1],
        "goals_a": goals_final_a,
        "goals_b": goals_final_b,
        "winner": champion
    }
    
    return {
        "champion": champion,
        "runner_up": runner_up,
        "third_place": third_place_winner,
        "top_4": sf_winners + sf_losers,
        "top_8": qf_winners,
        "top_16": r16_winners,
        "top_32": r32_winners,
        "bracket": {
            "group_matches": group_matches_played,
            "r32_matches": r32_matches,
            "r16_matches": r16_matches,
            "qf_matches": qf_matches,
            "sf_matches": sf_matches,
            "final_match": final_match
        }
    }

def run_monte_carlo(n_simulations: int = config.NUM_SIMULATIONS):
    """
    Runs N simulations and compiles statistical probabilities.
    Saves the aggregated metrics as a JSON file in data/processed/.
    """
    logging.info(f"Starting Monte Carlo simulation (N={n_simulations} runs)...")
    
    champions = []
    runners_up = []
    thirds = []
    reached_sf = []
    reached_qf = []
    reached_r16 = []
    reached_r32 = []
    
    # To save a sample bracket visualization run
    sample_run = None
    
    for i in range(n_simulations):
        if (i+1) % 100 == 0:
            logging.info(f"Completed {i+1}/{n_simulations} simulations...")
            
        res = run_single_tournament()
        
        champions.append(res["champion"])
        runners_up.append(res["runner_up"])
        thirds.append(res["third_place"])
        reached_sf.extend(res["top_4"])
        reached_qf.extend(res["top_8"])
        reached_r16.extend(res["top_16"])
        reached_r32.extend(res["top_32"])
        
        if i == 0:
            sample_run = res
            
    # Calculate probabilities
    total_runs = n_simulations
    
    champions_count = Counter(champions)
    runners_up_count = Counter(runners_up)
    thirds_count = Counter(thirds)
    reached_sf_count = Counter(reached_sf)
    reached_qf_count = Counter(reached_qf)
    reached_r16_count = Counter(reached_r16)
    reached_r32_count = Counter(reached_r32)
    
    stats = {}
    for team in config.ALL_TEAMS:
        stats[team] = {
            "champion_prob": round(champions_count[team] / total_runs, 4),
            "finalist_prob": round((champions_count[team] + runners_up_count[team]) / total_runs, 4),
            "semi_finalist_prob": round(reached_sf_count[team] / total_runs, 4),
            "quarter_finalist_prob": round(reached_qf_count[team] / total_runs, 4),
            "round_of_16_prob": round(reached_r16_count[team] / total_runs, 4),
            "round_of_32_prob": round(reached_r32_count[team] / total_runs, 4)
        }
        
    output_data = {
        "sim_stats": stats,
        "sample_run": sample_run["bracket"],
        "n_simulations": n_simulations
    }
    
    output_path = os.path.join(config.PROCESSED_DATA_DIR, "simulation_results.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
        
    logging.info(f"Saved Monte Carlo simulation statistics to {output_path}")
    
    # Print top 5 predicted winners
    top_winners = sorted(champions_count.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\n--- TOP 5 PREDICTED WORLD CUP WINNERS ---")
    for team, count in top_winners:
        print(f"{team:15s}: {count/total_runs:.2%}")
        
    return stats

if __name__ == "__main__":
    run_monte_carlo(1000) # Official simulation runs

