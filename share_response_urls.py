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
logger = logging.getLogger('form_response_urls_script')

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

try:
    from app.models import database
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.error("Make sure you run this script from the root directory of the project.")
    sys.exit(1)

def generate_response_urls():
    """Generate and display response URLs for all forms"""
    logger.info("Generating response URLs for all forms")
    
    # Get all surveys from the database
    surveys = database.list_surveys(skip_deleted=False)
    logger.info(f"Found {len(surveys)} surveys in the database")
    
    # Track results
    valid_forms = 0
    invalid_forms = 0
    response_urls = []
    
    # Process each survey
    for survey in surveys:
        if not survey.form_id or survey.form_id.startswith("ERROR-") or survey.form_id.startswith("MOCK-"):
            logger.warning(f"Skipping survey '{survey.title}' with invalid form_id: {survey.form_id}")
            invalid_forms += 1
            continue
        
        # Generate response URL and summary URL
        form_url = survey.form_url
        
        # Direct response URL for anyone to view
        response_url = f"https://docs.google.com/forms/d/{survey.form_id}/viewanalytics"
        
        # Also generate an embedded response URL that can be shared directly
        embedded_response_url = f"https://docs.google.com/forms/d/e/{survey.form_id}/viewanalytics?embedded=true"
        
        response_urls.append({
            "title": survey.title,
            "form_url": form_url,
            "response_url": response_url,
            "embedded_response_url": embedded_response_url
        })
        
        logger.info(f"Generated response URLs for '{survey.title}'")
        logger.info(f"  Form URL: {form_url}")
        logger.info(f"  Response URL: {response_url}")
        logger.info(f"  Embedded Response URL: {embedded_response_url}")
        
        # Also update the survey in the database with the response URL
        survey.response_url = response_url
        database.update_survey(survey.id, survey)
        
        valid_forms += 1
    
    # Print summary
    logger.info("=" * 50)
    logger.info("RESPONSE URLS SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total surveys processed: {len(surveys)}")
    logger.info(f"Valid forms with URLs: {valid_forms}")
    logger.info(f"Invalid forms skipped: {invalid_forms}")
    logger.info("=" * 50)
    
    # Create an HTML file with all the response links for easy sharing
    with open("response_links.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Survey Response Links</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        .survey { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .survey h2 { margin-top: 0; color: #3498db; }
        .links { margin-left: 20px; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .note { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #4CAF50; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Survey Response Links</h1>
    <div class="note">
        <p><strong>Note:</strong> These links allow anyone to view the response summaries for your surveys without needing to log in.</p>
        <p>Share these links with anyone who needs to see the survey responses.</p>
    </div>
""")
        
        for item in response_urls:
            f.write(f"""
    <div class="survey">
        <h2>{item['title']}</h2>
        <div class="links">
            <p><strong>Form URL:</strong> <a href="{item['form_url']}" target="_blank">{item['form_url']}</a></p>
            <p><strong>Response Summary:</strong> <a href="{item['response_url']}" target="_blank">{item['response_url']}</a></p>
            <p><strong>Embedded Response Summary:</strong> <a href="{item['embedded_response_url']}" target="_blank">{item['embedded_response_url']}</a></p>
        </div>
    </div>
""")
        
        f.write("""
</body>
</html>
""")
    
    logger.info(f"\nAn HTML file with all response links has been created: {os.path.abspath('response_links.html')}")
    
    return valid_forms > 0

if __name__ == "__main__":
    logger.info("Google Forms Response URL Generator")
    logger.info("This script will generate URLs for viewing form responses.")
    logger.info("=" * 80)
    
    # Generate response URLs
    success = generate_response_urls()
    
    if success:
        logger.info("\nSUCCESS! Response URLs have been generated.")
        logger.info("You can now share these URLs with anyone who needs to see the responses.")
        logger.info(f"A summary HTML file has been created at: {os.path.abspath('response_links.html')}")
        logger.info("Open this file in a browser to easily access and share all response links.")
    else:
        logger.warning("\nThe script completed with some issues.")
        logger.info("Please review the logs above for details.") 