import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StartupIdea {
  idea: string;
  problem?: string;
  audience?: string;
  website?: string;
  startup_name?: string;
}

export interface AnalysisResponse {
  status: string;
  report: any;
}

export const analyzeStartup = async (data: StartupIdea): Promise<AnalysisResponse> => {
  const response = await api.post('/api/analyze', data);
  return response.data;
};

export const getExamples = async () => {
  const response = await api.get('/api/examples');
  return response.data.examples;
};
