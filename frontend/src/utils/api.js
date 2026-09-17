import axios from 'axios';
import { clearToken, getToken } from './auth';

export const api = axios.create({ baseURL: import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000', timeout: 35000 });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) clearToken();
    return Promise.reject(error);
  },
);

export function messageOf(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(', ');
  return detail || error?.message || 'Something went wrong';
}
