# User Inputs
RUN_NAME = 'vacuum_resonance_test'  # Name for the output data file
RP_HOST = 'rp-f0acab.local'  # Red Pitaya host name or IP address
MW_DEVICE = 'COM5'  # Windfreak SynthHD Mini COM port (Windows) or serial device (Linux)
MW_POWER_DB = 10.0  # Microwave generator power (dB)
MW_FREQUENCY_MIN_MHz = 1750  # Minimum frequency (MHz)
MW_FREQUENCY_MAX_MHz = 2500  # Maximum frequency (MHz)
MW_FREQUENCY_STEP_MHz = 0.1  # Frequency step size (MHz)
FREQUENCY_DECIMAL_PLACES = 2  # Number of decimal places for frequency
AVERAGES = 5  # Number of readings to average at each frequency
DELAY_BETWEEN_STEPS = 0.1  # Delay in seconds between frequency steps

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from windfreak_mini import SynthHDMini
import redpitaya_scpi as rp_scpi
import time

def acquire_vacuum_resonance_data(
    rp_host,
    mw_device,
    mw_power_dB,
    mw_frequency_min_MHz,
    mw_frequency_max_MHz,
    mw_frequency_step_MHz,
    frequency_decimal_places,
    averages,
    run_name,
    delay_between_steps
):
    # Connect to Red Pitaya
    rp = rp_scpi.scpi(rp_host)

    # Initialize Windfreak SynthHD Mini
    mw = SynthHDMini(mw_device)
    mw.enable()
    mw.set_power(mw_power_dB)

    # Generate frequency range and round to specified decimal places
    frequencies = np.round(np.arange(mw_frequency_min_MHz, mw_frequency_max_MHz + mw_frequency_step_MHz, mw_frequency_step_MHz), frequency_decimal_places)

    # Initialize data storage
    probe_signals = []
    error_frequencies = []

    # Perform frequency sweep
    total_steps = len(frequencies)
    for i, freq in enumerate(frequencies, 1):
        mw.set_frequency(freq)
        time.sleep(delay_between_steps)  # Add a small delay between steps
        
        # Acquire data (average of 'averages' readings)
        signal = 0
        error_occurred = False
        for _ in range(averages):
            try:
                # Acquire a single data point from channel 2 (probe signal)
                rp.tx_txt('ACQ:START')
                rp.tx_txt('ACQ:STOP')
                response = rp.txrx_txt('ACQ:SOUR2:DATA?')
                signal_value = float(response.split(',')[1])
                signal += signal_value
            except (ValueError, IndexError) as e:
                print(f"Error at frequency {freq:.{frequency_decimal_places}f} MHz: {str(e)}")
                print(f"Full response: {response}")
                error_occurred = True
                break
        
        if error_occurred:
            error_frequencies.append(freq)
            continue
        
        signal /= averages
        probe_signals.append(signal)

        # Print progress
        print(f"Frequency: {freq:.{frequency_decimal_places}f} MHz ({i}/{total_steps})")

    # Clean up
    rp.close()
    mw.enable(False)

    # Create DataFrame
    df = pd.DataFrame({'Frequency (MHz)': frequencies[~np.isin(frequencies, error_frequencies)], 'Signal': probe_signals})

    # Save data
    df.to_pickle(f'{run_name}_data.pkl')

    print(f"\nData acquisition complete. Data saved to {run_name}_data.pkl")
    if error_frequencies:
        print(f"Errors occurred at the following frequencies: {error_frequencies}")

    # Plot raw data
    plt.figure(figsize=(10, 6))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Raw Data: Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.savefig(f'{run_name}_raw_data_plot.png')
    plt.show()

    return df

# Run the script
if __name__ == "__main__":
    print("Starting data acquisition...")
    print(f"Frequency range: {MW_FREQUENCY_MIN_MHz} MHz to {MW_FREQUENCY_MAX_MHz} MHz")
    print(f"Step size: {MW_FREQUENCY_STEP_MHz} MHz")
    print(f"Frequency decimal places: {FREQUENCY_DECIMAL_PLACES}")
    print(f"Averages per frequency: {AVERAGES}")
    print(f"Delay between steps: {DELAY_BETWEEN_STEPS} seconds")
    print("----------------------------------------")

    data = acquire_vacuum_resonance_data(
        rp_host=RP_HOST,
        mw_device=MW_DEVICE,
        mw_power_dB=MW_POWER_DB,
        mw_frequency_min_MHz=MW_FREQUENCY_MIN_MHz,
        mw_frequency_max_MHz=MW_FREQUENCY_MAX_MHz,
        mw_frequency_step_MHz=MW_FREQUENCY_STEP_MHz,
        frequency_decimal_places=FREQUENCY_DECIMAL_PLACES,
        averages=AVERAGES,
        run_name=RUN_NAME,
        delay_between_steps=DELAY_BETWEEN_STEPS
    )

    print("Data acquisition script completed.")
    print(f"Raw data plot saved as {RUN_NAME}_raw_data_plot.png")