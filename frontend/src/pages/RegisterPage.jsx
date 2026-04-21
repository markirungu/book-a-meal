import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser } from '../services/authService'
import { setError, setLoading } from '../store/authSlice'

function RegisterPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'customer',
  })

  const [message, setMessage] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(setLoading(true))
    if (formData.password !== formData.confirmPassword) {
      setMessage('Passwords do not match')
      dispatch(setLoading(false))
      return
    }
    try {
      await registerUser({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: formData.role,
      })
      setMessage('Registration successful! Check your email to verify your account.')
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      dispatch(setError(err.response?.data?.error || 'Registration failed'))
      setMessage(err.response?.data?.error || 'Registration failed')
    } finally {
      dispatch(setLoading(false))
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__header">
          <h2>Create Account</h2>
          <p>Set up your account and start ordering daily meals.</p>
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Name"
            value={formData.name}
            onChange={handleChange}
            required
            className="input input--spaced"
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            className="input input--spaced"
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            className="input input--spaced"
          />
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            className="input input--spaced"
          />
          <select name="role" value={formData.role} onChange={handleChange} className="input input--spaced">
            <option value="customer">Customer</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" className="button button--primary button--full">Register</button>
        </form>
        {message && <div className={`feedback ${message.toLowerCase().includes('successful') ? 'feedback--success' : 'feedback--error'}`}>{message}</div>}
        <p className="auth-card__footer">Already have an account? <Link to="/login">Login</Link></p>
      </div>
    </div>
  )
}

export default RegisterPage