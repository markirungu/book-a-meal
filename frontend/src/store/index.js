import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import menuReducer from './menuSlice'
import orderReducer from './orderSlice'
import adminReducer from './adminSlice'
import cartReducer from './cartSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    menu: menuReducer,
    orders: orderReducer,
    admin: adminReducer,
    cart: cartReducer,
  },
})