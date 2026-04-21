import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const registerUser = async (userData) => {
  const response = await axios.post(`${API_URL}/auth/register`, userData)
  return response.data
}

export const loginUser = async (credentials) => {
  const response = await axios.post(`${API_URL}/auth/login`, credentials)
  return response.data
}

export const verifyEmail = async (token) => {
  const response = await axios.get(`${API_URL}/auth/verify/${token}`)
  return response.data
}

export const getCurrentUser = async (token) => {
  const response = await axios.get(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  return response.data
}