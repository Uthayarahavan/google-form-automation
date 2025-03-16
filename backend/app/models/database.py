from typing import Dict, List, Optional
from app.models.survey import SurveyDB, SurveyStatus
import json
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Define IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# In-memory storage
surveys_db: Dict[str, SurveyDB] = {}

# Parse DATABASE_URL for file path if it's a sqlite URL
database_url = os.getenv('DATABASE_URL', 'sqlite:///./forms.db')
if database_url.startswith('sqlite:///'):
    # Extract the path part from the URL
    path = database_url.replace('sqlite:///', '')
    
    # If it's a relative path, make it absolute
    if not os.path.isabs(path):
        # Handle ./ at the beginning of the path
        if path.startswith('./'):
            path = path[2:]
        path = os.path.join(os.path.dirname(__file__), '..', '..', path)
    
    # The database is a file, we'll use a corresponding JSON file next to it
    DB_FILE = os.path.splitext(path)[0] + '.json'
else:
    # Default file path for persistence
    DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'surveys.json')

# Print for debugging
print(f"Using database file: {DB_FILE}")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def _get_ist_now():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

def _serialize_datetime(obj):
    """Helper function to serialize datetime objects to ISO format for JSON storage"""
    if isinstance(obj, datetime):
        # If the datetime is naive (no timezone), assume it's in IST
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=IST)
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def _serialize_survey(survey: SurveyDB) -> dict:
    """Convert a SurveyDB model to a JSON-serializable dict"""
    survey_dict = survey.dict()
    survey_dict["created_at"] = _serialize_datetime(survey.created_at)
    survey_dict["updated_at"] = _serialize_datetime(survey.updated_at)
    survey_dict["status"] = survey.status.value
    return survey_dict

def _deserialize_survey(survey_dict: dict) -> SurveyDB:
    """Convert a dict to a SurveyDB model"""
    survey_dict["status"] = SurveyStatus(survey_dict["status"])
    # Parse datetime strings with timezone info
    survey_dict["created_at"] = datetime.fromisoformat(survey_dict["created_at"])
    survey_dict["updated_at"] = datetime.fromisoformat(survey_dict["updated_at"])
    return SurveyDB(**survey_dict)

def save_to_file():
    """Save the in-memory database to a file"""
    serialized_surveys = {
        survey_id: _serialize_survey(survey)
        for survey_id, survey in surveys_db.items()
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(serialized_surveys, f, indent=2)

def load_from_file():
    """Load the database from a file"""
    global surveys_db
    
    if not os.path.exists(DB_FILE):
        surveys_db = {}
        return
        
    try:
        with open(DB_FILE, 'r') as f:
            serialized_surveys = json.load(f)
            
        surveys_db = {
            survey_id: _deserialize_survey(survey_dict)
            for survey_id, survey_dict in serialized_surveys.items()
        }
    except (json.JSONDecodeError, FileNotFoundError):
        surveys_db = {}

# Try to load existing data on module initialization
try:
    load_from_file()
except Exception as e:
    print(f"Error loading database: {e}")
    surveys_db = {}

# Survey CRUD operations
def create_survey(survey: SurveyDB) -> SurveyDB:
    surveys_db[survey.id] = survey
    save_to_file()
    return survey

def get_survey(survey_id: str) -> Optional[SurveyDB]:
    return surveys_db.get(survey_id)

def update_survey(survey_id: str, updated_survey: SurveyDB) -> Optional[SurveyDB]:
    if survey_id in surveys_db:
        updated_survey.updated_at = _get_ist_now()
        surveys_db[survey_id] = updated_survey
        save_to_file()
        return updated_survey
    return None

def delete_survey(survey_id: str) -> bool:
    if survey_id in surveys_db:
        survey = surveys_db[survey_id]
        survey.status = SurveyStatus.DELETED
        survey.updated_at = _get_ist_now()
        save_to_file()
        return True
    return False

def list_surveys(skip_deleted: bool = True) -> List[SurveyDB]:
    if skip_deleted:
        return [
            survey for survey in surveys_db.values()
            if survey.status != SurveyStatus.DELETED
        ]
    return list(surveys_db.values()) 