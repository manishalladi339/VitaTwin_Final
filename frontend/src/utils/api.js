import axios from "axios";
import { getToken } from "./auth";

const API_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function analyzeHealth(data) {
  const response = await api.post(`/register`, data); // placeholder legacy helper
  const user_id = response.data.user_id;
  const prediction = await api.get(`/predict_health/${user_id}`);
  return prediction.data;
}
