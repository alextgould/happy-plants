"""
This script sends emails from a Gmail account.

~ Pre-requisites ~

To use Google's Gmail API, you need to first create a Google Cloud Project, enable the Gmail API within the project, and create some OAuth 2.0 credentials

Step 1: Create a Google Cloud Project
  - Go to [Google Cloud Console](https://console.cloud.google.com)
  - (optional) Swap to the new Gmail account you created (top right)
  - Select a project (top left; will be set to the last active project or "Select a project" if you don't have any existing ones)
    > "New Project" > add a name (e.g. "Gmail SMTP OAuth2") > Create > (wait a moment) Select project
  - Can use a generic name and reuse this project across multiple apps that require access to the same gmail, or name it specific to the app
    (more secure but more effort); recommendation is to make a generic until such time as you need it to be specific (due to scale, multiple users etc)
  - optionally rename the project ID to make it easier to type/remember/read

Step 2: Enable the Gmail API
  - (within project) APIs & Services > Library > Gmail API (under "Google Workspace or use search box) > Enable

Step 3: Create OAuth 2.0 Credentials
  - APIs & Services > Credentials
  - (if prompted) Configure Consent Screen > Get started
    - App Information: Fill in app name (e.g. Alex Gould's blog) and user support email (your new Gmail address) > Next
    - Audience: External
    - Contact Information: your new Gmail address
  - Create OAuth client > Application Type: "Desktop App" > Name (e.g. happy-plants) > Create > Download JSON (save as credentials.json in .config folder)
  - In Audience add your email as a "test user"
    - using Internal instead of External could avoid this step, but requires a Google Workspace subscription

The credentials.json file contains:
* client_id: Identifies your app to Google.
* client_secret: Used to authenticate your app.
* project_id: The project associated with your Google API client.
* auth_uri: URL to initiate the OAuth2 authorization flow.
* token_uri: URL used to exchange the authorization code for an access token.
* auth_provider_x509_cert_url: URL for Google's public certificates to verify the authentication token.
* redirect_uris: The URI(s) used during the OAuth2 flow (usually your local or cloud redirect URI)

The code below uses this file to authenticate the app as an authorised client to allow OAuth authentication.
Once the app is authenticated, it creates a token.json file. This file contains a short-lived (2 hour) access_token to authenticate API requests 
and a long-lived refresh_token that allows the script to obtain new access tokens without requiring manual login.

The first time the script is run, a manual login is required. You'll see "You've been given access to an app that's currently being tested. 
You should only continue if you know the developer that invited you." > Continue

When deployed to the cloud, our options are:
a) authenticate locally, then manually upload token.json to the cloud server
b) SSH into the server and run the script (if using a headless server, use --no-launch-browser and copy the auth URL to a local browser)
(note for some APIs you can alternatively use a Service Account, but this approach doesn't work with the Gmail API)
"""

import os  # Handle environment variables and file paths
import base64  # Encode authentication strings
from google.auth.transport.requests import Request  # Refresh OAuth2 tokens
from google.oauth2.credentials import Credentials  # Handle OAuth2 credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # OAuth2 authentication flow
from email.mime.text import MIMEText  # Create email body
from email.mime.multipart import MIMEMultipart  # Create multipart email
from email.mime.image import MIMEImage # Image attachments
from email.mime.application import MIMEApplication # General attachments
import smtplib  # Send email via SMTP

# Logging setup
import logging
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CRED_PATH = os.path.join(PROJECT_ROOT, ".config")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", os.path.join(CRED_PATH, "credentials.json")) # Saved when you create an OAuth client (see "Pre-requisites comments at the top")
TOKEN_FILE = os.path.join(CRED_PATH, "token.json")  # File to store OAuth2 tokens
SCOPES = ["https://mail.google.com/"]  # Full access to send emails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def _get_credentials() -> Credentials:
    """Obtain and refresh OAuth2 credentials as needed."""

    creds = None
    
    # Load existing credentials if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or obtain new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    
    return creds

def send_email(sender_email: str = "alexgouldblog@gmail.com",
               receiver_email: str = "alextgould@gmail.com",
               subject: str = "Test email",
               body: str = "This is a test email",
               attach_path: str = None) -> None:
    """Send an email using Gmail SMTP with OAuth2 authentication."""

    creds = _get_credentials()
    
    # Generate OAuth2 authentication string
    auth_string = base64.b64encode(f"user={sender_email}\x01auth=Bearer {creds.token}\x01\x01".encode()).decode()
    
    # Create email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attach_path:
        with open(attach_path, 'rb') as file:
            if attach_path.endswith('.png') or attach_path.endswith('.jpg') or attach_path.endswith('.jpeg'):
                mimefile = MIMEImage(file.read(), name=attach_path)
            else:
                mimefile = MIMEApplication(file.read())
                mimefile.add_header('Content-Disposition', 'attachment', filename=attach_path)
            msg.attach(mimefile)
            
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.docmd("AUTH", "XOAUTH2 " + auth_string)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

# for local testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # try sending a basic test email
    if False:
        send_email()

    # test sending an email with an image attached
    if True:
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)
        import create_plots
        image_path = os.path.join(PROJECT_ROOT, 'img', "forecast.png")
        create_plots.plot_forecast(image_path=image_path)
        send_email(subject="Test attaching an image", body="Here is today's rainfall forecast (see image attached)", attach_path=image_path)