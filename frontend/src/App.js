import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import SurveyCreate from './components/SurveyCreate';
import SurveyList from './components/SurveyList';
import SurveyDetail from './components/SurveyDetail';
import './App.css';

function App() {
  return (
    <div className="App">
      <Navigation />
      <Container fluid className="px-lg-4 py-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/surveys" element={<SurveyList />} />
          <Route path="/surveys/create" element={<SurveyCreate />} />
          <Route path="/surveys/:id" element={<SurveyDetail />} />
        </Routes>
      </Container>
    </div>
  );
}

export default App;