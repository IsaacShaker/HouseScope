import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

// Expense Breakdown Doughnut Chart
export const ExpenseBreakdownChart = ({ expenseBreakdown }) => {
  const data = {
    labels: Object.keys(expenseBreakdown).map(
      (cat) => cat.charAt(0).toUpperCase() + cat.slice(1)
    ),
    datasets: [
      {
        label: 'Expenses',
        data: Object.values(expenseBreakdown),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(199, 199, 199, 0.8)',
          'rgba(83, 102, 255, 0.8)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)',
          'rgba(83, 102, 255, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: $${value.toFixed(2)}`;
          },
        },
      },
    },
  };

  return <Doughnut data={data} options={options} />;
};

// Income vs Expenses Bar Chart
export const IncomeExpensesChart = ({ monthlyIncome, monthlyExpenses }) => {
  const data = {
    labels: ['This Month'],
    datasets: [
      {
        label: 'Income',
        data: [monthlyIncome],
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 2,
      },
      {
        label: 'Expenses',
        data: [monthlyExpenses],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const label = context.dataset.label || '';
            const value = context.parsed.y || 0;
            return `${label}: $${value.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return '$' + value.toLocaleString();
          },
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
};

// Net Worth Trend Chart (placeholder for now - would need historical data)
export const NetWorthTrendChart = ({ netWorth, assets, liabilities }) => {
  const data = {
    labels: ['Previous', 'Current'],
    datasets: [
      {
        label: 'Net Worth',
        data: [netWorth * 0.9, netWorth], // Simulated previous value
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.parsed.y || 0;
            return `Net Worth: $${value.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: function (value) {
            return '$' + value.toLocaleString();
          },
        },
      },
    },
  };

  return <Line data={data} options={options} />;
};

// Financial Health Gauge Chart
export const FinancialHealthChart = ({ savingsRate, dtiRatio, emergencyBuffer }) => {
  // Calculate overall health score (0-100)
  const savingsScore = Math.min((savingsRate / 20) * 33, 33); // 20% savings = full marks
  const dtiScore = Math.max(0, 33 - (dtiRatio / 43) * 33); // 0% DTI = full marks, 43% = 0
  const bufferScore = Math.min((emergencyBuffer / 6) * 34, 34); // 6 months = full marks
  
  const totalScore = savingsScore + dtiScore + bufferScore;
  
  const data = {
    labels: ['Financial Health', 'Room for Improvement'],
    datasets: [
      {
        data: [totalScore, 100 - totalScore],
        backgroundColor: [
          totalScore >= 70 ? 'rgba(34, 197, 94, 0.8)' : 
          totalScore >= 50 ? 'rgba(234, 179, 8, 0.8)' : 
          'rgba(239, 68, 68, 0.8)',
          'rgba(229, 231, 235, 0.3)',
        ],
        borderColor: [
          totalScore >= 70 ? 'rgba(34, 197, 94, 1)' : 
          totalScore >= 50 ? 'rgba(234, 179, 8, 1)' : 
          'rgba(239, 68, 68, 1)',
          'rgba(229, 231, 235, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    circumference: 180,
    rotation: 270,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            if (context.dataIndex === 0) {
              return `Health Score: ${totalScore.toFixed(0)}/100`;
            }
            return null;
          },
        },
      },
    },
  };

  return (
    <div>
      <div style={{ height: '200px', position: 'relative' }}>
        <Doughnut data={data} options={options} />
      </div>
      <div className="text-center mt-4">
        <div className="text-3xl font-bold text-gray-900">{totalScore.toFixed(0)}</div>
        <div className="text-sm text-gray-600">Health Score</div>
      </div>
    </div>
  );
};
