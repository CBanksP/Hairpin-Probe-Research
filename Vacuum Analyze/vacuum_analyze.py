import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import linregress


# User input: Set the run name here
RUN_NAME = 'vacuum_resonance_nofilter_data'


# Construct the full path to the data file
DATA_FILE = os.path.join('..', 'Vacuum Acquire', f'{RUN_NAME}.pkl')


def gaussian(x, a, x0, sigma):
   return a * np.exp(-(x - x0)**2 / (2 * sigma**2))


def baseline_correction(x, y, degree=1):
   coeffs = np.polyfit(x, y, degree)
   baseline = np.polyval(coeffs, x)
   return y - baseline, baseline


def analyze_vacuum_resonance_data(data_file):
   print(f"Starting analysis of vacuum resonance data: {data_file}")


   # Check if the data file exists
   if not os.path.exists(data_file):
       print(f"Error: Data file '{data_file}' not found. Please ensure the file exists in the correct location.")
       return None, None, None


   try:
       df = pd.read_pickle(data_file)
       print(f"Data loaded. Shape: {df.shape}")
   except Exception as e:
       print(f"Error loading data file: {e}")
       return None, None, None
  
   # Baseline correction
   corrected_signal, baseline = baseline_correction(df['Frequency (MHz)'], df['Signal'])
   df['Corrected_Signal'] = corrected_signal
  
   # Apply Savitzky-Golay filter with adjusted parameters
   df['Smooth_Signal'] = savgol_filter(df['Corrected_Signal'], window_length=101, polyorder=3)
  
   print("Performing resonance detection using multiple methods...")


   # Method 1: Maximum Detection
   max_index = df['Smooth_Signal'].idxmax()
   resonance_freq_max = df['Frequency (MHz)'].iloc[max_index]
   print(f"Maximum method complete. Resonance frequency: {resonance_freq_max:.2f} MHz")
  
   # Method 2: Improved Gaussian Fit
   try:
       # Use the maximum point as initial guess
       p0 = [df['Smooth_Signal'].max(), resonance_freq_max, 10]
       popt, _ = curve_fit(gaussian, df['Frequency (MHz)'], df['Smooth_Signal'], p0=p0, maxfev=10000)
       resonance_freq_gauss = popt[1]
       print(f"Gaussian fit complete. Resonance frequency: {resonance_freq_gauss:.2f} MHz")
   except RuntimeError:
       resonance_freq_gauss = None
       print("Gaussian fit failed to converge.")
  
   # Method 3: Improved Peak Detection
   peaks, properties = find_peaks(df['Smooth_Signal'], height=0, prominence=0.01, width=5)
   if len(peaks) > 0:
       # Select the peak with the highest prominence
       best_peak = peaks[np.argmax(properties["prominences"])]
       resonance_freq_peak = df['Frequency (MHz)'].iloc[best_peak]
       print(f"Peak detection complete. Resonance frequency: {resonance_freq_peak:.2f} MHz")
   else:
       resonance_freq_peak = None
       print("Peak detection did not find a clear peak.")


   # Plotting
   plt.figure(figsize=(12, 8))
   plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', alpha=0.5, label='Raw Data')
   plt.plot(df['Frequency (MHz)'], df['Smooth_Signal'], 'g-', label='Smoothed Data')
   plt.plot(df['Frequency (MHz)'], baseline, 'k--', label='Baseline')
  
   max_color, gauss_color, peak_color = 'green', 'red', 'magenta'
  
   plt.axvline(x=resonance_freq_max, color=max_color, linestyle='--')
   plt.annotate(f'Maximum: {resonance_freq_max:.2f} MHz',
                xy=(resonance_freq_max, df['Smooth_Signal'].max()),
                xytext=(10, 30), textcoords='offset points',
                color=max_color,
                arrowprops=dict(arrowstyle="->", color=max_color))
  
   if resonance_freq_gauss is not None:
       plt.plot(df['Frequency (MHz)'], gaussian(df['Frequency (MHz)'], *popt), 'r-', label='Gaussian Fit')
       plt.axvline(x=resonance_freq_gauss, color=gauss_color, linestyle='--')
       plt.annotate(f'Gaussian: {resonance_freq_gauss:.2f} MHz',
                    xy=(resonance_freq_gauss, df['Smooth_Signal'].max()),
                    xytext=(10, 60), textcoords='offset points',
                    color=gauss_color,
                    arrowprops=dict(arrowstyle="->", color=gauss_color))
  
   if resonance_freq_peak is not None:
       plt.axvline(x=resonance_freq_peak, color=peak_color, linestyle='--')
       plt.annotate(f'Peak Detection: {resonance_freq_peak:.2f} MHz',
                    xy=(resonance_freq_peak, df['Smooth_Signal'].max()),
                    xytext=(10, 90), textcoords='offset points',
                    color=peak_color,
                    arrowprops=dict(arrowstyle="->", color=peak_color))
  
   plt.xlabel('Frequency (MHz)')
   plt.ylabel('Signal Amplitude')
   plt.title('Vacuum Resonance of Plasma Chamber')
   plt.grid(True)
   plt.legend()
   plt.tight_layout()
  
   # Save the plot in the same directory as the script
   plot_file = os.path.join(os.path.dirname(__file__), f'{RUN_NAME}_analysis_plot.png')
   plt.savefig(plot_file, dpi=300)
   print(f"Analysis plot saved as: {plot_file}")
   plt.show()


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


   return resonance_freq_max, resonance_freq_gauss, resonance_freq_peak


if __name__ == "__main__":
   print(f"Starting analysis for run: {RUN_NAME}")
   print(f"Data file: {DATA_FILE}")
   resonance_max, resonance_gauss, resonance_peak = analyze_vacuum_resonance_data(DATA_FILE)
   if resonance_max is not None:
       print("\nAnalysis complete. Please review the plot and printed results to determine the most appropriate resonance frequency.")
   else:
       print("\nAnalysis could not be completed due to errors. Please check the data file and try again.")

