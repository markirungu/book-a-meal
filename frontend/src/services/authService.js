import axios from 'axios'

const API_URL = 'https://book-a-meal-backend.onrender.com'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const registerUser = (data) => api.post('/auth/register', data)
export const loginUser = (data) => api.post('/auth/login', data)
export const verifyEmail = (token) => api.get(`/auth/verify/${token}`)
export const getCurrentUser = () => api.get('/auth/me')