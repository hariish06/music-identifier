# fingerprint.py
# YOUR EXACT CODE - copied directly from q3.py
# NO MODIFICATIONS - using exactly what you wrote

import numpy as np
import librosa
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter


# YOUR FUNCTION 1: Exact copy from your code
def get_constellation_peaks(Sxx_dB, times, frequencies, min_amplitude_db=-60, neighborhood_size=20):
    """
    Finds local maxima in the spectrogram matrix to form a constellation map.
    """
    local_max = (maximum_filter(Sxx_dB, size=neighborhood_size) == Sxx_dB)
    background_mask = (Sxx_dB > min_amplitude_db)
    peaks_mask = local_max & background_mask
    
    freq_indices, time_indices = np.where(peaks_mask)
    peak_times = times[time_indices]
    peak_freqs = frequencies[freq_indices]
    peak_indices = list(zip(time_indices, freq_indices))
    
    return peak_times, peak_freqs, peak_indices


# YOUR FUNCTION 2: Exact copy from your code
def generate_song_hashes(peak_indices, times, frequencies, max_time_gap_idx=40):
    """
    Pairs nearby peaks from a single constellation map together into hashes.
    """
    song_hashes = {}
    sorted_peaks = sorted(peak_indices, key=lambda p: p[0])
    num_peaks = len(sorted_peaks)
    
    for i in range(num_peaks):
        t_anchor_idx, f_anchor_idx = sorted_peaks[i]
        
        for j in range(i + 1, num_peaks):
            t_next_idx, f_next_idx = sorted_peaks[j]
            dt_idx = t_next_idx - t_anchor_idx
            
            if dt_idx > max_time_gap_idx:
                break
            
            if dt_idx >= 2:
                f1 = int(frequencies[f_anchor_idx])
                f2 = int(frequencies[f_next_idx])
                dt = float(times[t_next_idx] - times[t_anchor_idx])
                hash_key = (f1, f2, round(dt, 3))
                t1_anchor_time = float(times[t_anchor_idx])
                
                if hash_key not in song_hashes:
                    song_hashes[hash_key] = []
                song_hashes[hash_key].append(t1_anchor_time)
    
    return song_hashes


# YOUR FUNCTION 3: Exact copy from your code
def fingerprint_audio_file(file_path):
    """
    Processes an audio file through the entire pipeline:
    Loads it, computes the spectrogram, extracts peaks, and generates hash pairs.
    """
    # 1. Load Audio
    data, sample_rate = librosa.load(file_path, sr=None)
    
    # 2. Compute Spectrogram
    window_duration = 0.05
    nperseg = int(window_duration * sample_rate)
    noverlap = nperseg // 2
    frequencies_spec, times_spec, Sxx = spectrogram(data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap)
    
    # 3. Filter down to 4000Hz
    freq_mask = frequencies_spec <= 4000
    frequencies_filtered = frequencies_spec[freq_mask]
    Sxx_filtered = Sxx[freq_mask, :]
    Sxx_dB = 10 * np.log10(Sxx_filtered + 1e-10)
    
    # 4. Extract Peaks
    peak_times, peak_freqs, peak_indices = get_constellation_peaks(
        Sxx_dB, times_spec, frequencies_filtered, min_amplitude_db=-55, neighborhood_size=25
    )
    
    # 5. Generate Hashes
    query_hashes = generate_song_hashes(peak_indices, times_spec, frequencies_filtered)
    
    return query_hashes, {
        'spectrogram': Sxx_dB,
        'times': times_spec,
        'frequencies': frequencies_filtered,
        'peak_indices': peak_indices,
        'peak_times': peak_times,
        'peak_freqs': peak_freqs
    }


# YOUR FUNCTION 4: Exact copy from your code
def identify_query_clip(query_audio_path, master_database):
    """
    Matches an unknown query clip against the master database by tallying time offsets.
    """
    # 1. Fingerprint the unknown clip
    print(f"Fingerprinting query: {query_audio_path.split('/')[-1]}...")
    query_hashes, metadata = fingerprint_audio_file(query_audio_path)
    
    # 2. Initialize offset tracking
    song_offset_matches = {}
    
    # 3. Loop through every hash found in the query clip
    for hash_key, q_timestamps in query_hashes.items():
        if hash_key in master_database:
            for song_name, db_t1 in master_database[hash_key]:
                if song_name not in song_offset_matches:
                    song_offset_matches[song_name] = []
                
                for q_t1 in q_timestamps:
                    offset = db_t1 - q_t1
                    song_offset_matches[song_name].append(round(offset, 2))
    
    # 4. Find which song has the highest structural alignment
    best_song = "Unknown / No Match"
    highest_peak_count = 0
    best_offsets_list = []
    match_counts = {}
    
    for song_name, offsets in song_offset_matches.items():
        if len(offsets) == 0:
            continue
        
        match_counts[song_name] = len(offsets)
        
        # Group offsets into bins to find where they structurally align
        counts, bin_edges = np.histogram(offsets, bins=np.arange(min(offsets)-1, max(offsets)+1, 0.5))
        max_spike = np.max(counts)
        
        if max_spike > highest_peak_count:
            highest_peak_count = max_spike
            best_song = song_name
            best_offsets_list = offsets
    
    print(f"Prediction: '{best_song}' with consensus peak score of {highest_peak_count}!")
    
    return best_song, highest_peak_count, best_offsets_list, match_counts, metadata
