import axios from 'axios';
import config from '@/config.js';
import store from '@/store';

const api = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});


api.interceptors.request.use(
  (config) => {
    const token = store.getters['auth/token'];
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);


api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    
    if (error.response?.status === 401) {
      // Logout user via Vuex
      await store.dispatch('auth/logout');
      window.location.href = '/login';
    }

   
    if (error.response?.status === 403) {
      console.error('Access forbidden - insufficient permissions');
    }

    
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response?.data?.message);
    }

    return Promise.reject(error);
  }
);

export default api;