# User Inputs
DATA_FILE = 'vacuum_resonance_test_data.pkl'  # Name of the data file to analyze

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

def lorentzian(x, a, x0, gam):
    return a * gam**2 / (gam**2 + (x - x0)**2)

def analyze_vacuum_resonance_data(data_file):
    # Load data
    df = pd.read_pickle(data_file)

    # Find peaks to estimate initial parameters
    peaks, _ = find_peaks(df['Signal'], height=np.mean(df['Signal']))
    if len(peaks) > 0:
        max_peak = peaks[np.argmax(df['Signal'].iloc[peaks])]
        a_guess = df['Signal'].iloc[max_peak]
        x0_guess = df['Frequency (MHz)'].iloc[max_peak]
    else:
        a_guess = df['Signal'].max()
        x0_guess = df['Frequency (MHz)'].mean()
    
    gam_guess = (df['Frequency (MHz)'].max() - df['Frequency (MHz)'].min()) / 10

    # Fit Lorentzian function
    try:
        popt, pcov = curve_fit(lorentzian, df['Frequency (MHz)'], df['Signal'], 
                               p0=[a_guess, x0_guess, gam_guess],
                               maxfev=10000)  # Increase max function evaluations
        
        resonance_freq = popt[1]  # x0 parameter of the Lorentzian fit
        
        # Plot the data and fit
        plt.figure(figsize=(10, 6))
        plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', label='Data')
        plt.plot(df['Frequency (MHz)'], lorentzian(df['Frequency (MHz)'], *popt), 'r-', label='Lorentzian Fit')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Signal Amplitude')
        plt.title('Vacuum Resonance of Plasma Chamber')
        plt.grid(True)
        plt.legend()

        plt.plot(resonance_freq, lorentzian(resonance_freq, *popt), 'go', markersize=10)
        plt.annotate(f'Resonance: {resonance_freq:.2f} MHz', 
                     xy=(resonance_freq, lorentzian(resonance_freq, *popt)),
                     xytext=(10, 10), textcoords='offset points')

        plt.savefig(f'{data_file[:-4]}_analysis_plot.png')
        plt.show()

        print(f"Resonance frequency: {resonance_freq:.2f} MHz")
        return resonance_freq

    except RuntimeError as e:
        print(f"Curve fitting failed: {str(e)}")
        print("Plotting raw data for inspection...")
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-', label='Data')
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Signal Amplitude')
        plt.title('Vacuum Resonance of Plasma Chamber (Raw Data)')
        plt.grid(True)
        plt.legend()
        plt.savefig(f'{data_file[:-4]}_raw_data_plot.png')
        plt.show()
        
        return None

# Run the script
if __name__ == "__main__":
    resonance = analyze_vacuum_resonance_data(DATA_FILE)
    if resonance is not None:
        print(f"Analysis complete. Resonance frequency found at {resonance:.2f} MHz")
    else:
        print("Analysis could not determine a resonance frequency. Please inspect the raw data plot.")