import os
from typing import List, Dict, Any, Optional
import json
import logging
import sys
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import random
import time

# Import Google libraries but don't require them to work
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    GOOGLE_IMPORTS_AVAILABLE = True
except ImportError:
    GOOGLE_IMPORTS_AVAILABLE = False
    print("Google API libraries not available. Using mock mode only.")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('google_forms_service')

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the token.pickle file.
SCOPES = [
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]

TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'token.pickle')
CLIENT_SECRET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('GOOGLE_CLIENT_SECRET_FILE', '../credentials/client_secret.json')))
SERVICE_ACCOUNT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', '../credentials/service_account.json')))

# For debugging
logger.info(f"CLIENT_SECRET_PATH: {CLIENT_SECRET_PATH}")
logger.info(f"SERVICE_ACCOUNT_PATH: {SERVICE_ACCOUNT_PATH}")
logger.info(f"MOCK_API_CALLS: {os.getenv('MOCK_API_CALLS', 'False')}")

def get_credentials():
    """Get and refresh Google API credentials"""
    # Prioritize OAuth flow (personal account) over service account
    # Try OAuth flow first
    creds = None
    
    # Load the token.pickle file
    if os.path.exists(TOKEN_PATH):
        try:
            logger.info(f"Loading credentials from token file: {TOKEN_PATH}")
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
            logger.info("Successfully loaded credentials from token file")
        except Exception as e:
            logger.error(f"Error loading credentials from token file: {e}")
            logger.error(traceback.format_exc())
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
                logger.info("Successfully refreshed credentials")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                logger.error(traceback.format_exc())
        else:
            # Only show authentication instructions if we actually need to authenticate
            if not os.path.exists(CLIENT_SECRET_PATH):
                error_msg = f"client_secret.json not found at {CLIENT_SECRET_PATH}. Please download it from Google Cloud Console and place it in the credentials directory."
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            try:
                logger.info(f"Starting OAuth flow with client secrets from: {CLIENT_SECRET_PATH}")
                # Show authentication instructions only when we need to authenticate
                logger.info("=" * 80)
                logger.info("GOOGLE AUTHENTICATION REQUIRED")
                logger.info("=" * 80)
                logger.info("A browser window will open for Google authentication.")
                logger.info("If no window appears, check the console log for a URL to copy.")
                logger.info("Complete the Google sign-in process to continue.")
                logger.info("The form creation will continue automatically after authentication is complete.")
                logger.info("=" * 80)
                
                # Use a fixed port number to prevent port collisions
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_PATH, 
                    SCOPES
                )
                
                # Generate the auth URL with specific prompt options
                auth_url, _ = flow.authorization_url(
                    prompt='consent',
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                # Print the URL prominently so user can copy it if browser doesn't open
                logger.info("*" * 80)
                logger.info(f"AUTH URL: {auth_url}")
                logger.info("Copy and paste this URL in your browser if no window opens automatically")
                logger.info("*" * 80)
                
                # Try multiple browser opening approaches
                import webbrowser
                # Try to open with system default browser
                browser_opened = False
                try:
                    webbrowser.open(auth_url)
                    browser_opened = True
                    logger.info("Browser window opened successfully")
                except Exception as e:
                    logger.error(f"Error opening browser: {e}")
                    logger.error("Could not open browser automatically. Please use the URL printed above.")
                    
                if not browser_opened:
                    logger.warning("Could not open browser automatically. Please use the URL printed above.")
                
                logger.info("Waiting for authentication to complete...")
                try:
                    # Run with a fixed port
                    creds = flow.run_local_server(
                        port=8085,
                        open_browser=True,
                        success_message="Authentication successful! You can close this window and return to the application."
                    )
                    logger.info("Successfully completed OAuth flow!")
                    logger.info("*" * 80)
                    logger.info("AUTHENTICATION COMPLETE - You can now continue with form creation")
                    logger.info("*" * 80)
                except Exception as server_error:
                    logger.error(f"Error during local server flow: {server_error}")
                    logger.error("Authentication server timed out or encountered an error")
                    raise
                
                # Save the credentials for the next run
                try:
                    logger.info(f"Saving credentials to token file: {TOKEN_PATH}")
                    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
                    with open(TOKEN_PATH, 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("Successfully saved credentials to token file")
                except Exception as e:
                    logger.error(f"Error saving credentials to token file: {e}")
                    logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"Error during OAuth flow: {e}")
                logger.error(traceback.format_exc())
                logger.error("*" * 80)
                logger.error("AUTHENTICATION FAILED - Unable to complete Google authentication")
                logger.error("Please try again and make sure to complete the authentication in the browser")
                logger.error("*" * 80)
                
                # Only fall back to service account if OAuth fails
                if os.path.exists(SERVICE_ACCOUNT_PATH):
                    try:
                        logger.info(f"Falling back to service account credentials from {SERVICE_ACCOUNT_PATH}")
                        credentials = service_account.Credentials.from_service_account_file(
                            SERVICE_ACCOUNT_PATH, 
                            scopes=SCOPES
                        )
                        logger.info("Successfully loaded service account credentials as fallback")
                        return credentials
                    except Exception as sa_error:
                        logger.error(f"Error loading service account credentials: {sa_error}")
                        logger.error(traceback.format_exc())
                        raise e  # Re-raise the original OAuth error
                else:
                    raise
                
    return creds

def create_form(title: str, description: str, questions: List[str]) -> Dict[str, Any]:
    """
    Create a Google Form with the given title, description, and questions.
    The form is created using the user's personal Google account.
    The form is configured to allow anyone with the link to see response summaries.
    
    Parameters:
    - title: The title of the Google Form
    - description: The description of the Google Form (optional)
    - questions: A list of questions for the Google Form
    
    Returns:
    - Dictionary with form URL and form ID
    """
    try:
        logger.info(f"Creating Google Form: {title}")
        
        # Get credentials - this handles the OAuth flow with personal account
        creds = get_credentials()
        
        # Build the Forms API service
        form_service = build('forms', 'v1', credentials=creds)
        
        # Create form
        form = {
            'info': {
                'title': title,
                'documentTitle': title
            }
        }
        
        if description:
            form['info']['description'] = description
        
        # Create the initial form
        logger.info("Creating initial form")
        result = form_service.forms().create(body=form).execute()
        form_id = result['formId']
        logger.info(f"Form created with ID: {form_id}")
        
        # Batch update to add questions
        batch_update_request = {
            'requests': []
        }
        
        # Add all questions
        for i, question_text in enumerate(questions):
            batch_update_request['requests'].append({
                'createItem': {
                    'item': {
                        'title': question_text,
                        'questionItem': {
                            'question': {
                                'required': True,
                                'textQuestion': {
                                    'paragraph': True
                                }
                            }
                        }
                    },
                    'location': {
                        'index': i
                    }
                }
            })
        
        # Execute batch update
        logger.info(f"Adding {len(questions)} questions to form")
        form_service.forms().batchUpdate(formId=form_id, body=batch_update_request).execute()
        
        # Make the form viewable
        logger.info("Making form viewable to anyone with the link")
        drive_service = build('drive', 'v3', credentials=creds)
        drive_service.permissions().create(
            fileId=form_id,
            body={
                'role': 'reader',
                'type': 'anyone'
            }
        ).execute()
        logger.info("Permission set successfully")
        
        # Get the personal email for logging purposes
        personal_email = "Using personal Google account"
        try:
            # Try to get the email address of the currently logged in user
            profile = drive_service.about().get(fields="user").execute()
            personal_email = profile.get("user", {}).get("emailAddress", "personal account")
            logger.info(f"Form created with personal account: {personal_email}")
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
        
        # Get the form URL
        logger.info("Retrieving responder URI")
        form_info = form_service.forms().get(formId=form_id).execute()
        form_url = form_info.get('responderUri', '')
        if not form_url:
            # Fall back to constructed URL if responderUri is not available
            form_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
        
        # Also get the response summary URL
        response_url = f"https://docs.google.com/forms/d/{form_id}/viewanalytics"
        logger.info(f"Form URL: {form_url}")
        logger.info(f"Response URL: {response_url}")
        
        return {
            "success": True,
            "form_url": form_url,
            "response_url": response_url,
            "form_id": form_id,
            "edit_url": f"https://docs.google.com/forms/d/{form_id}/edit",
            "created_by": personal_email
        }
        
    except Exception as e:
        logger.error(f"Error creating form: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "form_url": f"There was an error connecting to Google Forms API. {str(e)}",
            "form_id": f"ERROR-{random.randint(100, 999)}",
            "error": str(e)
        }

def send_email(recipient_email: str, form_url: str = None, subject: str = None, body: str = None) -> Dict[str, Any]:
    """
    Send an email with the form URL to the recipient using the personal Gmail account.
    Uses Gmail API with authenticated user credentials.
    Falls back to SMTP if the Gmail API fails.
    
    Parameters:
    - recipient_email: The email address of the recipient
    - form_url: The Google Form URL (optional if body is provided and already contains the URL)
    - subject: Custom email subject (optional)
    - body: Custom email body (optional)
    """
    # Use provided subject or default
    email_subject = subject if subject else "New Survey Form Available"
    
    # Ensure form_url is in the body if provided
    form_url_included = False
    if form_url and body and form_url not in body:
        # If form_url is provided but not in the body, append it
        email_body = body + f"\n\nSurvey Link: {form_url}\n"
        form_url_included = True
    elif form_url and body and form_url in body:
        # If form URL is already in the provided body
        email_body = body
        form_url_included = True
    elif body:
        # If only body is provided (and might contain the form_url)
        email_body = body
        if form_url:
            form_url_included = form_url in body
    else:
        # Default body if nothing is provided
        email_body = f"""
Hello,

A new survey form has been created for you. Please click the link below to access it:

{form_url or "No survey link provided"}

Thank you for your participation!

This is an automated message, please do not reply.
"""
        form_url_included = bool(form_url)
    
    # Log whether form URL is included
    if form_url:
        if form_url_included:
            logger.info(f"Form URL is included in the email body: {form_url}")
        else:
            logger.warning(f"WARNING: Form URL may not be properly included in the email body: {form_url}")
    
    # Try using Gmail API first
    try:
        logger.info("Attempting to send email via Gmail API...")
        
        # Get personal account credentials
        creds = get_credentials()
        
        if creds is not None:
            # Build Gmail API service
            gmail_service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            from email.mime.text import MIMEText
            import base64
            
            # Create a message
            message = MIMEText(email_body)
            message['to'] = recipient_email
            message['subject'] = email_subject
            
            # Get the sender's email from Gmail profile
            try:
                profile = gmail_service.users().getProfile(userId='me').execute()
                sender_email = profile['emailAddress']
                message['from'] = sender_email
                logger.info(f"Using sender email from Gmail profile: {sender_email}")
            except Exception as e:
                logger.error(f"Error getting Gmail profile, using default sender: {e}")
                message['from'] = os.getenv("EMAIL_FROM", "formautomation@example.com")
            
            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send the message
            send_request = gmail_service.users().messages().send(
                userId='me', 
                body={'raw': encoded_message}
            )
            sent_message = send_request.execute()
            
            logger.info(f"Email sent via Gmail API, Message ID: {sent_message['id']}")
            
            return {
                "success": True,
                "email_status": "sent",
                "email_detail": f"Email successfully sent to {recipient_email} via Gmail API",
                "message_id": sent_message['id'],
                "form_url_included": form_url_included
            }
            
    except Exception as gmail_error:
        logger.warning(f"Gmail API error, falling back to SMTP: {gmail_error}")
        # Fall back to SMTP if Gmail API fails
    
    # Fall back to using SMTP
    try:
        # Log that we're sending an email
        logger.info(f"Sending email via SMTP to {recipient_email}")
        
        # Email parameters from environment
        email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        email_port = int(os.getenv("EMAIL_PORT", "587"))
        email_username = os.getenv("EMAIL_USERNAME", "")
        email_password = os.getenv("EMAIL_PASSWORD", "")
        email_from = os.getenv("EMAIL_FROM", "formautomation@example.com")
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = email_from
        msg["To"] = recipient_email
        msg["Subject"] = email_subject
        msg.attach(MIMEText(email_body, "plain"))
        
        try:
            # Connect to SMTP server and send email
            logger.info(f"Connecting to SMTP server: {email_host}:{email_port}")
            server = smtplib.SMTP(email_host, email_port)
            server.set_debuglevel(1)  # Add detailed SMTP logs
            server.starttls()
            
            # Log in to SMTP server
            if email_username and email_password:
                logger.info(f"Logging in to SMTP server with username: {email_username}")
                server.login(email_username, email_password)
            
            # Send email
            logger.info("Sending email message")
            result = server.send_message(msg)
            logger.info(f"SMTP server response: {result}")
            server.quit()
            logger.info("Email sent successfully via SMTP")
            
            return {
                "success": True,
                "email_status": "sent",
                "email_detail": f"Email successfully sent to {recipient_email} via SMTP",
                "form_url_included": form_url_included
            }
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return {
                "success": False,
                "email_status": "failed",
                "email_detail": f"SMTP error: {str(e)}",
                "form_url_included": form_url_included
            }
            
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "email_status": "error",
            "email_detail": f"Error: {str(e)}",
            "form_url_included": form_url_included
        } 