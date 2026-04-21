import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import api from '../api'

export const fetchOrders = createAsyncThunk('orders/fetchOrders', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await api.get('/orders', { params })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load orders')
  }
})

export const fetchOrderHistory = createAsyncThunk('orders/fetchHistory', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await api.get('/orders/history', { params })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load order history')
  }
})

export const placeOrder = createAsyncThunk('orders/placeOrder', async (payload, { rejectWithValue }) => {
  try {
    const response = await api.post('/orders', payload)
    return response.data.order
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to place order')
  }
})

export const updateOrder = createAsyncThunk('orders/updateOrder', async ({ orderId, payload }, { rejectWithValue }) => {
  try {
    const response = await api.put(`/orders/${orderId}`, payload)
    return response.data.order
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to update order')
  }
})

const orderSlice = createSlice({
  name: 'orders',
  initialState: {
    active: [],
    history: [],
    meta: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false
        state.active = action.payload.data || []
        state.meta = action.payload.meta || null
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload || 'Failed to load orders'
      })
      .addCase(fetchOrderHistory.fulfilled, (state, action) => {
        state.history = action.payload.data || []
      })
      .addCase(placeOrder.fulfilled, (state, action) => {
        state.active = [action.payload, ...state.active]
      })
      .addCase(updateOrder.fulfilled, (state, action) => {
        state.active = state.active.map((order) => (order.id === action.payload.id ? action.payload : order))
        state.history = state.history.map((order) => (order.id === action.payload.id ? action.payload : order))
      })
  },
})

export default orderSlice.reducer
