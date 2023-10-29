import os
import pickle
import base64
import openai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the Gmail API version and OAuth2.0 scope
API_VERSION = 'v1'
GMAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail_api(credentials_path, token_path):
    # ... [The rest of the function's content] ...
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
    
def fetch_recent_email(service):
    # ... [The rest of the function's content] ...
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    message_id = results['messages'][0]['id']
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return message
def extract_email_body(email_details):
    """
    Extract the body content of an email from its details.
    
    Args:
    - email_details (dict): Details of the email fetched from the Gmail API.
    
    Returns:
    - str: Decoded email body content.
    """
    try:
        # If the email is simple and not multipart
        email_data_encoded = email_details['payload']['body']['data']
    except KeyError:
        # The email might be multipart, so we'll look for the 'parts' key
        for part in email_details['payload']['parts']:
            # We'll look for the part containing 'data'
            if 'data' in part['body']:
                email_data_encoded = part['body']['data']
                break
        else:
            # If we still can't find the data, return a default message
            return "Unable to extract email body."

    email_data_decoded = base64.urlsafe_b64decode(email_data_encoded).decode('utf-8')
    return email_data_decoded


def generate_response(email_body):
    """
    Generate a response based on the email body content using ChatGPT.
    
    Args:
    - email_body (str): The content of the email.
    
    Returns:
    - str: A response generated for the email.
    """
    openai.api_key = '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'  # Replace with your OpenAI API key

    response = openai.Completion.create(
      model="gpt-3.5-turbo-instruct",
      prompt=f"reply this email with the most natural language and the most relevant response: {email_body}",
      max_tokens=150  # Adjust as needed
    )
    
    return response.choices[0].text.strip()

def send_reply(service, original_email, response_text):
    """
    Send a reply to an email using the Gmail API.

    Args:
    - service: Authenticated Gmail API service.
    - original_email (dict): The original email to reply to.
    - response_text (str): The response text to send.

    Returns:
    - dict: The sent message details.
    """
    # Extract the sender's email from the original email to set as the recipient
    sender_email = None
    for header in original_email['payload']['headers']:
        if header['name'] == 'From':
            sender_email = header['value']
            break

    if not sender_email:
        raise ValueError("Could not extract sender's email from the original message.")

    # Create the email content with headers and body
    email_content = f"To: {sender_email}\n" \
                    f"Subject: Re: Automated Response\n\n" \
                    f"{response_text}"

    raw_response = base64.urlsafe_b64encode(email_content.encode('utf-8')).decode('utf-8')
    body = {
        'raw': raw_response,
        'threadId': original_email['threadId']
    }
    sent_message = service.users().messages().send(userId='me', body=body).execute()
    return sent_message

if __name__ == '__main__':
    # Path to the OAuth 2.0 credentials JSON file you downloaded
    CREDENTIALS_PATH = 'C:\\Users\\mochalfa\\Downloads\\client_secret_525230611896-h16ui3amttdv9rg4j67v5efvs6bgfmmp.apps.googleusercontent.com.json'
    
    # Path to save the token.pickle file (you can choose any location)
    TOKEN_PATH = 'token.pickle'

    try:
        service = authenticate_gmail_api(CREDENTIALS_PATH, TOKEN_PATH)
        print("Successfully authenticated with Gmail!")
        
        # Fetch the most recent email
        recent_email = fetch_recent_email(service)
        
        # Extract and print the email body
        email_body = extract_email_body(recent_email)
        print("Email Body:")
        print(email_body)

        # Generate and print the response
        response = generate_response(email_body)
        print("\nGenerated Response:")
        print(response)

        # Send the response as a reply to the original email
        sent_message = send_reply(service, recent_email, response)
        print("\nReply sent with ID:", sent_message['id'])

    except HttpError as error:
        print(f"An error occurred: {error}")
