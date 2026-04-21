import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children, adminOnly = false, allowGuest = false }) {
  const token = sessionStorage.getItem('token')
  const role = sessionStorage.getItem('role')

  if (!allowGuest && !token) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && (!token || role !== 'admin')) {
    return <Navigate to="/login" replace />
  }

  return children
}


export default ProtectedRoute