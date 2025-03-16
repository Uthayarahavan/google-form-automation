import React, { useState } from 'react';
import { Navbar, Nav, Container, Dropdown } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  const [expanded, setExpanded] = useState(false);
  
  // Check if a path is active
  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path === '/dashboard' && location.pathname === '/dashboard') return true;
    if (path !== '/' && path !== '/dashboard' && location.pathname.includes(path)) return true;
    return false;
  };
  
  return (
    <Navbar 
      expand="lg" 
      className="modern-navbar shadow-sm py-2 sticky-top" 
      expanded={expanded}
      onToggle={() => setExpanded(!expanded)}
    >
      <Container fluid className="px-lg-4">
        <Navbar.Brand as={Link} to="/" className="d-flex align-items-center" onClick={() => setExpanded(false)}>
          <div className="brand-logo me-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" className="bi bi-file-earmark-text" viewBox="0 0 16 16">
              <path d="M5.5 7a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zM5 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5z"/>
              <path d="M9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5L9.5 0zm0 1v2A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5z"/>
            </svg>
          </div>
          <span className="brand-text">Forms Creator</span>
        </Navbar.Brand>
        
        <Navbar.Toggle aria-controls="responsive-navbar-nav" className="border-0">
          <span className="navbar-toggler-icon"></span>
        </Navbar.Toggle>
        
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="ms-auto align-items-center">
            <Nav.Link 
              as={Link} 
              to="/" 
              className={`nav-item px-3 py-2 mx-1 ${isActive('/') || isActive('/dashboard') ? 'active' : ''}`}
              onClick={() => setExpanded(false)}
            >
              <i className="bi bi-speedometer2 me-2"></i>
              Dashboard
            </Nav.Link>
            
            <Nav.Link 
              as={Link} 
              to="/surveys" 
              className={`nav-item px-3 py-2 mx-1 ${isActive('/surveys') && !isActive('/create') ? 'active' : ''}`}
              onClick={() => setExpanded(false)}
            >
              <i className="bi bi-list-ul me-2"></i>
              My Surveys
            </Nav.Link>
            
            <Nav.Link 
              as={Link} 
              to="/surveys/create" 
              className={`nav-item px-3 py-2 mx-1 ${isActive('/create') ? 'active' : ''}`}
              onClick={() => setExpanded(false)}
            >
              <i className="bi bi-plus-square me-2"></i>
              Create Survey
            </Nav.Link>
            
            <div className="ms-lg-2 mt-3 mt-lg-0">
              <button className="user-profile-btn">
                <span className="profile-initial">U</span>
              </button>
            </div>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation; 