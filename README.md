# IntelXScan Script Usage Documentation

## Overview
IntelXScan is a Python script designed to monitor and alert on data leaks. It reads keywords (such as domains, emails, IPs) from a specified Google Sheet, fetches data from IntelX (a data leak platform), and checks for new or additional leaks compared to previously stored data. If new leaks are found, it sends notifications to a configured Slack channel and saves all leaks in local storage for future comparisons.

![IntelXScan](https://github.com/foreseon/IntelXScan/assets/25774631/a5f976e6-f31e-4069-895d-84c97e5b0827)

## Setup and Configuration

### Prerequisites
- Python 3.x installed.
- Access to Google Sheets API.
- A Slack workspace with permissions to create a bot.
- An IntelX account with an API key.

### Steps

#### 1. Google Sheets API Setup
1. **Enable Google Sheets API**: Visit the [Google Developers Console](https://console.developers.google.com/), create a new project, and enable the Google Sheets API for it.
2. **Create Credentials**: In the API & Services dashboard, create credentials for a service account. Download the JSON file containing the credentials.
3. **Share Your Sheet**: Share your Google Sheet with the email address of the service account.

#### 2. Slack Bot Setup
1. **Create a Slack App**: Go to your Slack API [dashboard](https://api.slack.com/apps), create a new app, and assign it to your workspace.
2. **Add Bot User**: In the Slack app settings, add a bot user.
3. **Install App to Workspace**: Install the app to your workspace to generate a Slack token.
4. **Permissions**: Ensure the bot has permissions to post messages.

#### 3. IntelX API Key
Obtain your IntelX API key from your IntelX account settings.

#### 4. Script Configuration
1. **Clone the Repository**: Clone the IntelXScan repository from GitHub.
2. **Install Dependencies**: Install required Python packages (`requests`, `google-auth`, `google-api-python-client`, `slack_sdk`).
3. **Configure the Script**:
   - Replace `LEAKS_API_KEY` with your IntelX API key.
   - Place the downloaded Google Sheets credentials JSON in the script's directory and update `GOOGLE_SHEETS_CREDENTIALS_FILE` with its path.
   - Update `SPREADSHEET_ID` and `RANGE_NAME` with the ID and range of your Google Sheet.
   - Replace `SLACK_TOKEN` and `SLACK_CHANNEL_ID` with your Slack bot token and channel ID.
   - Update `LOCAL_STORAGE_PATH` to the desired path for storing leak data.

#### 5. Running the Script
Execute the script using Python. It's recommended to run the script multiple times initially to accumulate all existing leaks.

```bash
python IntelXScan.py
```

## Script Runtime Behavior
- **Data Fetching**: The script reads keywords from the specified Google Sheet range.
- **Leak Checking**: For each keyword, it queries the IntelX API for leaks and parses the results.
- **Comparison and Notification**:
  - Compares new data with previously stored leaks.
  - Identifies new leaks and appends them to the stored data.
  - Sends a Slack notification for each new leak.
- **Data Storage**: Saves the updated leak data in local storage for future comparisons.
- **Rate Limiting**: Includes a delay between requests to avoid rate limiting.

## Notes
- Due to potential inconsistencies in the IntelX API responses, it's advised to run the script multiple times initially to ensure comprehensive data collection.
- Ensure the script has appropriate permissions to access and modify files in the specified local storage path.
- Regularly update the script and dependencies to maintain compatibility and security.
