import axios from 'axios'

const viteEnv = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env : {}

const api = axios.create({
  baseURL: viteEnv.VITE_API_URL || 'http://127.0.0.1:5000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
