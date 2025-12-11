import api from './api';

const financialService = {
  async getDashboard() {
    const response = await api.get('/financial/dashboard');
    return response.data;
  },

  async getAffordability(params = {}) {
    const response = await api.get('/financial/affordability', { params });
    return response.data;
  },

  async updateProfile(profileData) {
    const response = await api.post('/financial/profile', profileData);
    return response.data;
  },

  async getProfile() {
    const response = await api.get('/financial/profile');
    return response.data;
  },
};

export default financialService;
