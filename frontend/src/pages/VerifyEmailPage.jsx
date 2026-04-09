import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { verifyEmail } from '../services/authService'

function VerifyEmailPage() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [message, setMessage] = useState('Verifying your email...')

  useEffect(() => {
    const verify = async () => {
      try {
        const response = await verifyEmail(token)
        setMessage(response.data.message)
        setTimeout(() => navigate('/login'), 3000)
      } catch (err) {
        setMessage(err.response?.data?.error || 'Verification failed')
      }
    }
    verify()
  }, [token])

  return (
    <div>
      <h2>Email Verification</h2>
      <p>{message}</p>
    </div>
  )
}

export default VerifyEmailPage