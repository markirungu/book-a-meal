import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import api from '../api'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [accountType, setAccountType] = useState('user')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const infoMessage = new URLSearchParams(location.search).get('message')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await api.post('/auth/login', { email, password })
      const accessToken = response.data?.access_token
      const backendRole = response.data?.user?.role || 'customer'

      if (!accessToken) {
        throw new Error('Authentication token missing from response')
      }

      if (accountType === 'admin' && backendRole !== 'admin') {
        throw new Error('This account is not an admin account')
      }

      if (accountType === 'staff' && backendRole !== 'admin') {
        throw new Error('This account is not a staff account')
      }

      if (accountType === 'user' && backendRole !== 'customer') {
        throw new Error('Please use a user account for this login type')
      }

      const role = backendRole === 'customer' ? 'user' : backendRole

      sessionStorage.setItem('token', accessToken)
      sessionStorage.setItem('role', role)
      sessionStorage.setItem('userEmail', response.data?.user?.email || email)

      const guestCartRaw = sessionStorage.getItem('dishdash_cart_guest')
      const userCartRaw = sessionStorage.getItem('dishdash_cart_user')
      if (guestCartRaw && !userCartRaw) {
        sessionStorage.setItem('dishdash_cart_user', guestCartRaw)
      }

      navigate(backendRole === 'admin' ? '/admin/meals' : '/menu')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Invalid email or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const continueAsGuest = () => {
    sessionStorage.removeItem('token')
    sessionStorage.setItem('role', 'guest')
    navigate('/menu')
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__header">
          <h1>Login</h1>
          <p>Access your menu, orders, and notifications.</p>
        </div>

        {infoMessage && <div className="info-strip">{infoMessage}</div>}

        {error && <div className="feedback feedback--error">{error}</div>}

        <div className="type-switch" role="tablist" aria-label="Account type">
          <button type="button" aria-pressed={accountType === 'user'} className={`filter-chip ${accountType === 'user' ? 'filter-chip--active' : ''}`} onClick={() => setAccountType('user')}>User Login</button>
          <button type="button" aria-pressed={accountType === 'staff'} className={`filter-chip ${accountType === 'staff' ? 'filter-chip--active' : ''}`} onClick={() => setAccountType('staff')}>Staff Login</button>
          <button type="button" aria-pressed={accountType === 'admin'} className={`filter-chip ${accountType === 'admin' ? 'filter-chip--active' : ''}`} onClick={() => setAccountType('admin')}>Admin Login</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input"
            />
          </div>

          <div className="form-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input"
            />
            <div className="auth-inline-link">
              <Link to="/forgot-password">Forgot password?</Link>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="button button--primary button--full"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="button-row">
          <button type="button" className="button button--secondary button--small" onClick={continueAsGuest}>Continue as Guest</button>
          <Link to="/" className="button button--ghost button--small">Back to Home</Link>
        </div>

        <p className="auth-card__footer">Don&apos;t have an account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  )
}

export default LoginPage