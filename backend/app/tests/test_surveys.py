import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.survey import SurveyStatus
from app.models.database import surveys_db, create_survey, SurveyDB
import uuid
from datetime import datetime
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def test_survey():
    """Create a test survey in draft status"""
    survey_id = str(uuid.uuid4())
    survey = SurveyDB(
        id=survey_id,
        title="Test Survey",
        description="This is a test survey",
        questions=["Question 1", "Question 2"],
        status=SurveyStatus.DRAFT,
        form_url="https://docs.google.com/forms/d/test",
        form_id="test_form_id",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    surveys_db[survey_id] = survey
    return survey

@pytest.fixture
def approved_survey():
    """Create a test survey in approved status"""
    survey_id = str(uuid.uuid4())
    survey = SurveyDB(
        id=survey_id,
        title="Approved Survey",
        description="This is an approved survey",
        questions=["Question 1", "Question 2"],
        status=SurveyStatus.APPROVED,
        form_url="https://docs.google.com/forms/d/approved",
        form_id="approved_form_id",
        recipient_email="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    surveys_db[survey_id] = survey
    return survey

@pytest.fixture
def deleted_survey():
    """Create a test survey in deleted status"""
    survey_id = str(uuid.uuid4())
    survey = SurveyDB(
        id=survey_id,
        title="Deleted Survey",
        description="This is a deleted survey",
        questions=["Question 1", "Question 2"],
        status=SurveyStatus.DELETED,
        form_url="https://docs.google.com/forms/d/deleted",
        form_id="deleted_form_id",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    surveys_db[survey_id] = survey
    return survey

def test_list_surveys(test_survey, approved_survey, deleted_survey):
    """Test listing all surveys (excluding deleted ones by default)"""
    response = client.get("/api/surveys/")
    assert response.status_code == 200
    
    data = response.json()
    assert "surveys" in data
    assert len(data["surveys"]) == 2  # Excluding deleted survey
    
    # Test with including deleted
    response = client.get("/api/surveys/?skip_deleted=false")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["surveys"]) == 3  # Including deleted survey

def test_get_survey(test_survey):
    """Test getting a specific survey"""
    response = client.get(f"/api/surveys/{test_survey.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == test_survey.id
    assert data["title"] == test_survey.title
    assert data["status"] == "draft"

def test_get_nonexistent_survey():
    """Test getting a survey that doesn't exist"""
    response = client.get(f"/api/surveys/{uuid.uuid4()}")
    assert response.status_code == 404

@patch("app.services.google_forms.create_form")
def test_create_survey(mock_create_form):
    """Test creating a new survey"""
    # Mock the Google Forms API call
    mock_create_form.return_value = {
        "form_id": "test_form_id",
        "form_url": "https://docs.google.com/forms/d/test"
    }
    
    survey_data = {
        "title": "New Test Survey",
        "description": "This is a new test survey",
        "questions": ["Question 1", "Question 2", "Question 3"],
        "recipient_email": "recipient@example.com"
    }
    
    response = client.post("/api/surveys/", json=survey_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == survey_data["title"]
    assert data["status"] == "draft"
    assert "form_url" in data and data["form_url"] is not None

@patch("app.services.google_forms.send_email")
def test_approve_survey(mock_send_email, test_survey):
    """Test approving a survey"""
    # Mock the email sending
    mock_send_email.return_value = True
    
    approval_data = {
        "recipient_email": "recipient@example.com"
    }
    
    response = client.post(f"/api/surveys/{test_survey.id}/approve", json=approval_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"

@patch("app.services.google_forms.send_email")
def test_approve_already_approved_survey(mock_send_email, approved_survey):
    """Test approving an already approved survey (should fail)"""
    approval_data = {
        "recipient_email": "another@example.com"
    }
    
    response = client.post(f"/api/surveys/{approved_survey.id}/approve", json=approval_data)
    assert response.status_code == 400
    assert "already approved" in response.json()["detail"].lower()

def test_approve_deleted_survey(deleted_survey):
    """Test approving a deleted survey (should fail)"""
    approval_data = {
        "recipient_email": "test@example.com"
    }
    
    response = client.post(f"/api/surveys/{deleted_survey.id}/approve", json=approval_data)
    assert response.status_code == 400
    assert "cannot approve a deleted survey" in response.json()["detail"].lower()

def test_delete_survey(test_survey):
    """Test deleting a survey"""
    response = client.delete(f"/api/surveys/{test_survey.id}")
    assert response.status_code == 204
    
    # Verify it's now marked as deleted
    survey = surveys_db[test_survey.id]
    assert survey.status == SurveyStatus.DELETED 