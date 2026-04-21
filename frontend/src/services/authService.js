import axios from 'axios'

const API_URL = 'https://book-a-meal-backend.onrender.com'

const register = async (userData) => {
  const response = await axios.post(`${API_URL}/auth/register`, userData)
  return response.data
}

const login = async (credentials) => {
  const response = await axios.post(`${API_URL}/auth/login`, credentials)
  return response.data
}

const verifyEmail = async (token) => {
  const response = await axios.get(`${API_URL}/auth/verify/${token}`)
  return response.data
}

const getCurrentUser = async (token) => {
  const response = await axios.get(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  return response.data
}

export default {
  register,
  login,
  verifyEmail,
  getCurrentUser
}
