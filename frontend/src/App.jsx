import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

// Import pages (to be created)
// import Dashboard from './pages/Dashboard'
// import FinanceDashboard from './pages/FinanceDashboard'
// import Affordability from './pages/Affordability'
// import Properties from './pages/Properties'
// import Login from './pages/Login'

function App() {
  return (
    <Router>
      <div className="App">
        <h1>HouseScope</h1>
        <p>Welcome to HouseScope - Your Personal Finance & Real Estate Analysis Tool</p>
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* Add more routes as components are created */}
          {/* <Route path="/dashboard" element={<Dashboard />} /> */}
          {/* <Route path="/finance" element={<FinanceDashboard />} /> */}
          {/* <Route path="/affordability" element={<Affordability />} /> */}
          {/* <Route path="/properties" element={<Properties />} /> */}
          {/* <Route path="/login" element={<Login />} /> */}
        </Routes>
      </div>
    </Router>
  )
}

// Temporary homepage component
function HomePage() {
  return (
    <div style={{ padding: '20px' }}>
      <h2>Getting Started</h2>
      <p>This is the HouseScope frontend. The application is under development.</p>
      <ul>
        <li>Backend API: http://localhost:8000</li>
        <li>API Documentation: http://localhost:8000/docs</li>
      </ul>
    </div>
  )
}

export default App
