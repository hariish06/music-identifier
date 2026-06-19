# app.py — Music Identifier (SQLite backend)
# Maintained all original logic + new UI + YouTube + batch visualizations

import streamlit as st
import sqlite3
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import urllib.parse

# ── MUST BE FIRST ─────────────────────────────
st.set_page_config(
    page_title="Music Identifier",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* App background */
.stApp { background: #0d0f1a !important; }
.main .block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #12141f !important;
    border-right: 1px solid #ffffff10 !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }

.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0 24px;
    border-bottom: 1px solid #ffffff10;
    margin-bottom: 24px;
}
.sidebar-logo-icon {
    width: 36px; height: 36px; background: #a78bfa;
    border-radius: 8px; display: flex; align-items: center;
    justify-content: center; font-size: 1.2rem;
}
.sidebar-logo-text {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.2rem; font-weight: 700; color: #ffffff !important;
}

.sidebar-section {
    font-size: 0.65rem; font-weight: 600; color: #ffffff40 !important;
    letter-spacing: 2px; text-transform: uppercase;
    margin: 20px 0 10px;
}

.sidebar-nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; border-radius: 8px;
    color: #ffffff80 !important; font-size: 0.9rem;
    cursor: pointer; margin-bottom: 4px;
    transition: background 0.15s;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: #ffffff10 !important; color: #ffffff !important;
}
.sidebar-nav-item.active { background: #a78bfa20 !important; color: #a78bfa !important; }

.stat-block {
    margin-bottom: 16px;
}
.stat-block-label {
    font-size: 0.75rem; color: #ffffff50 !important; margin-bottom: 2px;
}
.stat-block-value {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.6rem; font-weight: 700; color: #ffffff !important;
}

/* ── HEADER ── */
.page-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem; font-weight: 700; color: #ffffff;
    margin-bottom: 4px;
}
.page-subtitle { font-size: 0.9rem; color: #ffffff50; margin-bottom: 2rem; }

/* ── MODE CARDS ── */
.mode-card {
    background: #1a1d2e;
    border: 2px solid #ffffff15;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    height: 120px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.mode-card.active { border-color: #a78bfa; background: #a78bfa15; }
.mode-card h3 { color: #ffffff; margin: 0 0 6px; font-size: 1.1rem; }
.mode-card p  { color: #ffffff60; font-size: 0.8rem; margin: 0; }

/* ── RESULT CARD ── */
.result-card {
    background: linear-gradient(135deg, #1a1d2e, #1e1040);
    border: 1px solid #a78bfa50;
    border-left: 5px solid #a78bfa;
    border-radius: 12px;
    padding: 28px 32px;
    margin: 20px 0;
}
.result-label { font-size: 0.7rem; color: #a78bfa; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 8px; }
.result-song  { font-family: 'Space Grotesk', sans-serif !important; font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
.result-meta  { font-size: 0.85rem; color: #ffffff40; }
.result-meta b { color: #a78bfa; }
.result-time  { font-size: 1rem; color: #a3e635; font-weight: 600; margin-top: 8px; }

.yt-btn {
    display: inline-block; margin-top: 14px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #ffffff !important; text-decoration: none !important;
    padding: 10px 24px; border-radius: 8px;
    font-size: 0.85rem; font-weight: 600;
}

/* ── CANDIDATE ROW ── */
.cand-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 8px;
    background: #1a1d2e; margin-bottom: 6px;
}
.cand-rank { font-size: 0.75rem; color: #ffffff40; width: 24px; }
.cand-name { color: #ffffff; font-size: 0.9rem; flex: 1; }
.cand-score{ color: #a78bfa; font-size: 0.85rem; font-weight: 600; }

/* ── SECTION HEADER ── */
.sec-hdr {
    font-size: 1rem; font-weight: 600; color: #ffffff;
    border-left: 3px solid #a78bfa;
    padding-left: 10px; margin: 24px 0 14px;
}

/* ── BATCH RESULT CARD ── */
.batch-match {
    background: #1a1d2e; border: 1px solid #a78bfa30;
    border-radius: 10px; padding: 16px 20px; margin-bottom: 8px;
}
.batch-filename { font-size: 0.8rem; color: #ffffff50; margin-bottom: 4px; }
.batch-songname { font-size: 1.1rem; font-weight: 600; color: #ffffff; }
.batch-time { font-size: 0.85rem; color: #a3e635; margin-top: 4px; }

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 10px 24px !important;
}
div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(118,75,162,0.4) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1d2e !important;
    border-radius: 8px !important; padding: 4px !important;
    gap: 4px !important; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #ffffff60 !important;
    border-radius: 6px !important; font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: #a78bfa20 !important; color: #a78bfa !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 1rem !important; }

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: #1a1d2e !important;
    border: 1px solid #ffffff10 !important;
    border-radius: 10px !important; padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: #ffffff50 !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.4rem !important; font-weight: 700 !important; }

/* ── MISC ── */
.stProgress > div > div { background: #a78bfa !important; }
[data-testid="stFileUploader"] { background: #1a1d2e !important; border-radius: 10px !important; }
.stDataFrame { border-radius: 8px !important; overflow: hidden; }
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }
.stAlert   { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE
# ============================================================
@st.cache_resource
def get_db_connection():
    try:
        conn = sqlite3.connect("music_database.db", check_same_thread=False)
        return conn
    except Exception as e:
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
        db_size = os.path.getsize("music_database.db") / (1024*1024) if os.path.exists("music_database.db") else 0
        return num_songs, unique_hashes, total_entries, db_size
    except:
        return 0, 0, 0, 0

# ============================================================
# IDENTIFY FUNCTION (unchanged logic)
# ============================================================
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
        results = cursor.fetchall()
        for song_name, db_t1 in results:
            if song_name not in song_offset_matches:
                song_offset_matches[song_name] = []
            for q_t1 in q_timestamps:
                offset = db_t1 - q_t1
                song_offset_matches[song_name].append(round(offset, 2))

    best_song = "Unknown / No Match"
    highest_peak_count = 0
    best_offsets_list  = []
    match_counts       = {}
    best_offset_value  = None

    for song_name, offsets in song_offset_matches.items():
        if not offsets:
            continue
        match_counts[song_name] = len(offsets)
        counts, bin_edges = np.histogram(
            offsets,
            bins=np.arange(min(offsets)-1, max(offsets)+1, 0.5)
        )
        max_spike = int(np.max(counts))
        if max_spike > highest_peak_count:
            highest_peak_count = max_spike
            best_song          = song_name
            best_offsets_list  = offsets
            peak_bin_idx       = int(np.argmax(counts))
            best_offset_value  = float(bin_edges[peak_bin_idx])

    return best_song, highest_peak_count, best_offsets_list, match_counts, metadata, best_offset_value

# ============================================================
# PLOT HELPERS
# ============================================================
def make_fig():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor('#12141f')
    ax.set_facecolor('#0d0f1a')
    for sp in ax.spines.values(): sp.set_edgecolor('#ffffff15')
    ax.tick_params(colors='#ffffff60')
    ax.xaxis.label.set_color('#ffffff60')
    ax.yaxis.label.set_color('#ffffff60')
    ax.title.set_color('#ffffff90')
    return fig, ax

def plot_spectrogram(metadata, title="Spectrogram"):
    fig, ax = make_fig()
    spec_db = metadata['spectrogram']
    times   = metadata['times']
    freqs   = metadata['frequencies']
    im = ax.imshow(spec_db, aspect='auto', origin='lower', cmap='magma',
                   extent=[times[0], times[-1], freqs[0], freqs[-1]])
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Frequency (Hz)")
    ax.set_title(title)
    cb = plt.colorbar(im, ax=ax, label="dB")
    cb.ax.tick_params(colors='#ffffff60')
    cb.set_label("dB", color='#ffffff60')
    plt.tight_layout()
    return fig

def plot_constellation(metadata, title="Constellation Map"):
    fig, ax = make_fig()
    pt = metadata['peak_times']
    pf = metadata['peak_freqs']
    if len(pt) > 0:
        ax.scatter(pt, pf, s=12, color='#a78bfa', alpha=0.7, edgecolors='none')
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Frequency (Hz)")
    ax.set_title(f"{title} — {len(pt)} peaks")
    ax.grid(True, alpha=0.1)
    plt.tight_layout()
    return fig

def plot_histogram(offsets, song_name):
    fig, ax = make_fig()
    if offsets:
        ax.hist(offsets, bins=50, color='#a78bfa', edgecolor='#7c3aed', alpha=0.85)
    ax.set_xlabel("Time Offset (s)"); ax.set_ylabel("Matching Hashes")
    ax.set_title(f"Offset Histogram — {song_name}")
    ax.grid(True, alpha=0.1, axis='y')
    plt.tight_layout()
    return fig

# ============================================================
# SIDEBAR
# ============================================================
num_songs, unique_hashes, total_entries, db_size = get_db_stats()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎵</div>
        <div class="sidebar-logo-text">SongID</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Database Stats</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-block">
        <div class="stat-block-label">Songs</div>
        <div class="stat-block-value">{num_songs}</div>
    </div>
    <div class="stat-block">
        <div class="stat-block-label">Unique Hashes</div>
        <div class="stat-block-value">{unique_hashes:,}</div>
    </div>
    <div class="stat-block">
        <div class="stat-block-label">Total Entries</div>
        <div class="stat-block-value">{total_entries:,}</div>
    </div>
    <div class="stat-block">
        <div class="stat-block-label">DB Size</div>
        <div class="stat-block-value">{db_size:.2f} MB</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)

    if "mode" not in st.session_state:
        st.session_state.mode = "Single"

    if st.button("🎧  Single Clip", use_container_width=True):
        st.session_state.mode = "Single"
        st.rerun()
    if st.button("📂  Batch Mode", use_container_width=True):
        st.session_state.mode = "Batch"
        st.rerun()

# ============================================================
# MAIN HEADER
# ============================================================
db_conn = get_db_connection()
if db_conn is None:
    st.error("❌ music_database.db not found. Run build_database_sqlite.py first.")
    st.stop()

st.markdown('<div class="page-title">🎵 Music Identifier</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Identify songs using spectrogram fingerprinting — SQLite powered</div>', unsafe_allow_html=True)

# Mode cards
col1, col2 = st.columns(2)
with col1:
    is_single = st.session_state.mode == "Single"
    st.markdown(f"""
    <div class="mode-card {'active' if is_single else ''}">
        <h3>🎧 Single Clip</h3>
        <p>Identify a single song using fast fingerprint matching.</p>
    </div>""", unsafe_allow_html=True)
    st.write("")
    if st.button("Activate Single Mode", use_container_width=True):
        st.session_state.mode = "Single"; st.rerun()

with col2:
    is_batch = st.session_state.mode == "Batch"
    st.markdown(f"""
    <div class="mode-card {'active' if is_batch else ''}">
        <h3>📂 Batch Mode</h3>
        <p>Process and catalog multiple audio files at once.</p>
    </div>""", unsafe_allow_html=True)
    st.write("")
    if st.button("Activate Batch Mode", use_container_width=True):
        st.session_state.mode = "Batch"; st.rerun()

st.markdown("---")

# ============================================================
# SINGLE CLIP MODE
# ============================================================
if st.session_state.mode == "Single":
    st.markdown('<div class="sec-hdr">Upload Audio Clip</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Supports WAV, MP3, OGG, FLAC, M4A",
        type=["wav","mp3","ogg","flac","m4a"]
    )

    if uploaded_file:
        st.audio(uploaded_file)

        temp_dir  = "./tmp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        tab_result, tab_spec, tab_const, tab_hist = st.tabs(
            ["🎯 Result", "🎼 Spectrogram", "⭐ Constellation", "📈 Histogram"]
        )

        # Run identification once and cache in session state
        run_key = f"result_{uploaded_file.name}"
        if run_key not in st.session_state:
            with st.spinner("🔍 Analyzing audio..."):
                try:
                    result = identify_query_clip_sqlite(temp_path, db_conn)
                    st.session_state[run_key] = result
                except Exception as e:
                    st.error(f"Error: {e}")
                    result = None
        else:
            result = st.session_state[run_key]

        if result:
            best_song, best_score, best_offsets, match_counts, metadata, best_offset = result

        # ── TAB 1: RESULT ──
        with tab_result:
            if result and best_song != "Unknown / No Match":
                # Position in song
                position_str = f"{best_offset:.1f}s" if best_offset is not None else "N/A"
                yt_query = urllib.parse.quote(best_song)
                yt_link  = f"https://www.youtube.com/results?search_query={yt_query}"

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">◈ Identified Song</div>
                    <div class="result-song">{best_song}</div>
                    <div class="result-meta">
                        Confidence Score: <b>{best_score}</b> &nbsp;|&nbsp;
                        Certainty: <b>{min(100, int((best_score/20)*100))}%</b>
                    </div>
                    <div class="result-time">📍 Matches at ~{position_str} in the reference song</div>
                    <a class="yt-btn" href="{yt_link}" target="_blank">▶ Watch on YouTube</a>
                </div>
                """, unsafe_allow_html=True)

                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Matched Song", best_song[:20]+"…" if len(best_song)>20 else best_song)
                c2.metric("Confidence",   best_score)
                c3.metric("Position in Song", position_str)

                # Top candidates
                st.markdown('<div class="sec-hdr">Top Candidates</div>', unsafe_allow_html=True)
                top5 = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                for rank, (sname, score) in enumerate(top5, 1):
                    st.markdown(f"""
                    <div class="cand-row">
                        <span class="cand-rank">#{rank}</span>
                        <span class="cand-name">{sname}</span>
                        <span class="cand-score">{score} matches</span>
                    </div>""", unsafe_allow_html=True)
            elif result:
                st.warning("⚠️ No match found in database.")

        # ── TAB 2: SPECTROGRAM ──
        with tab_spec:
            if result:
                try:
                    st.pyplot(plot_spectrogram(metadata, f"Spectrogram — {uploaded_file.name}"))
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── TAB 3: CONSTELLATION ──
        with tab_const:
            if result:
                try:
                    st.pyplot(plot_constellation(metadata, f"Constellation — {uploaded_file.name}"))
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── TAB 4: HISTOGRAM ──
        with tab_hist:
            if result and best_offsets:
                try:
                    st.pyplot(plot_histogram(best_offsets, best_song))
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.info("No offset data available.")

        try:
            os.remove(temp_path)
        except:
            pass

# ============================================================
# BATCH MODE
# ============================================================
else:
    st.markdown('<div class="sec-hdr">📂 Batch Processing</div>', unsafe_allow_html=True)
    st.markdown("Choose multiple audio files — WAV, MP3, OGG, FLAC, M4A")

    uploaded_files = st.file_uploader(
        "Upload audio files",
        type=["wav","mp3","ogg","flac","m4a"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} files selected")

        if st.button("▶️ Process All Files", use_container_width=True):
            results      = []
            batch_data   = []   # stores per-file metadata for visualizations
            progress_bar = st.progress(0)
            status       = st.empty()
            temp_dir     = "./tmp"
            os.makedirs(temp_dir, exist_ok=True)

            for idx, uf in enumerate(uploaded_files):
                status.markdown(
                    f'<span style="color:#a78bfa;font-size:0.85rem;">Processing {idx+1}/{len(uploaded_files)}: {uf.name}</span>',
                    unsafe_allow_html=True
                )
                progress_bar.progress((idx+1)/len(uploaded_files))

                temp_path = os.path.join(temp_dir, uf.name)
                with open(temp_path, "wb") as f:
                    f.write(uf.getbuffer())

                try:
                    best_song, best_score, best_offsets, match_counts, metadata, best_offset = \
                        identify_query_clip_sqlite(temp_path, db_conn)

                    pred       = best_song if best_song != "Unknown / No Match" else "UNKNOWN"
                    pred_clean = os.path.splitext(pred)[0]
                    position   = f"{best_offset:.1f}s" if best_offset is not None else "N/A"

                    results.append({"filename": os.path.splitext(uf.name)[0], "prediction": pred_clean})
                    batch_data.append({
                        "filename": uf.name, "song": pred,
                        "score": best_score, "position": position,
                        "offsets": best_offsets, "metadata": metadata,
                        "matched": best_song != "Unknown / No Match"
                    })

                except Exception as e:
                    results.append({"filename": os.path.splitext(uf.name)[0], "prediction": "ERROR"})
                    batch_data.append({"filename": uf.name, "song": "ERROR", "matched": False,
                                       "score": 0, "position": "N/A", "offsets": [], "metadata": None})

                try:
                    os.remove(temp_path)
                except:
                    pass

            status.success("✅ Batch processing complete!")
            progress_bar.empty()

            # ── Summary metrics ──
            identified = sum(1 for r in results if r['prediction'] not in ['UNKNOWN','ERROR'])
            errors     = sum(1 for r in results if r['prediction'] == 'ERROR')
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Files",  len(results))
            c2.metric("Identified",   identified)
            c3.metric("Errors",       errors)

            # ── Results table ──
            st.markdown('<div class="sec-hdr">Results Table</div>', unsafe_allow_html=True)
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)
            st.download_button(
                "📥 Download results.csv",
                data=df_results.to_csv(index=False),
                file_name="results.csv", mime="text/csv"
            )

            # ── Per-file visualizations ──
            st.markdown('<div class="sec-hdr">Per-File Analysis</div>', unsafe_allow_html=True)

            for item in batch_data:
                yt_query = urllib.parse.quote(item['song']) if item['matched'] else ""
                yt_link  = f"https://www.youtube.com/results?search_query={yt_query}"

                with st.expander(f"{'✅' if item['matched'] else '❌'}  {item['filename']}  →  {item['song']}", expanded=False):

                    if item['matched']:
                        st.markdown(f"""
                        <div class="batch-match">
                            <div class="batch-filename">{item['filename']}</div>
                            <div class="batch-songname">🎵 {item['song']}</div>
                            <div class="batch-time">📍 Matches at ~{item['position']} in the reference song</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<a class="yt-btn" href="{yt_link}" target="_blank">▶ Watch on YouTube</a>', unsafe_allow_html=True)
                        st.write("")
                    else:
                        st.warning("No match found.")

                    if item['metadata'] is not None:
                        t1, t2, t3 = st.tabs(["🎼 Spectrogram", "⭐ Constellation", "📈 Histogram"])
                        with t1:
                            try:
                                st.pyplot(plot_spectrogram(item['metadata'], f"Spectrogram — {item['filename']}"))
                            except Exception as e:
                                st.error(f"Spectrogram error: {e}")
                        with t2:
                            try:
                                st.pyplot(plot_constellation(item['metadata'], f"Constellation — {item['filename']}"))
                            except Exception as e:
                                st.error(f"Constellation error: {e}")
                        with t3:
                            try:
                                if item['offsets']:
                                    st.pyplot(plot_histogram(item['offsets'], item['song']))
                                else:
                                    st.info("No offset data.")
                            except Exception as e:
                                st.error(f"Histogram error: {e}")
