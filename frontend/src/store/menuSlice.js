import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import api from '../api'

export const fetchTodayMenu = createAsyncThunk('menu/fetchToday', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await api.get('/menus/today', { params })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load today menu')
  }
})

export const fetchMenus = createAsyncThunk('menu/fetchMenus', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await api.get('/menus', { params })
    return response.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to load menus')
  }
})

export const createMenu = createAsyncThunk('menu/createMenu', async (payload, { rejectWithValue }) => {
  try {
    const response = await api.post('/menus', payload)
    return response.data.menu
  } catch (err) {
    return rejectWithValue(err.response?.data?.error || 'Failed to create menu')
  }
})

const menuSlice = createSlice({
  name: 'menu',
  initialState: {
    today: null,
    items: [],
    meta: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodayMenu.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTodayMenu.fulfilled, (state, action) => {
        state.loading = false
        state.today = action.payload
      })
      .addCase(fetchTodayMenu.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload || 'Failed to load today menu'
      })
      .addCase(fetchMenus.fulfilled, (state, action) => {
        state.items = action.payload.data || []
        state.meta = action.payload.meta || null
      })
      .addCase(createMenu.fulfilled, (state, action) => {
        state.items = [action.payload, ...state.items]
      })
  },
})

export default menuSlice.reducer
