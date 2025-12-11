import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Import pages
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Accounts from './pages/Accounts'
import Affordability from './pages/Affordability'
import ProtectedRoute from './components/ProtectedRoute'
import authService from './services/authService'

function App() {
  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            authService.isAuthenticated() ? 
              <Navigate to="/dashboard" replace /> : 
              <Navigate to="/login" replace />
          } 
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/accounts"
          element={
            <ProtectedRoute>
              <Accounts />
            </ProtectedRoute>
          }
        />
        <Route
          path="/affordability"
          element={
            <ProtectedRoute>
              <Affordability />
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions"
          element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Transactions Page</h2>
                  <p className="text-gray-600">Coming soon...</p>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/affordability"
          element={
            <ProtectedRoute>
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Affordability Calculator</h2>
                  <p className="text-gray-600">Coming soon...</p>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
