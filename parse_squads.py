"""
Parse the official FIFA World Cup 2026 squad list PDF text into structured data.
"""
import re
import json

with open(r"c:\Users\Krish\Desktop\FIFA WORLD CUP PREDICTION MODEL\squad_raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split by SQUAD LIST headers
sections = re.split(r"SQUAD LIST\n", text)

teams = {}

for section in sections[1:]:  # Skip preamble
    lines = section.strip().split("\n")
    
    # First line is team name like "Austria (AUT)"
    team_match = re.match(r"(.+?)\s*\(([A-Z]{3})\)", lines[0])
    if not team_match:
        continue
    team_name = team_match.group(1).strip()
    team_code = team_match.group(2)
    
    # Parse players - look for POS lines followed by player data
    players = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in ("GK", "DF", "MF", "FW"):
            pos = line
            # Next line is "SURNAME FirstName" format
            if i + 1 < len(lines):
                player_name = lines[i + 1].strip()
                
                # Look ahead for the club (contains country code in parens)
                club = ""
                for j in range(i + 2, min(i + 12, len(lines))):
                    club_line = lines[j].strip()
                    club_match = re.search(r"(.+?)\s*\(([A-Z]{3})\)\s*$", club_line)
                    if club_match and not re.match(r"^\d{2}/\d{2}/\d{4}$", club_line):
                        club = club_match.group(1).strip()
                        break
                
                # Clean player name: "SURNAME FirstName" -> "FirstName Surname"
                parts = player_name.split(" ", 1)
                if len(parts) == 2:
                    surname = parts[0]
                    firstname = parts[1]
                    # Capitalize properly
                    display_name = f"{firstname} {surname.title()}"
                else:
                    display_name = player_name.title()
                
                players.append({
                    "pos": pos,
                    "name": display_name,
                    "raw_name": player_name,
                    "club": club,
                })
        i += 1
    
    teams[team_name] = {
        "code": team_code,
        "players": players,
        "count": len(players),
    }

# Map FIFA PDF team names to our config names
name_map = {
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
    "Congo DR": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Korea Republic": "South Korea",
    "Czechia": "Czechia",
    "IR Iran": "Iran",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "United States": "United States",
    "USA": "United States",
}

# Print all teams with full rosters
print(f"Total teams parsed: {len(teams)}\n")
for team_name in sorted(teams.keys()):
    data = teams[team_name]
    mapped = name_map.get(team_name, team_name)
    print(f"=== {team_name} ({data['code']}) -> {mapped} === [{data['count']} players]")
    for p in data["players"]:
        print(f"  {p['pos']:3s} | {p['name']:30s} | {p['club']}")
    print()
