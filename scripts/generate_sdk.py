#!/usr/bin/env python
import os
import sys
import subprocess
import requests
import time
import tempfile
import shutil
import argparse
from pathlib import Path

def wait_for_backend(url, max_retries=10, retry_interval=2):
    """Wait for the backend to be ready"""
    print(f"Waiting for backend at {url} to be ready...")
    
    for i in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Backend is ready!")
                return True
        except requests.RequestException:
            pass
        
        print(f"Backend not ready. Retrying in {retry_interval} seconds...")
        time.sleep(retry_interval)
    
    print("Could not connect to backend.")
    return False

def generate_sdk(openapi_url, output_dir):
    """Generate SDK using openapi-generator-cli"""
    # Check if java is installed
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Java is required to run openapi-generator-cli.")
        print("Please install Java and try again.")
        return False
    
    # Get the openapi.json
    try:
        response = requests.get(openapi_url)
        if response.status_code != 200:
            print(f"Error: Failed to get OpenAPI spec from {openapi_url}")
            print(f"Status code: {response.status_code}")
            return False
        
        openapi_spec = response.text
    except requests.RequestException as e:
        print(f"Error: Failed to get OpenAPI spec from {openapi_url}")
        print(f"Exception: {e}")
        return False
    
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as tmp:
        tmp.write(openapi_spec)
        tmp_path = tmp.name
    
    # Download openapi-generator-cli
    generator_version = "6.6.0"
    generator_jar = f"openapi-generator-cli-{generator_version}.jar"
    generator_url = f"https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/{generator_version}/{generator_jar}"
    
    if not os.path.exists(generator_jar):
        print(f"Downloading openapi-generator-cli v{generator_version}...")
        try:
            response = requests.get(generator_url)
            with open(generator_jar, "wb") as f:
                f.write(response.content)
        except requests.RequestException as e:
            print(f"Error: Failed to download openapi-generator-cli")
            print(f"Exception: {e}")
            return False
    
    # Ensure output directory exists and is empty
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Run openapi-generator-cli
    print(f"Generating Python SDK in {output_dir}...")
    try:
        subprocess.run([
            "java", "-jar", generator_jar, "generate",
            "-i", tmp_path,
            "-g", "python",
            "-o", output_dir,
            "--package-name", "google_form_sdk",
            "--additional-properties=packageVersion=1.0.0"
        ], check=True)
        print(f"Successfully generated SDK in {output_dir}")
    except subprocess.SubprocessError as e:
        print(f"Error: Failed to generate SDK")
        print(f"Exception: {e}")
        return False
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
    
    return True

def install_sdk(sdk_dir):
    """Install the generated SDK"""
    print(f"Installing SDK from {sdk_dir}...")
    try:
        subprocess.run(["pip", "install", "-e", sdk_dir], check=True)
        print("SDK installed successfully!")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error: Failed to install SDK")
        print(f"Exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Python SDK for Google Forms Creation API")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="URL of the backend API")
    parser.add_argument("--output-dir", default="../sdk", help="Output directory for the SDK")
    parser.add_argument("--install", action="store_true", help="Install the SDK after generation")
    
    args = parser.parse_args()
    
    backend_url = args.backend_url
    openapi_url = f"{backend_url}/openapi.json"
    output_dir = args.output_dir
    
    # Make output_dir absolute
    output_dir = os.path.abspath(output_dir)
    
    # Wait for backend to be ready
    if not wait_for_backend(backend_url):
        sys.exit(1)
    
    # Generate SDK
    if not generate_sdk(openapi_url, output_dir):
        sys.exit(1)
    
    # Install SDK if requested
    if args.install:
        if not install_sdk(output_dir):
            sys.exit(1)
    
    # Create a sample script
    sample_path = os.path.join(output_dir, "sample_usage.py")
    with open(sample_path, "w") as f:
        f.write("""#!/usr/bin/env python
import time
from google_form_sdk.api.surveys_api import SurveysApi
from google_form_sdk.api_client import ApiClient
from google_form_sdk.configuration import Configuration
from pprint import pprint

def main():
    # Configure API client
    config = Configuration(host="http://localhost:8000")
    client = ApiClient(config)
    surveys_api = SurveysApi(client)
    
    # Create a survey
    print("Creating a survey...")
    survey_data = {
        "title": "Sample Survey from SDK",
        "description": "This survey was created using the Python SDK",
        "questions": [
            "What is your favorite color?",
            "What is your favorite food?",
            "What is your favorite hobby?"
        ],
        "recipient_email": "recipient@example.com"
    }
    
    try:
        survey = surveys_api.create_survey(survey_data)
        print("Survey created successfully:")
        pprint(survey)
        
        # Get the survey by ID
        survey_id = survey["id"]
        print(f"\\nGetting survey with ID {survey_id}...")
        retrieved_survey = surveys_api.get_survey(survey_id)
        print("Retrieved survey:")
        pprint(retrieved_survey)
        
        # List all surveys
        print("\\nListing all surveys...")
        surveys = surveys_api.list_surveys()
        print(f"Found {len(surveys['surveys'])} surveys:")
        for s in surveys["surveys"]:
            print(f"- {s['title']} (ID: {s['id']}, Status: {s['status']})")
        
        # Approve the survey
        if retrieved_survey["status"] == "draft":
            print(f"\\nApproving survey with ID {survey_id}...")
            approval_data = {
                "recipient_email": "recipient@example.com"
            }
            approved_survey = surveys_api.approve_survey(survey_id, approval_data)
            print("Survey approved successfully:")
            pprint(approved_survey)
        
        # Delete the survey
        print(f"\\nDeleting survey with ID {survey_id}...")
        surveys_api.delete_survey(survey_id)
        print("Survey deleted successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
""")
    
    print(f"\nSDK generated successfully in {output_dir}")
    print(f"Sample usage script created at {sample_path}")
    print("\nTo use the SDK, install it with:")
    print(f"  pip install -e {output_dir}")
    print("\nThen you can import and use it in your Python code:")
    print("  from google_form_sdk.api.surveys_api import SurveysApi")
    print("  from google_form_sdk.api_client import ApiClient")
    print("  from google_form_sdk.configuration import Configuration")
    print("\nSee the sample script for a complete example.")

if __name__ == "__main__":
    main() 