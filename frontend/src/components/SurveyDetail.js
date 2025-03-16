import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Badge, Button, Form, Alert, Spinner, ListGroup, Modal, Tabs, Tab, Row, Col } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { surveyApi } from '../services/api';

const SurveyDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [survey, setSurvey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [recipientEmails, setRecipientEmails] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [useAiContent, setUseAiContent] = useState(false);
  const [approveLoading, setApproveLoading] = useState(false);
  const [approveError, setApproveError] = useState('');
  const [activeTab, setActiveTab] = useState('basic');
  const [generatingAiContent, setGeneratingAiContent] = useState(false);

  // Fetch survey details when the component mounts
  useEffect(() => {
    const fetchSurvey = async () => {
      try {
        setLoading(true);
        const data = await surveyApi.getById(id);
        setSurvey(data);
        setError('');
        
        // Show a toast notification if this is a mock survey
        if (data.is_mock) {
          toast.warning('This is a mock survey with a non-functional form link. To create real forms, ensure Google API credentials are properly configured.');
        }
      } catch (err) {
        console.error('Error fetching survey:', err);
        setError('Failed to load survey details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSurvey();
  }, [id]);

  // Set default email subject when survey data is loaded
  useEffect(() => {
    if (survey) {
      setEmailSubject(`Survey: ${survey.title}`);
      
      // Set default email body
      const defaultBody = `
Hello,

A new survey has been approved and is ready for your response:

Title: ${survey.title}
Description: ${survey.description || 'No description provided'}

Please click the following link to access the survey:
${survey.form_url}

Thank you for your participation!
      `;
      setEmailBody(defaultBody);
    }
  }, [survey]);

  // Add effect to initialize the form when the modal opens
  useEffect(() => {
    if (showApproveModal) {
      // Initialize with default values when modal opens
      if (!emailSubject && survey) {
        setEmailSubject(`Survey: ${survey.title}`);
      }
      
      // Clear previous error
      setApproveError('');
      
      // If survey has recipient_email from a previous attempt, populate it
      if (!recipientEmail && survey && survey.recipient_email) {
        setRecipientEmail(survey.recipient_email);
      }
    }
  }, [showApproveModal, survey]);

  const handleApproveClick = () => {
    if (survey && survey.status === 'approved') {
      toast.info('This survey is already approved');
      return;
    }
    
    // Show a warning toast if this is a mock survey
    if (survey && survey.is_mock) {
      toast.warning('This is a mock survey. Approving it will not send a real email.');
    }
    
    setShowApproveModal(true);
    setApproveError('');
    
    // Pre-fill email if it exists in the survey
    if (survey && survey.recipient_email) {
      setRecipientEmail(survey.recipient_email);
    }
  };

  const handleApprove = async () => {
    // Validate that at least one recipient is provided
    const emails = recipientEmails.trim() ? recipientEmails.split(',').map(email => email.trim()) : [];
    
    if (!recipientEmail.trim() && emails.length === 0) {
      setApproveError('At least one recipient email is required');
      return;
    }
    
    // Validate that if AI content is enabled, we either have content or need to generate it
    if (useAiContent && !emailBody.trim()) {
      setApproveError('Please wait for AI to generate email content or uncheck the "Use AI" option');
      // Try to generate content automatically
      handleGenerateAiContent();
      return;
    }
    
    try {
      setApproveLoading(true);
      setApproveError('');
      
      // Prepare approval data
      const approveData = {
        use_ai_generated_content: useAiContent
      };
      
      // Add recipient email(s)
      if (recipientEmail.trim()) {
        approveData.recipient_email = recipientEmail.trim();
      }
      
      if (emails.length > 0) {
        approveData.recipient_emails = emails;
      }
      
      // Add custom email subject and body if provided
      if (emailSubject.trim()) {
        approveData.email_subject = emailSubject.trim();
      }
      
      // Only include email body if we have content or are using AI generation
      if (emailBody.trim()) {
        approveData.email_body = emailBody.trim();
      } else if (!useAiContent) {
        // If not using AI and no custom body provided, show an error
        setApproveError('Please provide an email body or enable AI-generated content');
        setApproveLoading(false);
        return;
      }
      
      const updatedSurvey = await surveyApi.approve(id, approveData);
      
      // Close the modal immediately to improve UX
      setShowApproveModal(false);
      
      // Update the survey in the state
      setSurvey(updatedSurvey);
      
      // Show success message
      toast.success('Survey approved successfully!');
      
      // Handle different scenarios
      if (updatedSurvey.is_mock) {
        console.warn('Survey approved but this is a MOCK operation. No email was actually sent.');
      } else {
        console.log('Survey approved and email sent successfully!');
      }
    } catch (err) {
      console.error('Error approving survey:', err);
      setApproveError(err.detail || 'Failed to approve survey. Please try again.');
      
      // Show a more detailed error message if available
      if (err.detail && err.detail.includes('email')) {
        setApproveError(`Email error: ${err.detail}`);
      } else {
        setApproveError('Failed to approve survey or send email. Please try again.');
      }
    } finally {
      setApproveLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this survey?')) {
      try {
        await surveyApi.delete(id);
        toast.success('Survey deleted successfully');
        navigate('/surveys');
      } catch (err) {
        console.error('Error deleting survey:', err);
        toast.error(err.detail || 'Failed to delete survey');
      }
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'draft':
        return <Badge bg="warning">Draft</Badge>;
      case 'approved':
        return <Badge bg="success">Approved</Badge>;
      case 'deleted':
        return <Badge bg="danger">Deleted</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const formatDate = (dateString) => {
    // Parse the ISO date string
    const date = new Date(dateString);
    
    // Format options for India locale with IST timezone
    const options = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
      timeZoneName: 'short'
    };
    
    return date.toLocaleString('en-IN', options);
  };

  const handleGenerateAiContent = async () => {
    setGeneratingAiContent(true);
    setApproveError('');
    
    try {
      // Call the new backend API endpoint for real-time email generation
      const result = await surveyApi.generateEmail(id);
      
      if (result && result.success && result.email_body) {
        setEmailBody(result.email_body);
        toast.success('AI-generated email content created successfully!');
      } else {
        throw new Error('Failed to generate email content');
      }
    } catch (err) {
      console.error('Error generating AI email content:', err);
      setApproveError('Failed to generate AI email content. Please try again or use a custom email.');
      toast.error('Error generating email content');
    } finally {
      setGeneratingAiContent(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading survey details...</p>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (!survey) {
    return <Alert variant="warning">Survey not found</Alert>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Survey Details</h2>
        <Button variant="outline-secondary" onClick={() => navigate('/surveys')}>
          Back to Surveys
        </Button>
      </div>

      {survey.is_mock && (
        <Alert variant="warning" className="mb-4">
          <Alert.Heading>Mock Survey Notice</Alert.Heading>
          <p>
            This is a mock survey with a non-functional Google Form link. The form link will not work 
            when clicked and emails will not be sent when approving.
          </p>
          <p className="mb-0">
            To create real forms and send real emails, ensure Google API credentials are properly 
            configured in the backend. Contact your administrator for assistance.
          </p>
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h4 className="mb-0">{survey.title}</h4>
          <div>
            {survey.is_mock && <Badge bg="info" className="me-2">MOCK</Badge>}
            {getStatusBadge(survey.status)}
          </div>
        </Card.Header>
        <Card.Body>
          <Card.Text>
            <strong>Description:</strong> {survey.description || <em>No description provided</em>}
          </Card.Text>
          <div className="text-muted mb-3">
            <div><strong>Created:</strong> {formatDate(survey.created_at)}</div>
            <div><strong>Last Updated:</strong> {formatDate(survey.updated_at)}</div>
          </div>

          {survey.form_url && (
            <div className="mb-3">
              <strong>Form URL:</strong>{' '}
              {survey.is_mock ? (
                <>
                  <span className="text-muted">{survey.form_url}</span>
                  <span className="text-danger ms-2">(Non-functional mock URL)</span>
                </>
              ) : (
                <a href={survey.form_url} target="_blank" rel="noopener noreferrer">
                  {survey.form_url}
                </a>
              )}
            </div>
          )}

          <div className="action-buttons">
            {survey.status === 'draft' && (
              <Button variant="success" onClick={handleApproveClick}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-envelope-check me-2" viewBox="0 0 16 16">
                  <path d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z"/>
                  <path d="M16 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-1.993-1.679a.5.5 0 0 0-.686.172l-1.17 1.95-.547-.547a.5.5 0 0 0-.708.708l.774.773a.75.75 0 0 0 1.174-.144l1.335-2.226a.5.5 0 0 0-.172-.686Z"/>
                </svg>
                Approve & Send
              </Button>
            )}
            <Button 
              variant="danger" 
              onClick={handleDelete}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-trash me-2" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"/>
                <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"/>
              </svg>
              Delete Survey
            </Button>
            {survey.form_url && !survey.is_mock && (
              <Button 
                variant="primary" 
                href={survey.form_url} 
                target="_blank" 
                rel="noopener noreferrer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-box-arrow-up-right me-2" viewBox="0 0 16 16">
                  <path fillRule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                  <path fillRule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                </svg>
                Open Form
              </Button>
            )}
            {survey.form_url && survey.is_mock && (
              <Button 
                variant="secondary" 
                disabled
                title="This is a mock form URL and cannot be opened"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-file-earmark-lock me-2" viewBox="0 0 16 16">
                  <path d="M10 7v1.076c.54.166 1 .597 1 1.224v2.4c0 .816-.781 1.3-1.5 1.3h-3c-.719 0-1.5-.484-1.5-1.3V9.3c0-.627.46-1.058 1-1.224V7a2 2 0 1 1 4 0zM7 7v1h2V7a1 1 0 0 0-2 0zM6 9.3v2.4c0 .042.02.107.105.175A.637.637 0 0 0 6.5 12h3a.64.64 0 0 0 .395-.125c.085-.068.105-.133.105-.175V9.3c0-.042-.02-.107-.105-.175A.637.637 0 0 0 9.5 9h-3a.637.637 0 0 0-.395.125C6.02 9.193 6 9.258 6 9.3z"/>
                  <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
                </svg>
                Form Unavailable (Mock)
              </Button>
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Approve Survey Modal */}
      <Modal show={showApproveModal} onHide={() => setShowApproveModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" className="bi bi-envelope-paper text-success me-2" viewBox="0 0 16 16">
              <path d="M4 0a2 2 0 0 0-2 2v1.133l-.941.502A2 2 0 0 0 0 5.4V14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5.4a2 2 0 0 0-1.059-1.765L14 3.133V2a2 2 0 0 0-2-2H4Zm10 4.267.47.25A1 1 0 0 1 15 5.4v.817l-1 .6v-2.55Zm-1 3.15-3.75 2.25L8 8.917l-1.25.75L3 7.417V2a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v5.417Zm-11-.6-1-.6V5.4a1 1 0 0 1 .53-.882L2 4.267v2.55Zm13 .566v5.734l-4.778-2.867L15 7.383Zm-.035 6.88A1 1 0 0 1 14 15H2a1 1 0 0 1-.965-.738L8 10.083l6.965 4.18ZM1 13.116V7.383l4.778 2.867L1 13.117Z"/>
            </svg>
            Approve Survey & Send Email
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {survey && survey.is_mock ? (
            <Alert variant="warning">
              <p><strong>Mock Operation Notice:</strong></p>
              <p>
                This is a mock survey. Approving it will not send a real email to the recipient.
                For real operations, ensure Google API credentials are properly configured.
              </p>
            </Alert>
          ) : null}
          
          {approveError && <Alert variant="danger">{approveError}</Alert>}
          
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-3"
          >
            <Tab eventKey="basic" title="Basic">
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Single Recipient Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    placeholder="Enter recipient email"
                  />
                  <Form.Text className="text-muted">
                    Enter a single email address or use the Advanced tab for multiple recipients.
                  </Form.Text>
                </Form.Group>
              </Form>
            </Tab>
            <Tab eventKey="advanced" title="Advanced">
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Multiple Recipients</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    value={recipientEmails}
                    onChange={(e) => setRecipientEmails(e.target.value)}
                    placeholder="Enter multiple email addresses separated by commas"
                  />
                  <Form.Text className="text-muted">
                    Enter multiple email addresses separated by commas (e.g., user1@example.com, user2@example.com)
                  </Form.Text>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Email Subject</Form.Label>
                  <Form.Control
                    type="text"
                    value={emailSubject}
                    onChange={(e) => setEmailSubject(e.target.value)}
                    placeholder="Enter email subject"
                  />
                </Form.Group>
                
                <Row className="mb-3">
                  <Col>
                    <Form.Group className="d-flex align-items-center">
                      <Form.Check
                        type="checkbox"
                        id="use-ai-content"
                        checked={useAiContent}
                        onChange={(e) => {
                          const isChecked = e.target.checked;
                          setUseAiContent(isChecked);
                          // If turning on AI content, automatically generate it
                          if (isChecked && !generatingAiContent && !emailBody) {
                            handleGenerateAiContent();
                          }
                        }}
                        label="Use AI to generate email content"
                      />
                      {useAiContent && (
                        <Button 
                          variant="outline-primary" 
                          size="sm" 
                          className="ms-2"
                          onClick={handleGenerateAiContent}
                          disabled={generatingAiContent}
                        >
                          {generatingAiContent ? (
                            <>
                              <Spinner animation="border" size="sm" className="me-1" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-arrow-repeat me-1" viewBox="0 0 16 16">
                                <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                                <path fillRule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                              </svg>
                              Regenerate
                            </>
                          )}
                        </Button>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-3">
                  <Form.Label>Email Body</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={8}
                    value={emailBody}
                    onChange={(e) => {
                      setEmailBody(e.target.value);
                      // If user is manually editing, and the edit is substantial, turn off AI
                      if (useAiContent && e.target.value !== emailBody && e.target.value.length > 10) {
                        // Only turn off if there's a significant edit
                        const difference = Math.abs(e.target.value.length - emailBody.length);
                        if (difference > 10) {
                          setUseAiContent(false);
                          toast.info('AI content generation disabled due to manual editing');
                        }
                      }
                    }}
                    placeholder={useAiContent && generatingAiContent 
                      ? "Generating AI content..." 
                      : "Enter email body or enable AI generation"}
                    disabled={useAiContent && generatingAiContent}
                  />
                  <Form.Text className="text-muted">
                    {useAiContent 
                      ? "AI will generate a personalized email based on survey questions. You can edit afterwards." 
                      : "Customize the email message. The survey link will be automatically included if not present."}
                  </Form.Text>
                </Form.Group>
              </Form>
            </Tab>
          </Tabs>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApproveModal(false)} disabled={approveLoading}>
            Cancel
          </Button>
          <Button variant="success" onClick={handleApprove} disabled={approveLoading}>
            {approveLoading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Processing...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-send-check me-2" viewBox="0 0 16 16">
                  <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855a.75.75 0 0 0-.124 1.329l4.995 3.178 1.531 2.406a.5.5 0 0 0 .844-.536L6.637 10.07l7.494-7.494-1.895 4.738a.5.5 0 1 0 .928.372l2.8-7Zm-2.54 1.183L5.93 9.363 1.591 6.602l11.833-4.733Z"/>
                  <path d="M16 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-1.993-1.679a.5.5 0 0 0-.686.172l-1.17 1.95-.547-.547a.5.5 0 0 0-.708.708l.774.773a.75.75 0 0 0 1.174-.144l1.335-2.226a.5.5 0 0 0-.172-.686Z"/>
                </svg>
                {survey && survey.is_mock ? 'Approve (Mock Operation)' : 'Approve & Send Email'}
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default SurveyDetail; 