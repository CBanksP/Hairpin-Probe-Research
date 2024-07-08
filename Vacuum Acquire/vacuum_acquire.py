# User Inputs
RUN_NAME = 'vacuum_resonance_test'  # Name for the output data file
RP_HOST = 'rp-f0acab.local'  # Red Pitaya host name or IP address
MW_DEVICE = 'COM5'  # Windfreak SynthHD Mini COM port (Windows) or serial device (Linux)
MW_POWER_DB = 10.0  # Microwave generator power (dB)
MW_FREQUENCY_MIN_MHz = 1750  # Minimum frequency (MHz)
MW_FREQUENCY_MAX_MHz = 2500  # Maximum frequency (MHz)
MW_FREQUENCY_STEP_MHz = 0.1  # Frequency step size (MHz)
AVERAGES = 5  # Number of readings to average at each frequency

# Import necessary libraries
import numpy as np
import pandas as pd
from windfreak_mini import SynthHDMini
import redpitaya_scpi as rp_scpi

def acquire_vacuum_resonance_data(
    rp_host,
    mw_device,
    mw_power_dB,
    mw_frequency_min_MHz,
    mw_frequency_max_MHz,
    mw_frequency_step_MHz,
    averages,
    run_name
):
    # Connect to Red Pitaya
    rp = rp_scpi.scpi(rp_host)

    # Initialize Windfreak SynthHD Mini
    mw = SynthHDMini(mw_device)
    mw.enable()
    mw.set_power(mw_power_dB)

    # Generate frequency range
    frequencies = np.arange(mw_frequency_min_MHz, mw_frequency_max_MHz + mw_frequency_step_MHz, mw_frequency_step_MHz)

    # Initialize data storage
    probe_signals = []

    # Perform frequency sweep
    for freq in frequencies:
        mw.set_frequency(freq)
        
        # Acquire data (average of 'averages' readings)
        signal = 0
        for _ in range(averages):
            # Acquire a single data point from channel 2 (probe signal)
            rp.tx_txt('ACQ:START')
            rp.tx_txt('ACQ:STOP')
            signal += float(rp.txrx_txt('ACQ:SOUR2:DATA?').split(',')[1])
        signal /= averages
        
        probe_signals.append(signal)

    # Clean up
    rp.close()
    mw.enable(False)

    # Create DataFrame
    df = pd.DataFrame({'Frequency (MHz)': frequencies, 'Signal': probe_signals})

    # Save data
    df.to_pickle(f'{run_name}_data.pkl')

    print(f"Data acquisition complete. Data saved to {run_name}_data.pkl")

    return df

# Run the script
if __name__ == "__main__":
    data = acquire_vacuum_resonance_data(
        rp_host=RP_HOST,
        mw_device=MW_DEVICE,
        mw_power_dB=MW_POWER_DB,
        mw_frequency_min_MHz=MW_FREQUENCY_MIN_MHz,
        mw_frequency_max_MHz=MW_FREQUENCY_MAX_MHz,
        mw_frequency_step_MHz=MW_FREQUENCY_STEP_MHz,
        averages=AVERAGES,
        run_name=RUN_NAME
    )