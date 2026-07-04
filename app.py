import streamlit as st
import pandas as pd
import os
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="NVFL War Room 2026", layout="wide", initial_sidebar_state="expanded")

# --- SPREADSHEET-STYLE ULTRA-COMPACT PINK CSS ---
st.markdown("""
<style>
    .stApp { 
        background-color: #1f0010; 
        color: #f0dbf4; 
        font-family: 'Segoe UI', -apple-system, Arial, sans-serif; 
    }
    h1, h2, h3, h4, b, strong { 
        font-family: 'Segoe UI', Arial, sans-serif; 
        color: #ff3399; 
        margin: 0px; 
        padding: 0px;
    }
    .board-card {
        background: #2b0018;
        border: 1px solid #4a002a;
        border-radius: 2px;
        padding: 4px 6px;
        margin: 1px 0px;
        font-size: 12px;
        line-height: 1.2;
    }
    .rec-card {
        background: #380020;
        border: 1px solid #ff3399;
        border-radius: 2px;
        padding: 6px 10px;
        margin: 4px 0px;
        font-size: 12px;
    }
    .pos-badge { 
        padding: 1px 4px; 
        border-radius: 2px; 
        font-weight: bold; 
        font-size: 10px; 
        text-align: center; 
        display: inline-block;
        color: white;
    }
    .pos-QB { background-color: #d62828; }
    .pos-RB { background-color: #0077b6; }
    .pos-WR { background-color: #2b9348; }
    .pos-TE { background-color: #cc9900; color: black; }
    .pos-DEF { background-color: #6a0dad; }
    .pos-K { background-color: #e65c00; }
    
    .cheat-row {
        border-bottom: 1px solid #3d0022;
        padding: 2px 0px;
        font-size: 12px;
    }
    .cheat-row-meta {
        color: #b589a6; 
        font-size: 11px;
    }
    .status-banner {
        padding: 6px;
        border-radius: 2px;
        font-weight: bold;
        text-align: center;
        margin: 4px 0;
        font-size: 12px;
    }
    .status-otc { background-color: #ff3399; color: white; }
    .status-next { background-color: #cc9900; color: black; }
    .status-waiting { background-color: #4a002a; color: #f0dbf4; border: 1px solid #66003b; }
    
    .stButton>button {
        padding: 2px 8px !important;
        font-size: 12px !important;
        border-radius: 2px !important;
        margin-top: 2px !important;
    }
    .stTextInput>div>div>input {
        padding: 4px !important;
        font-size: 12px !important;
        border-radius: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DEFAULT TEAM LIST (14 TEAMS) ---
DEFAULT_14_TEAMS = [
    "Sleeper Cell", "Phantasm", "Icelanders", "El Nino", "Buttheads", 
    "Big Boys Big Work", "Turbo-Ginz", "Luddite", "Achains", "Daddy's Dogs", 
    "TDs and Beers", "DD Riders", "Nasty", "Red Hammer"
]

DEFAULT_HORN = "https://actions.google.com/sounds/v1/alarms/air_horn_so_loud.ogg"
TOTAL_REGULAR_ROUNDS = 15
TOTAL_KEEPER_PICKS = 28  # 2 rounds * 14 teams
TOTAL_ABS_PICKS = TOTAL_KEEPER_PICKS + (TOTAL_REGULAR_ROUNDS * 14)

def trigger_draft_sound():
    st.markdown(f'<audio src="{DEFAULT_HORN}" autoplay></audio>', unsafe_allow_html=True)

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

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### ⚙️ [A] Draft Settings (14-Team Snake)")
    
    # Expandable manager to rename the 14 structural teams
    with st.expander("Edit 14 Team Names Lineup"):
        teams_14 = []
        for i in range(14):
            default_val = DEFAULT_14_TEAMS[i] if i < len(DEFAULT_14_TEAMS) else f"Team {i+1}"
            t_name = st.text_input(f"Pick Slot #{i+1}", value=default_val, key=f"cfg_team_{i}")
            teams_14.append(t_name if t_name.strip() else f"Team {i+1}")

    # Re-calculate the master multi-phase matrix dynamically if configurations change
    order_map = {}
    for abs_pick in range(1, TOTAL_ABS_PICKS + 1):
        if abs_pick <= TOTAL_KEEPER_PICKS:
            idx = (abs_pick - 1) % 14
            order_map[abs_pick] = teams_14[idx]
        else:
            reg_pick_num = abs_pick - TOTAL_KEEPER_PICKS
            round_num = ((reg_pick_num - 1) // 14) + 1
            pick_in_round = (reg_pick_num - 1) % 14
            if round_num % 2 != 0:
                order_map[abs_pick] = teams_14[pick_in_round]
            else:
                order_map[abs_pick] = teams_14[14 - 1 - pick_in_round]
                
    st.session_state.custom_draft_order = order_map

    st.markdown("---")
    st.markdown("### 👤 [B] Client Settings")
    user_team = st.selectbox("Franchise Context Identity:", ["Spectator / Commissioner Mode"] + teams_14)

    if 'drafted_players' not in st.session_state:
        st.session_state.drafted_players = {}
    if 'current_absolute_pick' not in st.session_state:
        st.session_state.current_absolute_pick = 1
    if 'selected_cheat_player' not in st.session_state:
        st.session_state.selected_cheat_player = ""

    def get_draft_metadata(abs_pick):
        assigned_team = st.session_state.custom_draft_order.get(abs_pick, "Unknown")
        if abs_pick <= TOTAL_KEEPER_PICKS:
            k_round = ((abs_pick - 1) // 14) + 1
            return assigned_team, f"Keeper Rd {k_round}", True, abs_pick
        
        reg_pick_num = abs_pick - TOTAL_KEEPER_PICKS
        round_num = ((reg_pick_num - 1) // 14) + 1
        return assigned_team, f"Round {round_num}", False, reg_pick_num

    otc_team, round_label, is_keeper_phase, display_pick_num = get_draft_metadata(st.session_state.current_absolute_pick)
    can_draft = (user_team == "Spectator / Commissioner Mode") or (user_team == otc_team)
    
    if user_team != "Spectator / Commissioner Mode":
        upcoming_picks = [p_idx for p_idx, t_name in st.session_state.custom_draft_order.items() if t_name == user_team and p_idx >= st.session_state.current_absolute_pick]
        if not upcoming_picks:
            st.markdown('<div class="status-banner status-waiting">Roster Full</div>', unsafe_allow_html=True)
        else:
            picks_away = upcoming_picks[0] - st.session_state.current_absolute_pick
            if picks_away == 0:
                st.markdown('<div class="status-banner status-otc">YOUR PICK NOW</div>', unsafe_allow_html=True)
            elif picks_away == 1:
                st.markdown('<div class="status-banner status-next">YOU ARE NEXT</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-banner status-waiting">Drafting in {picks_away} picks</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⌨️ [C] Command Console")
    
    default_search = st.session_state.selected_cheat_player if st.session_state.selected_cheat_player else ""
    search_query = st.text_input("Active Target Lookup", value=default_search)
    
    taken_names = [p['Player'] for p in st.session_state.drafted_players.values()]
    avail_df = player_pool[~player_pool['Player'].isin(taken_names)] if not player_pool.empty else pd.DataFrame()
    
    if search_query and not avail_df.empty:
        avail_df = avail_df[avail_df['Player'].str.contains(search_query, case=False, na=False)]
        
    if not avail_df.empty:
        avail_df = avail_df.sort_values(by='PPR', ascending=True)
        target_row = avail_df.iloc[0]
        player_adp = target_row['PPR']
        
        if not is_keeper_phase and pd.notna(player_adp):
            diff = round(display_pick_num - player_adp, 1)
            diff_text = f"+{diff} Value" if diff > 0 else f"{diff} Reach"
            st.caption(f"ADP: {player_adp} | ({diff_text})")
            
        st.info(f"Target: {target_row['Player']} ({target_row['Pos']})")
        if not can_draft:
            st.warning("Locked out: OTC Turn mismatch.")
        else:
            if st.button("EXECUTE DRAFT SELECTION", use_container_width=True):
                st.session_state.drafted_players[st.session_state.current_absolute_pick] = {
                    "Player": target_row['Player'],
                    "Pos": target_row['Pos'],
                    "Team": target_row['Team'],
                    "DraftedBy": otc_team,
                    "IsKeeper": is_keeper_phase
                }
                trigger_draft_sound()
                st.session_state.current_absolute_pick += 1
                st.session_state.selected_cheat_player = ""  
                st.rerun()

    st.markdown("<br><br><hr style='border-color: #4a002a;'>", unsafe_allow_html=True)
    st.markdown("### ⏪ [D] Overrides")
    
    if st.session_state.current_absolute_pick > 1:
        if st.button("ROLLBACK LAST PICK", use_container_width=True):
            last_pick = st.session_state.current_absolute_pick - 1
            if last_pick in st.session_state.drafted_players:
                del st.session_state.drafted_players[last_pick]
            st.session_state.current_absolute_pick = last_pick
            st.rerun()

# --- SPREADSHEET HEAD OVERVIEW ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(f"<h1 style='font-size: 20px; font-weight: 700; letter-spacing: -0.5px;'>🍸 NVFL WAR ROOM 2026</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #cc9900; font-size: 12px; margin: 0px;'>{round_label.upper()} • {'KEEPER PHASE' if is_keeper_phase else f'PICK {display_pick_num}'} • OTC: <b>{otc_team.upper()}</b></p>", unsafe_allow_html=True)

with header_col2:
    if os.path.exists("stare.png"):
        st.image("stare.png", width=120)

st.markdown("<hr style='margin: 6px 0px; border-color: #4a002a;'>", unsafe_allow_html=True)

# --- WORKSPACE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🎯 My Team Dashboard", "📋 Interactive Cheat Sheets", "🏆 League Rosters", "📋 Live Drafted Breakdown"])

with tab1:
    active_dashboard_team = user_team if user_team != "Spectator / Commissioner Mode" else otc_team
    st.markdown(f"#### Roster Worksheet: {active_dashboard_team.upper()}")
    
    st.markdown("<p style='font-size:12px; font-weight:bold; color:#ff3399; margin-top:8px;'>🎯 RECOMMENDED AVAILABLE OPTIONS (SORTED BEST TO WORST)</p>", unsafe_allow_html=True)
    if not player_pool.empty:
        rec_pool = player_pool[~player_pool['Player'].isin(taken_names)].sort_values(by='PPR', ascending=True).head(3)
        if not rec_pool.empty:
            rec_cols = st.columns(3)
            for r_idx, (_, r_player) in enumerate(rec_pool.iterrows()):
                with rec_cols[r_idx]:
                    p_name_short = r_player['Player'].split('–')[0]
                    st.markdown(f"""
                    <div class="rec-card">
                        <b>RANK #{r_idx+1}: {p_name_short}</b> <span class="pos-badge pos-{r_player['Pos']}">{r_player['Pos']}</span><br>
                        <span class="cheat-row-meta">ADP: {round(r_player['PPR'], 1)} | NFL: {r_player['Team']} | Bye: {r_player['Bye']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if can_draft:
                        if st.button(f"⚡ Queue #{r_idx+1}", key=f"rec-queue-{r_idx}"):
                            st.session_state.selected_cheat_player = r_player['Player']
                            st.rerun()
        else:
            st.caption("No recommendations left.")
            
    st.markdown("<hr style='border-color: #4a002a; margin: 10px 0px;'>", unsafe_allow_html=True)
    
    my_selections = [p for p in st.session_state.drafted_players.values() if p['DraftedBy'] == active_dashboard_team]
    dash_col1, dash_col2 = st.columns([1, 2])
    
    with dash_col1:
        st.markdown("<p style='font-size:12px; font-weight:bold;'>Matrix Cell Allocations</p>", unsafe_allow_html=True)
        counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "DEF": 0, "K": 0}
        for p in my_selections:
            if p['Pos'] in counts:
                counts[p['Pos']] += 1
        for pos, cnt in counts.items():
            st.markdown(f"• **{pos}:** `{cnt}`")
        st.markdown(f"**Total Elements:** `{len(my_selections)}`")
        
    with dash_col2:
        st.markdown("<p style='font-size:12px; font-weight:bold;'>Franchise Line Entries</p>", unsafe_allow_html=True)
        if my_selections:
            for p in my_selections:
                lbl = "[KEEPER] " if p.get('IsKeeper') else ""
                st.markdown(f"""
                <div class="board-card">
                    {lbl}<b>{p['Player'].split('–')[0]}</b> | {p['Team']} <span class="pos-badge pos-{p['Pos']}">{p['Pos']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No row entries compiled yet.")

with tab2:
    st.markdown("<p style='font-size:12px; color:#b589a6; margin-bottom:8px;'>Click name token cell to instantly sync player choice.</p>", unsafe_allow_html=True)
    
    if not player_pool.empty:
        remaining_players = player_pool[~player_pool['Player'].isin(taken_names)].sort_values(by='PPR', ascending=True)
        pos_cols = st.columns(5)
        positions_list = ["QB", "RB", "WR", "TE", "DEF_K"]
        
        for idx, pos_group in enumerate(positions_list):
            with pos_cols[idx]:
                if pos_group == "DEF_K":
                    st.markdown("💬 **DEF / K**")
                    pos_df = remaining_players[remaining_players['Pos'].isin(["DEF", "K"])].head(30)
                else:
                    st.markdown(f"💬 **{pos_group}**")
                    pos_df = remaining_players[remaining_players['Pos'] == pos_group].head(30)
                    
                if not pos_df.empty:
                    for _, row in pos_df.iterrows():
                        p_full_name = row['Player']
                        p_short_name = p_full_name.split('–')[0]
                        adp_val = f"ADP:{round(row['PPR'], 1)}" if pd.notna(row['PPR']) else f"B:{row['Bye']}"
                        
                        if can_draft:
                            if st.button(f"📄 {p_short_name[:15]}", key=f"btn-{p_full_name}-{idx}", use_container_width=True):
                                st.session_state.selected_cheat_player = p_full_name
                                st.rerun()
                        else:
                            st.button(f"🔒 {p_short_name[:15]}", key=f"btn-{p_full_name}-{idx}", disabled=True, use_container_width=True)
                            
                        st.markdown(f"<div class='cheat-row'><span class='cheat-row-meta'>{adp_val} | {row['Team']} | {row['Pos']}</span></div>", unsafe_allow_html=True)
                else:
                    st.caption("Empty cell block.")

with tab3:
    st.subheader("Master League Roster Grid")
    t_cols = st.columns(4)
    for idx, t in enumerate(teams_14):
        with t_cols[idx % 4]:
            st.markdown(f"📝 **{t}**")
            t_picks = [p for p in st.session_state.drafted_players.values() if p['DraftedBy'] == t]
            if t_picks:
                for tp in t_picks:
                    lbl = "[K] " if tp.get('IsKeeper') else ""
                    st.markdown(f"<div style='font-size:12px;'>• {lbl}{tp['Player'].split('–')[0]} <span class='pos-badge pos-{tp['Pos']}'>{tp['Pos']}</span></div>", unsafe_allow_html=True)
            else:
                st.caption("No elements.")

with tab4:
    st.markdown("### Positional Run Log Worksheet")
    if st.session_state.drafted_players:
        dp_df = pd.DataFrame(st.session_state.drafted_players.values())
        d_cols = st.columns(5)
        d_positions = ["QB", "RB", "WR", "TE", "DEF_K"]
        
        for idx, pos_group in enumerate(d_positions):
            with d_cols[idx]:
                st.markdown(f"**Log: {pos_group}**")
                if pos_group == "DEF_K":
                    sub_dp = dp_df[dp_df['Pos'].isin(["DEF", "K"])]
                else:
                    sub_dp = dp_df[dp_df['Pos'] == pos_group]
                    
                if not sub_dp.empty:
                    for _, row in sub_dp.iterrows():
                        lbl = "[K] " if row.get('IsKeeper') else ""
                        st.markdown(f"<div class='cheat-row'><b>{lbl}{row['Player'].split('–')[0]}</b> ({row['Team']})<br><span style='font-size:10px; color:#ff3399;'>Mgr: {row['DraftedBy'][:10]}</span></div>", unsafe_allow_html=True)
                else:
                    st.caption("Empty cell entry.")
    else:
        st.caption("No rows drafted yet.")
