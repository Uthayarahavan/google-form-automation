import React, { useState } from 'react';
import { Form, Button, Card, Alert, Row, Col, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { surveyApi } from '../services/api';

const SurveyCreate = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questionsText, setQuestionsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewQuestions, setPreviewQuestions] = useState([]);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [showPreview, setShowPreview] = useState(false);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Only accept text files
    if (file.type !== 'text/plain') {
      setError('Please upload a text file (.txt)');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      setQuestionsText(event.target.result);
    };
    reader.onerror = () => {
      setError('Error reading file');
    };
    reader.readAsText(file);
  };

  const handlePreview = (e) => {
    e.preventDefault();
    
    // Split questions by new line and filter out empty lines
    const questions = questionsText
      .split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0);
    
    if (questions.length === 0) {
      setError('Please enter at least one question');
      return;
    }
    
    setPreviewQuestions(questions);
    // Initialize all questions as selected
    setSelectedQuestions(questions.map(() => true));
    setShowPreview(true);
    setError('');
  };

  const toggleQuestionSelection = (index) => {
    const newSelection = [...selectedQuestions];
    newSelection[index] = !newSelection[index];
    setSelectedQuestions(newSelection);
  };

  const getSelectedQuestionsList = () => {
    return previewQuestions.filter((_, index) => selectedQuestions[index]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    
    if (previewQuestions.length === 0) {
      setError('Please preview your questions first');
      return;
    }

    const selectedQuestionsList = getSelectedQuestionsList();
    if (selectedQuestionsList.length === 0) {
      setError('Please select at least one question');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // Show simple form creation message (removed authentication instructions)
      toast.info(
        '🔄 Creating form...',
        {
          autoClose: false,
          toastId: 'creating-form',
          className: 'creating-form-toast'
        }
      );
      
      const surveyData = {
        title: title.trim(),
        description: description.trim() || undefined,
        questions: selectedQuestionsList
      };
      
      const createdSurvey = await surveyApi.create(surveyData);
      
      // Close the pending toast
      toast.dismiss('creating-form');
      
      // Check for error in the response
      if (createdSurvey.form_url && createdSurvey.form_url.includes('ERROR')) {
        throw new Error(createdSurvey.error || 'Error creating form. Please try again.');
      }
      
      // Check for mock URL
      if (createdSurvey.form_url && createdSurvey.form_url.includes('mock')) {
        // This is a mock URL, but we don't need to treat it as an error now
        toast.info('Created a mock survey form for demonstration purposes.');
      } else {
        toast.success('Survey created successfully!');
      }
      
      navigate(`/surveys/${createdSurvey.id}`);
    } catch (err) {
      console.error('Error creating survey:', err);
      
      // Close the pending toast
      toast.dismiss('creating-form');
      
      // Show appropriate error message
      if (err.message && err.message.includes('Authentication')) {
        setError('Authentication failed. Please try again.');
        toast.error(
          <div>
            <h5>Authentication Required</h5>
            <p>If you see authentication prompts:</p>
            <ul>
              <li>Look for a browser window asking for Google permissions</li>
              <li>Check the console for an authentication URL if no window opens</li>
              <li>Complete the authentication flow to create forms</li>
            </ul>
          </div>,
          {
            autoClose: 10000
          }
        );
      } else {
        setError(err.detail || err.message || 'Failed to create survey. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setQuestionsText('');
    setPreviewQuestions([]);
    setSelectedQuestions([]);
    setShowPreview(false);
    setError('');
  };

  return (
    <div className="survey-form fade-in">
      <div className="d-flex align-items-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" className="bi bi-file-earmark-plus text-primary me-3" viewBox="0 0 16 16">
          <path d="M8 6.5a.5.5 0 0 1 .5.5v1.5H10a.5.5 0 0 1 0 1H8.5V11a.5.5 0 0 1-1 0V9.5H6a.5.5 0 0 1 0-1h1.5V7a.5.5 0 0 1 .5-.5z"/>
          <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
        </svg>
        <h2 className="mb-0">Create New Survey</h2>
      </div>
      
      {error && (
        <Alert variant="danger" className="d-flex align-items-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" className="bi bi-exclamation-triangle-fill me-2 flex-shrink-0" viewBox="0 0 16 16">
            <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
          </svg>
          <div>{error}</div>
        </Alert>
      )}
      
      <Card className="border-0 shadow-sm">
        <Card.Body>
          <Form onSubmit={showPreview ? handleSubmit : handlePreview}>
            <Form.Group className="mb-4">
              <Form.Label>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-type-h1 me-2" viewBox="0 0 16 16">
                  <path d="M8.637 13V3.669H7.379V7.62H2.758V3.67H1.5V13h1.258V8.728h4.62V13h1.259zm5.329 0V3.669h-1.244L10.5 5.316v1.265l2.16-1.565h.062V13h1.244z"/>
                </svg>
                Survey Title
              </Form.Label>
              <Form.Control
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter survey title"
                className="form-control-lg"
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-4">
              <Form.Label>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-text-paragraph me-2" viewBox="0 0 16 16">
                  <path fillRule="evenodd" d="M2 12.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm4-3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5z"/>
                </svg>
                Description (Optional)
              </Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter survey description"
              />
            </Form.Group>
            
            {!showPreview ? (
              <>
                <Row className="mb-4">
                  <Col md={12}>
                    <Form.Group>
                      <Form.Label className="d-flex align-items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-question-circle me-2" viewBox="0 0 16 16">
                          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                          <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
                        </svg>
                        Questions (One per line)
                      </Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={5}
                        value={questionsText}
                        onChange={(e) => setQuestionsText(e.target.value)}
                        placeholder="Enter one question per line"
                        required
                      />
                      <Form.Text className="text-muted">
                        Each line will be treated as a separate question.
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Row className="mb-4">
                  <Col md={12}>
                    <Form.Group>
                      <Form.Label className="d-flex align-items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-upload me-2" viewBox="0 0 16 16">
                          <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                          <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
                        </svg>
                        Or Upload Questions File
                      </Form.Label>
                      <Form.Control
                        type="file"
                        accept=".txt"
                        onChange={handleFileUpload}
                      />
                      <Form.Text className="text-muted">
                        Upload a text file with one question per line.
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>
              </>
            ) : (
              <div className="questions-container mb-4">
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5 className="mb-0">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" className="bi bi-eye me-2" viewBox="0 0 16 16">
                      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>
                      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                    </svg>
                    Preview Questions
                  </h5>
                  <Badge bg="primary" pill>
                    {getSelectedQuestionsList().length} selected
                  </Badge>
                </div>
                <p className="text-muted mb-3">Select the questions you want to include in your survey:</p>
                
                {previewQuestions.map((question, index) => (
                  <div key={index} className={`question-item d-flex align-items-start ${!selectedQuestions[index] ? 'opacity-50' : ''}`}>
                    <Form.Check 
                      type="checkbox"
                      id={`question-${index}`}
                      className="me-3 mt-1"
                      checked={selectedQuestions[index]}
                      onChange={() => toggleQuestionSelection(index)}
                    />
                    <div>
                      <strong className="text-primary">Question {index + 1}:</strong> {question}
                    </div>
                  </div>
                ))}
                
                <Button 
                  variant="link" 
                  className="p-0 mt-3 d-flex align-items-center" 
                  onClick={() => setShowPreview(false)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-pencil-square me-2" viewBox="0 0 16 16">
                    <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                    <path fillRule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                  </svg>
                  Edit Questions
                </Button>
              </div>
            )}
            
            <div className="d-flex justify-content-between">
              <Button 
                variant="outline-secondary" 
                onClick={resetForm} 
                disabled={loading}
                className="d-flex align-items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-arrow-repeat me-2" viewBox="0 0 16 16">
                  <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                  <path fillRule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                </svg>
                Reset
              </Button>
              
              <Button 
                variant="primary" 
                type="submit" 
                disabled={loading}
                className="d-flex align-items-center"
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                  </>
                ) : showPreview ? (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-check2-circle me-2" viewBox="0 0 16 16">
                      <path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"/>
                      <path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"/>
                    </svg>
                    Create Survey
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-eye me-2" viewBox="0 0 16 16">
                      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>
                      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                    </svg>
                    Preview Questions
                  </>
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default SurveyCreate; 