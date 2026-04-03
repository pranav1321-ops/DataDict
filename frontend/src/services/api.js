import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes — Cohere + DB can be slow
});

export const askQuestion = async (question) => {
  try {
    const response = await api.post('/ask', { question });
    return response.data;
  } catch (error) {
    // Extract meaningful error from backend response
    if (error.response) {
      // Backend responded with error status (4xx, 5xx)
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message || '';
      
      if (status === 422) {
        throw new Error('Invalid question format. Please try rephrasing your question.');
      }
      if (status === 400) {
        throw new Error(detail || 'The query could not be processed. Please try a different question.');
      }
      if (status === 500) {
        // Check for timeout-related keywords in the detail
        if (detail.toLowerCase().includes('timeout') || detail.toLowerCase().includes('timed out')) {
          throw new Error('The AI took too long to respond. Please try again — simpler questions work faster.');
        }
        throw new Error(detail || 'An internal server error occurred. Please try again.');
      }
      throw new Error(`Server error (${status}): ${detail || 'Unknown error'}`);
    } 
    
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error('Request timed out. The backend may be processing a complex query — please try again.');
    }
    
    if (error.request) {
      // Request was made but no response — backend is down
      throw new Error("Couldn't reach the backend. Make sure the FastAPI server is running on http://localhost:8000.");
    }
    
    // Something else happened
    throw new Error(error.message || 'An unexpected error occurred.');
  }
};