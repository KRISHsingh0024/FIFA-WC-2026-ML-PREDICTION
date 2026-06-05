"""
FIFA World Cup 2026 Prediction Model Dashboard.
Provides an interactive web interface using Streamlit to visualize predictions, team strengths,
player impacts, and run custom matchups with what-if injury scenarios.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.predict import MatchPredictor, predict_match
from model.explain import explain_match_prediction

# Page config
st.set_page_config(
    page_title="FIFA World Cup 2026 Predictor",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode, Sleek Theme)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1f2937;
        border-radius: 4px 4px 0px 0px;
        color: #9ca3af;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #3b82f6;
    }
    .bracket-box {
        background-color: #1f2937;
        padding: 10px;
        border-radius: 6px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .bracket-box-winner {
        border-left: 5px solid #10b981;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Load Resources ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    team_path = os.path.join(config.PROCESSED_DATA_DIR, "team_features.parquet")
    sim_path = os.path.join(config.PROCESSED_DATA_DIR, "simulation_results.json")
    player_path = os.path.join(config.PROCESSED_DATA_DIR, "player_features.parquet")
    
    teams_df = pd.read_parquet(team_path) if os.path.exists(team_path) else None
    players_df = pd.read_parquet(player_path) if os.path.exists(player_path) else None
    
    sim_results = None
    if os.path.exists(sim_path):
        with open(sim_path, "r") as f:
            sim_results = json.load(f)
            
    return teams_df, players_df, sim_results

teams_df, players_df, sim_results = load_data()

# Check if data exists
if teams_df is None or sim_results is None:
    st.error("⚠️ Data files are missing! Please run the pipeline first to generate them.")
    st.info("You can run the pipeline by executing `python main.py` in your terminal.")
    if st.button("Run ML Pipeline Now (Will generate datasets)"):
        with st.spinner("Executing pipeline (collecting data, building features, training model)..."):
            import subprocess
            subprocess.run(["python", "main.py"])
            st.cache_data.clear()
            st.rerun()
    st.stop()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.title("🏆 World Cup 2026")
st.sidebar.markdown("---")

# What-if Scenarios: Injury simulator
st.sidebar.subheader("🏥 Injury Simulator")
st.sidebar.write("Select players to simulate as injured. Their national team's stats will update dynamically!")

# Selectable players to injure
injury_candidates = [
    ("Kylian Mbappé", "France"),
    ("Lionel Messi", "Argentina"),
    ("Erling Haaland", "Norway"),
    ("Kevin De Bruyne", "Belgium"),
    ("Mohamed Salah", "Egypt"),
    ("Son Heung-min", "South Korea"),
    ("Jude Bellingham", "England"),
    ("Vinícius Júnior", "Brazil")
]

injured_players = []
for p_name, p_team in injury_candidates:
    if st.sidebar.checkbox(f"🤕 {p_name} ({p_team})"):
        injured_players.append(p_name)

# Modify team features dynamically based on injured players
@st.cache_data
def get_modified_team_features(injured_list):
    """Recalculates team features if key players are injured."""
    teams_mod = teams_df.copy().set_index("national_team")
    players_mod = players_df.copy()
    
    for injured in injured_list:
        p_row = players_mod[players_mod["player_name"] == injured]
        if len(p_row) > 0:
            team = p_row.iloc[0]["national_team"]
            
            # Reduce team features by removing this player's contributions
            # Specifically reduce attack strength, star impact, and xG
            teams_mod.loc[team, "team_attack_strength"] *= 0.85
            teams_mod.loc[team, "team_star_player_impact"] *= 0.6
            teams_mod.loc[team, "team_overall_xg"] *= 0.8
            
            # Recalculate other metrics
            teams_mod.loc[team, "team_midfield_creativity"] *= 0.95
            
    return teams_mod.reset_index()

active_teams_df = get_modified_team_features(injured_players)

# Display a notice if there are active injuries
if injured_players:
    st.sidebar.warning(f"Active injuries simulated for: {', '.join(injured_players)}")
    
# Footer info
st.sidebar.markdown("---")
st.sidebar.caption("FIFA World Cup 2026 ML Predictor")
st.sidebar.caption("Powered by XGBoost & FBref Data")

# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🏆 FIFA World Cup 2026 ML Predictor")
st.markdown("An interactive machine learning prediction model deriving national team strengths from player-level club performance.")

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab_bracket, tab_strengths, tab_players, tab_predictor = st.tabs([
    "📊 Bracket & Projections",
    "📈 Team Radar Comparison",
    "⭐ Player Performance",
    "🎯 Head-to-Head Predictor"
])

# ─── Tab 1: Bracket & Projections ───────────────────────────────────────────
with tab_bracket:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔮 Winner Probabilities")
        st.write("Calculated from Monte Carlo simulations of the 104-match tournament.")
        
        # Display top teams in a chart
        sim_stats = sim_results["sim_stats"]
        prob_records = []
        for team, probs in sim_stats.items():
            prob_records.append({
                "Team": team,
                "Champion Prob": probs["champion_prob"] * 100,
                "Finalist Prob": probs["finalist_prob"] * 100,
                "Top 4 Prob": probs["semi_finalist_prob"] * 100
            })
            
        prob_df = pd.DataFrame(prob_records).sort_values("Champion Prob", ascending=False).head(15)
        
        fig = px.bar(
            prob_df,
            x="Champion Prob",
            y="Team",
            orientation="h",
            color="Champion Prob",
            color_continuous_scale="Viridis",
            labels={"Champion Prob": "Champion Probability (%)"},
            title="Top 15 Title Contenders"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=450, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("🏆 Sample Simulation Bracket")
        st.write("Visual progression of the knockout stages from a single simulation run.")
        
        sample = sim_results["sample_run"]
        
        # Display progression columns
        # Columns: R32 -> R16 -> QF -> SF -> Final -> Champion
        col_r32, col_r16, col_qf, col_sf, col_fin = st.columns(5)
        
        with col_r32:
            st.markdown("**Round of 32 (Selected)**")
            # Show first 8 matches for space
            for i, m in enumerate(sample["r32_matches"][:8]):
                winner_style = "bracket-box-winner" if m["winner"] == m["team_a"] else ""
                st.markdown(f"""
                    <div class="bracket-box {winner_style}">
                        <b>Match {i+1}</b><br/>
                        {m['team_a']} ({m['goals_a']})<br/>
                        {m['team_b']} ({m['goals_b']})
                    </div>
                """, unsafe_allow_html=True)
                
        with col_r16:
            st.markdown("**Round of 16**")
            for i, m in enumerate(sample["r16_matches"][:4]):
                winner_style = "bracket-box-winner" if m["winner"] == m["team_a"] else ""
                st.markdown(f"""
                    <div class="bracket-box {winner_style}">
                        <b>R16 Match {i+1}</b><br/>
                        {m['team_a']} ({m['goals_a']})<br/>
                        {m['team_b']} ({m['goals_b']})
                    </div>
                """, unsafe_allow_html=True)
                
        with col_qf:
            st.markdown("**Quarter-Finals**")
            for i, m in enumerate(sample["qf_matches"]):
                winner_style = "bracket-box-winner" if m["winner"] == m["team_a"] else ""
                st.markdown(f"""
                    <div class="bracket-box {winner_style}">
                        <b>QF Match {i+1}</b><br/>
                        {m['team_a']} ({m['goals_a']})<br/>
                        {m['team_b']} ({m['goals_b']})
                    </div>
                """, unsafe_allow_html=True)
                
        with col_sf:
            st.markdown("**Semi-Finals**")
            for i, m in enumerate(sample["sf_matches"]):
                winner_style = "bracket-box-winner" if m["winner"] == m["team_a"] else ""
                st.markdown(f"""
                    <div class="bracket-box {winner_style}">
                        <b>Semi-Final {i+1}</b><br/>
                        {m['team_a']} ({m['goals_a']})<br/>
                        {m['team_b']} ({m['goals_b']})
                    </div>
                """, unsafe_allow_html=True)
                
        with col_fin:
            st.markdown("**Final & Champion**")
            m = sample["final_match"]
            winner_style = "bracket-box-winner"
            st.markdown(f"""
                <div class="bracket-box {winner_style}" style="border-left: 5px solid #f59e0b; background-color: #2d220f;">
                    <b>🏆 FINAL MATCH</b><br/>
                    {m['team_a']} ({m['goals_a']})<br/>
                    {m['team_b']} ({m['goals_b']})<br/>
                    <span style="color: #f59e0b; font-weight: bold;">Winner: {m['winner']}</span>
                </div>
            """, unsafe_allow_html=True)

# ─── Tab 2: Team Radar Comparison ──────────────────────────────────────────
with tab_strengths:
    st.subheader("📊 Team Strengths Comparison")
    st.write("Compare the metric-by-metric strength profile of any two national teams.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        team_a = st.selectbox("Select Team A", config.ALL_TEAMS, index=config.ALL_TEAMS.index("France"))
    with col_t2:
        team_b = st.selectbox("Select Team B", config.ALL_TEAMS, index=config.ALL_TEAMS.index("Argentina"))
        
    if team_a == team_b:
        st.warning("Please select two different teams for comparison.")
    else:
        # Get team features
        active_teams_df = active_teams_df.set_index("national_team")
        feat_a = active_teams_df.loc[team_a]
        feat_b = active_teams_df.loc[team_b]
        
        # Reset index to reuse active_teams_df later
        active_teams_df = active_teams_df.reset_index()
        
        categories = ["Attack Strength", "Midfield Creativity", "Defense Solidity", "Squad Depth", "Star Impact"]
        
        # Standardize features roughly on a 0-1 scale for radar chart display
        val_a = [
            float(feat_a["team_attack_strength"]) * 2.0,
            float(feat_a["team_midfield_creativity"]) * 2.5,
            float(feat_a["team_defense_solidity"]) * 2.0,
            float(feat_a["team_depth_score"]),
            float(feat_a["team_star_player_impact"]) * 0.5
        ]
        
        val_b = [
            float(feat_b["team_attack_strength"]) * 2.0,
            float(feat_b["team_midfield_creativity"]) * 2.5,
            float(feat_b["team_defense_solidity"]) * 2.0,
            float(feat_b["team_depth_score"]),
            float(feat_b["team_star_player_impact"]) * 0.5
        ]
        
        # Plotly Radar Chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=val_a,
            theta=categories,
            fill='toself',
            name=team_a,
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.4)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=val_b,
            theta=categories,
            fill='toself',
            name=team_b,
            line_color='#ef4444',
            fillcolor='rgba(239, 68, 68, 0.4)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1.2]
                )
            ),
            showlegend=True,
            template="plotly_dark",
            title=f"{team_a} vs {team_b} Strength Comparison"
        )
        
        # Display side-by-side stats
        col_chart, col_stats = st.columns([2, 1])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
            
        with col_stats:
            st.markdown(f"### 📋 Profile Cards")
            
            # FIFA Rankings
            rank_a = config.FIFA_RANKINGS.get(team_a, 50)
            rank_b = config.FIFA_RANKINGS.get(team_b, 50)
            
            st.markdown(f"""
                <div style="background-color: #1f2937; padding: 15px; border-radius: 6px; margin-bottom: 10px;">
                    <h4 style="color: #3b82f6; margin-top:0;">{team_a}</h4>
                    <b>FIFA World Rank:</b> #{rank_a}<br/>
                    <b>Attack Rating:</b> {feat_a['team_attack_strength']:.3f}<br/>
                    <b>Creativity Rating:</b> {feat_a['team_midfield_creativity']:.3f}<br/>
                    <b>Defense Solidity:</b> {feat_a['team_defense_solidity']:.3f}<br/>
                    <b>Star Impact:</b> {feat_a['team_star_player_impact']:.3f}
                </div>
                <div style="background-color: #1f2937; padding: 15px; border-radius: 6px;">
                    <h4 style="color: #ef4444; margin-top:0;">{team_b}</h4>
                    <b>FIFA World Rank:</b> #{rank_b}<br/>
                    <b>Attack Rating:</b> {feat_b['team_attack_strength']:.3f}<br/>
                    <b>Creativity Rating:</b> {feat_b['team_midfield_creativity']:.3f}<br/>
                    <b>Defense Solidity:</b> {feat_b['team_defense_solidity']:.3f}<br/>
                    <b>Star Impact:</b> {feat_b['team_star_player_impact']:.3f}
                </div>
            """, unsafe_allow_html=True)

# ─── Tab 3: Player Performance ──────────────────────────────────────────────
with tab_players:
    st.subheader("⭐ Player Club Performance Stats")
    st.write("Browse and search player performance metrics across the top-5 European leagues & Champions League.")
    
    # Filter by country
    country_filter = st.selectbox("Filter by National Team", ["All Teams"] + config.ALL_TEAMS)
    
    if country_filter == "All Teams":
        display_players = players_df
    else:
        display_players = players_df[players_df["national_team"] == country_filter]
        
    # Search bar
    search_query = st.text_input("🔍 Search Player Name:")
    if search_query:
        display_players = display_players[display_players["player_name"].str.contains(search_query, case=False)]
        
    st.dataframe(
        display_players[[
            "player_name", "position", "club", "national_team", "is_starter",
            "goals_p90", "xg_p90", "assists_p90", "xa_p90", "key_passes_p90",
            "tackles_p90", "pass_completion_pct", "successful_dribbles_p90"
        ]].sort_values("goals_p90", ascending=False),
        use_container_width=True
    )
    
    st.subheader("💡 Player Game-Changer Index")
    st.write("Composite indicator representing overall attacking + creative output per 90 minutes.")
    
    # Calculate composite for visual ranking
    players_df["game_changer_score"] = players_df["goals_p90"] + players_df["assists_p90"] + (players_df["key_passes_p90"] * 0.4)
    top_changers = players_df.sort_values("game_changer_score", ascending=False).head(20)
    
    fig = px.bar(
        top_changers,
        x="game_changer_score",
        y="player_name",
        color="national_team",
        orientation="h",
        labels={"game_changer_score": "Game-Changer Index (Composite)", "player_name": "Player"},
        title="Top 20 Players by Club Performance Index"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=550)
    st.plotly_chart(fig, use_container_width=True)

# ─── Tab 4: Head-to-Head Predictor ──────────────────────────────────────────
with tab_predictor:
    st.subheader("🎯 Head-to-Head Match Predictor")
    st.write("Select any two teams and run model inference to see prediction probabilities.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sel_team_a = st.selectbox("Select Team 1", config.ALL_TEAMS, key="pred_t1", index=config.ALL_TEAMS.index("France"))
    with col_p2:
        sel_team_b = st.selectbox("Select Team 2", config.ALL_TEAMS, key="pred_t2", index=config.ALL_TEAMS.index("Argentina"))
        
    if sel_team_a == sel_team_b:
        st.warning("Please select two different teams for predictions.")
    else:
        if st.button("🔮 Run Model Inference", type="primary"):
            with st.spinner("Analyzing team rosters and compiling features..."):
                # Run explanation and prediction
                res = explain_match_prediction(sel_team_a, sel_team_b)
                probs = res["probabilities"]
                
                st.markdown("---")
                
                # Show results in metric cards
                col_ma, col_md, col_mb = st.columns(3)
                with col_ma:
                    st.metric(label=f"🥇 {sel_team_a} Win Probability", value=f"{probs['team_a_win']:.2%}")
                with col_md:
                    st.metric(label="🤝 Draw Probability", value=f"{probs['draw']:.2%}")
                with col_mb:
                    st.metric(label=f"🥈 {sel_team_b} Win Probability", value=f"{probs['team_b_win']:.2%}")
                    
                # Visual Bar Chart for probability breakdown
                prob_data = pd.DataFrame({
                    "Outcome": [f"{sel_team_a} Win", "Draw", f"{sel_team_b} Win"],
                    "Probability (%)": [probs["team_a_win"] * 100, probs["draw"] * 100, probs["team_b_win"] * 100]
                })
                
                fig = px.bar(
                    prob_data,
                    x="Probability (%)",
                    y="Outcome",
                    orientation="h",
                    color="Outcome",
                    color_discrete_map={
                        f"{sel_team_a} Win": "#3b82f6",
                        "Draw": "#6b7280",
                        f"{sel_team_b} Win": "#ef4444"
                    },
                    title="Outcome Probability Distribution"
                )
                fig.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Model Explanation Text
                st.markdown("### 🧠 Model Matchup Explanations")
                for exp in res["explanations"]:
                    st.markdown(f"- {exp}")
                    
                # SHAP feature contributions
                st.markdown("### 📊 Feature Contributions (SHAP Values)")
                st.write("Positive values favor Team 1; negative values favor Team 2.")
                
                shap_df = pd.DataFrame(list(res["shap_contributions"].items()), columns=["Feature", "Contribution"])
                shap_df = shap_df.sort_values("Contribution", key=abs, ascending=False)
                
                fig_shap = px.bar(
                    shap_df,
                    x="Contribution",
                    y="Feature",
                    orientation="h",
                    color="Contribution",
                    color_continuous_scale="RdBu",
                    title="Feature Contribution to Prediction"
                )
                st.plotly_chart(fig_shap, use_container_width=True)
