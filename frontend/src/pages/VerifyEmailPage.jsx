import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

function VerifyEmailPage() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('loading')
  const [message, setMessage] = useState('Verifying your email...')

  const API_URL = import.meta.env.VITE_API_URL || 'https://book-a-meal-backend.onrender.com'

  useEffect(() => {
    const verify = async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/verify/${token}`)
        setStatus('success')
        setMessage(response.data.message || 'Email verified successfully!')
        setTimeout(() => navigate('/login'), 2000)
      } catch (err) {
        setStatus('error')
        setMessage(err.response?.data?.error || 'Verification failed. Invalid or expired token.')
      }
    }
    
    if (token) {
      verify()
    }
  }, [token, navigate, API_URL])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        {status === 'loading' && (
          <>
            <div className="text-4xl mb-4">⏳</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Verifying...</h2>
            <p className="text-gray-600">{message}</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-4xl mb-4">✅</div>
            <h2 className="text-xl font-semibold text-green-600 mb-2">Success!</h2>
            <p className="text-gray-600 mb-4">{message}</p>
            <p className="text-sm text-gray-500">Redirecting to login...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-4xl mb-4">❌</div>
            <h2 className="text-xl font-semibold text-red-600 mb-2">Verification Failed</h2>
            <p className="text-gray-600 mb-4">{message}</p>
            <button 
              onClick={() => navigate('/login')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Go to Login
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default VerifyEmailPage