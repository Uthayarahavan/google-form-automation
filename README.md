# Google Forms Creator Pro

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![AI-Powered](https://img.shields.io/badge/AI--Powered-Gemini-green)

A comprehensive platform for creating, managing, reviewing, and analyzing Google Forms with a modern UI, powerful backend, and Gemini AI integration for intelligent email generation.

## 📊 Project Highlights

- **Modern Dashboard**: Interactive analytics with visual representations
- **Complete Form Management**: Create, review, approve, distribute, and analyze
- **AI-Powered Email Generation**: Gemini AI creates personalized survey invitation emails
- **Streamlined Workflow**: Simplified process from form creation to response analysis
- **Developer-Friendly**: API-driven architecture with comprehensive documentation
- **Enterprise-Ready**: Scalable design with authentication and permissions

---

## 🌟 Features

### Survey Creation & Management
- Create professional surveys with multiple question types
- Add descriptions, section breaks, and instructions
- Real-time preview of form appearance
- Save forms as drafts or submit for approval
- Edit, duplicate, or delete existing surveys

### Review & Approval System
- Multi-stage approval workflow
- Comment and annotation capabilities
- Email notifications for approval status changes
- Audit trail of all form modifications
- Role-based permissions for approval actions

### AI-Powered Email Generation
- **Gemini AI Integration**: Uses Google's Gemini models to craft personalized emails
- Analyzes survey questions to create contextually relevant invitations
- Generates professional, engaging email content automatically
- Customizable templates that highlight key survey questions
- Human-editable drafts with AI-suggested content

### Distribution & Sharing
- Automatic email distribution to recipients
- AI-generated or customizable email templates
- Sharing options for form links
- Schedule survey distribution
- Track delivery status

### Response Analysis
- Real-time response monitoring
- Visual analytics and data export
- Response rate statistics
- Share results with non-Google users via response sharing scripts
- Secure storage of response data

### Modern UI
- Responsive design for all devices
- Colorful, intuitive interface
- Interactive charts and visualizations
- Accessibility-compliant components
- Dark mode support

---

## 🛠️ Technical Architecture

### Frontend
- **React 18**: Component-based UI architecture
- **Bootstrap 5**: Responsive layout and styling
- **Chart.js**: Interactive data visualization
- **React Router 6**: Client-side routing
- **React-Toastify**: User notifications

### Backend
- **FastAPI**: High-performance API framework
- **Google Forms API**: Deep integration with Google services
- **Google Gemini AI**: Intelligent email content generation
- **SQLite Database**: Local data storage
- **JWT Authentication**: Secure API access
- **Swagger Documentation**: Auto-generated API docs

### AI Integration
- **Google Generative AI**: Gemini 1.5 Flash model integration
- Context-aware prompt engineering
- Safety settings for content moderation
- Customizable generation parameters
- Fallback mechanism for offline operation

### Infrastructure
- **Python Virtual Environment**: Isolated Python dependencies
- **Node.js**: JavaScript runtime for frontend
- **PowerShell Scripts**: Automation for Windows
- **GitHub Actions**: CI/CD capabilities (optional)
- **Local Storage**: No external database required

---

## 📋 Prerequisites

- **Operating System**: Windows 10 or newer
- **Python**: Version 3.8 or higher
- **Node.js**: Version 14 or higher
- **npm**: Version 6 or higher
- **Google Account**: With API access enabled
- **Gemini API Key**: Required for AI email generation (optional)
- **Network**: Internet connection for Google API calls
- **Storage**: Minimum 500MB free space

---

## 🚀 Setup Instructions

### Prerequisites
- Windows operating system
- Python 3.8 or newer
- Node.js 14 or newer
- npm 6 or newer
- Google account with API access
- Internet connection

### First-time Setup

1. **Prepare environment:**
   - Ensure Python and Node.js are installed on your system
   - If not installed, the setup script will attempt to download and install them

2. **Configure Google API access:**
   - The application comes with sample credentials for testing
   - For production use, replace credential files in the `credentials/` directory
   - Required APIs: Google Forms API, Google Drive API, Gmail API

3. **Configure Gemini AI** (for email generation):
   - Obtain a Gemini API key from [Google AI Studio](https://ai.google.dev/)
   - Add the key to your backend/.env file:
     ```
     GEMINI_API_KEY=your_api_key_here
     GEMINI_MODEL=gemini-1.5-flash
     ```

4. **Run the setup:**
   - Double-click on `Setup.bat` to install all required dependencies
   - This will create Python virtual environment and install npm packages
   - The script will configure all necessary environment variables

5. **Verify installation:**
   - Check the logs directory for any error messages
   - Ensure both backend and frontend dependencies are installed

### Running the Application

1. **Start the application:**
   - Double-click on `StartMenu.bat` to launch the application
   - This will start both backend and frontend servers
   - Alternatively, run `start.ps1` in PowerShell for more options

2. **Access the application:**
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

3. **Log in:**
   - First-time use will require Google account authentication
   - Grant necessary permissions for the application to access Google Forms

## 💡 Features & Usage Guide

### Dashboard
- **Analytics Overview**: View total surveys, approval rates, and response statistics
- **Survey Status Distribution**: Visual breakdown of draft, approved, and deleted surveys
- **Activity Charts**: Track form creation and response trends over time
- **Recent Activity**: Latest actions taken in the system

### Creating Surveys
1. Navigate to "Create Survey" in the navigation menu
2. Enter survey title, description, and recipient email address
3. Add questions using the form builder interface
4. Preview the survey appearance in real-time
5. Save as draft or submit for approval

### Managing Surveys
1. View all surveys in the "Surveys" section
2. Filter by status (draft, approved, deleted)
3. Search for specific surveys by title or content
4. Edit draft surveys or view details of any survey

### AI-Powered Email Generation
1. Select a survey to approve
2. Navigate to the Email tab
3. Enable "Use AI to generate email content"
4. Wait for Gemini to analyze the survey and generate an email
5. Review and edit the AI-generated content
6. Customize the email subject and recipients
7. Approve the survey to send the email

### Approving & Sending Surveys
1. Administrators can review pending surveys
2. Approve or reject with comments
3. Approved surveys are automatically sent to specified recipients
4. Email notifications include direct links to the Google Form

### Viewing Responses
1. Access response data from the survey details page
2. View summarized data and individual responses
3. Use the "Enable Response Sharing" feature to make results public
4. Generate shareable links for response data

## 🔧 Utility Scripts

The application includes several utility scripts to help manage Google Forms:

- **enable_response_sharing.py**: Makes form responses visible to anyone with the link
- **share_response_urls.py**: Generates shareable URLs for viewing form responses
- **share_existing_forms.py**: Updates sharing settings for existing forms

To use these scripts:
1. Open a command prompt in the application directory
2. Run `python script_name.py` (e.g., `python enable_response_sharing.py`)
3. Follow the on-screen instructions

## 🛠️ Troubleshooting

### Common Issues

1. **Application won't start:**
   - Check if Python and Node.js are correctly installed
   - Verify that port 3000 and 8000 are not in use by other applications
   - Review logs in the `logs/` directory for error messages

2. **Google API authentication errors:**
   - Ensure credential files are properly placed in the credentials directory
   - Check if the APIs are enabled in your Google Cloud Console
   - Verify the .env file contains the correct configuration

3. **AI email generation fails:**
   - Verify your Gemini API key is correctly set in the .env file
   - Check internet connectivity
   - Ensure survey contains valid questions
   - Try with a different model or reduced prompt size

4. **Form creation fails:**
   - Confirm internet connectivity
   - Check if the Google Forms API quota has been exceeded
   - Verify the service account has sufficient permissions

5. **Frontend display issues:**
   - Clear browser cache and cookies
   - Try a different browser
   - Check browser console for JavaScript errors

### Getting Help

If you encounter issues not covered in this documentation:
1. Check the application logs in the `logs/` directory
2. Review the API documentation at http://localhost:8000/docs
3. Contact the support team with detailed error information

## 🔄 Technology Stack

- **Frontend:** 
  - React 18 for component-based UI
  - Bootstrap for responsive layouts
  - Chart.js for data visualization
  - React Router for navigation
  - React-Toastify for notifications

- **Backend:** 
  - Python 3.8+ runtime
  - FastAPI framework for API development
  - Google API client libraries
  - Google Generative AI (Gemini) for email generation
  - SQLite for local data storage
  - JSON Web Tokens for authentication

- **Development Tools:**
  - PowerShell scripts for automation
  - npm for package management
  - Virtual environments for Python isolation
  - Git for version control

## 📝 Notes

- This package excludes `node_modules` and `venv` directories to reduce size
- When setting up on a new machine, these dependencies will be automatically installed
- The application includes sample credential files for demonstration purposes
- For production use, replace with your own Google API credentials
- To use AI email generation, add your Gemini API key to the .env file

## Google Cloud Credentials Setup

### Setting Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs in the "APIs & Services" section:
   - Google Forms API
   - Google Drive API
   - Gmail API

### Creating OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Set Application Type to "Web application"
4. Add "http://localhost:3000/oauth2callback" as an authorized redirect URI
5. Add "http://localhost:3000" as an authorized JavaScript origin
6. Click "Create" and download the credentials JSON file
7. Rename the file to `client_secret.json` and save it in the `credentials` directory

### Creating Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service account"
3. Enter a name for the service account and click "Create"
4. Grant this service account access to the project (Role: Editor)
5. Click "Done"
6. Find the service account in the credentials list and click on it
7. Go to the "Keys" tab and click "Add Key" > "Create new key"
8. Select JSON as the key type and click "Create"
9. Rename the downloaded file to `service_account.json` and save it in the `credentials` directory

### Setting Up Environment Variables

1. Open the `.env` file in the `backend` directory
2. Update the following variables with your credentials:
   - `GOOGLE_CLIENT_ID`: Your OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your OAuth client secret
   - `GEMINI_API_KEY`: Your Gemini API key (if using Gemini AI)
   - `EMAIL_USERNAME`: Your Gmail email address
   - `EMAIL_PASSWORD`: Your Gmail app password (generate from Google Account settings)
   - `SECRET_KEY`: A random secret key for the backend

### First-time Authentication

1. When you first run the application, it will open a browser window for OAuth authentication
2. Log in with your Google account and grant permissions
3. The application will store authentication tokens for future use

## Security Notes

- Never commit your actual credentials to GitHub
- The repository has been set up with placeholder values like `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET`
- Replace these placeholders with your actual credentials when running locally
- Consider using environment variables or a secret management solution in production 