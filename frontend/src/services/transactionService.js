import api from './api';

const transactionService = {
  async getTransactions(params = {}) {
    const response = await api.get('/transactions', { params });
    return response.data;
  },

  async getTransaction(id) {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },

  async createTransaction(transactionData) {
    const response = await api.post('/transactions', transactionData);
    return response.data;
  },

  async updateTransaction(id, transactionData) {
    const response = await api.put(`/transactions/${id}`, transactionData);
    return response.data;
  },

  async deleteTransaction(id) {
    await api.delete(`/transactions/${id}`);
  },

  async importCSV(accountId, file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/transactions/import-csv/${accountId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getCategories() {
    const response = await api.get('/transactions/categories/list');
    return response.data;
  },
};

export default transactionService;
