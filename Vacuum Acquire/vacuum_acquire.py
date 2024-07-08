import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from windfreak_mini import SynthHDMini
import redpitaya_scpi as rp_scpi
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import os

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
    # ... [The rest of this function remains unchanged] ...

    plt.figure(figsize=(10, 6))
    plt.plot(df['Frequency (MHz)'], df['Signal'], 'b-')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Signal Amplitude')
    plt.title('Raw Data: Vacuum Resonance of Plasma Chamber')
    plt.grid(True)
    plt.savefig(f'{run_name}_raw_data_plot.png')
    plt.close()  # Close the plot to free up memory

    return df

def send_notification_email(subject, body, plot_path):
    if not SEND_EMAIL:
        print("Email notification skipped as SEND_EMAIL is set to False.")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the plot
    with open(plot_path, 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename(plot_path))
    msg.attach(image)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
    server.quit()

    print("Email notification sent with plot attached.")

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

    plot_path = f'{RUN_NAME}_raw_data_plot.png'
    send_notification_email(
        subject="Vacuum Resonance Data Acquisition Complete",
        body=f"The vacuum resonance data acquisition script '{RUN_NAME}' has finished running. The raw data plot is attached to this email.",
        plot_path=plot_path
    )