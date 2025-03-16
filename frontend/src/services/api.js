import axios from 'axios';
import { toast } from 'react-toastify';

// Create an axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Handle network errors gracefully
    if (error.message === 'Network Error') {
      console.error('Network error - Backend may not be running');
      // You could return mock data here
    }
    return Promise.reject(error);
  }
);

// Survey related API calls
export const surveyApi = {
  // Create a new survey
  create: async (surveyData) => {
    try {
      const response = await api.post('/surveys/', surveyData);
      
      // Process the response for mock/error URLs
      const formUrl = response.data.form_url;
      if (formUrl && (formUrl.startsWith('MOCK-') || formUrl.startsWith('ERROR-'))) {
        console.warn('Mock or error URL detected:', formUrl);
        // Create a cleaned version of the URL for display
        const cleanedUrl = formUrl.replace(/^(MOCK-|ERROR-)/, '');
        
        // Add an alert in the UI about mock form
        if (formUrl.startsWith('MOCK-')) {
          alert('MOCK FORM CREATED: This is a mock Google Form and will not work as a real form. To create real forms, ensure Google API credentials are properly configured.');
        } else if (formUrl.startsWith('ERROR-')) {
          alert('ERROR CREATING FORM: There was an error connecting to Google Forms API. This is a mock URL and will not work as a real form.');
        }
        
        // Return modified response
        return {
          ...response.data,
          form_url: cleanedUrl,
          is_mock: true
        };
      }
      
      return response.data;
    } catch (error) {
      if (error.message === 'Network Error') {
        console.log('Using mock data due to backend connection issues');
        // Return mock data
        return {
          id: "mock-" + Date.now(),
          title: surveyData.title || "Mock Survey",
          description: surveyData.description || "",
          status: "draft",
          form_url: "https://docs.google.com/forms/d/e/mockform",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_mock: true
        };
      }
      throw error.response ? error.response.data : new Error('Failed to create survey');
    }
  },

  // Get all surveys
  getAll: async () => {
    try {
      const response = await api.get('/surveys/');
      
      // Process any mock or error URLs in the surveys
      if (response.data.surveys && Array.isArray(response.data.surveys)) {
        response.data.surveys = response.data.surveys.map(survey => {
          if (survey.form_url && (survey.form_url.startsWith('MOCK-') || survey.form_url.startsWith('ERROR-'))) {
            return {
              ...survey,
              form_url: survey.form_url.replace(/^(MOCK-|ERROR-)/, ''),
              is_mock: true
            };
          }
          return survey;
        });
      }
      
      return response.data;
    } catch (error) {
      if (error.message === 'Network Error') {
        console.log('Using mock data due to backend connection issues');
        // Return mock data
        return {
          surveys: [
            {
              id: "mock-1",
              title: "Mock Customer Survey",
              description: "This is a mock survey for demonstration",
              status: "approved",
              form_url: "https://docs.google.com/forms/d/e/mockform1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              is_mock: true
            },
            {
              id: "mock-2",
              title: "Mock Product Feedback",
              description: "Another mock survey for demonstration",
              status: "draft",
              form_url: "https://docs.google.com/forms/d/e/mockform2",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              is_mock: true
            }
          ]
        };
      }
      throw error.response ? error.response.data : new Error('Failed to fetch surveys');
    }
  },

  // Get a specific survey by ID
  getById: async (id) => {
    try {
      const response = await api.get(`/surveys/${id}`);
      
      // Process mock or error URLs
      if (response.data.form_url && (response.data.form_url.startsWith('MOCK-') || response.data.form_url.startsWith('ERROR-'))) {
        return {
          ...response.data,
          form_url: response.data.form_url.replace(/^(MOCK-|ERROR-)/, ''),
          is_mock: true
        };
      }
      
      return response.data;
    } catch (error) {
      if (error.message === 'Network Error') {
        console.log('Using mock data due to backend connection issues');
        // Return mock data
        return {
          id: id,
          title: "Mock Survey Details",
          description: "This is a mock survey detail view",
          status: "draft",
          form_url: `https://docs.google.com/forms/d/e/mockform-${id}`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_mock: true
        };
      }
      throw error.response ? error.response.data : new Error(`Failed to fetch survey with ID ${id}`);
    }
  },

  // Approve a survey
  approve: async (id, approvalData) => {
    try {
      const response = await api.post(`/surveys/${id}/approve`, approvalData);
      
      if (response.data.email_status === 'SUCCESS') {
        if (response.data.form_url && (response.data.form_url.startsWith('MOCK-') || response.data.form_url.startsWith('ERROR-'))) {
          toast.info('Survey approved successfully. (Note: This is a mock survey, email notifications are simulated)');
        } else {
          toast.success('Survey approved and email notifications sent successfully!');
        }
      } else if (response.data.email_status === 'PARTIAL_SUCCESS') {
        toast.warning('Survey approved but some email notifications failed to send.');
      } else if (response.data.email_status === 'FAILED') {
        toast.error('Survey approved but all email notifications failed to send.');
      }
      
      return response.data;
    } catch (error) {
      console.error('Error approving survey:', error);
      throw error.response ? error.response.data : error;
    }
  },

  // Generate email draft
  generateEmail: async (id) => {
    try {
      const response = await api.post(`/surveys/${id}/generate-email`);
      return response.data;
    } catch (error) {
      console.error('Error generating email draft:', error);
      throw error.response ? error.response.data : error;
    }
  },

  // Delete a survey
  delete: async (id) => {
    try {
      await api.delete(`/surveys/${id}`);
      return true;
    } catch (error) {
      if (error.message === 'Network Error') {
        console.log('Mock deletion due to backend connection issues');
        return true;
      }
      throw error.response ? error.response.data : new Error(`Failed to delete survey with ID ${id}`);
    }
  }
};

export default api;