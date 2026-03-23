import axios from 'axios';
import type { CreditEvaluationRequest, CreditEvaluationResponse } from '../types/credit';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function evaluateCredit(data: CreditEvaluationRequest): Promise<CreditEvaluationResponse> {
  const response = await api.post<CreditEvaluationResponse>('/api/credit/evaluate', data);
  return response.data;
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get('/health');
  return response.data;
}

export default api;
