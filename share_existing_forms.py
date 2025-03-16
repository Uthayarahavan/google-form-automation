import os
import sys
import json
from dotenv import load_dotenv
import logging

# Set up paths to go to the backend directory
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('form_sharing_script')

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

try:
    from app.services import google_forms
    from app.models import database
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.error("Make sure you run this script from the root directory of the project.")
    sys.exit(1)

def share_existing_forms():
    """Share all existing forms with the personal email account"""
    personal_email = os.getenv("EMAIL_USERNAME", "clashroyalur1319@gmail.com")
    logger.info(f"Starting to share existing forms with {personal_email}")
    
    # Get all surveys from the database
    surveys = database.list_surveys(skip_deleted=False)
    logger.info(f"Found {len(surveys)} surveys in the database")
    
    # Get credentials
    creds = google_forms.get_credentials()
    if not creds:
        logger.error("Failed to get Google API credentials")
        return False
    
    # Build Drive API service
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Track results
    successful = 0
    failed = 0
    already_shared = 0
    
    # Process each survey
    for survey in surveys:
        if not survey.form_id or survey.form_id.startswith("ERROR-") or survey.form_id.startswith("MOCK-"):
            logger.warning(f"Skipping survey '{survey.title}' with invalid form_id: {survey.form_id}")
            failed += 1
            continue
        
        try:
            # First check if the form is already shared with the user
            permissions = drive_service.permissions().list(fileId=survey.form_id).execute()
            is_already_shared = False
            
            for permission in permissions.get('permissions', []):
                if permission.get('emailAddress') == personal_email:
                    logger.info(f"Form '{survey.title}' is already shared with {personal_email}")
                    is_already_shared = True
                    already_shared += 1
                    break
            
            if not is_already_shared:
                # Share the form with the personal account
                drive_service.permissions().create(
                    fileId=survey.form_id,
                    sendNotificationEmail=True,
                    body={
                        'type': 'user',
                        'role': 'writer',  # 'writer' provides edit access including viewing responses
                        'emailAddress': personal_email
                    }
                ).execute()
                logger.info(f"Successfully shared form '{survey.title}' with {personal_email}")
                successful += 1
        except Exception as e:
            logger.error(f"Error sharing form '{survey.title}': {e}")
            failed += 1
    
    # Print summary
    logger.info("=" * 50)
    logger.info("SHARING SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total surveys processed: {len(surveys)}")
    logger.info(f"Successfully shared: {successful}")
    logger.info(f"Already shared: {already_shared}")
    logger.info(f"Failed to share: {failed}")
    logger.info("=" * 50)
    
    if successful > 0 or already_shared > 0:
        logger.info(f"To access your forms, go to https://docs.google.com/forms/ and log in with {personal_email}")
        logger.info("Then click on 'Shared with me' to see the forms")
        return True
    else:
        logger.error("No forms were successfully shared.")
        return False

def change_to_personal_account():
    """
    Sets the FORCE_OAUTH environment variable to True in the .env file,
    which forces the application to use OAuth authentication with your personal account
    instead of the service account.
    """
    env_file = os.path.join(backend_dir, '.env')
    personal_email = os.getenv("EMAIL_USERNAME", "clashroyalur1319@gmail.com")
    
    logger.info(f"Configuring application to use {personal_email} for creating forms")
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the FORCE_OAUTH setting
    updated_lines = []
    for line in lines:
        if line.startswith('FORCE_OAUTH='):
            updated_lines.append('FORCE_OAUTH=True\n')
        else:
            updated_lines.append(line)
    
    # Write the updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    logger.info("Updated .env file to force OAuth authentication with your personal account")
    logger.info("The next time you create a form, you'll be prompted to log in with your Google account")
    logger.info(f"Make sure to log in with {personal_email} when prompted")
    
    # Remove the token.pickle file to force re-authentication
    token_path = os.path.join(backend_dir, 'token.pickle')
    if os.path.exists(token_path):
        os.remove(token_path)
        logger.info("Removed existing authentication token to force re-authentication")
    
    return True

if __name__ == "__main__":
    logger.info("Google Forms Access Utility")
    logger.info("This script will help you access your forms and configure the application to use your personal account.")
    logger.info("=" * 80)
    
    # Share existing forms
    logger.info("1. Sharing existing forms with your personal account...")
    share_result = share_existing_forms()
    
    # Configure for personal account
    logger.info("\n2. Configuring application to use your personal account for creating forms...")
    config_result = change_to_personal_account()
    
    if share_result and config_result:
        logger.info("\nSUCCESS! The script has completed all tasks successfully.")
        logger.info("1. Your existing forms have been shared with your personal account.")
        logger.info("2. The application is now configured to use your personal account for creating new forms.")
        logger.info("\nNext steps:")
        logger.info("1. Restart the application")
        logger.info("2. When creating a new form, you'll be prompted to log in with your Google account")
        logger.info("3. Make sure to log in with clashroyalur1319@gmail.com")
        logger.info("4. Access your forms at https://docs.google.com/forms/")
    else:
        logger.warning("\nThe script completed with some issues.")
        logger.info("Please review the logs above for details.") 