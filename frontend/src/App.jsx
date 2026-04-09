import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify/:token" element={<VerifyEmailPage />} />
        <Route path="/" element={
          <ProtectedRoute>
            <div>Home Page - Coming Soon</div>
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute adminOnly={true}>
            <div>Admin Dashboard - Coming Soon</div>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  )
}

export default App