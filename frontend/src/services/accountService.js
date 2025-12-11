import api from './api';

const accountService = {
  async getAccounts() {
    const response = await api.get('/accounts');
    return response.data;
  },

  async getAccount(id) {
    const response = await api.get(`/accounts/${id}`);
    return response.data;
  },

  async createAccount(accountData) {
    const response = await api.post('/accounts', accountData);
    return response.data;
  },

  async updateAccount(id, accountData) {
    const response = await api.put(`/accounts/${id}`, accountData);
    return response.data;
  },

  async deleteAccount(id) {
    await api.delete(`/accounts/${id}`);
  },

  async getNetWorth() {
    const response = await api.get('/accounts/summary/net-worth');
    return response.data;
  },
};

export default accountService;
