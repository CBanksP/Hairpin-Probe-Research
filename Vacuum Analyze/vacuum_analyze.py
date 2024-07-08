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
    print("Starting analysis of vacuum resonance data...")

    print("Loading data from file...")
    # Load data
    df = pd.read_pickle(data_file)
    print(f"Data loaded. Shape: {df.shape}")
    
    print("Smoothing data using Savitzky-Golay filter...")
    # Smooth the data using Savitzky-Golay filter
    df['Smooth_Signal'] = savgol_filter(df['Signal'], window_length=51, polyorder=3)
    print("Data smoothing complete.")

    print("Performing resonance detection using multiple methods...")
    print("Method 1: Finding minimum (resonance typically corresponds to minimum)")
    # Method 1: Find minimum (resonance typically corresponds to minimum)
    min_index = df['Smooth_Signal'].idxmin()
    resonance_freq_min = df['Frequency (MHz)'].iloc[min_index]
    print(f"Minimum method complete. Resonance frequency: {resonance_freq_min:.2f} MHz")
    
    print("Method 2: Performing Lorentzian fit")
    # Method 2: Lorentzian fit
    try:
        popt, _ = curve_fit(lorentzian, df['Frequency (MHz)'], df['Smooth_Signal'], 
                            p0=[df['Smooth_Signal'].min(), resonance_freq_min, 1],
                            maxfev=10000)
        resonance_freq_lorentz = popt[1]
        print(f"Lorentzian fit complete. Resonance frequency: {resonance_freq_lorentz:.2f} MHz")
    except RuntimeError:
        resonance_freq_lorentz = None
        print("Lorentzian fit failed to converge.")
    
    print("Method 3: Performing peak detection")
    # Method 3: Peak detection (as a backup)
    peaks, _ = find_peaks(-df['Smooth_Signal'], distance=len(df)//10)
    if len(peaks) > 0:
        resonance_freq_peak = df['Frequency (MHz)'].iloc[peaks[0]]
        print(f"Peak detection complete. Resonance frequency: {resonance_freq_peak:.2f} MHz")
    else:
        resonance_freq_peak = None
        print("Peak detection did not find a clear peak.")

    print("Generating plot...")
    # Plot the data and analysis results
    plt.figure(figsize=(12, 8))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', alpha=0.5, label='Raw Data')
    plt.plot(df['Frequency (MHz)'], df['Smooth_Signal'], 'g-', label='Smoothed Data')
    
    # Lorentzian fit
    if resonance_freq_lorentz is not None:
        plt.plot(df['Frequency (MHz)'], lorentzian(df['Frequency (MHz)'], *popt), 'r-', label='Lorentzian Fit')
        plt.axvline(x=resonance_freq_lorentz, color='r', linestyle='--')
        plt.annotate(f'Lorentzian: {resonance_freq_lorentz:.2f} MHz', 
                     xy=(resonance_freq_lorentz, df['Smooth_Signal'].min()),
                     xytext=(10, 30), textcoords='offset points',
                     arrowprops=dict(arrowstyle="->", color='r'))
    
    # Minimum method
    plt.axvline(x=resonance_freq_min, color='g', linestyle='--')
    plt.annotate(f'Minimum: {resonance_freq_min:.2f} MHz', 
                 xy=(resonance_freq_min, df['Smooth_Signal'].min()),
                 xytext=(10, 60), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", color='g'))
    
    # Peak detection
    if resonance_freq_peak is not None:
        plt.axvline(x=resonance_freq_peak, color='m', linestyle='--')
        plt.annotate(f'Peak Detection: {resonance_freq_peak:.2f} MHz', 
                     xy=(resonance_freq_peak, df['Smooth_Signal'].min()),
                     xytext=(10, 90), textcoords='offset points',
                     arrowprops=dict(arrowstyle="->", color='m'))
    
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    print(f"Saving plot as {data_file[:-4]}_analysis_plot.png")
    plt.savefig(f'{data_file[:-4]}_analysis_plot.png', dpi=300)
    print("Displaying plot...")
    plt.show()

    print("\nAnalysis Results:")
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
    print(f"Starting analysis for file: {DATA_FILE}")
    resonance_min, resonance_lorentz, resonance_peak = analyze_vacuum_resonance_data(DATA_FILE)
    print("\nAnalysis complete. Please review the plot and printed results to determine the most appropriate resonance frequency.")