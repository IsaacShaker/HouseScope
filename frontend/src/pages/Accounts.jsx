import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import accountService from '../services/accountService';

const Accounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    account_type: 'checking',
    institution_name: '',
    account_name: '',
    balance: '',
    credit_limit: '',
    interest_rate: '',
  });

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await accountService.getAccounts();
      setAccounts(data);
    } catch (err) {
      console.error('Failed to load accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await accountService.createAccount({
        ...formData,
        balance: parseFloat(formData.balance) || 0,
        credit_limit: formData.credit_limit ? parseFloat(formData.credit_limit) : null,
        interest_rate: formData.interest_rate ? parseFloat(formData.interest_rate) : null,
      });
      setShowModal(false);
      setFormData({
        account_type: 'checking',
        institution_name: '',
        account_name: '',
        balance: '',
        credit_limit: '',
        interest_rate: '',
      });
      loadAccounts();
    } catch (err) {
      alert('Failed to create account');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this account?')) {
      try {
        await accountService.deleteAccount(id);
        loadAccounts();
      } catch (err) {
        alert('Failed to delete account');
      }
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getAccountIcon = (type) => {
    const icons = {
      checking: '🏦',
      savings: '💰',
      credit: '💳',
      loan: '📋',
      investment: '📈',
    };
    return icons[type] || '💼';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="text-2xl font-bold text-indigo-600">
                🏠 HouseScope
              </Link>
            </div>
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0 flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Accounts</h1>
          <button
            onClick={() => setShowModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            + Add Account
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
        ) : accounts.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 mb-4">No accounts yet. Add your first account to get started!</p>
            <button
              onClick={() => setShowModal(true)}
              className="bg-indigo-600 text-white px-6 py-3 rounded-md hover:bg-indigo-700"
            >
              Add Account
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {accounts.map((account) => (
              <div key={account.id} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-4xl">{getAccountIcon(account.account_type)}</div>
                    <button
                      onClick={() => handleDelete(account.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-1">
                    {account.account_name || account.institution_name}
                  </h3>
                  <p className="text-sm text-gray-500 capitalize mb-3">{account.account_type}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(account.balance)}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">{account.institution_name}</p>
                  {account.credit_limit && (
                    <p className="text-xs text-gray-500">
                      Limit: {formatCurrency(account.credit_limit)}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Add Account Modal */}
        {showModal && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setShowModal(false)}></div>
              <div className="relative bg-white rounded-lg max-w-lg w-full p-6">
                <h2 className="text-2xl font-bold mb-4">Add New Account</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Account Type</label>
                    <select
                      value={formData.account_type}
                      onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                      required
                    >
                      <option value="checking">Checking</option>
                      <option value="savings">Savings</option>
                      <option value="credit">Credit Card</option>
                      <option value="loan">Loan</option>
                      <option value="investment">Investment</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Institution Name</label>
                    <input
                      type="text"
                      value={formData.institution_name}
                      onChange={(e) => setFormData({ ...formData, institution_name: e.target.value })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="e.g., Chase, Bank of America"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Account Name (Optional)</label>
                    <input
                      type="text"
                      value={formData.account_name}
                      onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="e.g., Main Checking, Emergency Fund"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Current Balance</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.balance}
                      onChange={(e) => setFormData({ ...formData, balance: e.target.value })}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="0.00"
                      required
                    />
                  </div>
                  {formData.account_type === 'credit' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Credit Limit</label>
                      <input
                        type="number"
                        step="0.01"
                        value={formData.credit_limit}
                        onChange={(e) => setFormData({ ...formData, credit_limit: e.target.value })}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                        placeholder="0.00"
                      />
                    </div>
                  )}
                  <div className="flex space-x-4 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                    >
                      Add Account
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Accounts;
