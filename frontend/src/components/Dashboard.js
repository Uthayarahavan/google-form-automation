import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, ProgressBar, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { surveyApi } from '../services/api';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  BarElement
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  BarElement
);

const Dashboard = () => {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    approved: 0,
    deleted: 0,
    recentlyCreated: 0,
    responseRate: 0
  });

  // Fetch surveys and calculate stats
  useEffect(() => {
    const fetchSurveys = async () => {
      try {
        setLoading(true);
        const data = await surveyApi.getAll();
        const surveysList = data.surveys || [];
        setSurveys(surveysList);
        
        // Calculate statistics
        const now = new Date();
        const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        const totalSurveys = surveysList.length;
        const draftSurveys = surveysList.filter(s => s.status === 'draft').length;
        const approvedSurveys = surveysList.filter(s => s.status === 'approved').length;
        const deletedSurveys = surveysList.filter(s => s.status === 'deleted').length;
        const recentlyCreated = surveysList.filter(s => new Date(s.created_at) > lastWeek).length;
        
        // Calculate response rate (this is placeholder - adjust based on your data model)
        const responsesReceived = surveysList.reduce((total, survey) => total + (survey.responses_count || 0), 0);
        const potentialResponses = approvedSurveys * 10; // Assuming 10 potential responses per survey
        const responseRate = potentialResponses > 0 ? Math.round((responsesReceived / potentialResponses) * 100) : 0;
        
        setStats({
          total: totalSurveys,
          draft: draftSurveys,
          approved: approvedSurveys,
          deleted: deletedSurveys,
          recentlyCreated,
          responseRate
        });
        
        setError('');
      } catch (err) {
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSurveys();
  }, []);

  // Prepare chart data for survey status distribution
  const statusChartData = {
    labels: ['Draft', 'Approved', 'Deleted'],
    datasets: [
      {
        label: 'Survey Status',
        data: [stats.draft, stats.approved, stats.deleted],
        backgroundColor: [
          'rgba(245, 158, 11, 0.7)',  // Warning/Amber for draft
          'rgba(16, 185, 129, 0.7)',  // Success/Green for approved
          'rgba(239, 68, 68, 0.7)'    // Error/Red for deleted
        ],
        borderColor: [
          'rgba(245, 158, 11, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  // Activity over time chart (placeholder data - replace with real data)
  const activityData = {
    labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday'],
    datasets: [
      {
        label: 'Surveys Created',
        data: [3, 5, 2, 8, 6, 4, 7],
        backgroundColor: 'rgba(99, 102, 241, 0.5)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 2,
        tension: 0.4
      },
      {
        label: 'Responses Received',
        data: [8, 12, 5, 18, 14, 10, 20],
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 2,
        tension: 0.4
      }
    ],
  };

  // Recent activity list
  const recentActivity = surveys
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  if (loading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container fade-in">
      {error && <Alert variant="danger">{error}</Alert>}
      
      <div className="dashboard-header mb-4">
        <h1 className="dashboard-title">Welcome to Your Form Dashboard</h1>
        <p className="text-muted">Get insights and manage your surveys in one place</p>
      </div>
      
      {/* Quick Stats Cards */}
      <Row className="stats-cards mb-4 g-3">
        <Col xs={12} sm={6} lg={3}>
          <Card className="stat-card h-100 shadow-sm">
            <Card.Body className="d-flex flex-column align-items-center text-center p-3">
              <div className="stat-icon bg-primary-light mb-3">
                <i className="bi bi-file-earmark-text"></i>
              </div>
              <h3 className="stat-value">{stats.total}</h3>
              <p className="stat-label mb-0">Total Surveys</p>
            </Card.Body>
          </Card>
        </Col>
        
        <Col xs={12} sm={6} lg={3}>
          <Card className="stat-card h-100 shadow-sm">
            <Card.Body className="d-flex flex-column align-items-center text-center p-3">
              <div className="stat-icon bg-success-light mb-3">
                <i className="bi bi-check-circle"></i>
              </div>
              <h3 className="stat-value">{stats.approved}</h3>
              <p className="stat-label mb-0">Approved Surveys</p>
            </Card.Body>
          </Card>
        </Col>
        
        <Col xs={12} sm={6} lg={3}>
          <Card className="stat-card h-100 shadow-sm">
            <Card.Body className="d-flex flex-column align-items-center text-center p-3">
              <div className="stat-icon bg-warning-light mb-3">
                <i className="bi bi-pencil-square"></i>
              </div>
              <h3 className="stat-value">{stats.draft}</h3>
              <p className="stat-label mb-0">Draft Surveys</p>
            </Card.Body>
          </Card>
        </Col>
        
        <Col xs={12} sm={6} lg={3}>
          <Card className="stat-card h-100 shadow-sm">
            <Card.Body className="d-flex flex-column align-items-center text-center p-3">
              <div className="stat-icon bg-accent-light mb-3">
                <i className="bi bi-graph-up"></i>
              </div>
              <h3 className="stat-value">{stats.recentlyCreated}</h3>
              <p className="stat-label mb-0">Created This Week</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Charts and Activity Row */}
      <Row className="mb-4 g-3">
        {/* Chart Section */}
        <Col lg={8}>
          <Row className="g-3 h-100">
            <Col md={6}>
              <Card className="h-100 shadow-sm">
                <Card.Header className="bg-white border-bottom-0 pt-3">
                  <h5 className="card-title">Survey Status Distribution</h5>
                </Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Pie data={statusChartData} options={{ responsive: true, maintainAspectRatio: false }} />
                  </div>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={6}>
              <Card className="h-100 shadow-sm">
                <Card.Header className="bg-white border-bottom-0 pt-3 d-flex justify-content-between align-items-center">
                  <h5 className="card-title">Response Rate</h5>
                  <Badge bg="info" className="demo-badge">Demo Data</Badge>
                </Card.Header>
                <Card.Body className="d-flex flex-column justify-content-center">
                  <div className="text-center mb-3">
                    <h2 className="display-4 fw-bold text-primary">{stats.responseRate}%</h2>
                    <p className="text-muted">Average response rate</p>
                    <small className="text-muted font-italic">* Showing demo data - not connected to actual responses</small>
                  </div>
                  <ProgressBar 
                    variant={stats.responseRate > 70 ? "success" : stats.responseRate > 40 ? "warning" : "danger"}
                    now={stats.responseRate} 
                    className="response-progress"
                  />
                </Card.Body>
              </Card>
            </Col>
            
            <Col xs={12}>
              <Card className="shadow-sm">
                <Card.Header className="bg-white border-bottom-0 pt-3 d-flex justify-content-between align-items-center">
                  <h5 className="card-title">Activity Over Time</h5>
                  <Badge bg="info" className="demo-badge">Demo Data</Badge>
                </Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Line data={activityData} options={{ 
                      responsive: true, 
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      }
                    }} />
                  </div>
                  <div className="text-center mt-2">
                    <small className="text-muted font-italic">* Showing demo data - will update with actual usage</small>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
        
        {/* Recent Activity and Quick Actions */}
        <Col lg={4}>
          <Card className="shadow-sm mb-3">
            <Card.Header className="bg-white border-bottom-0 pt-3">
              <h5 className="card-title">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button as={Link} to="/surveys/create" variant="primary" className="quick-action-btn">
                  <i className="bi bi-plus-circle me-2"></i> Create New Survey
                </Button>
                <Button as={Link} to="/surveys" variant="outline-primary" className="quick-action-btn">
                  <i className="bi bi-list-ul me-2"></i> View All Surveys
                </Button>
              </div>
            </Card.Body>
          </Card>
          
          <Card className="shadow-sm">
            <Card.Header className="bg-white border-bottom-0 pt-3">
              <h5 className="card-title">Recent Activity</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {recentActivity.length > 0 ? (
                <div className="recent-activity-list">
                  {recentActivity.map(survey => (
                    <Link 
                      key={survey.id} 
                      to={`/surveys/${survey.id}`} 
                      className="activity-item d-flex align-items-center p-3 border-bottom text-decoration-none"
                    >
                      <div className={`activity-icon bg-${
                        survey.status === 'draft' ? 'warning' : 
                        survey.status === 'approved' ? 'success' : 'danger'
                      }-light me-3`}>
                        {survey.status === 'draft' ? '📝' : survey.status === 'approved' ? '✓' : '🗑️'}
                      </div>
                      <div className="activity-details flex-grow-1">
                        <h6 className="mb-0 text-truncate">{survey.title}</h6>
                        <small className="text-muted">
                          {new Date(survey.created_at).toLocaleDateString()} • 
                          <Badge 
                            bg={
                              survey.status === 'draft' ? 'warning' : 
                              survey.status === 'approved' ? 'success' : 'danger'
                            }
                            className="ms-1 py-1"
                          >
                            {survey.status}
                          </Badge>
                        </small>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-center my-4">No recent activity</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 