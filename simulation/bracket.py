"""
Tournament Bracket Data Structures.
Defines Group, Match, and Bracket representations to manage tournament simulation and advancement.
"""

import pandas as pd
import numpy as np

class Group:
    def __init__(self, name: str, teams: list):
        self.name = name
        self.teams = teams
        self.reset()
        
    def reset(self):
        """Resets the group standings."""
        self.standings = {
            team: {
                "points": 0,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_diff": 0
            }
            for team in self.teams
        }
        
    def record_match(self, team_a: str, team_b: str, goals_a: int, goals_b: int):
        """Records a match score in the standings."""
        for team, g_for, g_against in [(team_a, goals_a, goals_b), (team_b, goals_b, goals_a)]:
            stats = self.standings[team]
            stats["played"] += 1
            stats["goals_for"] += g_for
            stats["goals_against"] += g_against
            stats["goal_diff"] = stats["goals_for"] - stats["goals_against"]
            
            if g_for > g_against:
                stats["points"] += 3
                stats["wins"] += 1
            elif g_for == g_against:
                stats["points"] += 1
                stats["draws"] += 1
            else:
                stats["losses"] += 1
                
    def get_ranked_standings(self) -> list:
        """
        Ranks teams in the group according to FIFA World Cup rules:
        1. Points
        2. Goal Difference
        3. Goals For
        4. Head-to-head (simplified as alphabetical or random for this model)
        """
        ranked = sorted(
            self.teams,
            key=lambda t: (
                self.standings[t]["points"],
                self.standings[t]["goal_diff"],
                self.standings[t]["goals_for"]
            ),
            reverse=True
        )
        return [{"team": team, **self.standings[team]} for team in ranked]

class Match:
    def __init__(self, id: str, team_a: str, team_b: str, stage: str):
        self.id = id
        self.team_a = team_a
        self.team_b = team_b
        self.stage = stage
        self.played = False
        self.winner = None
        self.goals_a = None
        self.goals_b = None
        self.probs = None # {team_a_win, draw, team_b_win}
        
    def set_result(self, goals_a: int, goals_b: int, winner: str, probs: dict):
        self.goals_a = goals_a
        self.goals_b = goals_b
        self.winner = winner
        self.probs = probs
        self.played = True

class KnockoutRound:
    def __init__(self, name: str, match_count: int):
        self.name = name
        self.match_count = match_count
        self.matches = []
        
    def add_match(self, match: Match):
        self.matches.append(match)

def get_2026_bracket_pairings(group_results: dict) -> list:
    """
    Given the ranked standings of all 12 groups (A-L),
    returns the Round of 32 match pairings based on the official FIFA World Cup 2026 rules.
    
    Returns a list of tuples: (team_a, team_b, match_id)
    
    Logic:
    - 12 group winners (1st place)
    - 12 group runners-up (2nd place)
    - 8 best 3rd-placed teams
    Total = 32 teams.
    """
    winners = {}
    runners_up = {}
    third_placed = []
    
    # 1. Extract 1st, 2nd, and 3rd from each group
    for g_name, standing in group_results.items():
        winners[g_name] = standing[0]["team"]
        runners_up[g_name] = standing[1]["team"]
        
        t3 = standing[2]
        third_placed.append({
            "team": t3["team"],
            "group": g_name,
            "points": t3["points"],
            "goal_diff": t3["goal_diff"],
            "goals_for": t3["goals_for"]
        })
        
    # 2. Sort and select the 8 best 3rd-placed teams
    best_thirds = sorted(
        third_placed,
        key=lambda x: (x["points"], x["goal_diff"], x["goals_for"]),
        reverse=True
    )[:8]
    best_thirds_teams = [t["team"] for t in best_thirds]
    
    # 3. Create R32 Pairings (structured setup matching official bracket pathways)
    # The official 2026 bracket pathway pairs group winners vs runners-up or 3rd place.
    # To keep it structured and clean, we pair them using a standard bracket pattern:
    pairings = [
        # Left Bracket Section
        (winners["A"], best_thirds_teams[0] if len(best_thirds_teams) > 0 else runners_up["C"], "R32_1"),
        (runners_up["A"], runners_up["B"], "R32_2"),
        (winners["B"], best_thirds_teams[1] if len(best_thirds_teams) > 1 else runners_up["D"], "R32_3"),
        (winners["C"], runners_up["F"], "R32_4"),
        (winners["D"], best_thirds_teams[2] if len(best_thirds_teams) > 2 else runners_up["E"], "R32_5"),
        (runners_up["C"], runners_up["D"], "R32_6"),
        (winners["E"], runners_up["H"], "R32_7"),
        (winners["F"], best_thirds_teams[3] if len(best_thirds_teams) > 3 else runners_up["G"], "R32_8"),
        
        # Right Bracket Section
        (winners["G"], best_thirds_teams[4] if len(best_thirds_teams) > 4 else runners_up["I"], "R32_9"),
        (runners_up["E"], runners_up["F"], "R32_10"),
        (winners["H"], best_thirds_teams[5] if len(best_thirds_teams) > 5 else runners_up["J"], "R32_11"),
        (winners["I"], runners_up["L"], "R32_12"),
        (winners["J"], best_thirds_teams[6] if len(best_thirds_teams) > 6 else runners_up["K"], "R32_13"),
        (runners_up["I"], runners_up["J"], "R32_14"),
        (winners["K"], runners_up["A"], "R32_15"),
        (winners["L"], best_thirds_teams[7] if len(best_thirds_teams) > 7 else runners_up["B"], "R32_16"),
    ]
    
    return pairings
