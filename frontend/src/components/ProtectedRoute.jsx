import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children, adminOnly = false, allowGuest = false }) {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (!allowGuest && !token) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && (!token || role !== 'admin')) {
    return <Navigate to="/login" replace />
  }

  return children
}


export default ProtectedRoute