import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { loginUser } from '../services/authService'
import { setCredentials, setError, setLoading } from '../store/authSlice'

function LoginPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const [message, setMessage] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(setLoading(true))
    try {
      const response = await loginUser(formData)
      dispatch(setCredentials(response.data))
      navigate('/')
    } catch (err) {
      dispatch(setError(err.response?.data?.error || 'Login failed'))
      setMessage(err.response?.data?.error || 'Login failed')
    } finally {
      dispatch(setLoading(false))
    }
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        <button type="submit">Login</button>
      </form>
      {message && <p>{message}</p>}
      <p>No account? <a href="/register">Register</a></p>
    </div>
  )
}

export default LoginPage