import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import financialService from '../services/financialService';
import authService from '../services/authService';
import { Lightbulb, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const Affordability = () => {
  const [user] = useState(authService.getUser());
  const [loading, setLoading] = useState(false);
  const [affordability, setAffordability] = useState(null);
  const [error, setError] = useState('');
  
  // Form inputs
  const [downPaymentPercent, setDownPaymentPercent] = useState(20);
  const [interestRate, setInterestRate] = useState(5.8);
  const [loanTermYears, setLoanTermYears] = useState(30);
  const [propertyTaxRate, setPropertyTaxRate] = useState(1.2);
  const [insuranceRate, setInsuranceRate] = useState(0.5);
  const [hoaMonthly, setHoaMonthly] = useState(0);

  useEffect(() => {
    calculateAffordability();
  }, []);

  const calculateAffordability = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = {
        down_payment_percent: downPaymentPercent,
        interest_rate: interestRate,
        loan_term_years: loanTermYears,
        property_tax_rate: propertyTaxRate,
        insurance_rate: insuranceRate,
        hoa_monthly: hoaMonthly,
      };
      
      const data = await financialService.getAffordability(params);
      setAffordability(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to calculate affordability');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Home Affordability Calculator</h1>
        <p className="text-gray-600 mt-2">
          Calculate how much house you can afford based on your current financial situation
        </p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6 sticky top-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Loan Parameters</h2>
              
            <div className="space-y-6">
                {/* Down Payment */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Down Payment: {downPaymentPercent}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    step="5"
                    value={downPaymentPercent}
                    onChange={(e) => setDownPaymentPercent(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>50%</span>
                  </div>
                </div>

                {/* Interest Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interest Rate: {interestRate}%
                  </label>
                  <input
                    type="range"
                    min="3"
                    max="10"
                    step="0.25"
                    value={interestRate}
                    onChange={(e) => setInterestRate(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>3%</span>
                    <span>10%</span>
                  </div>
                </div>

                {/* Loan Term */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Term: {loanTermYears} years
                  </label>
                  <select
                    value={loanTermYears}
                    onChange={(e) => setLoanTermYears(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value={15}>15 years</option>
                    <option value={20}>20 years</option>
                    <option value={30}>30 years</option>
                  </select>
                </div>

                {/* Property Tax Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Property Tax Rate: {propertyTaxRate}%
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="3"
                    step="0.1"
                    value={propertyTaxRate}
                    onChange={(e) => setPropertyTaxRate(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.5%</span>
                    <span>3%</span>
                  </div>
                </div>

                {/* Insurance Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Insurance Rate: {insuranceRate}%
                  </label>
                  <input
                    type="range"
                    min="0.2"
                    max="2"
                    step="0.1"
                    value={insuranceRate}
                    onChange={(e) => setInsuranceRate(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.2%</span>
                    <span>2%</span>
                  </div>
                </div>

                {/* HOA Fees */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly HOA Fees
                  </label>
                  <input
                    type="number"
                    value={hoaMonthly}
                    onChange={(e) => setHoaMonthly(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="0"
                  />
                </div>

                <button
                  onClick={calculateAffordability}
                  disabled={loading}
                  className="w-full bg-indigo-600 text-white px-4 py-3 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? 'Calculating...' : 'Calculate Affordability'}
                </button>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {loading ? (
              <div className="bg-white shadow rounded-lg p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Calculating your home affordability...</p>
              </div>
            ) : affordability ? (
              <>
                {/* Price Range */}
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 shadow rounded-lg p-6 text-white">
                  <h2 className="text-xl font-semibold mb-4">Your Home Price Range</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm opacity-90">Maximum Price</p>
                      <p className="text-3xl font-bold">{formatCurrency(affordability.max_home_price)}</p>
                    </div>
                    <div>
                      <p className="text-sm opacity-90">Recommended Safe Price</p>
                      <p className="text-3xl font-bold">{formatCurrency(affordability.safe_home_price)}</p>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-white bg-opacity-20 rounded">
                    <div className="flex items-start gap-2">
                      <Lightbulb className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      <p className="text-sm">
                        We recommend staying in the range of{' '}
                        <strong>{formatCurrency(affordability.recommended_range.min)}</strong> to{' '}
                        <strong>{formatCurrency(affordability.recommended_range.max)}</strong>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Monthly Payment Breakdown */}
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Payment Breakdown</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center pb-3 border-b">
                      <span className="text-gray-700">Principal & Interest</span>
                      <span className="font-semibold text-gray-900">
                        {formatCurrency(affordability.monthly_payment.principal_interest)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b">
                      <span className="text-gray-700">Property Tax</span>
                      <span className="font-semibold text-gray-900">
                        {formatCurrency(affordability.monthly_payment.property_tax)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pb-3 border-b">
                      <span className="text-gray-700">Insurance</span>
                      <span className="font-semibold text-gray-900">
                        {formatCurrency(affordability.monthly_payment.insurance)}
                      </span>
                    </div>
                    {affordability.monthly_payment.pmi > 0 && (
                      <div className="flex justify-between items-center pb-3 border-b">
                        <span className="text-gray-700">PMI (Private Mortgage Insurance)</span>
                        <span className="font-semibold text-orange-600">
                          {formatCurrency(affordability.monthly_payment.pmi)}
                        </span>
                      </div>
                    )}
                    {affordability.monthly_payment.hoa > 0 && (
                      <div className="flex justify-between items-center pb-3 border-b">
                        <span className="text-gray-700">HOA Fees</span>
                        <span className="font-semibold text-gray-900">
                          {formatCurrency(affordability.monthly_payment.hoa)}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-lg font-semibold text-gray-900">Total Monthly Payment</span>
                      <span className="text-2xl font-bold text-indigo-600">
                        {formatCurrency(affordability.monthly_payment.total)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Cash Requirements */}
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Cash Requirements</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800 mb-1">Down Payment ({downPaymentPercent}%)</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {formatCurrency(affordability.down_payment.amount)}
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-800 mb-1">Emergency Reserves (6 months)</p>
                      <p className="text-2xl font-bold text-green-900">
                        {formatCurrency(affordability.cash_requirements.emergency_reserves)}
                      </p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <p className="text-sm text-purple-800 mb-1">Estimated Closing Costs</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {formatCurrency(affordability.cash_requirements.closing_costs)}
                      </p>
                    </div>
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <p className="text-sm text-indigo-800 mb-1">Total Cash Needed</p>
                      <p className="text-2xl font-bold text-indigo-900">
                        {formatCurrency(affordability.cash_requirements.total_needed)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-700">Your Available Cash</span>
                      <span className={`text-xl font-bold ${
                        affordability.cash_requirements.available >= affordability.cash_requirements.total_needed
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}>
                        {formatCurrency(affordability.cash_requirements.available)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Financial Health */}
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Health Indicators</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-sm text-gray-600 mb-2">DTI Ratio</p>
                      <p className={`text-3xl font-bold ${
                        affordability.financial_health.dti_ratio <= 43 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {affordability.financial_health.dti_ratio.toFixed(1)}%
                      </p>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        {affordability.financial_health.dti_ratio <= 43 ? (
                          <><CheckCircle className="h-3 w-3 text-green-600" /><span className="text-xs text-gray-500">Good</span></>
                        ) : (
                          <><AlertTriangle className="h-3 w-3 text-red-600" /><span className="text-xs text-gray-500">High</span></>
                        )}
                      </div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-sm text-gray-600 mb-2">Emergency Buffer</p>
                      <p className={`text-3xl font-bold ${
                        affordability.financial_health.emergency_buffer_months >= 6 ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {affordability.financial_health.emergency_buffer_months.toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">months</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-sm text-gray-600 mb-2">Monthly Income</p>
                      <p className="text-3xl font-bold text-gray-900">
                        {formatCurrency(affordability.financial_health.monthly_income)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Warnings & Recommendations */}
                {(affordability.warnings.length > 0 || affordability.recommendations.length > 0) && (
                  <div className="bg-white shadow rounded-lg p-6">
                    {affordability.warnings.length > 0 && (
                      <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                          <AlertTriangle className="h-5 w-5 text-red-600" />
                          <h3 className="text-lg font-semibold text-red-700">Warnings</h3>
                        </div>
                        <ul className="space-y-2">
                          {affordability.warnings.map((warning, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-red-500 mr-2">•</span>
                              <span className="text-gray-700">{warning}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {affordability.recommendations.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Lightbulb className="h-5 w-5 text-blue-600" />
                          <h3 className="text-lg font-semibold text-blue-700">Recommendations</h3>
                        </div>
                        <ul className="space-y-2">
                          {affordability.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="text-blue-500 mr-2">•</span>
                              <span className="text-gray-700">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white shadow rounded-lg p-8 text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Calculate</h3>
                <p className="text-gray-600">
                  Adjust the parameters on the left and click "Calculate Affordability" to see your results.
                </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Affordability;
