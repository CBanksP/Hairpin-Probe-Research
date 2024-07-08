# User Inputs
DATA_FILE = 'vacuum_resonance_test_data.pkl'  # Name of the data file to analyze

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def lorentzian(x, a, x0, gam):
    return a * gam**2 / (gam**2 + (x - x0)**2)

def analyze_vacuum_resonance_data(data_file):
    # Load data
    df = pd.read_pickle(data_file)

    # Fit Lorentzian function
    popt, _ = curve_fit(lorentzian, df['Frequency (MHz)'], df['Signal'], 
                        p0=[df['Signal'].max(), df['Frequency (MHz)'].mean(), 1])
    
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

# Run the script
if __name__ == "__main__":
    resonance = analyze_vacuum_resonance_data(DATA_FILE)