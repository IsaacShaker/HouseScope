import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import financialService from '../services/financialService';
import {
  ExpenseBreakdownChart,
  IncomeExpensesChart,
  NetWorthTrendChart,
  FinancialHealthChart,
} from '../components/Charts';

const Dashboard = () => {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const dashboardData = await financialService.getDashboard();
      setDashboard(dashboardData);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const hasData = dashboard && dashboard.account_count > 0;

  return (
    <>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Financial Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your financial health</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {!hasData ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to HouseScope! 👋</h2>
          <p className="text-gray-600 mb-6">
            Get started by adding your financial accounts and transactions.
          </p>
          <div className="space-x-4">
            <Link
              to="/accounts"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add Account
            </Link>
          </div>
        </div>
      ) : (
        <>
            {/* Financial Metrics */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-3xl">💰</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Net Worth</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {formatCurrency(dashboard.net_worth)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-3xl">📈</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Monthly Income</dt>
                        <dd className="text-2xl font-semibold text-green-600">
                          {formatCurrency(dashboard.monthly_income)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-3xl">📉</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Monthly Expenses</dt>
                        <dd className="text-2xl font-semibold text-red-600">
                          {formatCurrency(dashboard.monthly_expenses)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-3xl">💸</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Savings Rate</dt>
                        <dd className="text-2xl font-semibold text-indigo-600">
                          {dashboard.savings_rate.toFixed(1)}%
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Emergency Buffer</h3>
                <p className="text-3xl font-bold text-indigo-600">
                  {dashboard.emergency_buffer_months.toFixed(1)} months
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {dashboard.emergency_buffer_months >= 6 ? '✅ Well protected' : '⚠️ Build more reserves'}
                </p>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <h3 className="text-lg font-medium text-gray-900 mb-2">DTI Ratio</h3>
                <p className="text-3xl font-bold text-indigo-600">
                  {dashboard.dti_ratio.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {dashboard.dti_ratio <= 43 ? '✅ Good ratio' : '⚠️ High debt load'}
                </p>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Total Assets</h3>
                <p className="text-3xl font-bold text-green-600">
                  {formatCurrency(dashboard.assets)}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Liabilities: {formatCurrency(dashboard.liabilities)}
                </p>
              </div>
            </div>

            {/* Data Visualizations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Income vs Expenses Chart */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Income vs Expenses</h3>
                <div style={{ height: '300px' }}>
                  <IncomeExpensesChart
                    monthlyIncome={dashboard.monthly_income}
                    monthlyExpenses={dashboard.monthly_expenses}
                  />
                </div>
              </div>

              {/* Financial Health Score */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Health Score</h3>
                <FinancialHealthChart
                  savingsRate={dashboard.savings_rate}
                  dtiRatio={dashboard.dti_ratio}
                  emergencyBuffer={dashboard.emergency_buffer_months}
                />
                <div className="mt-6 grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <div className="font-semibold text-gray-700">Savings Rate</div>
                    <div className="text-gray-600">{dashboard.savings_rate.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-700">DTI Ratio</div>
                    <div className="text-gray-600">{dashboard.dti_ratio.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-700">Emergency Buffer</div>
                    <div className="text-gray-600">{dashboard.emergency_buffer_months.toFixed(1)}mo</div>
                  </div>
                </div>
              </div>

              {/* Net Worth Trend */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Net Worth Trend</h3>
                <div style={{ height: '300px' }}>
                  <NetWorthTrendChart
                    netWorth={dashboard.net_worth}
                    assets={dashboard.assets}
                    liabilities={dashboard.liabilities}
                  />
                </div>
              </div>

              {/* Expense Breakdown Pie Chart */}
              {dashboard.expense_breakdown && Object.keys(dashboard.expense_breakdown).length > 0 && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Expense Distribution</h3>
                  <div style={{ height: '300px' }}>
                    <ExpenseBreakdownChart expenseBreakdown={dashboard.expense_breakdown} />
                  </div>
                </div>
              )}
            </div>



            {/* Affordability Calculator CTA */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 shadow rounded-lg p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    🏠 Ready to Buy a Home?
                  </h3>
                  <p className="text-indigo-100 mb-4">
                    Calculate how much house you can afford based on your financial situation
                  </p>
                  <Link
                    to="/affordability"
                    className="inline-flex items-center px-6 py-3 bg-white text-indigo-600 font-semibold rounded-md hover:bg-indigo-50 transition"
                  >
                    Calculate Affordability →
                  </Link>
                </div>
                <div className="hidden md:block text-6xl">
                  🏡
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Link
                  to="/accounts"
                  className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <span className="mr-2">🏦</span>
                  Manage Accounts
                </Link>
                <Link
                  to="/transactions"
                  className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <span className="mr-2">💳</span>
                  View Transactions
                </Link>
                <Link
                  to="/affordability"
                  className="flex items-center justify-center px-4 py-3 border border-indigo-600 rounded-md shadow-sm text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50"
                >
                  <span className="mr-2">🏠</span>
                  Check Affordability
                </Link>
              </div>
            </div>
          </>
        )}
    </>
  );
};

export default Dashboard;
