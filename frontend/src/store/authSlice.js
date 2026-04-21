import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  user: null,
  token: sessionStorage.getItem('token') || null,
  isAuthenticated: !!sessionStorage.getItem('token'),
  loading: false,
  error: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      state.user = action.payload.user
      state.token = action.payload.access_token
      state.isAuthenticated = true
      sessionStorage.setItem('token', action.payload.access_token)
      if (action.payload.user?.role) {
        sessionStorage.setItem('role', action.payload.user.role)
      }
    },
    logout: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('role')
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
  },
})

export const { setCredentials, logout, setLoading, setError } = authSlice.actions
export default authSlice.reducer