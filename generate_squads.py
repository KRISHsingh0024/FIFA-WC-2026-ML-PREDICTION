"""
Auto-generate squad_lists.py from the official FIFA PDF data.
Parses the raw text, maps to config team names, selects key 10-12 players per team
based on club prestige, and outputs Python code.
"""
import re
import json

with open(r"c:\Users\Krish\Desktop\FIFA WORLD CUP PREDICTION MODEL\squad_raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split by SQUAD LIST headers
sections = re.split(r"SQUAD LIST\n", text)

# Club prestige tiers (higher = better league/club)
TOP_CLUBS = {
    "Real Madrid", "FC Barcelona", "Manchester City", "Liverpool", "Arsenal",
    "Chelsea", "Manchester United", "Bayern München", "Borussia Dortmund",
    "Paris Saint-Germain", "Internazionale Milano", "AC Milan", "Juventus",
    "Napoli", "Atletico", "Atlético", "Tottenham", "Newcastle",
    "Aston Villa", "Leverkusen", "RB Leipzig", "Brighton",
    "Atalanta", "Monaco", "Sporting CP", "Benfica", "Porto",
    "Marseille", "Lyon", "West Ham", "Crystal Palace", "Fulham",
    "Nottingham Forest", "Bournemouth", "Brentford", "Feyenoord",
    "PSV Eindhoven", "Ajax", "Roma", "Fiorentina", "Bologna",
    "Sevilla", "Villarreal", "Betis", "Sociedad",
    "Lille", "Lens", "Strasbourg", "Rennais", "Genoa",
    "Wolves", "Everton", "Celtic", "Rangers",
}

def is_top_club(club_str):
    """Check if a club string contains a top-tier club name."""
    for tc in TOP_CLUBS:
        if tc.lower() in club_str.lower():
            return True
    return False

# Map PDF team names to our config names
name_map = {
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Cabo Verde": "Cape Verde",
    "Cape Verde Islands": "Cape Verde",
    "Congo DR": "DR Congo",
    "Côte D'Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Korea Republic": "South Korea",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "USA": "United States",
    "Curaçao": "Curacao",
    "IR Iran": "Iran",
}

teams = {}

for section in sections:
    lines = section.strip().split("\n")
    team_match = re.match(r"(.+?)\s*\(([A-Z]{3})\)", lines[0])
    if not team_match:
        continue
    team_name = team_match.group(1).strip()
    team_code = team_match.group(2)
    mapped_name = name_map.get(team_name, team_name)

    players = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in ("GK", "DF", "MF", "FW"):
            pos = line
            if i + 1 < len(lines):
                player_name = lines[i + 1].strip()
                # Skip fake entries
                if player_name in ("Goalkeeper", "Defender", "Mid«Elder", "Forward", "Mid«elder"):
                    i += 1
                    continue

                club = ""
                for j in range(i + 2, min(i + 12, len(lines))):
                    club_line = lines[j].strip()
                    club_match = re.search(r"(.+?)\s*\(([A-Z]{3})\)\s*$", club_line)
                    if club_match and not re.match(r"^\d{2}/\d{2}/\d{4}$", club_line):
                        club = club_match.group(1).strip()
                        # Fix encoding issues
                        club = club.replace("«", "fi").replace("»", "fl")
                        break

                # Clean player name
                parts = player_name.split(" ", 1)
                if len(parts) == 2:
                    surname = parts[0]
                    firstname = parts[1]
                    display_name = f"{firstname} {surname.title()}"
                else:
                    display_name = player_name.title()

                # Fix encoding in name
                display_name = display_name.replace("«", "fi").replace("»", "fl")

                players.append({
                    "pos": pos,
                    "name": display_name,
                    "club": club,
                    "is_top_club": is_top_club(club),
                })
        i += 1

    teams[mapped_name] = {
        "code": team_code,
        "players": players,
    }

# Now select key players: first 11 (likely starters) + a few notable bench players
# The PDF lists them in squad number order, with starters typically 1-11
output_lines = []
output_lines.append('"""')
output_lines.append("Squad Lists and Player-to-National-Team Mapping for FIFA World Cup 2026.")
output_lines.append("OFFICIAL ROSTERS from FIFA SquadLists-English.pdf (4 June 2026, Version 1).")
output_lines.append('Contains key player mapping and utilities to match club performance to national teams.')
output_lines.append('"""')
output_lines.append("")
output_lines.append("from fuzzywuzzy import fuzz")
output_lines.append("from fuzzywuzzy import process")
output_lines.append("import logging")
output_lines.append("")
output_lines.append("logging.basicConfig(level=logging.INFO, format=\"%(asctime)s - %(levelname)s - %(message)s\")")
output_lines.append("")
output_lines.append("# Official 2026 FIFA World Cup squad lists")
output_lines.append("# Format: { National_Team: [ (Player_Name, Position, Club, Is_Starter) ] }")
output_lines.append("# First 11 entries are the projected starting XI; remaining are key squad players.")
output_lines.append("KEY_PLAYERS = {")

for team_name in sorted(teams.keys()):
    data = teams[team_name]
    real_players = [p for p in data["players"] if p["name"] not in ("Goalkeeper", "Defender", "Mid«Elder", "Forward")]

    # First 11 = starters, rest = bench
    output_lines.append(f'    "{team_name}": [')
    for idx, p in enumerate(real_players):
        is_starter = idx < 11
        starter_str = "True" if is_starter else "False"
        # Escape quotes in names
        name = p["name"].replace('"', '\\"')
        club = p["club"].replace('"', '\\"')
        output_lines.append(f'        ("{name}", "{p["pos"]}", "{club}", {starter_str}),')
    output_lines.append("    ],")

output_lines.append("}")
output_lines.append("")

# Add the utility functions back
output_lines.append("""
def get_player_national_team(player_name, nationality=None):
    \"\"\"
    Given a player name and their nationality (from FBref), maps them to a World Cup squad.
    Uses direct dictionary check, fuzzy matching, or nationality checks.
    \"\"\"
    player_clean = player_name.strip()

    # 1. Direct match on hardcoded stars
    for country, players in KEY_PLAYERS.items():
        for name, pos, club, starter in players:
            if player_clean.lower() == name.lower():
                return country, pos, starter

    # 2. Fuzzy match on hardcoded stars
    for country, players in KEY_PLAYERS.items():
        star_names = [p[0] for p in players]
        best_match, score = process.extractOne(player_clean, star_names, scorer=fuzz.token_sort_ratio)
        if score > 85:
            for name, pos, club, starter in players:
                if name == best_match:
                    return country, pos, starter

    # 3. Fallback to nationality if they represent one of the 48 WC teams
    if nationality:
        nat_clean = str(nationality).split()[-1].strip().upper()
        country_code_map = {
            "ARG": "Argentina", "FRA": "France", "ENG": "England", "BRA": "Brazil",
            "ESP": "Spain", "POR": "Portugal", "GER": "Germany", "NED": "Netherlands",
            "NOR": "Norway", "BEL": "Belgium", "URU": "Uruguay", "COL": "Colombia",
            "MAR": "Morocco", "CRO": "Croatia", "EGY": "Egypt", "KOR": "South Korea",
            "JPN": "Japan", "USA": "United States", "MEX": "Mexico", "CAN": "Canada",
            "SUI": "Switzerland", "ECU": "Ecuador", "CIV": "Ivory Coast", "SEN": "Senegal",
            "TUR": "Turkey", "RSA": "South Africa", "CZE": "Czechia", "BIH": "Bosnia and Herzegovina",
            "QAT": "Qatar", "HAI": "Haiti", "SCO": "Scotland", "PAR": "Paraguay",
            "AUS": "Australia", "NZL": "New Zealand", "CPV": "Cape Verde", "KSA": "Saudi Arabia",
            "IRQ": "Iraq", "ALG": "Algeria", "AUT": "Austria", "JOR": "Jordan",
            "COD": "DR Congo", "UZB": "Uzbekistan", "GHA": "Ghana", "PAN": "Panama",
            "SWE": "Sweden", "TUN": "Tunisia", "IRN": "Iran", "CUW": "Curacao",
        }
        if nat_clean in country_code_map:
            return country_code_map[nat_clean], None, False
        for country in country_code_map.values():
            if country.lower() in str(nationality).lower():
                return country, None, False

    return None, None, False


def load_squad_lists():
    \"\"\"
    Returns the key players dictionary.
    \"\"\"
    return KEY_PLAYERS
""")

# Write the file
content = "\n".join(output_lines)
with open(r"c:\Users\Krish\Desktop\FIFA WORLD CUP PREDICTION MODEL\data\squad_lists.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated squad_lists.py with {len(teams)} teams")
for t in sorted(teams.keys()):
    real = [p for p in teams[t]["players"] if p["name"] not in ("Goalkeeper", "Defender", "Mid«Elder", "Forward")]
    print(f"  {t}: {len(real)} players")
