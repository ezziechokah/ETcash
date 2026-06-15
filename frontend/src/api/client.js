import axios from 'axios';

let apiClient = null;

export async function initApiClient() {
  let baseURL = 'http://127.0.0.1:8765';
  if (typeof window !== 'undefined' && window.etcash) {
    try { baseURL = await window.etcash.getApiUrl(); } catch {}
  }
  apiClient = axios.create({
    baseURL: `${baseURL}/api`,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000
  });
  apiClient.interceptors.request.use(config => {
    const token  = localStorage.getItem('etcash_token');
    const entity = localStorage.getItem('etcash_entity');
    if (token)  config.headers['Authorization'] = `Token ${token}`;
    if (entity) config.headers['X-Entity-ID']   = entity;
    return config;
  });
  apiClient.interceptors.response.use(res => res, err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('etcash_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  });
  return apiClient;
}

export function getApiClient() {
  if (!apiClient) throw new Error('API client not initialized');
  return apiClient;
}

export const api = {
  get:    (url, cfg)       => getApiClient().get(url, cfg),
  post:   (url, data, cfg) => getApiClient().post(url, data, cfg),
  put:    (url, data, cfg) => getApiClient().put(url, data, cfg),
  patch:  (url, data, cfg) => getApiClient().patch(url, data, cfg),
  delete: (url, cfg)       => getApiClient().delete(url, cfg),
};
