import streamlit as st
import sqlite3
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import urllib.parse

st.set_page_config(
    page_title="Music Identifier",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── MAIN BG ── */
.stApp { background: #f0f2f8 !important; }
.main .block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.2) !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

/* Collapse button styling */
[data-testid="collapsedControl"] {
    background: #4f46e5 !important;
    border-radius: 0 12px 12px 0 !important;
    color: white !important;
    top: 50% !important;
}
[data-testid="stSidebarCollapsedControl"] svg { color: white !important; fill: white !important; }

.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 20px;
}
.sidebar-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #818cf8, #6366f1);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 1.3rem;
    box-shadow: 0 4px 12px rgba(99,102,241,0.5);
}
.sidebar-logo-text {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.3rem; font-weight: 800; color: #ffffff !important;
    letter-spacing: -0.5px;
}

.sidebar-section {
    font-size: 0.6rem; font-weight: 700; color: rgba(255,255,255,0.4) !important;
    letter-spacing: 3px; text-transform: uppercase; margin: 20px 0 12px;
}

/* 2x2 stats grid */
.stats-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;
}
.stat-cell {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px; padding: 12px 10px; text-align: center;
    backdrop-filter: blur(10px);
}
.stat-cell-num {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.3rem; font-weight: 800; color: #ffffff !important;
    display: block; line-height: 1.1;
}
.stat-cell-lbl {
    font-size: 0.62rem; color: rgba(255,255,255,0.5) !important;
    text-transform: uppercase; letter-spacing: 1px; margin-top: 3px; display: block;
}

.sidebar-nav-btn {
    display: flex; align-items: center; gap: 10px;
    padding: 11px 14px; border-radius: 10px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.8) !important;
    font-size: 0.9rem; font-weight: 500; margin-bottom: 8px; cursor: pointer;
    transition: all 0.2s;
}
.sidebar-nav-btn.active {
    background: linear-gradient(135deg, #818cf8, #6366f1) !important;
    border-color: transparent !important; color: white !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4) !important;
}

/* ── PAGE HEADER ── */
.page-header {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    border-radius: 20px; padding: 32px 36px; margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(99,102,241,0.3);
    display: flex; align-items: center; justify-content: space-between;
}
.page-header-left h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem; font-weight: 800; color: white; margin: 0 0 6px;
}
.page-header-left p { color: rgba(255,255,255,0.75); margin: 0; font-size: 0.95rem; }
.page-header-icon { font-size: 4rem; opacity: 0.3; }

/* ── MODE CARDS ── */
.mode-card {
    background: white; border-radius: 16px; padding: 28px 24px;
    border: 2px solid #e8eaf6; text-align: center; cursor: pointer;
    transition: all 0.2s; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    height: 130px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.mode-card.active {
    border-color: #6366f1; background: linear-gradient(135deg, #eef2ff, #f5f3ff);
    box-shadow: 0 8px 25px rgba(99,102,241,0.2);
}
.mode-card h3 { color: #1e1b4b; margin: 0 0 6px; font-size: 1.1rem; font-weight: 700; }
.mode-card p  { color: #6b7280; font-size: 0.82rem; margin: 0; }
.mode-card.active h3 { color: #4f46e5; }

/* ── RESULT CARD ── */
.result-card {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 20px; padding: 32px 36px; margin: 20px 0;
    box-shadow: 0 12px 40px rgba(99,102,241,0.35);
    position: relative; overflow: hidden;
}
.result-card::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 180px; height: 180px; background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.result-label { font-size: 0.65rem; color: rgba(255,255,255,0.6); letter-spacing: 4px; text-transform: uppercase; margin-bottom: 8px; }
.result-song  { font-family: 'Space Grotesk', sans-serif !important; font-size: 2.2rem; font-weight: 800; color: white; margin-bottom: 8px; line-height: 1.1; }
.result-meta  { font-size: 0.85rem; color: rgba(255,255,255,0.65); }
.result-meta b { color: #a5f3fc; }
.result-time  { display: inline-block; margin-top: 10px; background: rgba(255,255,255,0.15); padding: 5px 14px; border-radius: 20px; font-size: 0.85rem; color: white; font-weight: 600; }
.yt-btn {
    display: inline-block; margin-top: 14px; margin-left: 10px;
    background: white; color: #4f46e5 !important; text-decoration: none !important;
    padding: 9px 20px; border-radius: 20px; font-size: 0.82rem; font-weight: 700;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* ── CANDIDATE ROWS ── */
.cand-row {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 16px; border-radius: 12px;
    background: white; margin-bottom: 8px;
    border: 1px solid #e8eaf6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.15s;
}
.cand-row:hover { transform: translateX(4px); border-color: #c7d2fe; }
.cand-rank { font-size: 0.75rem; color: #9ca3af; width: 24px; font-weight: 700; }
.cand-name { color: #1e1b4b; font-size: 0.9rem; font-weight: 600; flex: 1; }
.cand-score{ color: #6366f1; font-size: 0.85rem; font-weight: 700;
             background: #eef2ff; padding: 3px 10px; border-radius: 10px; }

/* ── SECTION HEADER ── */
.sec-hdr {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem; font-weight: 700; color: #1e1b4b;
    border-left: 4px solid #6366f1; padding-left: 12px;
    margin: 24px 0 14px;
}

/* ── METRIC CARDS ── */
[data-testid="metric-container"] {
    background: white !important; border-radius: 14px !important;
    border: 1px solid #e8eaf6 !important; padding: 18px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 0.75rem !important; font-weight: 600 !important; letter-spacing: 1px; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #1e1b4b !important; font-size: 1.6rem !important; font-weight: 800 !important; font-family: 'Space Grotesk', sans-serif !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: white !important; border-radius: 12px !important;
    padding: 4px !important; gap: 4px !important; border: 1px solid #e8eaf6 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #6b7280 !important;
    border-radius: 8px !important; font-size: 0.85rem !important; font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 1rem !important; }

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 0.9rem !important; padding: 11px 24px !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.45) !important;
}

/* ── BATCH CARDS ── */
.batch-match {
    background: white; border: 1px solid #e8eaf6; border-radius: 14px;
    padding: 18px 20px; margin-bottom: 6px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.batch-filename { font-size: 0.75rem; color: #9ca3af; margin-bottom: 3px; }
.batch-songname { font-size: 1.1rem; font-weight: 700; color: #1e1b4b; }
.batch-time { display: inline-block; margin-top: 6px; background: #dcfce7; color: #166534; padding: 3px 12px; border-radius: 10px; font-size: 0.78rem; font-weight: 600; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: white !important; border-radius: 14px !important;
    border: 2px dashed #c7d2fe !important; padding: 8px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }

/* ── DIVIDER ── */
hr { border-color: #e8eaf6 !important; margin: 1.5rem 0 !important; }

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; border-radius: 4px !important; }

/* ── ALERTS ── */
.stSuccess { background: #f0fdf4 !important; border-color: #86efac !important; color: #166534 !important; border-radius: 10px !important; }
.stWarning { background: #fffbeb !important; border-color: #fcd34d !important; border-radius: 10px !important; }
.stInfo    { background: #eff6ff !important; border-color: #93c5fd !important; border-radius: 10px !important; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: white !important; border-radius: 12px !important;
    border: 1px solid #e8eaf6 !important; font-weight: 600 !important; color: #1e1b4b !important;
}

/* ── INPUT ── */
.stTextInput input, .stSelectbox select {
    background: white !important; border-radius: 8px !important;
    border: 1px solid #e8eaf6 !important; color: #1e1b4b !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════
@st.cache_resource
def get_db_connection():
    try:
        return sqlite3.connect("music_database.db", check_same_thread=False)
    except:
        return None

@st.cache_resource
def get_db_stats():
    conn = get_db_connection()
    if conn is None:
        return 0, 0, 0, 0
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT song_name) FROM hashes")
        num_songs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM (SELECT DISTINCT f1,f2,delta_t FROM hashes)")
        unique_hashes = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hashes")
        total_entries = cur.fetchone()[0]
        db_size = os.path.getsize("music_database.db")/1024/1024 if os.path.exists("music_database.db") else 0
        return num_songs, unique_hashes, total_entries, db_size
    except:
        return 0, 0, 0, 0

# ═══════════════════════════════════════════════
# IDENTIFY (unchanged logic)
# ═══════════════════════════════════════════════
def identify_query_clip_sqlite(query_audio_path, conn):
    from fingerprint import fingerprint_audio_file
    query_hashes, metadata = fingerprint_audio_file(query_audio_path)
    cursor = conn.cursor()
    song_offset_matches = {}

    for hash_key, q_timestamps in query_hashes.items():
        f1, f2, dt = hash_key
        cursor.execute(
            "SELECT DISTINCT song_name, t1_anchor_time FROM hashes WHERE f1=? AND f2=? AND delta_t=?",
            (int(f1), int(f2), round(dt, 3))
        )
        for song_name, db_t1 in cursor.fetchall():
            if song_name not in song_offset_matches:
                song_offset_matches[song_name] = []
            for q_t1 in q_timestamps:
                song_offset_matches[song_name].append(round(db_t1 - q_t1, 2))

    best_song, highest_peak, best_offsets, match_counts, best_offset_val = \
        "Unknown / No Match", 0, [], {}, None

    for song_name, offsets in song_offset_matches.items():
        if not offsets: continue
        match_counts[song_name] = len(offsets)
        counts, bin_edges = np.histogram(offsets, bins=np.arange(min(offsets)-1, max(offsets)+1, 0.5))
        peak = int(np.max(counts))
        if peak > highest_peak:
            highest_peak   = peak
            best_song      = song_name
            best_offsets   = offsets
            best_offset_val = float(bin_edges[int(np.argmax(counts))])

    return best_song, highest_peak, best_offsets, match_counts, metadata, best_offset_val

# ═══════════════════════════════════════════════
# PLOT HELPERS
# ═══════════════════════════════════════════════
def make_fig():
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8f9ff')
    for sp in ax.spines.values(): sp.set_edgecolor('#e8eaf6')
    ax.tick_params(colors='#6b7280')
    ax.xaxis.label.set_color('#6b7280')
    ax.yaxis.label.set_color('#6b7280')
    ax.title.set_color('#1e1b4b')
    return fig, ax

def plot_spectrogram(metadata, title="Spectrogram"):
    fig, ax = make_fig()
    im = ax.imshow(metadata['spectrogram'], aspect='auto', origin='lower', cmap='plasma',
                   extent=[metadata['times'][0], metadata['times'][-1],
                           metadata['frequencies'][0], metadata['frequencies'][-1]])
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Frequency (Hz)"); ax.set_title(title, fontweight='bold')
    cb = plt.colorbar(im, ax=ax); cb.set_label("dB", color='#6b7280'); cb.ax.tick_params(colors='#6b7280')
    plt.tight_layout(); return fig

def plot_constellation(metadata, title="Constellation Map"):
    fig, ax = make_fig()
    pt, pf = metadata['peak_times'], metadata['peak_freqs']
    if len(pt) > 0:
        ax.scatter(pt, pf, s=14, color='#6366f1', alpha=0.75, edgecolors='#4f46e5', linewidths=0.3)
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Frequency (Hz)")
    ax.set_title(f"{title} — {len(pt)} peaks", fontweight='bold')
    ax.grid(True, alpha=0.15, color='#e8eaf6')
    plt.tight_layout(); return fig

def plot_histogram(offsets, song_name):
    fig, ax = make_fig()
    if offsets:
        ax.hist(offsets, bins=50, color='#8b5cf6', edgecolor='#6366f1', alpha=0.8)
    ax.set_xlabel("Time Offset (s)"); ax.set_ylabel("Matching Hashes")
    ax.set_title(f"Offset Histogram — {song_name}", fontweight='bold')
    ax.grid(True, alpha=0.15, color='#e8eaf6', axis='y')
    plt.tight_layout(); return fig

# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════
num_songs, unique_hashes, total_entries, db_size = get_db_stats()

if "mode" not in st.session_state:
    st.session_state.mode = "Single"

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎵</div>
        <div class="sidebar-logo-text">SongID</div>
    </div>
    <div class="sidebar-section">Database Stats</div>
    """, unsafe_allow_html=True)

    # 2×2 stats grid
    uh_display = f"{unique_hashes/1000:.0f}K" if unique_hashes >= 1000 else str(unique_hashes)
    te_display = f"{total_entries/1000:.0f}K" if total_entries >= 1000 else str(total_entries)
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-cell">
            <span class="stat-cell-num">{num_songs}</span>
            <span class="stat-cell-lbl">Songs</span>
        </div>
        <div class="stat-cell">
            <span class="stat-cell-num">{uh_display}</span>
            <span class="stat-cell-lbl">Uniq Hashes</span>
        </div>
        <div class="stat-cell">
            <span class="stat-cell-num">{te_display}</span>
            <span class="stat-cell-lbl">Total Entries</span>
        </div>
        <div class="stat-cell">
            <span class="stat-cell-num">{db_size:.1f}MB</span>
            <span class="stat-cell-lbl">DB Size</span>
        </div>
    </div>
    <div class="sidebar-section">Navigation</div>
    """, unsafe_allow_html=True)

    single_active = "active" if st.session_state.mode == "Single" else ""
    batch_active  = "active" if st.session_state.mode == "Batch"  else ""

    st.markdown(f'<div class="sidebar-nav-btn {single_active}">🎧 &nbsp; Single Clip</div>', unsafe_allow_html=True)
    if st.button("Go to Single Clip", key="nav_single", use_container_width=True):
        st.session_state.mode = "Single"; st.rerun()

    st.markdown(f'<div class="sidebar-nav-btn {batch_active}">📂 &nbsp; Batch Mode</div>', unsafe_allow_html=True)
    if st.button("Go to Batch Mode", key="nav_batch", use_container_width=True):
        st.session_state.mode = "Batch"; st.rerun()

# ═══════════════════════════════════════════════
# DB CHECK
# ═══════════════════════════════════════════════
db_conn = get_db_connection()
if db_conn is None:
    st.error("❌ music_database.db not found. Run build_database_sqlite.py first.")
    st.stop()

# ═══════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <div class="page-header-left">
        <h1>🎵 Music Identifier</h1>
        <p>Identify songs using spectrogram fingerprinting — SQLite powered</p>
    </div>
    <div class="page-header-icon">🎶</div>
</div>
""", unsafe_allow_html=True)

# ── Mode cards ──
col1, col2 = st.columns(2)
with col1:
    is_s = st.session_state.mode == "Single"
    st.markdown(f'<div class="mode-card {"active" if is_s else ""}"><h3>🎧 Single Clip</h3><p>Identify a single song using fast fingerprint matching.</p></div>', unsafe_allow_html=True)
    st.write("")
    if st.button("Activate Single Mode", use_container_width=True, key="btn_single"):
        st.session_state.mode = "Single"; st.rerun()

with col2:
    is_b = st.session_state.mode == "Batch"
    st.markdown(f'<div class="mode-card {"active" if is_b else ""}"><h3>📂 Batch Mode</h3><p>Process and catalog multiple audio files at once.</p></div>', unsafe_allow_html=True)
    st.write("")
    if st.button("Activate Batch Mode", use_container_width=True, key="btn_batch"):
        st.session_state.mode = "Batch"; st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════
# SINGLE CLIP MODE
# ═══════════════════════════════════════════════
if st.session_state.mode == "Single":
    st.markdown('<div class="sec-hdr">Upload Audio Clip</div>', unsafe_allow_html=True)
    st.markdown("Supports WAV, MP3, OGG, FLAC, M4A")

    uploaded_file = st.file_uploader("", type=["wav","mp3","ogg","flac","m4a"], label_visibility="collapsed")

    if uploaded_file:
        st.audio(uploaded_file)

        temp_dir  = "./tmp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        run_key = f"result_{uploaded_file.name}_{uploaded_file.size}"
        if run_key not in st.session_state:
            with st.spinner("🔍 Analyzing audio..."):
                try:
                    st.session_state[run_key] = identify_query_clip_sqlite(temp_path, db_conn)
                except Exception as e:
                    st.error(f"Error: {e}"); st.stop()

        result = st.session_state.get(run_key)
        if not result:
            st.stop()

        best_song, best_score, best_offsets, match_counts, metadata, best_offset = result

        tab_result, tab_spec, tab_const, tab_hist = st.tabs(
            ["🎯 Result", "🎼 Spectrogram", "⭐ Constellation", "📈 Histogram"]
        )

        with tab_result:
            if best_song != "Unknown / No Match":
                position_str = f"{best_offset:.1f}s" if best_offset is not None else "N/A"
                yt_link = f"https://www.youtube.com/results?search_query={urllib.parse.quote(best_song)}"

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">◈ Identified Song</div>
                    <div class="result-song">{best_song}</div>
                    <div class="result-meta">Confidence: <b>{best_score}</b> &nbsp;|&nbsp; Certainty: <b>{min(100,int((best_score/20)*100))}%</b></div>
                    <div class="result-time">📍 Matches at ~{position_str} in the reference song</div>
                    <a class="yt-btn" href="{yt_link}" target="_blank">▶ Watch on YouTube</a>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Matched Song",     best_song[:18]+"…" if len(best_song)>18 else best_song)
                c2.metric("Confidence Score", best_score)
                c3.metric("Position in Song", position_str)

                st.markdown('<div class="sec-hdr">Top Candidates</div>', unsafe_allow_html=True)
                for rank, (sname, score) in enumerate(sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5], 1):
                    st.markdown(f"""
                    <div class="cand-row">
                        <span class="cand-rank">#{rank}</span>
                        <span class="cand-name">{sname}</span>
                        <span class="cand-score">{score} matches</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No match found in database.")

        with tab_spec:
            try: st.pyplot(plot_spectrogram(metadata, f"Spectrogram — {uploaded_file.name}"))
            except Exception as e: st.error(f"Error: {e}")

        with tab_const:
            try: st.pyplot(plot_constellation(metadata, f"Constellation — {uploaded_file.name}"))
            except Exception as e: st.error(f"Error: {e}")

        with tab_hist:
            if best_offsets:
                try: st.pyplot(plot_histogram(best_offsets, best_song))
                except Exception as e: st.error(f"Error: {e}")
            else:
                st.info("No offset data available.")

        try: os.remove(temp_path)
        except: pass

# ═══════════════════════════════════════════════
# BATCH MODE
# ═══════════════════════════════════════════════
else:
    st.markdown('<div class="sec-hdr">📂 Batch Processing</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload audio files", type=["wav","mp3","ogg","flac","m4a"],
        accept_multiple_files=True, label_visibility="collapsed"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} files selected")

        if st.button("▶️ Process All Files", use_container_width=True):
            results, batch_data = [], []
            progress = st.progress(0)
            status   = st.empty()
            temp_dir = "./tmp"
            os.makedirs(temp_dir, exist_ok=True)

            for idx, uf in enumerate(uploaded_files):
                status.markdown(f'Processing **{idx+1}/{len(uploaded_files)}**: {uf.name}')
                progress.progress((idx+1)/len(uploaded_files))

                temp_path = os.path.join(temp_dir, uf.name)
                with open(temp_path, "wb") as f:
                    f.write(uf.getbuffer())

                try:
                    best_song, best_score, best_offsets, match_counts, metadata, best_offset = \
                        identify_query_clip_sqlite(temp_path, db_conn)
                    matched    = best_song != "Unknown / No Match"
                    pred_clean = os.path.splitext(best_song if matched else "UNKNOWN")[0]
                    position   = f"{best_offset:.1f}s" if best_offset is not None else "N/A"
                    results.append({"filename": os.path.splitext(uf.name)[0], "prediction": pred_clean})
                    batch_data.append({"filename": uf.name, "song": best_song, "matched": matched,
                                       "score": best_score, "position": position,
                                       "offsets": best_offsets, "metadata": metadata})
                except Exception as e:
                    results.append({"filename": os.path.splitext(uf.name)[0], "prediction": "ERROR"})
                    batch_data.append({"filename": uf.name, "song": "ERROR", "matched": False,
                                       "score": 0, "position": "N/A", "offsets": [], "metadata": None})

                try: os.remove(temp_path)
                except: pass

            status.success("✅ Batch processing complete!")
            progress.empty()

            # Summary
            identified = sum(1 for r in results if r['prediction'] not in ['UNKNOWN','ERROR'])
            errors     = sum(1 for r in results if r['prediction'] == 'ERROR')
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Files",  len(results))
            c2.metric("Identified",   identified)
            c3.metric("Errors",       errors)

            # Table + download
            st.markdown('<div class="sec-hdr">Results Table</div>', unsafe_allow_html=True)
            df_res = pd.DataFrame(results)
            st.dataframe(df_res, use_container_width=True)
            st.download_button("📥 Download results.csv",
                               data=df_res.to_csv(index=False),
                               file_name="results.csv", mime="text/csv")

            # Per-file visualizations
            st.markdown('<div class="sec-hdr">Per-File Analysis</div>', unsafe_allow_html=True)

            for item in batch_data:
                icon = "✅" if item['matched'] else "❌"
                with st.expander(f"{icon}  {item['filename']}  →  {item['song']}", expanded=False):
                    if item['matched']:
                        yt_link = f"https://www.youtube.com/results?search_query={urllib.parse.quote(item['song'])}"
                        st.markdown(f"""
                        <div class="batch-match">
                            <div class="batch-filename">{item['filename']}</div>
                            <div class="batch-songname">🎵 {item['song']}</div>
                            <span class="batch-time">📍 Matches at ~{item['position']} in reference song</span>
                        </div>
                        <a class="yt-btn" href="{yt_link}" target="_blank" style="margin-left:0;margin-top:10px;">▶ Watch on YouTube</a>
                        <br><br>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("No match found.")

                    if item['metadata'] is not None:
                        t1, t2, t3 = st.tabs(["🎼 Spectrogram", "⭐ Constellation", "📈 Histogram"])
                        with t1:
                            try: st.pyplot(plot_spectrogram(item['metadata'], f"Spectrogram — {item['filename']}"))
                            except Exception as e: st.error(f"Error: {e}")
                        with t2:
                            try: st.pyplot(plot_constellation(item['metadata'], f"Constellation — {item['filename']}"))
                            except Exception as e: st.error(f"Error: {e}")
                        with t3:
                            try:
                                if item['offsets']: st.pyplot(plot_histogram(item['offsets'], item['song']))
                                else: st.info("No offset data.")
                            except Exception as e: st.error(f"Error: {e}")
