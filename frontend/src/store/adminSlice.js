import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import api from '../api'

export const fetchAdminRevenue = createAsyncThunk('admin/fetchRevenue', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await api.get('/orders/admin/revenue', { params })
    return response.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load revenue')
  }
})

export const fetchAdminAnalytics = createAsyncThunk('admin/fetchAnalytics', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get('/orders/admin/analytics')
    return response.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load analytics')
  }
})

const adminSlice = createSlice({
  name: 'admin',
  initialState: {
    revenue: null,
    analytics: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAdminRevenue.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchAdminRevenue.fulfilled, (state, action) => {
        state.loading = false
        state.revenue = action.payload
      })
      .addCase(fetchAdminRevenue.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload || 'Failed to load revenue'
      })
      .addCase(fetchAdminAnalytics.fulfilled, (state, action) => {
        state.analytics = action.payload
      })
  },
})

export default adminSlice.reducer
