// API configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  analyze: `${API_BASE_URL}/api/analyze`,
  getAnalysis: (id) => `${API_BASE_URL}/api/analyses/${id}`,
  getRisk: (id) => `${API_BASE_URL}/api/analyses/${id}/risk`,
  getReport: (id) => `${API_BASE_URL}/api/analyses/${id}/report`,
  listAnalyses: `${API_BASE_URL}/api/analyses`
};