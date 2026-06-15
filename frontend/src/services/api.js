import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const response = await apiClient.post('/auth/login/', { username, password });
    return response.data;
  },
  logout: async () => {
    const response = await apiClient.post('/auth/logout/');
    return response.data;
  },
  setup: async (data) => {
    const response = await apiClient.post('/auth/setup/', data);
    return response.data;
  },
};

// M-Pesa API
export const mpesaAPI = {
  getConfig: async (token) => {
    const response = await apiClient.get('/mpesa/config/');
    return response.data;
  },
  getDashboardStats: async (token, days = 30) => {
    const response = await apiClient.get(`/mpesa/dashboard_stats/?days=${days}`);
    return response.data;
  },
  getTransactions: async (token, params = {}) => {
    const response = await apiClient.get('/mpesa/transactions/', { params });
    return response.data;
  },
  simulatePayment: async (token, data) => {
    const response = await apiClient.post('/mpesa/simulate_payment/', data);
    return response.data;
  },
  sendSTKPush: async (token, data) => {
    const response = await apiClient.post('/mpesa/send_stk_push/', data);
    return response.data;
  },
  reconcile: async (token, transactionId) => {
    const response = await apiClient.post('/mpesa/reconcile/', { transaction_id: transactionId });
    return response.data;
  },
};

// Invoice API
export const invoiceAPI = {
  getInvoices: async (params = {}) => {
    const response = await apiClient.get('/invoicing/invoices/', { params });
    return response.data;
  },
  getInvoice: async (id) => {
    const response = await apiClient.get(`/invoicing/invoices/${id}/`);
    return response.data;
  },
  createInvoice: async (data) => {
    const response = await apiClient.post('/invoicing/invoices/', data);
    return response.data;
  },
  updateInvoice: async (id, data) => {
    const response = await apiClient.put(`/invoicing/invoices/${id}/`, data);
    return response.data;
  },
  deleteInvoice: async (id) => {
    const response = await apiClient.delete(`/invoicing/invoices/${id}/`);
    return response.data;
  },
  sendSTKForInvoice: async (invoiceId, phoneNumber) => {
    const response = await apiClient.post('/invoicing/invoices/send_stk/', {
      invoice_id: invoiceId,
      phone_number: phoneNumber,
    });
    return response.data;
  },
};

// WhatsApp API
export const whatsappAPI = {
  sendInvoice: async (invoiceId) => {
    const response = await apiClient.post('/whatsapp/send_invoice/', { invoice_id: invoiceId });
    return response.data;
  },
  sendReminder: async (invoiceId) => {
    const response = await apiClient.post('/whatsapp/send_reminder/', { invoice_id: invoiceId });
    return response.data;
  },
  sendBulkReminders: async () => {
    const response = await apiClient.post('/whatsapp/send_bulk_reminders/');
    return response.data;
  },
};

// KRA API
export const kraAPI = {
  validatePIN: async (pin) => {
    const response = await apiClient.post('/kra/validate_pin/', { pin });
    return response.data;
  },
  submitVATReturn: async (vatReturnId) => {
    const response = await apiClient.post('/kra/submit_vat_return/', { vat_return_id: vatReturnId });
    return response.data;
  },
};

// Company API
export const companyAPI = {
  getCompany: async () => {
    const response = await apiClient.get('/core/company/');
    return response.data;
  },
  updateCompany: async (data) => {
    const response = await apiClient.put('/core/company/', data);
    return response.data;
  },
  getSettings: async () => {
    const response = await apiClient.get('/core/settings/');
    return response.data;
  },
  updateSettings: async (data) => {
    const response = await apiClient.put('/core/settings/', data);
    return response.data;
  },
};

export default apiClient;