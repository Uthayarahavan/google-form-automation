from fastapi import APIRouter, HTTPException, Depends, status, Body, Query
from typing import List, Optional
from app.models.survey import (
    SurveyCreate, SurveyResponse, SurveyDB, SurveyStatus, 
    SurveyList, SurveyApprove, ErrorResponse
)
from app.models import database
from app.services import google_forms
from datetime import datetime
import os
import traceback

router = APIRouter()

@router.post("/surveys/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(survey_data: SurveyCreate):
    """
    Create a new survey in draft status.
    
    This endpoint:
    1. Parses and validates the questions.
    2. Creates a Google Form.
    3. Saves the metadata in the system.
    """
    try:
        # Create the form in Google Forms
        form_result = google_forms.create_form(
            title=survey_data.title,
            description=survey_data.description or "",
            questions=survey_data.questions
        )
        
        # Create a new survey in our database
        survey = SurveyDB(
            title=survey_data.title,
            description=survey_data.description,
            questions=survey_data.questions,
            form_url=form_result.get('form_url'),
            form_id=form_result.get('form_id'),
            response_url=form_result.get('response_url'),
            recipient_email=survey_data.recipient_email
        )
        
        # Save to database
        created_survey = database.create_survey(survey)
        
        return SurveyResponse(
            id=created_survey.id,
            title=created_survey.title,
            description=created_survey.description,
            status=created_survey.status,
            form_url=created_survey.form_url,
            response_url=created_survey.response_url,
            created_at=created_survey.created_at,
            updated_at=created_survey.updated_at,
            questions=created_survey.questions  # Include questions in the response
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create survey: {str(e)}"
        )

@router.get("/surveys/", response_model=SurveyList)
async def list_surveys(skip_deleted: bool = True):
    """
    Retrieve all surveys.
    """
    surveys = database.list_surveys(skip_deleted=skip_deleted)
    
    survey_responses = [
        SurveyResponse(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            status=survey.status,
            form_url=survey.form_url,
            response_url=survey.response_url,
            created_at=survey.created_at,
            updated_at=survey.updated_at,
            questions=survey.questions  # Include questions in the response
        ) for survey in surveys
    ]
    
    return SurveyList(surveys=survey_responses)

@router.get("/surveys/{survey_id}", response_model=SurveyResponse)
async def get_survey(survey_id: str):
    """
    Retrieve a specific survey by ID.
    """
    survey = database.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    return SurveyResponse(
        id=survey.id,
        title=survey.title,
        description=survey.description,
        status=survey.status,
        form_url=survey.form_url,
        response_url=survey.response_url,
        created_at=survey.created_at,
        updated_at=survey.updated_at,
        questions=survey.questions  # Include questions in the response
    )

@router.post("/surveys/{survey_id}/approve", response_model=SurveyResponse)
async def approve_survey(survey_id: str, approval_data: SurveyApprove):
    """
    Approve a survey and send email notifications to recipients.
    
    This endpoint:
    1. Changes the survey status from draft to approved.
    2. Sends emails to one or multiple recipients with the form URL.
    3. Supports custom email subject and body, or can use AI-generated content.
    """
    survey = database.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    # Check if the survey is already approved
    if survey.status == SurveyStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey is already approved"
        )
    
    # Check if the survey is deleted
    if survey.status == SurveyStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve a deleted survey"
        )
    
    # Process email recipients - support both single email and list of emails
    recipient_emails = []
    if approval_data.recipient_emails:
        recipient_emails = approval_data.recipient_emails
    elif approval_data.recipient_email:
        recipient_emails = [approval_data.recipient_email]
    
    # Validate that at least one recipient email is provided
    if not recipient_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recipient email is required"
        )
    
    # Set email subject and body - use user-provided or default
    email_subject = approval_data.email_subject or f"Survey: {survey.title}"
    
    # Determine email body
    email_body = ""
    if approval_data.email_body:
        # Use user-provided email body
        email_body = approval_data.email_body
    elif approval_data.use_ai_generated_content:
        try:
            # Use AI-generated content if requested
            email_body = generate_ai_email_content(survey, recipient_emails[0])
        except Exception as e:
            print(f"Error generating AI email content: {str(e)}")
            # Fall back to default if AI generation fails
            email_body = generate_default_email_body(survey)
    else:
        # Use default email body
        email_body = generate_default_email_body(survey)
    
    # Update the survey status and metadata
    survey.status = SurveyStatus.APPROVED
    survey.recipient_emails = recipient_emails
    survey.recipient_email = recipient_emails[0]  # Keep first email in legacy field for compatibility
    survey.email_subject = email_subject
    survey.email_body = email_body
    survey.updated_at = datetime.utcnow()
    
    # Update in the database
    updated_survey = database.update_survey(survey_id, survey)
    
    if not updated_survey:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update survey status"
        )
    
    # Send email notifications to all recipients
    email_status = "SUCCESS"
    email_detail = "Emails sent successfully"
    email_results = []
    
    try:
        # Send email to each recipient
        for recipient_email in recipient_emails:
            email_result = google_forms.send_email(
                recipient_email=recipient_email,
                form_url=survey.form_url,
                subject=email_subject,
                body=email_body
            )
            email_results.append(email_result)
            
            # If any email fails, update status
            if not email_result.get("success", False):
                email_status = "PARTIAL_SUCCESS"
                email_detail = f"Failed to send email to one or more recipients"
                print(f"Warning: Email notification failed for recipient {recipient_email}")
        
        # If all emails failed, update status to FAILED
        if all(not result.get("success", False) for result in email_results):
            email_status = "FAILED"
            email_detail = "Failed to send all email notifications"
            
    except Exception as e:
        email_status = "ERROR"
        email_detail = f"Error sending emails: {str(e)}"
        print(f"Error sending emails: {e}")
    
    # Create the response
    response = SurveyResponse(
        id=updated_survey.id,
        title=updated_survey.title,
        description=updated_survey.description,
        status=updated_survey.status,
        form_url=updated_survey.form_url,
        response_url=updated_survey.response_url,
        created_at=updated_survey.created_at,
        updated_at=updated_survey.updated_at,
        recipient_emails=updated_survey.recipient_emails,
        questions=updated_survey.questions  # Include questions in the response
    )
    
    # Add email status information to response (will be accessible via .dict())
    response_dict = response.dict()
    response_dict["email_status"] = email_status
    response_dict["email_detail"] = email_detail
    
    return response

@router.post("/surveys/{survey_id}/generate-email", response_model=dict)
async def generate_survey_email(survey_id: str):
    """
    Generate a fresh AI email for the survey without saving it.
    
    This endpoint always creates a brand new email draft using the Gemini API.
    """
    survey = database.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    try:
        # Add a timestamp to ensure a unique prompt each time
        timestamp = datetime.utcnow().isoformat()
        
        # Generate email content with a unique prompt variant each time
        email_body = generate_ai_email_content(
            survey, 
            recipient_email=None,  # We're just drafting, not sending
            unique_seed=timestamp  # Pass a unique seed to avoid caching
        )
        
        return {
            "email_body": email_body,
            "timestamp": timestamp,
            "success": True
        }
        
    except Exception as e:
        print(f"Error generating AI email: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI email: {str(e)}"
        )

def generate_default_email_body(survey):
    """Generate a default email body for the survey"""
    return f"""
Hello,

A new survey has been approved and is ready for your response:

Title: {survey.title}
Description: {survey.description or 'No description provided'}

Please click the following link to access the survey:
{survey.form_url}

Thank you for your participation!
"""

def generate_ai_email_content(survey, recipient_email, unique_seed=None):
    """Generate an AI-created email body using Google Gemini API"""
    try:
        # Debug: Print detailed survey details to verify questions are available
        print(f"\n==== GENERATING AI EMAIL FOR SURVEY ====")
        print(f"Survey ID: {survey.id}")
        print(f"Survey title: {survey.title}")
        print(f"Survey description: {survey.description}")
        print(f"Unique seed: {unique_seed}")
        
        # More detailed debugging for questions
        print(f"Survey has 'questions' attribute: {hasattr(survey, 'questions')}")
        
        questions_available = False
        if hasattr(survey, 'questions'):
            if survey.questions:
                print(f"Number of questions: {len(survey.questions)}")
                print(f"Questions content: {survey.questions}")
                for i, q in enumerate(survey.questions):
                    print(f"  Question {i+1}: {q}")
                questions_available = len(survey.questions) > 0
            else:
                print("Questions attribute exists but is empty or None")
        else:
            print("WARNING: Survey object has no 'questions' attribute. Email will be generic.")
            # Try to access questions as a dictionary if it's a dict-like object
            if hasattr(survey, "__getitem__") and "questions" in survey:
                print(f"Found questions in dictionary access: {survey['questions']}")
                if survey["questions"]:
                    questions_available = True
        
        # Check if Google Gemini integration is available
        try:
            import google.generativeai as genai
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
        except ImportError:
            print("Google Generative AI library not installed. Please install with: pip install google-generativeai")
            return generate_default_email_body(survey)
            
        # Get API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        if not api_key:
            print("GEMINI_API_KEY not found in environment variables")
            return generate_default_email_body(survey)
            
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Set up the model
        model = genai.GenerativeModel(model_name)
        
        # Add safety settings
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Add recipient email information to the prompt if available
        recipient_info = ""
        if recipient_email:
            recipient_info = f"- Recipient Email: {recipient_email}"
        
        # Format survey questions if available - enhanced version
        questions_section = ""
        questions_list = []
        
        if hasattr(survey, 'questions') and survey.questions and len(survey.questions) > 0:
            questions_list = [f"  {i+1}. {q}" for i, q in enumerate(survey.questions)]
            questions_formatted = "\n".join(questions_list)
            questions_section = f"""
Survey Questions:
{questions_formatted}
"""
            print(f"Added {len(questions_list)} questions to the prompt")
        # Backup way to get questions if attribute doesn't exist but has dict access
        elif hasattr(survey, "__getitem__") and "questions" in survey and survey["questions"]:
            questions_list = [f"  {i+1}. {q}" for i, q in enumerate(survey["questions"])]
            questions_formatted = "\n".join(questions_list)
            questions_section = f"""
Survey Questions:
{questions_formatted}
"""
            print(f"Added {len(questions_list)} questions to the prompt using dictionary access")
        else:
            print("WARNING: No questions available to include in the prompt. Email will be generic.")
        
        # Add unique seed to generate different results each time
        uniqueness_factor = f"\nGeneration ID: {unique_seed or datetime.utcnow().isoformat()}"
        
        # Enhanced prompt that emphasizes using the actual questions
        prompt = f"""
        Please create a professional and personalized email to invite someone to complete a survey.
        
        Survey details:
        - Title: {survey.title}
        - Description: {survey.description or 'No description provided'}
        - Survey Link: {survey.form_url}
        {recipient_info}
        {questions_section}
        {uniqueness_factor}
        
        The email should:
        1. Be polite and professional with a warm greeting
        2. Briefly explain the purpose of the survey based on its title and description
        3. IMPORTANT: Specifically mention at least 3 questions from the survey to give the recipient an idea of what to expect. Use the exact wording of the actual questions listed above.
        4. Emphasize the importance and value of the recipient's feedback
        5. Include the survey link prominently
        6. Thank the recipient for their time
        7. End with a professional sign-off
        8. Be concise but engaging (maximum 250 words)
        9. Create a NEW, FRESH draft each time - don't use a templated approach
        
        Format the email with proper spacing, include an appropriate greeting and sign-off.
        Make it feel personalized rather than generic.
        """
        
        # Debug: Print the complete prompt being sent to Gemini
        print("\n==== PROMPT BEING SENT TO GEMINI ====")
        print(prompt)
        print("=====================================\n")
        
        # Generate email content with slightly higher temperature for more creative variation
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings,
            generation_config={
                "temperature": 0.9,  # Increased temperature for more variety
                "top_p": 0.95,       # Increased top_p for more variety
                "top_k": 40,
                "max_output_tokens": 1000,
            }
        )
        
        # Extract the generated text
        email_body = response.text
        
        # Replace any placeholders with actual values if needed
        email_body = email_body.replace("[SURVEY LINK]", survey.form_url)
        email_body = email_body.replace("[SURVEY TITLE]", survey.title)
        
        print("\n==== GENERATED EMAIL ====")
        print(email_body[:100] + "..." if len(email_body) > 100 else email_body)
        print("===========================\n")
        
        return email_body
        
    except Exception as e:
        print(f"Error generating AI email content: {str(e)}")
        traceback.print_exc()  # Print full stack trace for debugging
        return generate_default_email_body(survey)

@router.delete("/surveys/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_id: str):
    """
    Mark a survey as deleted.
    """
    survey = database.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID {survey_id} not found"
        )
    
    # Mark as deleted
    success = database.delete_survey(survey_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete survey"
        )
    
    return None 