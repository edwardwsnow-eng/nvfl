import streamlit as st
import pandas as pd
import os
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="NVFL War Room 2026", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS WITH ADDED FLOATING IMAGE ANIMATION ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Rajdhani', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; color: #58a6ff; text-shadow: 0 0 10px rgba(88,166,255,0.4); }
    
    /* Neon Position Badges & Heatmap Cards */
    .pos-badge { padding: 4px 10px; border-radius: 4px; font-weight: bold; font-family: 'Orbitron'; font-size: 11px; text-align: center; display: inline-block;}
    .pos-QB { background-color: #ff3366; color: white; box-shadow: 0 0 8px #ff3366; }
    .pos-RB { background-color: #0099ff; color: white; box-shadow: 0 0 8px #0099ff; }
    .pos-WR { background-color: #00cc66; color: white; box-shadow: 0 0 8px #00cc66; }
    .pos-TE { background-color: #ffcc00; color: black; box-shadow: 0 0 8px #ffcc00; }
    .pos-DEF { background-color: #9933ff; color: white; box-shadow: 0 0 8px #9933ff; }
    .pos-K { background-color: #e67e22; color: white; box-shadow: 0 0 8px #e67e22; }
    
    /* Card Styling */
    .board-card {
        background: linear-gradient(145deg, #1f2937, #111827);
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 8px;
        margin: 4px 0px;
        text-align: center;
        transition: transform 0.2s;
    }
    .board-card-QB { border: 1px solid #ff3366; box-shadow: inset 0 0 5px rgba(255,51,102,0.2); }
    .board-card-RB { border: 1px solid #0099ff; box-shadow: inset 0 0 5px rgba(0,153,255,0.2); }
    .board-card-WR { border: 1px solid #00cc66; box-shadow: inset 0 0 5px rgba(0,204,102,0.2); }
    .board-card-TE { border: 1px solid #ffcc00; box-shadow: inset 0 0 5px rgba(255,204,0,0.2); }
    .board-card-DEF { border: 1px solid #9933ff; box-shadow: inset 0 0 5px rgba(153,51,255,0.2); }
    .board-card-K { border: 1px solid #e67e22; box-shadow: inset 0 0 5px rgba(230,126,34,0.2); }
    
    .otc-active { border: 2px solid #ffcc00 !important; box-shadow: 0 0 15px #ffcc00; animation: pulse 1.5s infinite; }
    
    .team-logo-img {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 4px;
        border: 1px solid #484f58;
    }

    /* 👁️ ANIMATED STARE GRAPHIC EFFECT 👁️ */
    .stare-container {
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        border-radius: 12px;
        background: rgba(255, 51, 102, 0.05);
        border: 1px dashed rgba(255, 51, 102, 0.2);
    }
    .stare-img {
        width: 85%;
        border-radius: 10px;
        animation: floatStare 4s ease-in-out infinite alternate;
        filter: drop-shadow(0 0 12px rgba(88,166,255,0.3));
    }
    
    @keyframes floatStare {
        0% { transform: translateY(0px) scale(0.98) rotate(0deg); filter: drop-shadow(0 0 8px rgba(255,51,102,0.3)); }
        50% { filter: drop-shadow(0 0 18px rgba(88,166,255,0.6)); }
        100% { transform: translateY(-12px) scale(1.02) rotate(1deg); filter: drop-shadow(0 0 8px rgba(255,51,102,0.3)); }
    }
    @keyframes pulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)

# --- TEAM MATRIX ---
TEAM_ASSETS = {
    "Sleeper Cell": {"logo": "https://placehold.co/100x100/1f2937/ff3366?text=SC", "sound": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"},
    "Phantasm": {"logo": "https://placehold.co/100x100/1f2937/0099ff?text=PH", "sound": ""},
    "Icelanders": {"logo": "https://placehold.co/100x100/1f2937/00cc66?text=ICE", "sound": ""},
    "El Nino": {"logo": "https://placehold.co/100x100/1f2937/ffcc00?text=EN", "sound": ""},
    "Buttheads": {"logo": "https://placehold.co/100x100/1f2937/9933ff?text=BH", "sound": "https://actions.google.com/sounds/v1/sports/soccer_stadium_whistle.ogg"},
    "Big Boys Big Work": {"logo": "https://placehold.co/100x100/1f2937/ffffff?text=BB", "sound": ""},
    "Turbo-Ginz": {"logo": "https://placehold.co/100x100/1f2937/e67e22?text=TG", "sound": ""},
    "Luddite": {"logo": "https://placehold.co/100x100/1f2937/ff3366?text=LUD", "sound": ""},
    "Achains": {"logo": "https://placehold.co/100x100/1f2937/0099ff?text=ACH", "sound": ""},
    "Daddy's Dogs": {"logo": "https://placehold.co/100x100/1f2937/00cc66?text=DDG", "sound": ""},
    "TDs and Beers": {"logo": "https://placehold.co/100x100/1f2937/ffcc00?text=TD", "sound": ""},
    "DD Riders": {"logo": "https://placehold.co/100x100/1f2937/9933ff?text=DDR", "sound": ""},
    "Nasty": {"logo": "https://placehold.co/100x100/1f2937/ffffff?text=NY", "sound": ""},
    "Red Hammer": {"logo": "https://placehold.co/100x100/1f2937/ff3366?text=RH", "sound": ""},
    "Expansion Team 15": {"logo": "https://placehold.co/100x100/1f2937/8b949e?text=E15", "sound": ""},
    "Expansion Team 16": {"logo": "https://placehold.co/100x100/1f2937/8b949e?text=E16", "sound": ""}
}

DEFAULT_HORN = "https://actions.google.com/sounds/v1/alarms/air_horn_so_loud.ogg"
TEAMS_16 = list(TEAM_ASSETS.keys())
TOTAL_REGULAR_ROUNDS = 15
TOTAL_KEEPER_PICKS = 32

def trigger_draft_sound(team_name):
    team_sound = TEAM_ASSETS.get(team_name, {}).get("sound", "")
    final_audio_url = team_sound if team_sound else DEFAULT_HORN
    st.markdown(f'<audio src="{final_audio_url}" autoplay></audio>', unsafe_allow_html=True)

FILE_NAME = "_NVFL Draft Sheet 2026.xlsx"

@st.cache_data
def load_base_data():
    if os.path.exists(FILE_NAME):
        return pd.read_excel(FILE_NAME, sheet_name='PlayerDB')
    return pd.DataFrame(columns=['Player', 'Team', 'Pos', 'Bye', 'PPR'])

player_pool = load_base_data()

# --- STATE MANAGEMENT ---
if 'drafted_players' not in st.session_state:
    st.session_state.drafted_players = {}
if 'current_absolute_pick' not in st.session_state:
    st.session_state.current_absolute_pick = 1
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = time.time()

def get_draft_metadata(abs_pick):
    if abs_pick <= TOTAL_KEEPER_PICKS:
        k_round = ((abs_pick - 1) // 16) + 1
        idx = (abs_pick - 1) % 16
        return TEAMS_16[idx], f"Keeper Round {k_round}", True, abs_pick
    
    reg_pick_num = abs_pick - TOTAL_KEEPER_PICKS
    round_num = ((reg_pick_num - 1) // 16) + 1
    pick_in_round = (reg_pick_num - 1) % 16
    
    if round_num % 2 != 0:
        team = TEAMS_16[pick_in_round]
    else:
        team = TEAMS_16[15 - pick_in_round]
        
    return team, f"Round {round_num}", False, reg_pick_num

otc_team, round_label, is_keeper_phase, display_pick_num = get_draft_metadata(st.session_state.current_absolute_pick)

# --- HEADER SECTION ---
st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>🚨 NVFL DRAFT WAR ROOM 2026 🚨</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #ffcc00; margin-top: 0px;'>{round_label.upper()} • {'KEEPER SLOT' if is_keeper_phase else f'PICK {display_pick_num}'} • {otc_team.upper()} IS ON THE CLOCK</h3>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: CLOCK, CONTROLS & NEW ANIMATED GRAPHIC ---
with st.sidebar:
    st.markdown("### ⏱️ Draft Room Clock")
    time_limit = st.number_input("Set Clock (Seconds)", min_value=15, max_value=300, value=90, step=15)
    
    elapsed = int(time.time() - st.session_state.timer_start)
    remaining = max(0, time_limit - elapsed)
    
    progress_pct = min(1.0, float(elapsed / time_limit))
    st.progress(progress_pct)
    
    if remaining > 0:
        st.metric(label="Time Remaining", value=f"{remaining}s")
    else:
        st.markdown("<h3 style='color: #ff3366; text-align: center;'>⚠️ CLOCK EXPIRED!</h3>", unsafe_allow_html=True)
        
    if st.button("🔄 Reset Timer"):
        st.session_state.timer_start = time.time()
        st.rerun()

    # 👁️ INJECTING THE HOVERING ANIMATION IMAGE HERE 👁️
    if os.path.exists("stare.png"):
        st.markdown("""
        <div class="stare-container">
            <small style="color: #ff3366; font-family: 'Orbitron'; font-weight: bold; letter-spacing: 1px;">🚨 PRESSURE IS ON 🚨</small><br><br>
            <img class="stare-img" src="app/static/stare.png">
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback if file isn't uploaded yet or named differently
        st.info("💡 Upload your photo to GitHub as 'stare.png' to activate the War Room pressure animation!")

    st.markdown("---")
    st.markdown("### 🛠️ Commish Dashboard")
    is_admin = st.checkbox("Enable Admin Drafting Mode", value=True)
    
    if is_admin:
        st.info(f"Drafting for: **{otc_team}**")
        search_query = st.text_input("Search Available Player Name")
        
        taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
        avail_df = player_pool[~player_pool['Player'].isin(taken_names)]
        
        if search_query:
            avail_df = avail_df[avail_df['Player'].str.contains(search_query, case=False, na=False)]
            
        if not avail_df.empty:
            target_row = avail_df.iloc[0]
            st.success(f"Top Match: {target_row['Player']} ({target_row['Pos']})")
            if st.button("🚀 SUBMIT PICK"):
                st.session_state.drafted_players[st.session_state.current_absolute_pick] = {
                    "Player": target_row['Player'],
                    "Pos": target_row['Pos'],
                    "Team": target_row['Team'],
                    "DraftedBy": otc_team,
                    "IsKeeper": is_keeper_phase
                }
                trigger_draft_sound(otc_team)
                st.session_state.current_absolute_pick += 1
                st.session_state.timer_start = time.time()
                st.rerun()
        
        st.markdown("---")
        if st.session_state.current_absolute_pick > 1:
            if st.button("⏪ UNDO LAST PICK"):
                last_pick = st.session_state.current_absolute_pick - 1
                if last_pick in st.session_state.drafted_players:
                    del st.session_state.drafted_players[last_pick]
                st.session_state.current_absolute_pick = last_pick
                st.session_state.timer_start = time.time()
                st.rerun()

# --- TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📊 Live Draft Matrix Board", "📋 Depth & Best Available", "🏆 Team Rosters"])

with tab1:
    st.markdown("### 🔐 Pre-Draft Keeper Phase")
    for kr in [1, 2]:
        st.markdown(f"**Keeper Round {kr}**")
        k_cols = st.columns(16)
        for i in range(1, 17):
            k_abs_pick = ((kr - 1) * 16) + i
            k_team = TEAMS_16[i-1]
            k_logo = TEAM_ASSETS.get(k_team, {}).get("logo", "")
            
            if k_abs_pick in st.session_state.drafted_players:
                p_data = st.session_state.drafted_players[k_abs_pick]
                p_pos = p_data['Pos']
                k_cols[i-1].markdown(f"""
                <div class="board-card board-card-{p_pos}">
                    <img class="team-logo-img" src="{k_logo}"><br>
                    <strong style="color: white; font-size: 11px;">{p_data['Player'].split('–')[0]}</strong><br>
                    <span class="pos-badge pos-{p_pos}">{p_pos}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                is_otc = (k_abs_pick == st.session_state.current_absolute_pick)
                card_style = "board-card otc-active" if is_otc else "board-card"
                opacity = "1.0" if is_otc else "0.3"
                k_cols[i-1].markdown(f"""
                <div class="{card_style}" style="opacity: {opacity};">
                    <img class="team-logo-img" src="{k_logo}"><br>
                    <small style="color: #8b949e;">{k_team[:8]}</small>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("### 🏈 Main Draft Board Matrix")
    for r in range(1, TOTAL_REGULAR_ROUNDS + 1):
        st.markdown(f"**Round {r}**")
        cols = st.columns(16)
        for i in range(1, 17):
            reg_pick_offset = ((r - 1) * 16) + i
            calc_abs_pick = TOTAL_KEEPER_PICKS + reg_pick_offset
            
            display_team, _, _, _ = get_draft_metadata(calc_abs_pick)
            team_logo = TEAM_ASSETS.get(display_team, {}).get("logo", "")
            
            if calc_abs_pick in st.session_state.drafted_players:
                pick_data = st.session_state.drafted_players[calc_abs_pick]
                p_pos = pick_data['Pos']
                
                cols[i-1].markdown(f"""
                <div class="board-card board-card-{p_pos}">
                    <small style="color: #8b949e;">Pk {reg_pick_offset}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: white; font-size: 12px;">{pick_data['Player'].split('–')[0]}</strong><br>
                    <span class="pos-badge pos-{p_pos}">{p_pos}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                is_otc = (calc_abs_pick == st.session_state.current_absolute_pick)
                card_style = "board-card otc-active" if is_otc else "board-card"
                opacity = "1.0" if is_otc else "0.4"
                
                cols[i-1].markdown(f"""
                <div class="{card_style}" style="opacity: {opacity};">
                    <small style="color: #8b949e;">Pk {reg_pick_offset}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: #8b949e; font-size: 10px;">{display_team[:8]}</strong>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("Available Pool Metrics")
    taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
    remaining_players = player_pool[~player_pool['Player'].isin(taken_names)]
    
    counts = remaining_players['Pos'].value_counts()
    st.markdown("#### 📊 Players Remaining By Position")
    st.bar_chart(counts)
    
    st.markdown("#### 📋 Top Available Board")
    st.dataframe(remaining_players[['Player', 'Pos', 'Bye', 'PPR']].head(50), use_container_width=True)

with tab3:
    st.subheader("Team Franchise Rosters")
    t_cols = st.columns(4)
    for idx, t in enumerate(TEAMS_16):
        with t_cols[idx % 4]:
            t_logo = TEAM_ASSETS.get(t, {}).get("logo", "")
            st.markdown(f"##### <img src='{t_logo}' style='width:24px; border-radius:50%; vertical-align:middle;'> {t}", unsafe_allow_html=True)
            
            t_picks = [p for p in st.session_state.drafted_players.values() if p['DraftedBy'] == t]
            if t_picks:
                for tp in t_picks:
                    lbl = "[KEEPER] " if tp.get('IsKeeper') else ""
                    st.markdown(f"• {lbl}**{tp['Player']}** <span class='pos-badge pos-{tp['Pos']}'>{tp['Pos']}</span>", unsafe_allow_html=True)
            else:
                st.write("*No roster entries recorded*")
            
