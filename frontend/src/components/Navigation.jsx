import { Link, useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = authService.getUser();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/properties', icon: '🏠', label: 'Properties' },
    { path: '/affordability', icon: '💰', label: 'Affordability' },
    { path: '/accounts', icon: '🏦', label: 'Accounts' },
    { path: '/transactions', icon: '💳', label: 'Transactions' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      width: '256px',
      minWidth: '256px',
      background: 'linear-gradient(to bottom, #3730a3, #312e81)',
      color: 'white',
      flexShrink: 0
    }}>
      {/* Logo/Header */}
      <div className="p-6 border-b border-indigo-700">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <span>🏠</span>
          <span>HouseScope</span>
        </h1>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 py-6 overflow-y-auto">
        <ul className="space-y-2 px-4">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive(item.path)
                    ? 'bg-indigo-600 shadow-lg'
                    : 'hover:bg-indigo-700'
                }`}
              >
                <span className="text-2xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-indigo-700">
        <div className="mb-3 px-4">
          <p className="text-sm text-indigo-200">Logged in as</p>
          <p className="text-sm font-medium truncate">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-indigo-700 hover:bg-indigo-600 transition-colors"
        >
          <span className="text-xl">🚪</span>
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Navigation;
