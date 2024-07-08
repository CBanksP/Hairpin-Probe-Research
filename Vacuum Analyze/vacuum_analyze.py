# User Inputs
DATA_FILE = 'vacuum_resonance_test_data.pkl'  # Name of the data file to analyze

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter

def lorentzian(x, a, x0, gam):
    return a * gam**2 / (gam**2 + (x - x0)**2)

def analyze_vacuum_resonance_data(data_file):
    # Load data
    df = pd.read_pickle(data_file)
    
    # Smooth the data using Savitzky-Golay filter
    df['Smooth_Signal'] = savgol_filter(df['Signal'], window_length=51, polyorder=3)

    # Method 1: Find minimum (resonance typically corresponds to minimum)
    min_index = df['Smooth_Signal'].idxmin()
    resonance_freq_min = df['Frequency (MHz)'].iloc[min_index]
    
    # Method 2: Lorentzian fit
    try:
        popt, _ = curve_fit(lorentzian, df['Frequency (MHz)'], df['Smooth_Signal'], 
                            p0=[df['Smooth_Signal'].min(), resonance_freq_min, 1],
                            maxfev=10000)
        resonance_freq_lorentz = popt[1]
    except RuntimeError:
        resonance_freq_lorentz = None
    
    # Method 3: Peak detection (as a backup)
    peaks, _ = find_peaks(-df['Smooth_Signal'], distance=len(df)//10)
    if len(peaks) > 0:
        resonance_freq_peak = df['Frequency (MHz)'].iloc[peaks[0]]
    else:
        resonance_freq_peak = None

    # Plot the data and analysis results
    plt.figure(figsize=(12, 8))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', alpha=0.5, label='Raw Data')
    plt.plot(df['Frequency (MHz)'], df['Smooth_Signal'], 'g-', label='Smoothed Data')
    
    if resonance_freq_lorentz is not None:
        plt.plot(df['Frequency (MHz)'], lorentzian(df['Frequency (MHz)'], *popt), 'r-', label='Lorentzian Fit')
        plt.axvline(x=resonance_freq_lorentz, color='r', linestyle='--', label='Lorentzian Resonance')
    
    plt.axvline(x=resonance_freq_min, color='g', linestyle='--', label='Minimum Resonance')
    
    if resonance_freq_peak is not None:
        plt.axvline(x=resonance_freq_peak, color='m', linestyle='--', label='Peak Detection Resonance')
    
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'{data_file[:-4]}_analysis_plot.png')
    plt.show()

    # Print results
    print(f"Resonance frequency (Minimum method): {resonance_freq_min:.2f} MHz")
    if resonance_freq_lorentz is not None:
        print(f"Resonance frequency (Lorentzian fit): {resonance_freq_lorentz:.2f} MHz")
    else:
        print("Lorentzian fit failed to converge.")
    if resonance_freq_peak is not None:
        print(f"Resonance frequency (Peak detection): {resonance_freq_peak:.2f} MHz")
    else:
        print("Peak detection did not find a clear peak.")

    return resonance_freq_min, resonance_freq_lorentz, resonance_freq_peak

# Run the script
if __name__ == "__main__":
    resonance_min, resonance_lorentz, resonance_peak = analyze_vacuum_resonance_data(DATA_FILE)
    print("\nAnalysis complete. Please review the plot and printed results to determine the most appropriate resonance frequency.")