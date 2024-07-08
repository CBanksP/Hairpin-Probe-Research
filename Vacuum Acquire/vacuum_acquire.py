import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from windfreak_mini import SynthHDMini
import redpitaya_scpi as rp_scpi
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# User Inputs
RUN_NAME = 'vacuum_resonance_test'
RP_HOST = 'rp-f0acab.local'
MW_DEVICE = 'COM5'
MW_POWER_DB = 10.0
MW_FREQUENCY_MIN_MHz = 1700
MW_FREQUENCY_MAX_MHz = 1850
MW_FREQUENCY_STEP_MHz = 0.1
FREQUENCY_DECIMAL_PLACES = 1
AVERAGES = 5
DELAY_BETWEEN_STEPS = 0.1
ESTIMATION_STEPS = 10

# Email notification settings
SEND_EMAIL = True  # Set to False to disable email notifications
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_email_password"
RECIPIENT_EMAIL = "recipient@example.com"

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
    delay_between_steps,
    estimation_steps
):
    rp = rp_scpi.scpi(rp_host)
    mw = SynthHDMini(mw_device)
    mw.enable()
    mw.set_power(mw_power_dB)

    frequencies = np.round(np.arange(mw_frequency_min_MHz, mw_frequency_max_MHz + mw_frequency_step_MHz, mw_frequency_step_MHz), frequency_decimal_places)

    probe_signals = []
    error_frequencies = []

    total_steps = len(frequencies)
    start_time = time.time()
    estimation_printed = False

    for i, freq in enumerate(frequencies, 1):
        mw.set_frequency(freq)
        time.sleep(delay_between_steps)
        
        signal = 0
        error_occurred = False
        for _ in range(averages):
            try:
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

        if i == estimation_steps and not estimation_printed:
            elapsed_time = time.time() - start_time
            time_per_step = elapsed_time / estimation_steps
            remaining_steps = total_steps - estimation_steps
            estimated_time_remaining = remaining_steps * time_per_step
            estimated_completion_time = datetime.now() + timedelta(seconds=estimated_time_remaining)
            
            print(f"\nEstimated time remaining: {timedelta(seconds=int(estimated_time_remaining))}")
            print(f"Estimated completion time: {estimated_completion_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            estimation_printed = True

    rp.close()
    mw.enable(False)

    df = pd.DataFrame({'Frequency (MHz)': frequencies[~np.isin(frequencies, error_frequencies)], 'Signal': probe_signals})
    df.to_pickle(f'{run_name}_data.pkl')

    print(f"\nData acquisition complete. Data saved to {run_name}_data.pkl")
    if error_frequencies:
        print(f"Errors occurred at the following frequencies: {error_frequencies}")

    plt.figure(figsize=(10, 6))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Raw Data: Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.savefig(f'{run_name}_raw_data_plot.png')
    plt.show()

    return df

def send_notification_email(subject, body):
    if not SEND_EMAIL:
        print("Email notification skipped as SEND_EMAIL is set to False.")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
    server.quit()

    print("Email notification sent.")

if __name__ == "__main__":
    print("Starting data acquisition...")
    print(f"Frequency range: {MW_FREQUENCY_MIN_MHz} MHz to {MW_FREQUENCY_MAX_MHz} MHz")
    print(f"Step size: {MW_FREQUENCY_STEP_MHz} MHz")
    print(f"Frequency decimal places: {FREQUENCY_DECIMAL_PLACES}")
    print(f"Averages per frequency: {AVERAGES}")
    print(f"Delay between steps: {DELAY_BETWEEN_STEPS} seconds")
    print(f"Email notifications: {'Enabled' if SEND_EMAIL else 'Disabled'}")
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
        delay_between_steps=DELAY_BETWEEN_STEPS,
        estimation_steps=ESTIMATION_STEPS
    )

    print("Data acquisition script completed.")
    print(f"Raw data plot saved as {RUN_NAME}_raw_data_plot.png")

    send_notification_email(
        subject="Vacuum Resonance Data Acquisition Complete",
        body=f"The vacuum resonance data acquisition script '{RUN_NAME}' has finished running."
    )