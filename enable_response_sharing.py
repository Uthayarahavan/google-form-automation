import os
import sys
import logging
from dotenv import load_dotenv

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
logger = logging.getLogger('form_response_sharing_script')

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

try:
    from app.services import google_forms
    from app.models import database
    from googleapiclient.discovery import build
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.error("Make sure you run this script from the root directory of the project.")
    sys.exit(1)

def enable_response_sharing_for_all_forms():
    """Enable public response sharing for all existing forms"""
    logger.info("Starting to enable response sharing for all forms")
    
    # Get all surveys from the database
    surveys = database.list_surveys(skip_deleted=False)
    logger.info(f"Found {len(surveys)} surveys in the database")
    
    # Get credentials
    creds = google_forms.get_credentials()
    if not creds:
        logger.error("Failed to get Google API credentials")
        return False
    
    # Build the Forms API service
    form_service = build('forms', 'v1', credentials=creds)
    
    # Track results
    successful = 0
    failed = 0
    skipped = 0
    response_urls = []
    
    # Process each survey
    for survey in surveys:
        if not survey.form_id or survey.form_id.startswith("ERROR-") or survey.form_id.startswith("MOCK-"):
            logger.warning(f"Skipping survey '{survey.title}' with invalid form_id: {survey.form_id}")
            skipped += 1
            continue
        
        try:
            # Update form settings to make responses visible to anyone with the link
            update_request = {
                'requests': [{
                    'updateSettings': {
                        'settings': {
                            'quizSettings': {
                                'isQuiz': False
                            },
                            'responseSettings': {
                                'responseViewerSetting': 'ANYONE_WITH_LINK'
                            }
                        },
                        'updateMask': 'responseSettings.responseViewerSetting'
                    }
                }]
            }
            
            # Execute the update
            form_service.forms().batchUpdate(formId=survey.form_id, body=update_request).execute()
            
            # Generate the response URL
            response_url = f"https://docs.google.com/forms/d/{survey.form_id}/viewanalytics"
            response_urls.append({
                "title": survey.title,
                "response_url": response_url
            })
            
            logger.info(f"Successfully enabled response sharing for '{survey.title}'")
            logger.info(f"Response summary URL: {response_url}")
            successful += 1
            
            # Also update the survey in the database
            survey.response_url = response_url
            database.update_survey(survey.id, survey)
            
        except Exception as e:
            logger.error(f"Error updating form '{survey.title}': {e}")
            failed += 1
    
    # Print summary
    logger.info("=" * 50)
    logger.info("RESPONSE SHARING SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total surveys processed: {len(surveys)}")
    logger.info(f"Successfully updated: {successful}")
    logger.info(f"Failed to update: {failed}")
    logger.info(f"Skipped (invalid forms): {skipped}")
    logger.info("=" * 50)
    
    # Print response URLs
    if successful > 0:
        logger.info("\nRESPONSE URLs (share these with anyone who needs to see responses):")
        for item in response_urls:
            logger.info(f"• {item['title']}: {item['response_url']}")
        return True
    else:
        logger.error("No forms were successfully updated.")
        return False

if __name__ == "__main__":
    logger.info("Google Forms Response Sharing Enabler")
    logger.info("This script will make form responses visible to anyone with the link.")
    logger.info("=" * 80)
    
    # Enable response sharing for all forms
    success = enable_response_sharing_for_all_forms()
    
    if success:
        logger.info("\nSUCCESS! Response sharing has been enabled for your forms.")
        logger.info("You can now share the response URLs with anyone who needs to see the responses.")
        logger.info("Recipients will be able to see response summaries without needing a Google account.")
    else:
        logger.warning("\nThe script completed with some issues.")
        logger.info("Please review the logs above for details.") 