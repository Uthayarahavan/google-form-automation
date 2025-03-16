from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime, timezone, timedelta
import uuid

# Define IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

class SurveyStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DELETED = "deleted"

class QuestionType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    LINEAR_SCALE = "linear_scale"
    DATE = "date"
    TIME = "time"

class SurveyQuestion(BaseModel):
    question_text: str
    question_type: QuestionType = QuestionType.TEXT
    options: Optional[List[str]] = None
    required: bool = False

class SurveyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    questions: List[str] = Field(..., min_items=1)
    recipient_email: Optional[EmailStr] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Customer Satisfaction Survey",
                "description": "Please help us improve our services by answering a few questions",
                "questions": [
                    "How satisfied are you with our service?",
                    "Would you recommend our product to others?",
                    "What improvements would you suggest?"
                ],
                "recipient_email": "recipient@example.com"
            }
        }

class SurveyDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    questions: List[str]
    status: SurveyStatus = SurveyStatus.DRAFT
    form_url: Optional[str] = None
    form_id: Optional[str] = None
    response_url: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_emails: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    created_at: datetime = Field(default_factory=get_ist_now)
    updated_at: datetime = Field(default_factory=get_ist_now)

class SurveyResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: SurveyStatus
    form_url: Optional[str] = None
    response_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    email_status: Optional[str] = None
    email_detail: Optional[str] = None
    recipient_emails: Optional[List[str]] = None
    questions: Optional[List[str]] = None

class SurveyList(BaseModel):
    surveys: List[SurveyResponse]

class SurveyApprove(BaseModel):
    recipient_email: Optional[EmailStr] = None
    recipient_emails: Optional[List[EmailStr]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    use_ai_generated_content: Optional[bool] = False
    
    class Config:
        schema_extra = {
            "example": {
                "recipient_emails": ["recipient1@example.com", "recipient2@example.com"],
                "email_subject": "Please Complete Our Survey",
                "email_body": "We value your feedback. Please complete our survey at the link below.",
                "use_ai_generated_content": True
            }
        }

class ErrorResponse(BaseModel):
    detail: str 