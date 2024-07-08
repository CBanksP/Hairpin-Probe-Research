# User Inputs
DATA_FILE = 'vacuum_resonance_test4_data.pkl'  # Name of the data file to analyze

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter

# Define the Gaussian function for curve fitting (better for peaks)
def gaussian(x, a, x0, sigma):
    """
    Gaussian function used for fitting the resonance curve.
    Parameters:
    x: Independent variable (frequency in this case)
    a: Amplitude of the peak
    x0: Center frequency (resonance frequency)
    sigma: Standard deviation (related to peak width)

    The function describes a symmetric peak shape characteristic of many resonance phenomena.
    """
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def analyze_vacuum_resonance_data(data_file):
    print("Starting analysis of vacuum resonance data...")

    # Load data from the pickle file
    print("Loading data from file...")
    df = pd.read_pickle(data_file)
    print(f"Data loaded. Shape: {df.shape}")
    
    # Apply Savitzky-Golay filter to smooth the data
    print("Smoothing data using Savitzky-Golay filter...")
    df['Smooth_Signal'] = savgol_filter(df['Signal'], window_length=51, polyorder=3)
    print("Data smoothing complete.")

    print("Performing resonance detection using multiple methods...")

    # Method 1: Maximum Detection
    # For a vacuum resonance peak, the maximum of the signal corresponds to the resonance frequency
    print("Method 1: Finding maximum (resonance corresponds to maximum)")
    max_index = df['Smooth_Signal'].idxmax()
    resonance_freq_max = df['Frequency (MHz)'].iloc[max_index]
    print(f"Maximum method complete. Resonance frequency: {resonance_freq_max:.2f} MHz")
    
    # Method 2: Gaussian Fit
    # Fit the data to a Gaussian function, which is a good approximation for a resonance peak
    print("Method 2: Performing Gaussian fit")
    try:
        # Initial guess for Gaussian parameters: [amplitude, center, width]
        p0 = [df['Smooth_Signal'].max(), resonance_freq_max, 1]
        popt, _ = curve_fit(gaussian, df['Frequency (MHz)'], df['Smooth_Signal'], p0=p0, maxfev=10000)
        resonance_freq_gauss = popt[1]  # The center parameter of the Gaussian is the resonance frequency
        print(f"Gaussian fit complete. Resonance frequency: {resonance_freq_gauss:.2f} MHz")
    except RuntimeError:
        resonance_freq_gauss = None
        print("Gaussian fit failed to converge.")
    
    # Method 3: Peak Detection
    # Find peaks in the signal
    print("Method 3: Performing peak detection")
    peaks, _ = find_peaks(df['Smooth_Signal'], distance=len(df)//10)
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
    max_color = 'green'
    gauss_color = 'red'
    peak_color = 'magenta'
    
    # Plot and annotate results from Maximum method
    plt.axvline(x=resonance_freq_max, color=max_color, linestyle='--')
    plt.annotate(f'Maximum: {resonance_freq_max:.2f} MHz', 
                 xy=(resonance_freq_max, df['Smooth_Signal'].max()),
                 xytext=(10, 30), textcoords='offset points',
                 color=max_color,
                 arrowprops=dict(arrowstyle="->", color=max_color))
    
    # Plot and annotate results from Gaussian fit (if successful)
    if resonance_freq_gauss is not None:
        plt.plot(df['Frequency (MHz)'], gaussian(df['Frequency (MHz)'], *popt), 'r-', label='Gaussian Fit')
        plt.axvline(x=resonance_freq_gauss, color=gauss_color, linestyle='--')
        plt.annotate(f'Gaussian: {resonance_freq_gauss:.2f} MHz', 
                     xy=(resonance_freq_gauss, df['Smooth_Signal'].max()),
                     xytext=(10, 60), textcoords='offset points',
                     color=gauss_color,
                     arrowprops=dict(arrowstyle="->", color=gauss_color))
    
    # Plot and annotate results from Peak detection (if a peak was found)
    if resonance_freq_peak is not None:
        plt.axvline(x=resonance_freq_peak, color=peak_color, linestyle='--')
        plt.annotate(f'Peak Detection: {resonance_freq_peak:.2f} MHz', 
                     xy=(resonance_freq_peak, df['Smooth_Signal'].max()),
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
    print(f"Resonance frequency (Maximum method): {resonance_freq_max:.2f} MHz")
    if resonance_freq_gauss is not None:
        print(f"Resonance frequency (Gaussian fit): {resonance_freq_gauss:.2f} MHz")
    else:
        print("Gaussian fit failed to converge.")
    if resonance_freq_peak is not None:
        print(f"Resonance frequency (Peak detection): {resonance_freq_peak:.2f} MHz")
    else:
        print("Peak detection did not find a clear peak.")

    # Display the plot (this will block until the plot window is closed)
    print("\nDisplaying plot...")
    plt.show()

    # Return the resonance frequencies found by each method
    return resonance_freq_max, resonance_freq_gauss, resonance_freq_peak

# Main execution block
if __name__ == "__main__":
    print(f"Starting analysis for file: {DATA_FILE}")
    resonance_max, resonance_gauss, resonance_peak = analyze_vacuum_resonance_data(DATA_FILE)
    print("\nAnalysis complete. Please review the plot and printed results to determine the most appropriate resonance frequency.")