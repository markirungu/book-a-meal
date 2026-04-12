import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children, adminOnly = false }) {
  const { token, user } = useSelector((state) => state.auth)

  if (!token) {
    return <Navigate to="/login" />
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/login" />
  }

  return children
}

export default ProtectedRoute