import requests
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
import subprocess
from datetime import datetime

# URL and headers based on your curl request
url = 'https://your_url_here'
headers = {
  'all_headers_here': 'all_headers_here'
}

def get_current_volume():
    # Get the current system volume level
    output = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"])
    return int(output.strip())

def set_volume(volume):
    command = f"osascript -e 'set volume output volume {volume}'"
    result = subprocess.call(command, shell=True)
    if result == 0:
            print(f"Volume successfully set to {volume}.")
    else:
            print("Failed to set volume.")

def check_response(response_data):
    # Parse the response data as JSON
    try:
        data = json.loads(response_data)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON.")
        return False

    for obj in data:
         # Iterate through the data, if condition met, return True
        if obj.get('id_offices') == 151:
            print("Current status ---- ", obj.get('sts'))
            if obj.get('sts') != 4:
                return True
    return False

def alert_user():
    # tested on macOS
    original_volume = get_current_volume()
    loud_volume = 100  # Set this to your desired volume level (0-100)

    # Set the volume to loud
    set_volume(loud_volume)
    current_time = str(datetime.now())

    # Log the current time
    print(f"Current time: {current_time}")

    # Trigger the alert
    os.system('osascript -e \'display notification "SEP 4 - Exam slot available!" with title "Alert" sound name "Funk"\'')
    time.sleep(1)
    # Restore the original volume
    set_volume(original_volume)

def send_email_alert():
    subject = "Slot is available"
    body = "A slot is now available. Act fast!"
    sender_email = "some_email@here"
    receiver_email = sender_email # keep the same as sender_email if you want to send to yourself
    recipients = [sender_email, receiver_email]
    google_password = "123456789"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ', '.join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender_email, google_password)
        smtp_server.sendmail(sender_email, recipients, msg.as_string())

# Loop to repeatedly send the request
while True:
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            if check_response(response.text):
                alert_user()
                send_email_alert()
                # Do what you want to do on success here

                # uncomment break if you want to you Exit from the loop if the condition is met
                # break
            else:
                print("Condition not met, checking again...")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Set a time you want in seconds
    time.sleep(30)
