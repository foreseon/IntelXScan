import requests
import json
import os
import time
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Constants
LEAKS_API_URL = "https://4.intelx.io/"
LEAKS_API_KEY = ""  # Replace with your actual Leaks API key
GOOGLE_SHEETS_CREDENTIALS_FILE = 'credentials.json'  # Replace with your credentials file path
SPREADSHEET_ID = ''  # Replace with your actual spreadsheet ID
RANGE_NAME = 'SHEET_NAME!A:D'  # Replace with your actual range name
SLACK_TOKEN = ""  # Replace with your actual Slack token
SLACK_CHANNEL_ID = ""  # Replace with your actual Slack channel ID
LOCAL_STORAGE_PATH = ''  # Replace with your local storage path

# Ensure local storage path exists
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

# Function to fetch current data from the sheet
def fetch_current_sheet_data(service, spreadsheet_id, range_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get('values', [])

# Function to adjust and parse date string
def parse_date_string(date_str):
    date_str = date_str.rstrip('Z')  # Remove 'Z' if present
    if '.' in date_str:
        date_str, microseconds = date_str.split('.')
        microseconds = microseconds.ljust(6, '0')  # Pad microseconds to 6 digits
        date_str = f"{date_str}.{microseconds}"
    return datetime.fromisoformat(date_str)

# Function to initiate a search and get search_job_id
def initiate_search(selector):
    headers = {'x-key': LEAKS_API_KEY}
    params = {'selector': selector, 'limit': 2000000000}
    response = requests.get(f"{LEAKS_API_URL}live/search/internal", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to fetch search results using search_job_id and parse relevant data
def fetch_search_results(search_job_id):
    url = f"{LEAKS_API_URL}live/search/result?id={search_job_id}&format=1&k={LEAKS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if not isinstance(data, dict) or data.get('records') is None:
            print("No valid records found in the response.")
            return []

        # Extract 'linea' and 'added' fields from each record
        limit_date = datetime(2023, 1, 1)
        extracted_data = []
        for record in data['records']:
            linea = record.get('linea')
            added = record.get('item', {}).get('added')
            #date_obj = parse_date_string(added)
            if linea and added:
                extracted_data.append({'linea': linea, 'added': added})
        # Sort the extracted data by 'added' date
        return sorted(extracted_data, key=lambda x: x['added'])
    else:
        print(f"Error: {response.status_code}")
        return []

# Function to save specific data fields to local storage
def save_data_to_local_storage(data, filename):
    if data is None:
        print("No data to save.")
        return

    full_path = os.path.join(LOCAL_STORAGE_PATH, filename)

    # Save the data to a file
    with open(full_path, 'w') as file:
        try:
            json.dump(data, file)
        except json.JSONDecodeError as e:
            print(f"Error saving JSON data: {e}")

# Function to check if data has changed
def has_data_changed(data, filename):
    filepath = os.path.join(LOCAL_STORAGE_PATH, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as file:
                old_data = json.load(file)
                return old_data != data
        except json.JSONDecodeError as e:
            print(f"Error reading JSON data: {e}")
            return True
    else:
        return True

# Function to send Slack notification
def send_slack_notification(message, slack_token, channel_id):
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(channel=channel_id, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

def main():
    # Initialize Google Sheets API
    creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_FILE)
    service = build('sheets', 'v4', credentials=creds)

    # Fetch emails from Google Sheets
    emails = fetch_current_sheet_data(service, SPREADSHEET_ID, RANGE_NAME)

    # Check for leaks for each email in the Google Sheets
    for email_row in emails:
        if email_row:  # Check if the row is not empty
            time.sleep(3)  # Sleep for 3 seconds to avoid rate limiting
            email = email_row[0]
            search_job_id = initiate_search(email)
            if search_job_id:
                new_data = fetch_search_results(search_job_id)
                if new_data:
                    filename = f"{email}.json"
                    file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
                    old_data = []
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r') as file:
                                old_data = json.load(file)
                        except json.JSONDecodeError as e:
                            print(f"Error reading JSON data: {e}")

                    # Identify new leaks
                    new_leaks = [leak for leak in new_data if leak not in old_data]
                    if new_leaks:
                        print(new_leaks)
                        # Add new leaks to old data and sort
                        combined_data = old_data + new_leaks
                        combined_data_sorted = sorted(combined_data, key=lambda x: x['added'])
                        # Save updated data
                        save_data_to_local_storage(combined_data_sorted, filename)
                        # Send notification for new leaks
                        for leak in new_leaks:
                            send_slack_notification(f"New leak found for email {email}: {leak}", SLACK_TOKEN, SLACK_CHANNEL_ID)

if __name__ == "__main__":
    main()
