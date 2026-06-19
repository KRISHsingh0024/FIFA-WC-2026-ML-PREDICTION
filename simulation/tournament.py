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

def load_real_results() -> dict:
    """Loads real results mapping from data/real_results.json."""
    real_path = os.path.join(config.DATA_DIR, "real_results.json")
    results_map = {}
    if os.path.exists(real_path):
        try:
            with open(real_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if item.get("status") == "completed":
                        t1 = item.get("team_a")
                        t2 = item.get("team_b")
                        key = tuple(sorted([t1, t2]))
                        results_map[key] = {
                            "goals_a": item.get("real_goals_a"),
                            "goals_b": item.get("real_goals_b"),
                            "winner": t1 if item.get("real_goals_a") > item.get("real_goals_b") else (t2 if item.get("real_goals_b") > item.get("real_goals_a") else "Draw"),
                            "team_a": t1,
                            "team_b": t2
                        }
        except Exception as e:
            logging.warning(f"Could not load real results: {e}")
    return results_map

def run_deterministic_tournament(verbose=False) -> dict:
    """
    Simulates the entire FIFA World Cup 2026 deterministically.
    Uses real match results for completed matches and ML-based predictions for the rest.
    """
    real_results = load_real_results()
    
    # ─── Group Stage ─────────────────────────────────────────────────────────
    group_standings = {}
    group_matches_played = []
    
    for g_name, teams in config.GROUPS.items():
        g = Group(g_name, teams)
        
        # Schedule round-robin (6 matches per group)
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                t1, t2 = teams[i], teams[j]
                
                key = tuple(sorted([t1, t2]))
                if key in real_results:
                    # Use real completed results
                    real_match = real_results[key]
                    goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
                    goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
                    
                    if goals1 > goals2:
                        winner = t1
                    elif goals1 < goals2:
                        winner = t2
                    else:
                        winner = "Draw"
                else:
                    # Predict deterministically
                    probs = predict_match(t1, t2)
                    pa = probs["team_a_win"]
                    pd = probs["draw"]
                    pb = probs["team_b_win"]
                    
                    if pa > pb and pa > pd:
                        winner = t1
                        goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
                    elif pb > pa and pb > pd:
                        winner = t2
                        goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
                    else:
                        winner = "Draw"
                        goals1, goals2 = 1, 1
                        
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
        key = tuple(sorted([t1, t2]))
        if key in real_results:
            real_match = real_results[key]
            goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
            goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
            winner = t1 if goals1 > goals2 else t2
        else:
            probs = predict_match(t1, t2)
            pa = probs["team_a_win"]
            pb = probs["team_b_win"]
            if pa >= pb:
                winner = t1
                goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
            else:
                winner = t2
                goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
                
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
    for i in range(0, 16, 2):
        t1 = r32_winners[i]
        t2 = r32_winners[i+1]
        key = tuple(sorted([t1, t2]))
        if key in real_results:
            real_match = real_results[key]
            goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
            goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
            winner = t1 if goals1 > goals2 else t2
        else:
            probs = predict_match(t1, t2)
            pa = probs["team_a_win"]
            pb = probs["team_b_win"]
            if pa >= pb:
                winner = t1
                goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
            else:
                winner = t2
                goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
                
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
        key = tuple(sorted([t1, t2]))
        if key in real_results:
            real_match = real_results[key]
            goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
            goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
            winner = t1 if goals1 > goals2 else t2
        else:
            probs = predict_match(t1, t2)
            pa = probs["team_a_win"]
            pb = probs["team_b_win"]
            if pa >= pb:
                winner = t1
                goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
            else:
                winner = t2
                goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
                
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
        key = tuple(sorted([t1, t2]))
        if key in real_results:
            real_match = real_results[key]
            goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
            goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
            winner = t1 if goals1 > goals2 else t2
        else:
            probs = predict_match(t1, t2)
            pa = probs["team_a_win"]
            pb = probs["team_b_win"]
            if pa >= pb:
                winner = t1
                goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
            else:
                winner = t2
                goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
                
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
    t1, t2 = sf_losers[0], sf_losers[1]
    key = tuple(sorted([t1, t2]))
    if key in real_results:
        real_match = real_results[key]
        goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
        goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
        third_place_winner = t1 if goals1 > goals2 else t2
    else:
        probs_3rd = predict_match(t1, t2)
        pa = probs_3rd["team_a_win"]
        pb = probs_3rd["team_b_win"]
        if pa >= pb:
            third_place_winner = t1
            goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
        else:
            third_place_winner = t2
            goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
            
    # ─── Final ───────────────────────────────────────────────────────────────
    t1, t2 = sf_winners[0], sf_winners[1]
    key = tuple(sorted([t1, t2]))
    if key in real_results:
        real_match = real_results[key]
        goals1 = real_match["goals_a"] if real_match["team_a"] == t1 else real_match["goals_b"]
        goals2 = real_match["goals_b"] if real_match["team_a"] == t1 else real_match["goals_a"]
        champion = t1 if goals1 > goals2 else t2
    else:
        probs_final = predict_match(t1, t2)
        pa = probs_final["team_a_win"]
        pb = probs_final["team_b_win"]
        if pa >= pb:
            champion = t1
            goals1, goals2 = (2, 0) if (pa - pb > 0.2) else (2, 1)
        else:
            champion = t2
            goals1, goals2 = (0, 2) if (pb - pa > 0.2) else (1, 2)
            
    runner_up = t1 if champion == t2 else t2
    
    final_match = {
        "match_id": "FINAL",
        "team_a": t1,
        "team_b": t2,
        "goals_a": goals1,
        "goals_b": goals2,
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
    Runs a stochastic Monte Carlo simulation to calculate realistic stage probabilities
    for each team, while keeping the visual predicted bracket pathway stable and deterministic.
    """
    logging.info(f"Running {n_simulations} stochastic Monte Carlo simulations to collect realistic stage probabilities...")
    
    # 1. Initialize stage counters
    champion_counts = Counter()
    finalist_counts = Counter()
    sf_counts = Counter()
    qf_counts = Counter()
    r16_counts = Counter()
    r32_counts = Counter()
    
    # 2. Run stochastic simulations
    for i in range(n_simulations):
        if i % 200 == 0 and i > 0:
            logging.info(f"Completed {i} simulations...")
        try:
            res_stoch = run_single_tournament()
            champ = res_stoch["champion"]
            runner_up = res_stoch["runner_up"]
            
            champion_counts[champ] += 1
            
            finalist_counts[champ] += 1
            finalist_counts[runner_up] += 1
            
            for t in res_stoch["top_4"]:
                sf_counts[t] += 1
            for t in res_stoch["top_8"]:
                qf_counts[t] += 1
            for t in res_stoch["top_16"]:
                r16_counts[t] += 1
            for t in res_stoch["top_32"]:
                r32_counts[t] += 1
        except Exception as e:
            logging.warning(f"Error in simulation run {i}: {e}")
            
    # 3. Load team features for stats rating
    team_features_path = os.path.join(config.PROCESSED_DATA_DIR, "team_features.parquet")
    df_teams = None
    if os.path.exists(team_features_path):
        try:
            df_teams = pd.read_parquet(team_features_path).set_index("national_team")
        except Exception as e:
            logging.warning(f"Error loading team features parquet: {e}")
            
    # Calculate Power Rating for each team based on performance stats
    raw_ratings = {}
    for team in config.ALL_TEAMS:
        rank = config.FIFA_RANKINGS.get(team, 50)
        rank_factor = (60.0 - rank) / 60.0 # scale rank 1 to 50
        
        if df_teams is not None and team in df_teams.index:
            feat = df_teams.loc[team]
            atk = feat.get("team_attack_strength", 0.5)
            dfn = feat.get("team_defense_solidity", 0.5)
            mid = feat.get("team_midfield_creativity", 0.5)
            dep = feat.get("team_depth_score", 0.5)
            star = feat.get("team_star_player_impact", 0.5)
            
            perf_factor = atk * 0.25 + mid * 0.25 + dfn * 0.25 + dep * 0.15 + star * 0.10
        else:
            perf_factor = 0.5
            
        raw_ratings[team] = perf_factor * 0.65 + rank_factor * 0.35
        
    # 4. Compile statistics
    stats = {}
    for team in config.ALL_TEAMS:
        # Calculate probabilities from Monte Carlo counts
        champion_prob = round(champion_counts[team] / n_simulations, 4)
        finalist_prob = round(finalist_counts[team] / n_simulations, 4)
        semi_finalist_prob = round(sf_counts[team] / n_simulations, 4)
        quarter_finalist_prob = round(qf_counts[team] / n_simulations, 4)
        round_of_16_prob = round(r16_counts[team] / n_simulations, 4)
        round_of_32_prob = round(r32_counts[team] / n_simulations, 4)
        
        stats[team] = {
            "champion_prob": champion_prob,
            "finalist_prob": finalist_prob,
            "semi_finalist_prob": semi_finalist_prob,
            "quarter_finalist_prob": quarter_finalist_prob,
            "round_of_16_prob": round_of_16_prob,
            "round_of_32_prob": round_of_32_prob,
            "power_rating": round(raw_ratings[team], 4)
        }
        
    # 5. Run deterministic tournament to get the single predicted bracket pathway
    res_det = run_deterministic_tournament()
    
    output_data = {
        "sim_stats": stats,
        "sample_run": res_det["bracket"],
        "n_simulations": n_simulations
    }
    
    output_path = os.path.join(config.PROCESSED_DATA_DIR, "simulation_results.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
        
    logging.info(f"Saved Monte Carlo statistics and deterministic pathway to {output_path}")
    print(f"\n--- DETERMINISTIC PREDICTED CHAMPION: {res_det['champion']} ---")
    print(f"Runner Up  : {res_det['runner_up']}")
    print(f"Third Place: {res_det['third_place']}")
    return stats

if __name__ == "__main__":
    run_monte_carlo(1000) # Official simulation runs

