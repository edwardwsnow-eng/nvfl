import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="NVFL War Room 2026", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR DARK MODE, NEON GRAPHICS & IMAGE RESPONSIVENESS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Rajdhani', sans-serif; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #58a6ff; text-shadow: 0 0 10px rgba(88,166,255,0.4); }
    
    /* Neon Position Cards */
    .pos-badge { padding: 4px 10px; border-radius: 4px; font-weight: bold; font-family: 'Orbitron'; font-size: 12px; text-align: center; display: inline-block;}
    .pos-QB { background-color: #ff3366; color: white; box-shadow: 0 0 8px #ff3366; }
    .pos-RB { background-color: #0099ff; color: white; box-shadow: 0 0 8px #0099ff; }
    .pos-WR { background-color: #00cc66; color: white; box-shadow: 0 0 8px #00cc66; }
    .pos-TE { background-color: #ffcc00; color: black; box-shadow: 0 0 8px #ffcc00; }
    .pos-DEF, .pos-DL, .pos-LB, .pos-DB { background-color: #9933ff; color: white; box-shadow: 0 0 8px #9933ff; }
    .pos-K { background-color: #e67e22; color: white; box-shadow: 0 0 8px #e67e22; }
    
    /* Draft Board Matrix Card */
    .board-card {
        background: linear-gradient(145deg, #1f2937, #111827);
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0px;
        text-align: center;
        transition: transform 0.2s;
    }
    .board-card:hover { transform: scale(1.03); border-color: #58a6ff; }
    .otc-active { border: 2px solid #ffcc00 !important; box-shadow: 0 0 15px #ffcc00; animation: pulse 1.5s infinite; }
    
    .team-logo-img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 5px;
        border: 1px solid #484f58;
    }

    @keyframes pulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURABLE TEAM ASSETS MATRIX ---
TEAM_ASSETS = {
    "Sleeper Cell": {
        "logo": "https://placehold.co/100x100/1f2937/ff3366?text=SC",
        "sound": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
    },
    "Phantasm": {
        "logo": "https://placehold.co/100x100/1f2937/0099ff?text=PH",
        "sound": "" 
    },
    "Icelanders": {
        "logo": "https://placehold.co/100x100/1f2937/00cc66?text=ICE",
        "sound": ""
    },
    "El Nino": {
        "logo": "https://placehold.co/100x100/1f2937/ffcc00?text=EN",
        "sound": ""
    },
    "Buttheads": {
        "logo": "https://placehold.co/100x100/1f2937/9933ff?text=BH",
        "sound": "https://actions.google.com/sounds/v1/sports/soccer_stadium_whistle.ogg" 
    },
    "Big Boys Big Work": {
        "logo": "https://placehold.co/100x100/1f2937/ffffff?text=BB",
        "sound": ""
    },
    "Turbo-Ginz": {
        "logo": "https://placehold.co/100x100/1f2937/e67e22?text=TG",
        "sound": ""
    },
    "Luddite": {
        "logo": "https://placehold.co/100x100/1f2937/ff3366?text=LUD",
        "sound": ""
    },
    "Achains": {
        "logo": "https://placehold.co/100x100/1f2937/0099ff?text=ACH",
        "sound": ""
    },
    "Daddy's Dogs": {
        "logo": "https://placehold.co/100x100/1f2937/00cc66?text=DDG",
        "sound": ""
    },
    "TDs and Beers": {
        "logo": "https://placehold.co/100x100/1f2937/ffcc00?text=TD",
        "sound": ""
    },
    "DD Riders": {
        "logo": "https://placehold.co/100x100/1f2937/9933ff?text=DDR",
        "sound": ""
    },
    "Nasty": {
        "logo": "https://placehold.co/100x100/1f2937/ffffff?text=NY",
        "sound": ""
    },
    "Red Hammer": {
        "logo": "https://placehold.co/100x100/1f2937/ff3366?text=RH",
        "sound": ""
    },
    "Expansion Team 15": {
        "logo": "https://placehold.co/100x100/1f2937/8b949e?text=E15",
        "sound": ""
    },
    "Expansion Team 16": {
        "logo": "https://placehold.co/100x100/1f2937/8b949e?text=E16",
        "sound": ""
    }
}

DEFAULT_HORN = "https://actions.google.com/sounds/v1/alarms/air_horn_so_loud.ogg"

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
TEAMS_16 = list(TEAM_ASSETS.keys())
TOTAL_ROUNDS = 15

if 'drafted_players' not in st.session_state:
    st.session_state.drafted_players = {}
if 'current_pick' not in st.session_state:
    st.session_state.current_pick = 1

def get_team_for_pick(pick_num, num_teams=16):
    round_num = ((pick_num - 1) // num_teams) + 1
    pick_in_round = (pick_num - 1) % num_teams
    if round_num % 2 != 0:
        return TEAMS_16[pick_in_round], round_num
    else:
        return TEAMS_16[num_teams - 1 - pick_in_round], round_num

otc_team, current_round = get_team_for_pick(st.session_state.current_pick)

st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>🚨 NVFL DRAFT WAR ROOM 2026 🚨</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #ffcc00; margin-top: 0px;'>ROUND {current_round} • PICK {st.session_state.current_pick} • {otc_team.upper()} IS ON THE CLOCK</h3>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("### 🛠️ Commish Dashboard")
    is_admin = st.checkbox("Enable Admin Drafting Mode")
    
    if is_admin:
        st.info(f"Currently Drafting for: **{otc_team}**")
        current_logo = TEAM_ASSETS.get(otc_team, {}).get("logo", "")
        if current_logo:
            st.image(current_logo, width=80)
            
        search_query = st.text_input("Search Available Player Name")
        already_taken = [p['Player'] for p in st.session_state.drafted_players.values()]
        avail_df = player_pool[~player_pool['Player'].isin(already_taken)]
        
        if search_query:
            avail_df = avail_df[avail_df['Player'].str.contains(search_query, case=False, na=False)]
            
        if not avail_df.empty:
            target_row = avail_df.iloc[0]
            st.success(f"Top Match: {target_row['Player']} ({target_row['Pos']})")
            if st.button("🚀 SUBMIT PICK & DETONATE SOUND"):
                st.session_state.drafted_players[st.session_state.current_pick] = {
                    "Player": target_row['Player'],
                    "Pos": target_row['Pos'],
                    "Team": target_row['Team'],
                    "DraftedBy": otc_team
                }
                trigger_draft_sound(otc_team)
                st.session_state.current_pick += 1
                st.rerun()
        else:
            st.write("No players match search.")
            
    st.markdown("---")
    st.markdown("### 🔍 Global Filters")
    pos_filter = st.multiselect("Filter Positions", options=['QB', 'RB', 'WR', 'TE', 'K', 'DEF'], default=['QB', 'RB', 'WR', 'TE'])

tab1, tab2, tab3 = st.tabs(["📊 Main Grid Draft Board", "📋 Best Available Base", "🏆 Roster Breakdowns"])

with tab1:
    st.subheader("The Draft Matrix Grid")
    for r in range(1, TOTAL_ROUNDS + 1):
        st.markdown(f"#### Round {r}")
        cols = st.columns(16)
        for i in range(1, 17):
            calculated_pick = ((r - 1) * 16) + i
            display_team, _ = get_team_for_pick(calculated_pick)
            team_logo = TEAM_ASSETS.get(display_team, {}).get("logo", "")
            
            if calculated_pick in st.session_state.drafted_players:
                pick_data = st.session_state.drafted_players[calculated_pick]
                p_name = pick_data['Player'].split("–")[0]
                p_pos = pick_data['Pos']
                
                cols[i-1].markdown(f"""
                <div class="board-card">
                    <small style="color: #8b949e;">Pick {calculated_pick}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: white; font-size: 13px;">{p_name}</strong><br>
                    <span class="pos-badge pos-{p_pos}">{p_pos}</span><br>
                    <small style="color: #58a6ff;">{pick_data['DraftedBy'][:10]}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                is_otc = (calculated_pick == st.session_state.current_pick)
                card_class = "board-card otc-active" if is_otc else "board-card"
                label = "ON CLOCK" if is_otc else display_team[:10]
                opacity = "opacity: 1.0;" if is_otc else "opacity: 0.4;"
                
                cols[i-1].markdown(f"""
                <div class="{card_class}" style="{opacity}">
                    <small style="color: #8b949e;">Pick {calculated_pick}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: #8b949e; font-size: 11px;">{label}</strong>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("Top Available Targets")
    taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
    remaining_players = player_pool[~player_pool['Player'].isin(taken_names)]
    if len(pos_filter) > 0:
        remaining_players = remaining_players[remaining_players['Pos'].isin(pos_filter)]
    st.dataframe(remaining_players[['Player', 'Pos', 'Bye']].head(40), use_container_width=True)

with tab3:
    st.subheader("Team Roster Allotments")
    team_cols = st.columns(4)
    for idx, t in enumerate(TEAMS_16):
        col_to_use = team_cols[idx % 4]
        with col_to_use:
            t_logo = TEAM_ASSETS.get(t, {}).get("logo", "")
            st.markdown(f"##### <img src='{t_logo}' style='width:25px; border-radius:50%; vertical-align:middle;'> {t}", unsafe_allow_html=True)
            t_picks = [p for p in st.session_state.drafted_players.values() if p['DraftedBy'] == t]
            if t_picks:
                for tp in t_picks:
                    st.markdown(f"• **{tp['Player']}** <span class='pos-badge pos-{tp['Pos']}'>{tp['Pos']}</span>", unsafe_allow_html=True)
            else:
                st.write("*No players selected yet*")
