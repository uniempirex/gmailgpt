import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the Gmail API version and OAuth2.0 scope
API_VERSION = 'v1'
GMAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail_api(credentials_path, token_path):
    """
    Authenticate with the Gmail API using OAuth 2.0 credentials.
    
    Args:
    - credentials_path (str): Path to OAuth 2.0 credentials JSON file.
    - token_path (str): Path to save the token.pickle file.
    
    Returns:
    - service: Authenticated Gmail API service.
    """
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials, authenticate using OAuth 2.0
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, GMAIL_SCOPE)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', API_VERSION, credentials=creds)
    return service

if __name__ == '__main__':
    # Path to the OAuth 2.0 credentials JSON file you downloaded
    CREDENTIALS_PATH = 'C:\\Users\\mochalfa\\Downloads\\client_secret_525230611896-h16ui3amttdv9rg4j67v5efvs6bgfmmp.apps.googleusercontent.com.json'
    
    # Path to save the token.pickle file (you can choose any location)
    TOKEN_PATH = 'token.pickle'

    try:
        service = authenticate_gmail_api(CREDENTIALS_PATH, TOKEN_PATH)
        print("Successfully authenticated with Gmail!")
    except HttpError as error:
        print(f"An error occurred: {error}")

