import os
import pickle
import base64
import openai
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_VERSION = 'v1'
GMAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail_api(credentials_path, token_path):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, GMAIL_SCOPE)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', API_VERSION, credentials=creds)
    return service 

def fetch_recent_email(service):
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    message_id = results['messages'][0]['id']
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return message

def extract_email_body(email_details):
    try:
        email_data_encoded = email_details['payload']['body']['data']
    except KeyError:
        for part in email_details['payload']['parts']:
            if 'data' in part['body']:
                email_data_encoded = part['body']['data']
                break
        else:
            return "Unable to extract email body."

    email_data_decoded = base64.urlsafe_b64decode(email_data_encoded).decode('utf-8')
    return email_data_decoded

def generate_response(email_body):
    openai.api_key = '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'
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"reply this email with the most natural language and the most relevant response: {email_body}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def send_reply(service, original_email, response_text):
    sender_email = None
    for header in original_email['payload']['headers']:
        if header['name'] == 'From':
            sender_email = header['value']
            break

    if not sender_email:
        raise ValueError("Could not extract sender's email from the original message.")

    email_content = f"To: {sender_email}\n" \
                    f"Subject: GPT Auto Response\n\n" \
                    f"{response_text}"

    raw_response = base64.urlsafe_b64encode(email_content.encode('utf-8')).decode('utf-8')
    body = {'raw': raw_response, 'threadId': original_email['threadId']}
    sent_message = service.users().messages().send(userId='me', body=body).execute()
    return sent_message

if __name__ == '__main__':
    CREDENTIALS_PATH = 'C:\\Users\\mochalfa\\Downloads\\client_secret_525230611896-h16ui3amttdv9rg4j67v5efvs6bgfmmp.apps.googleusercontent.com.json'
    TOKEN_PATH = 'token.pickle'
    MY_EMAIL = 'blackalmondz@gmail.com'  # Replace with your actual email address

    try:
        service = authenticate_gmail_api(CREDENTIALS_PATH, TOKEN_PATH)
        print("Successfully authenticated with Gmail!")
        
        last_processed_email_id = None
        while True:
            recent_email = fetch_recent_email(service)
            recent_email_id = recent_email['id']

            sender_email = None
            for header in recent_email['payload']['headers']:
                if header['name'] == 'From':
                    sender_email = header['value']
                    break

            if sender_email != MY_EMAIL and recent_email_id != last_processed_email_id:
                email_body = extract_email_body(recent_email)
                print("Email Body:")
                print(email_body)

                response = generate_response(email_body)
                print("\nGenerated Response:")
                print(response)

                sent_message = send_reply(service, recent_email, response)
                print("\nReply sent with ID:", sent_message['id'])

                last_processed_email_id = recent_email_id

            time.sleep(1)

    except HttpError as error:
        print(f"An error occurred: {error}")
