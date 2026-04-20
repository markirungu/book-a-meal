import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await api.post('/auth/forgot-password', { email })
      setSuccess('If an account exists for this email, reset instructions have been sent.')
    } catch (err) {
      setError(err.response?.data?.error || 'Password reset is currently unavailable. Please contact support.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__header">
          <h1>Forgot Password</h1>
          <p>Enter your email and we will send password reset instructions.</p>
        </div>

        {error && <div className="feedback feedback--error">{error}</div>}
        {success && <div className="feedback feedback--success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input"
              placeholder="you@example.com"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="button button--primary button--full"
          >
            {loading ? 'Sending...' : 'Send reset link'}
          </button>
        </form>

        <p className="auth-card__footer">
          Remembered your password? <Link to="/login">Back to login</Link>
        </p>
      </div>
    </div>
  )
}

export default ForgotPasswordPage
