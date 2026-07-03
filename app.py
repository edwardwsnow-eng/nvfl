import streamlit as st
import pandas as pd
import os
import time
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="NVFL War Room 2026", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM PINK CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=400;700&family=Rajdhani:wght=500;700&display=swap');
    
    /* Vibrant Pink Theme Overhaul */
    .stApp { background-color: #2b0016; color: #ecc4dc; font-family: 'Rajdhani', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; color: #ff007f; text-shadow: 0 0 10px rgba(255,0,127,0.4); margin: 0px; }
    
    /* Neon Position Badges */
    .pos-badge { padding: 2px 6px; border-radius: 4px; font-weight: bold; font-family: 'Orbitron'; font-size: 10px; text-align: center; display: inline-block;}
    .pos-QB { background-color: #ff3366; color: white; box-shadow: 0 0 6px #ff3366; }
    .pos-RB { background-color: #0099ff; color: white; box-shadow: 0 0 6px #0099ff; }
    .pos-WR { background-color: #00cc66; color: white; box-shadow: 0 0 6px #00cc66; }
    .pos-TE { background-color: #ffcc00; color: black; box-shadow: 0 0 6px #ffcc00; }
    .pos-DEF { background-color: #9933ff; color: white; box-shadow: 0 0 6px #9933ff; }
    .pos-K { background-color: #e67e22; color: white; box-shadow: 0 0 6px #e67e22; }
    
    /* Ultra Compact Card Styling */
    .board-card {
        background: linear-gradient(145deg, #420022, #1a000e);
        border: 1px solid #660033;
        border-radius: 6px;
        padding: 4px;
        margin: 2px 0px;
        text-align: center;
    }
    .otc-active { border: 2px solid #ff007f !important; box-shadow: 0 0 12px #ff007f; }
    
    /* Smaller Logos to Save Space */
    .team-logo-img {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 2px;
        border: 1px solid #880044;
    }

    /* Mini Cheat Sheet Rows */
    .cheat-row-meta {
        color: #ecc4dc; 
        font-size: 11px;
        font-family: 'Orbitron';
    }

    /* User Notice Banners */
    .status-banner {
        padding: 10px;
        border-radius: 8px;
        font-family: 'Orbitron';
        font-weight: bold;
        text-align: center;
        margin: 5px 0;
        font-size: 13px;
    }
    .status-otc { background-color: rgba(255, 0, 127, 0.2); border: 1px solid #ff007f; color: #ff007f; }
    .status-next { background-color: rgba(255, 204, 0, 0.15); border: 1px solid #ffcc00; color: #ffcc00; }
    .status-waiting { background-color: rgba(236, 196, 220, 0.1); border: 1px solid #ecc4dc; color: #ecc4dc; }
</style>
""", unsafe_allow_html=True)

# --- TEAM MATRIX ---
TEAM_ASSETS = {
    "Sleeper Cell": {"logo": "https://placehold.co/100x100/420022/ff3366?text=SC", "sound": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"},
    "Phantasm": {"logo": "https://placehold.co/100x100/420022/0099ff?text=PH", "sound": ""},
    "Icelanders": {"logo": "https://placehold.co/100x100/420022/00cc66?text=ICE", "sound": ""},
    "El Nino": {"logo": "https://placehold.co/100x100/420022/ffcc00?text=EN", "sound": ""},
    "Buttheads": {"logo": "https://placehold.co/100x100/420022/9933ff?text=BH", "sound": "https://actions.google.com/sounds/v1/sports/soccer_stadium_whistle.ogg"},
    "Big Boys Big Work": {"logo": "https://placehold.co/100x100/420022/ffffff?text=BB", "sound": ""},
    "Turbo-Ginz": {"logo": "https://placehold.co/100x100/420022/e67e22?text=TG", "sound": ""},
    "Luddite": {"logo": "https://placehold.co/100x100/420022/ff3366?text=LUD", "sound": ""},
    "Achains": {"logo": "https://placehold.co/100x100/420022/0099ff?text=ACH", "sound": ""},
    "Daddy's Dogs": {"logo": "https://placehold.co/100x100/420022/00cc66?text=DDG", "sound": ""},
    "TDs and Beers": {"logo": "https://placehold.co/100x100/420022/ffcc00?text=TD", "sound": ""},
    "DD Riders": {"logo": "https://placehold.co/100x100/420022/9933ff?text=DDR", "sound": ""},
    "Nasty": {"logo": "https://placehold.co/100x100/420022/ffffff?text=NY", "sound": ""},
    "Red Hammer": {"logo": "https://placehold.co/100x100/420022/ff3366?text=RH", "sound": ""},
    "Expansion Team 15": {"logo": "https://placehold.co/100x100/420022/8b949e?text=E15", "sound": ""},
    "Expansion Team 16": {"logo": "https://placehold.co/100x100/420022/8b949e?text=E16", "sound": ""}
}

DEFAULT_HORN = "https://actions.google.com/sounds/v1/alarms/air_horn_so_loud.ogg"
TEAMS_16 = list(TEAM_ASSETS.keys())
TOTAL_REGULAR_ROUNDS = 15
TOTAL_KEEPER_PICKS = 32
TOTAL_ABS_PICKS = TOTAL_KEEPER_PICKS + (TOTAL_REGULAR_ROUNDS * 16)

def trigger_draft_sound(team_name):
    team_sound = TEAM_ASSETS.get(team_name, {}).get("sound", "")
    final_audio_url = team_sound if team_sound else DEFAULT_HORN
    st.markdown(f'<audio src="{final_audio_url}" autoplay></audio>', unsafe_allow_html=True)

FILE_NAME = "_NVFL Draft Sheet 2026.xlsx"

@st.cache_data(ttl=21600)
def fetch_live_adp():
    try:
        url = "https://fantasyfootballcalculator.com/api/v1/adp/ppr?teams=12&year=2026"
        res = requests.get(url, timeout=2) 
        if res.status_code == 200:
            data = res.json()
            players_list = data.get("players", [])
            if players_list:
                df_adp = pd.DataFrame(players_list)
                df_adp['clean_name'] = df_adp['name'].str.lower().str.strip()
                return df_adp[['clean_name', 'adp']]
    except Exception:
        pass
    return None

@st.cache_data
def load_base_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME, sheet_name='PlayerDB')
    else:
        df = pd.DataFrame(columns=['Player', 'Team', 'Pos', 'Bye', 'PPR'])
    
    live_adp = fetch_live_adp()
    if live_adp is not None and not df.empty:
        df['clean_name'] = df['Player'].str.split('–').str[0].str.lower().str.strip()
        df = df.merge(live_adp, on='clean_name', how='left')
        df['PPR'] = df['adp'].fillna(df['PPR'])
        df.drop(columns=['clean_name', 'adp'], errors='ignore', inplace=True)
        
    return df

player_pool = load_base_data()

# Initialize session state variables
if 'custom_draft_order' not in st.session_state:
    order_map = {}
    for abs_pick in range(1, TOTAL_ABS_PICKS + 1):
        if abs_pick <= TOTAL_KEEPER_PICKS:
            idx = (abs_pick - 1) % 16
            order_map[abs_pick] = TEAMS_16[idx]
        else:
            reg_pick_num = abs_pick - TOTAL_KEEPER_PICKS
            round_num = ((reg_pick_num - 1) // 16) + 1
            pick_in_round = (reg_pick_num - 1) % 16
            if round_num % 2 != 0:
                order_map[abs_pick] = TEAMS_16[pick_in_round]
            else:
                order_map[abs_pick] = TEAMS_16[15 - pick_in_round]
    st.session_state.custom_draft_order = order_map

if 'drafted_players' not in st.session_state:
    st.session_state.drafted_players = {}
if 'current_absolute_pick' not in st.session_state:
    st.session_state.current_absolute_pick = 1
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = time.time()
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 90
if 'selected_cheat_player' not in st.session_state:
    st.session_state.selected_cheat_player = ""

def get_draft_metadata(abs_pick):
    assigned_team = st.session_state.custom_draft_order.get(abs_pick, "Unknown")
    if abs_pick <= TOTAL_KEEPER_PICKS:
        k_round = ((abs_pick - 1) // 16) + 1
        return assigned_team, f"Keeper Rd {k_round}", True, abs_pick
    
    reg_pick_num = abs_pick - TOTAL_KEEPER_PICKS
    round_num = ((reg_pick_num - 1) // 16) + 1
    return assigned_team, f"Round {round_num}", False, reg_pick_num

otc_team, round_label, is_keeper_phase, display_pick_num = get_draft_metadata(st.session_state.current_absolute_pick)

# --- ⏱️ INTEGRATED CLOCK & MARTINI HEADER ---
elapsed = int(time.time() - st.session_state.timer_start)
remaining = max(0, st.session_state.time_limit - elapsed)

header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(f"<h1 style='font-size: 26px;'>🍸 NVFL WAR ROOM 2026 🍸</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #ffcc00; font-family: \"Orbitron\"; margin: 0px;'>{round_label.upper()} • {'KEEPER SLOT' if is_keeper_phase else f'PICK {display_pick_num}'} • <b>{otc_team.upper()}</b> IS OTC</p>", unsafe_allow_html=True)

with header_col2:
    if remaining > 0:
        st.markdown(f"<h2 style='text-align: right; color: #ffcc00; font-size: 28px; margin: 0px;'>⏱️ {remaining}s</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: right; color: #ff3366; font-size: 28px; margin: 0px;'>⚠️ EXPIRED</h2>", unsafe_allow_html=True)
    st.progress(min(1.0, float(elapsed / st.session_state.time_limit)))

st.markdown("<hr style='margin: 8px 0px;'>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # 1. USER IDENTITY
    st.markdown("### 👤 User Identity Settings")
    user_team = st.selectbox("Select Your Managed Franchise:", ["Spectator / Commissioner Mode"] + TEAMS_16)
    
    # 2. QUEUE STATUS BANNERS
    if user_team != "Spectator / Commissioner Mode":
        st.markdown("---")
        st.markdown("### 🚦 My Queue Status")
        upcoming_picks = [p_idx for p_idx, t_name in st.session_state.custom_draft_order.items() if t_name == user_team and p_idx >= st.session_state.current_absolute_pick]
        if not upcoming_picks:
            st.markdown('<div class="status-banner status-waiting"> Roster Complete </div>', unsafe_allow_html=True)
        else:
            picks_away = upcoming_picks[0] - st.session_state.current_absolute_pick
            if picks_away == 0:
                st.markdown('<div class="status-banner status-otc">🎉 YOU ARE ON THE CLOCK!</div>', unsafe_allow_html=True)
            elif picks_away == 1:
                st.markdown('<div class="status-banner status-next">🚨 YOU ARE NEXT!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-banner status-waiting">⏳ Drafting in {picks_away} picks.</div>', unsafe_allow_html=True)

    # 3. LIVE PLAYER SUBMISSION INTERFACE
    st.markdown("---")
    st.markdown("### 🚀 Make Your Move")
    
    # Use selected cheat sheet player if available, otherwise clear
    default_search = st.session_state.selected_cheat_player if st.session_state.selected_cheat_player else ""
    search_query = st.text_input("Search or Clicked Player Board Target", value=default_search)
    
    taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
    avail_df = player_pool[~player_pool['Player'].isin(taken_names)] if not player_pool.empty else pd.DataFrame()
    
    if search_query and not avail_df.empty:
        avail_df = avail_df[avail_df['Player'].str.contains(search_query, case=False, na=False)]
        
    if not avail_df.empty:
        target_row = avail_df.iloc[0]
        player_adp = target_row['PPR']
        
        if not is_keeper_phase and pd.notna(player_adp):
            diff = round(display_pick_num - player_adp, 1)
            diff_text = f"+{diff} (Steal)" if diff > 0 else f"{diff} (Reach)"
            st.caption(f"📊 Live Market ADP: **{player_adp}** | Value Diff: **{diff_text}**")
            
        st.success(f"Selected Target: {target_row['Player']} ({target_row['Pos']})")
        if st.button("🔥 SUBMIT BOARD PICK", use_container_width=True):
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
            st.session_state.selected_cheat_player = ""  # Reset lock
            st.rerun()

    # 5. ADMIN UTILITIES (PUSHED TO BOTTOM)
    st.markdown("<br><br><br><hr style='border-top: 1px solid #660033;'>", unsafe_allow_html=True)
    st.markdown("### 🛠️ Administration (Bottom)")
    st.session_state.time_limit = st.number_input("Adjust Clock Speed Limit (Seconds)", min_value=15, max_value=300, value=st.session_state.time_limit, step=15)

    is_admin = st.checkbox("Enable Admin Actions", value=True)
    if is_admin:
        with st.expander("⚙️ Pick Swapper / Trades"):
            pick_a = st.number_input("Pick X", min_value=1, max_value=TOTAL_ABS_PICKS, value=33)
            pick_b = st.number_input("Pick Y", min_value=1, max_value=TOTAL_ABS_PICKS, value=34)
            if st.button("🔄 Swap Ownership Slots"):
                st.session_state.custom_draft_order[pick_a], st.session_state.custom_draft_order[pick_b] = st.session_state.custom_draft_order[pick_b], st.session_state.custom_draft_order[pick_a]
                st.success("Swapped!")
                st.rerun()
                
        if st.session_state.current_absolute_pick > 1:
            if st.button("⏪ UNDO LAST PICK", use_container_width=True):
                last_pick = st.session_state.current_absolute_pick - 1
                if last_pick in st.session_state.drafted_players:
                    del st.session_state.drafted_players[last_pick]
                st.session_state.current_absolute_pick = last_pick
                st.session_state.timer_start = time.time()
                st.rerun()

# --- TABS INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Draft Matrix Board", "📋 Interactive Cheat Sheets", "🏆 Team Rosters", "📋 Live Drafted Breakdown"])

with tab1:
    st.markdown("### 🔐 Pre-Draft Keeper Phase")
    for kr in [1, 2]:
        st.markdown(f"**Keeper Round {kr}**")
        k_cols = st.columns(16)
        for i in range(1, 17):
            k_abs_pick = ((kr - 1) * 16) + i
            k_team, _, _, _ = get_draft_metadata(k_abs_pick)
            k_logo = TEAM_ASSETS.get(k_team, {}).get("logo", "")
            
            if k_abs_pick in st.session_state.drafted_players:
                p_data = st.session_state.drafted_players[k_abs_pick]
                p_pos = p_data['Pos']
                k_cols[i-1].markdown(f"""
                <div class="board-card board-card-{p_pos}">
                    <img class="team-logo-img" src="{k_logo}"><br>
                    <strong style="color: white; font-size: 10px;">{p_data['Player'].split('–')[0][:7]}</strong><br>
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
                    <small style="color: #ecc4dc; font-size:9px;">{k_team[:5]}</small>
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
                    <small style="color: #ecc4dc; font-size: 8px;">Pk {reg_pick_offset}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: white; font-size: 10px;">{pick_data['Player'].split('–')[0][:7]}</strong><br>
                </div>
                """, unsafe_allow_html=True)
            else:
                is_otc = (calc_abs_pick == st.session_state.current_absolute_pick)
                card_style = "board-card otc-active" if is_otc else "board-card"
                opacity = "1.0" if is_otc else "0.4"
                
                cols[i-1].markdown(f"""
                <div class="{card_style}" style="opacity: {opacity};">
                    <small style="color: #ecc4dc; font-size: 8px;">Pk {reg_pick_offset}</small><br>
                    <img class="team-logo-img" src="{team_logo}"><br>
                    <strong style="color: #ecc4dc; font-size: 9px;">{display_team[:5]}</strong>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📋 Click a Player Name to Stage & Draft Instantly")
    
    taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
    
    if not player_pool.empty:
        remaining_players = player_pool[~player_pool['Player'].isin(taken_names)].sort_values(by='PPR', ascending=True)
        pos_cols = st.columns(5)
        positions_list = ["QB", "RB", "WR", "TE", "DEF_K"]
        
        for idx, pos_group in enumerate(positions_list):
            with pos_cols[idx]:
                if pos_group == "DEF_K":
                    st.markdown("#### 🛡️/🦶 DEF & K")
                    pos_df = remaining_players[remaining_players['Pos'].isin(["DEF", "K"])].head(20)
                else:
                    badge_style = f"pos-{pos_group}"
                    st.markdown(f"#### <span class='pos-badge {badge_style}'>{pos_group}</span>", unsafe_allow_html=True)
                    pos_df = remaining_players[remaining_players['Pos'] == pos_group].head(20)
                    
                if not pos_df.empty:
                    for _, row in pos_df.iterrows():
                        p_full_name = row['Player']
                        p_short_name = p_full_name.split('–')[0]
                        adp_val = f"ADP: {round(row['PPR'], 1)}" if pd.notna(row['PPR']) else f"B: {row['Bye']}"
                        
                        # Clickable selection button mechanics
                        if st.button(f"➕ {p_short_name}", key=f"btn-{p_full_name}-{idx}"):
                            st.session_state.selected_cheat_player = p_full_name
                            st.rerun()
                        st.markdown(f"<span class='cheat-row-meta'>{adp_val} ({row['Team']})</span><hr style='margin:3px 0;'>", unsafe_allow_html=True)
                else:
                    st.write("*Empty*")

with tab3:
    st.subheader("Team Franchise Rosters")
    t_cols = st.columns(4)
    for idx, t in enumerate(TEAMS_16):
        with t_cols[idx % 4]:
            t_logo = TEAM_ASSETS.get(t, {}).get("logo", "")
            st.markdown(f"##### <img src='{t_logo}' style='width:20px; border-radius:50%; vertical-align:middle;'> {t}", unsafe_allow_html=True)
            
            t_picks = [p for p in st.session_state.drafted_players.values() if p['DraftedBy'] == t]
            if t_picks:
                for tp in t_picks:
                    lbl = "🔒 " if tp.get('IsKeeper') else ""
                    st.markdown(f"• {lbl}**{tp['Player'].split('–')[0]}** <span class='pos-badge pos-{tp['Pos']}'>{tp['Pos']}</span>", unsafe_allow_html=True)
            else:
                st.write("*Roster Empty*")

with tab4:
    st.markdown("### 📋 Drafted Player Log By Position")
    if st.session_state.drafted_players:
        dp_df = pd.DataFrame(st.session_state.drafted_players.values())
        d_cols = st.columns(5)
        d_positions = ["QB", "RB", "WR", "TE", "DEF_K"]
        
        for idx, pos_group in enumerate(d_positions):
            with d_cols[idx]:
                st.markdown(f"#### Log: {pos_group}")
                if pos_group == "DEF_K":
                    sub_dp = dp_df[dp_df['Pos'].isin(["DEF", "K"])]
                else:
                    sub_dp = dp_df[dp_df['Pos'] == pos_group]
                    
                if not sub_dp.empty:
                    for _, row in sub_dp.iterrows():
                        lbl = "[K] " if row.get('IsKeeper') else ""
                        st.markdown(f"🏈 {lbl}**{row['Player'].split('–')[0]}** ({row['Team']})<br><small style='color: #ff007f;'>Drafted by: {row['DraftedBy'][:10]}</small><hr style='margin:4px 0;'>", unsafe_allow_html=True)
                else:
                    st.caption("*None drafted yet*")
    else:
        st.info("No players drafted yet in this league run.")
