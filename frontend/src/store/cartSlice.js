import { createSlice } from '@reduxjs/toolkit'

const getCartStorageKey = () => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  return !token || role === 'guest' ? 'dishdash_cart_guest' : 'dishdash_cart_user'
}

const readStoredCart = () => {
  try {
    const raw = localStorage.getItem(getCartStorageKey())
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const persistCart = (items) => {
  localStorage.setItem(getCartStorageKey(), JSON.stringify(items))
}

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: readStoredCart(),
  },
  reducers: {
    addToCart: (state, action) => {
      const item = action.payload
      const existing = state.items.find((entry) => entry.id === item.id)

      if (existing) {
        existing.quantity += item.quantity || 1
      } else {
        state.items.push({
          id: item.id,
          name: item.name,
          price: Number(item.price) || 0,
          image_url: item.image_url || '',
          description: item.description || '',
          quantity: item.quantity || 1,
        })
      }

      persistCart(state.items)
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter((item) => item.id !== action.payload)
      persistCart(state.items)
    },
    updateCartQuantity: (state, action) => {
      const { id, quantity } = action.payload
      const item = state.items.find((entry) => entry.id === id)

      if (!item) {
        return
      }

      item.quantity = Math.max(1, Number(quantity) || 1)
      persistCart(state.items)
    },
    clearCart: (state) => {
      state.items = []
      persistCart(state.items)
    },
  },
})

export const {
  addToCart,
  removeFromCart,
  updateCartQuantity,
  clearCart,
} = cartSlice.actions

export default cartSlice.reducer
