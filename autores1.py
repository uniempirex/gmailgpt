import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the Gmail API version and OAuth2.0 scope
API_VERSION = 'v1'
GMAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail_api(credentials_path, token_path):
    # ... [This part remains unchanged] ...

def fetch_recent_email(service):
    # ... [This part remains unchanged] ...

def extract_email_body(email_details):
    """
    Extract the body content of an email from its details.
    
    Args:
    - email_details (dict): Details of the email fetched from the Gmail API.
    
    Returns:
    - str: Decoded email body content.
    """
    email_data_encoded = email_details['payload']['body']['data']
    email_data_decoded = base64.urlsafe_b64decode(email_data_encoded).decode('utf-8')
    return email_data_decoded

if __name__ == '__main__':
    # Path to the OAuth 2.0 credentials JSON file you downloaded
    CREDENTIALS_PATH = 'C:/Users/mochalfa/Downloads/code.JSON'
    
    # Path to save the token.pickle file (you can choose any location)
    TOKEN_PATH = 'token.pickle'

    try:
        service = authenticate_gmail_api(CREDENTIALS_PATH, TOKEN_PATH)
        print("Successfully authenticated with Gmail!")
        
        # Fetch the most recent email
        recent_email = fetch_recent_email(service)
        
        # Extract and print the email body
        email_body = extract_email_body(recent_email)
        print(email_body)

    except HttpError as error:
        print(f"An error occurred: {error}")
