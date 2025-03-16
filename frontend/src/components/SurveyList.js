import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, Badge, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { surveyApi } from '../services/api';

const SurveyList = () => {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch surveys when the component mounts or refreshTrigger changes
  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        setLoading(true);
        const data = await surveyApi.getAll();
        setSurveys(data.surveys || []);
        setError('');
      } catch (err) {
        console.error('Error fetching surveys:', err);
        setError('Failed to load surveys. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSurveys();
  }, [refreshTrigger]);

  const handleDeleteSurvey = async (id) => {
    if (window.confirm('Are you sure you want to delete this survey?')) {
      try {
        await surveyApi.delete(id);
        toast.success('Survey deleted successfully');
        // Trigger a refresh to update the list
        setRefreshTrigger(prev => prev + 1);
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

  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading surveys...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Your Surveys</h2>
        <Button as={Link} to="/surveys/create" variant="primary">
          Create New Survey
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {surveys.length === 0 ? (
        <Alert variant="info">
          No surveys found. Click the "Create New Survey" button to get started.
        </Alert>
      ) : (
        <Row xs={1} md={2} className="g-4">
          {surveys.map(survey => (
            <Col key={survey.id}>
              <Card className="survey-card h-100">
                <Card.Body>
                  <Card.Title className="d-flex justify-content-between align-items-center">
                    {survey.title}
                    {getStatusBadge(survey.status)}
                  </Card.Title>
                  <Card.Text>
                    {survey.description || <em>No description provided</em>}
                  </Card.Text>
                  <div className="text-muted small mb-3">
                    Created: {formatDate(survey.created_at)}
                    <br />
                    Last Updated: {formatDate(survey.updated_at)}
                  </div>
                  <div className="d-flex justify-content-between">
                    <Button 
                      as={Link} 
                      to={`/surveys/${survey.id}`} 
                      variant="outline-primary"
                      size="sm"
                    >
                      View Details
                    </Button>
                    <Button 
                      variant="outline-danger" 
                      size="sm"
                      onClick={() => handleDeleteSurvey(survey.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default SurveyList; 