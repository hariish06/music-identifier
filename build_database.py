# build_database_sqlite.py
# Build SQLite database for fast indexed queries
# Run this ONCE locally: python build_database_sqlite.py

import os
import sqlite3
import numpy as np
from fingerprint import (
    get_constellation_peaks,
    generate_song_hashes
)
import librosa
from scipy.signal import spectrogram

SONGS_DIR = "songs/"
DB_FILE = "music_database.db"

def create_database_schema(db_path):
    """Create SQLite schema with proper indexes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing table if it exists (for rebuilding)
    cursor.execute("DROP TABLE IF EXISTS hashes")
    
    # Create hashes table
    cursor.execute("""
        CREATE TABLE hashes (
            f1 INTEGER NOT NULL,
            f2 INTEGER NOT NULL,
            delta_t REAL NOT NULL,
            song_name TEXT NOT NULL,
            t1_anchor_time REAL NOT NULL
        )
    """)
    
    conn.commit()
    return conn, cursor


def add_indexes(conn, cursor):
    """Create indexes for fast lookups"""
    print("Creating indexes for fast lookups...")
    
    # Primary index on (f1, f2, delta_t) - used for matching queries
    cursor.execute("""
        CREATE INDEX idx_hash_key ON hashes(f1, f2, delta_t)
    """)
    
    # Secondary index on song_name - used for statistics
    cursor.execute("""
        CREATE INDEX idx_song_name ON hashes(song_name)
    """)
    
    conn.commit()
    print("✓ Indexes created")


def build_database_sqlite(library_folder_path, db_path):
    """
    Build SQLite database from song library using YOUR functions
    """
    # Create schema
    conn, cursor = create_database_schema(db_path)
    
    if not os.path.exists(library_folder_path):
        print(f"❌ Directory '{library_folder_path}' not found!")
        conn.close()
        return False
    
    # Get all audio files
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    audio_files = [f for f in os.listdir(library_folder_path) 
                   if f.lower().endswith(audio_extensions)]
    
    print(f"🎵 Found {len(audio_files)} songs in '{library_folder_path}'...\n")
    
    if len(audio_files) == 0:
        print("⚠️  No audio files found!")
        conn.close()
        return False
    
    total_hashes = 0
    
    for idx, filename in enumerate(audio_files, start=1):
        song_label = os.path.splitext(filename)[0]
        file_full_path = os.path.join(library_folder_path, filename)
        
        print(f"[{idx}/{len(audio_files)}] Processing: '{song_label}'...")
        
        try:
            # 1. Load Audio
            data, sample_rate = librosa.load(file_full_path, sr=None)
            
            # 2. Compute Spectrogram
            window_duration = 0.05
            nperseg = int(window_duration * sample_rate)
            noverlap = nperseg // 2
            frequencies_spec, times_spec, Sxx = spectrogram(
                data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap
            )
            
            # 3. Filter to 4000Hz
            freq_mask = frequencies_spec <= 4000
            frequencies_filtered = frequencies_spec[freq_mask]
            Sxx_filtered = Sxx[freq_mask, :]
            Sxx_dB = 10 * np.log10(Sxx_filtered + 1e-10)
            
            # 4. REUSE YOUR PEAK DETECTION FUNCTION
            _, _, current_peak_indices = get_constellation_peaks(
                Sxx_dB, times_spec, frequencies_filtered, 
                min_amplitude_db=-55, neighborhood_size=25
            )
            
            # 5. REUSE YOUR HASH GENERATION FUNCTION
            song_hashes = generate_song_hashes(
                current_peak_indices, times_spec, frequencies_filtered, 
                max_time_gap_idx=40
            )
            
            # 6. Insert into SQLite database
            rows_inserted = 0
            for hash_key, timestamps in song_hashes.items():
                f1, f2, dt = hash_key
                for t1_anchor_time in timestamps:
                    cursor.execute("""
                        INSERT INTO hashes (f1, f2, delta_t, song_name, t1_anchor_time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (f1, f2, dt, song_label, t1_anchor_time))
                    rows_inserted += 1
            
            # Commit after each song
            conn.commit()
            total_hashes += rows_inserted
            
            print(f"   ✓ Inserted {rows_inserted} hash entries from {len(current_peak_indices)} peaks")
        
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            continue
    
    # Create indexes after all data is loaded
    add_indexes(conn, cursor)
    
    # Get database size and stats
    cursor.execute("SELECT COUNT(DISTINCT (f1, f2, delta_t)) FROM hashes")
    unique_hashes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT song_name) FROM hashes")
    num_songs = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ SQLite Database Created Successfully!")
    print("="*60)
    print(f"Database file: {db_path}")
    print(f"Total songs indexed: {num_songs}")
    print(f"Unique hash keys: {unique_hashes:,}")
    print(f"Total hash entries: {total_hashes:,}")
    print(f"Database size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BUILDING SQLITE MUSIC IDENTIFIER DATABASE")
    print("="*60 + "\n")
    
    # Check if songs folder exists
    if not os.path.exists(SONGS_DIR):
        print(f"⚠️  '{SONGS_DIR}' folder not found!")
        print(f"   Please create it and add your reference songs.\n")
        exit(1)
    
    # Build SQLite database
    success = build_database_sqlite(SONGS_DIR, DB_FILE)
    
    if success:
        print(f"🎵 Ready to deploy!")
        print(f"   Next: streamlit run app.py")
    else:
        print("\n❌ Database build failed. Check your songs folder.")
        exit(1)
