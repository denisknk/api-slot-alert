import requests
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
import subprocess
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Email credentials and other private info
sender_email = "email@email.com"
receiver_email = sender_email  # same as sender_email if you want to send to yourself
google_password = "some_password"

# Array representing days to check
arr = [1, 2, 3, 4, 5]
success_count = 0

# URL and headers based on your curl request
url = 'https://your_url_here'
headers = {
  'all_headers_here': 'all_headers_here'
}

def get_current_volume():
    output = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"])
    return int(output.strip())

def set_volume(volume):
    command = f"osascript -e 'set volume output volume {volume}'"
    result = subprocess.call(command, shell=True)
    if result == 0:
        print(f"Volume successfully set to {volume}.")
    else:
        print("Failed to set volume.")

def check_response(response_data, day):
    try:
        data = json.loads(response_data)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON.")
        return False

    for obj in data:
        if obj.get('id_offices') == 151:
            print("day", day, "Current status ---- ", obj.get('sts'))
            if obj.get('sts') != 4:
                return True
    return False

def alert_user(day):
    original_volume = get_current_volume()
    loud_volume = 100

    set_volume(loud_volume)

    os.system(f'osascript -e \'display notification "{day} Exam slot available!" with title "Alert" sound name "Funk"\'')
    time.sleep(0.3)
    set_volume(original_volume)

def send_email_alert(day):
    subject = f"{day} Slot is available"
    body = f"{day} A slot is now available. Act fast!"
    recipients = [sender_email, receiver_email]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ', '.join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender_email, google_password)
        smtp_server.sendmail(sender_email, recipients, msg.as_string())

def check_dates():
    global success_count
    for day in arr:
        url = url_template.format(day)
        try:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                if check_response(response.text, day):
                    success_count += 1
                    alert_user(day)
                    send_email_alert(day)
            else:
                print(f"Failed to fetch data for {day}. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred for {day}: {e}")
        time.sleep(0.5)  # 500ms delay between each request

loop_count = 0
while True:
    loop_count += 1
    print(f"Starting loop {loop_count}... Success count: {success_count}")
    check_dates()
    print("Waiting 2 seconds...")
    time.sleep(2)
