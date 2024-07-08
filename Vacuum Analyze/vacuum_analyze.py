# User Inputs
DATA_FILE = 'vacuum_resonance_test_data.pkl'  # Name of the data file to analyze

# Import necessary libraries
import numpy as np  # For numerical operations and array handling
import pandas as pd  # For data manipulation and analysis
import matplotlib.pyplot as plt  # For plotting the data and results
from scipy.optimize import curve_fit  # For fitting the Lorentzian function to the data
from scipy.signal import find_peaks, savgol_filter  # For peak detection and data smoothing

# Define the Lorentzian function for curve fitting
def lorentzian(x, a, x0, gam):
    """
    Lorentzian function used for fitting the resonance curve.
    Parameters:
    x: Independent variable (frequency in this case)
    a: Amplitude of the peak
    x0: Center frequency (resonance frequency)
    gam: Half-width at half-maximum (HWHM)

    The function describes a symmetric peak shape characteristic of many resonance phenomena.
    """
    return a * gam**2 / (gam**2 + (x - x0)**2)

def analyze_vacuum_resonance_data(data_file):
    print("Starting analysis of vacuum resonance data...")

    # Load data from the pickle file
    print("Loading data from file...")
    df = pd.read_pickle(data_file)
    print(f"Data loaded. Shape: {df.shape}")
    
    # Apply Savitzky-Golay filter to smooth the data
    # This reduces noise while preserving the shape of the signal
    print("Smoothing data using Savitzky-Golay filter...")
    df['Smooth_Signal'] = savgol_filter(df['Signal'], window_length=51, polyorder=3)
    print("Data smoothing complete.")

    print("Performing resonance detection using multiple methods...")

    # Method 1: Minimum Detection
    # For a vacuum resonance, the minimum of the signal often corresponds to the resonance frequency
    print("Method 1: Finding minimum (resonance typically corresponds to minimum)")
    min_index = df['Smooth_Signal'].idxmin()
    resonance_freq_min = df['Frequency (MHz)'].iloc[min_index]
    print(f"Minimum method complete. Resonance frequency: {resonance_freq_min:.2f} MHz")
    
    # Method 2: Lorentzian Fit
    # Fit the data to a Lorentzian function, which is the expected shape for a resonance peak
    print("Method 2: Performing Lorentzian fit")
    try:
        # Initial guess for Lorentzian parameters: [amplitude, center, width]
        p0 = [df['Smooth_Signal'].min(), resonance_freq_min, 1]
        popt, _ = curve_fit(lorentzian, df['Frequency (MHz)'], df['Smooth_Signal'], p0=p0, maxfev=10000)
        resonance_freq_lorentz = popt[1]  # The center parameter of the Lorentzian is the resonance frequency
        print(f"Lorentzian fit complete. Resonance frequency: {resonance_freq_lorentz:.2f} MHz")
    except RuntimeError:
        resonance_freq_lorentz = None
        print("Lorentzian fit failed to converge.")
    
    # Method 3: Peak Detection
    # Find peaks in the inverted signal (as we're looking for a minimum)
    print("Method 3: Performing peak detection")
    peaks, _ = find_peaks(-df['Smooth_Signal'], distance=len(df)//10)
    if len(peaks) > 0:
        resonance_freq_peak = df['Frequency (MHz)'].iloc[peaks[0]]
        print(f"Peak detection complete. Resonance frequency: {resonance_freq_peak:.2f} MHz")
    else:
        resonance_freq_peak = None
        print("Peak detection did not find a clear peak.")

    # Plotting the results
    print("Generating plot...")
    plt.figure(figsize=(12, 8))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', alpha=0.5, label='Raw Data')
    plt.plot(df['Frequency (MHz)'], df['Smooth_Signal'], 'g-', label='Smoothed Data')
    
    # Define colors for each method for consistency
    min_color = 'green'
    lorentz_color = 'red'
    peak_color = 'magenta'
    
    # Plot and annotate results from Minimum method
    plt.axvline(x=resonance_freq_min, color=min_color, linestyle='--')
    plt.annotate(f'Minimum: {resonance_freq_min:.2f} MHz', 
                 xy=(resonance_freq_min, df['Smooth_Signal'].min()),
                 xytext=(10, 30), textcoords='offset points',
                 color=min_color,
                 arrowprops=dict(arrowstyle="->", color=min_color))
    
    # Plot and annotate results from Lorentzian fit (if successful)
    if resonance_freq_lorentz is not None:
        plt.plot(df['Frequency (MHz)'], lorentzian(df['Frequency (MHz)'], *popt), 'r-', label='Lorentzian Fit')
        plt.axvline(x=resonance_freq_lorentz, color=lorentz_color, linestyle='--')
        plt.annotate(f'Lorentzian: {resonance_freq_lorentz:.2f} MHz', 
                     xy=(resonance_freq_lorentz, df['Smooth_Signal'].min()),
                     xytext=(10, 60), textcoords='offset points',
                     color=lorentz_color,
                     arrowprops=dict(arrowstyle="->", color=lorentz_color))
    
    # Plot and annotate results from Peak detection (if a peak was found)
    if resonance_freq_peak is not None:
        plt.axvline(x=resonance_freq_peak, color=peak_color, linestyle='--')
        plt.annotate(f'Peak Detection: {resonance_freq_peak:.2f} MHz', 
                     xy=(resonance_freq_peak, df['Smooth_Signal'].min()),
                     xytext=(10, 90), textcoords='offset points',
                     color=peak_color,
                     arrowprops=dict(arrowstyle="->", color=peak_color))
    
    # Set plot labels and title
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save the plot as a PNG file
    print(f"Saving plot as {data_file[:-4]}_analysis_plot.png")
    plt.savefig(f'{data_file[:-4]}_analysis_plot.png', dpi=300)

    # Print analysis results
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

    # Display the plot (this will block until the plot window is closed)
    print("\nDisplaying plot...")
    plt.show()

    # Return the resonance frequencies found by each method
    return resonance_freq_min, resonance_freq_lorentz, resonance_freq_peak

# Main execution block
if __name__ == "__main__":
    print(f"Starting analysis for file: {DATA_FILE}")
    resonance_min, resonance_lorentz, resonance_peak = analyze_vacuum_resonance_data(DATA_FILE)
    print("\nAnalysis complete. Please review the plot and printed results to determine the most appropriate resonance frequency.")