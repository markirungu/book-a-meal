import { useEffect, useMemo, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchTodayMenu } from '../store/menuSlice'
import { placeOrder } from '../store/orderSlice'
import api from '../api'
import {
  clearCart,
  removeFromCart,
  updateCartQuantity,
} from '../store/cartSlice'

function CheckoutPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { items } = useSelector((state) => state.cart)
  const { today } = useSelector((state) => state.menu)
  const [feedback, setFeedback] = useState('')
  const [checkingOut, setCheckingOut] = useState(false)
  const [guestForm, setGuestForm] = useState({
    name: '',
    email: '',
    phone: '',
    deliveryInfo: '',
  })

  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  const isGuest = !token || role === 'guest'

  const total = useMemo(
    () => items.reduce((sum, item) => sum + (Number(item.price) || 0) * item.quantity, 0),
    [items],
  )

  useEffect(() => {
    if (!today?.id) {
      dispatch(fetchTodayMenu())
    }
  }, [dispatch, today])

  const validateCartForCheckout = () => {
    if (items.length === 0) {
      return 'Your cart is empty.'
    }

    if (!today?.id) {
      return 'No active menu is available for checkout right now.'
    }

    if (today.cutoff_time && new Date() > new Date(today.cutoff_time)) {
      return 'Order cutoff time has passed for today.'
    }

    const menuMealIds = new Set((today.meals || []).map((meal) => meal.id))
    const hasUnavailableMeal = items.some((item) => !menuMealIds.has(item.id))

    if (hasUnavailableMeal) {
      return 'Some cart items are no longer available on today\'s menu.'
    }

    return ''
  }

  const validateGuestForm = () => {
    if (!guestForm.name.trim()) {
      return 'Please enter your name.'
    }
    if (!guestForm.email.trim()) {
      return 'Please enter your email address.'
    }
    if (!guestForm.phone.trim()) {
      return 'Please enter your phone number.'
    }
    return ''
  }

  const handleCheckout = async () => {
    if (items.length === 0) {
      setFeedback('Your cart is empty.')
      return
    }

    setCheckingOut(true)
    setFeedback('')

    const validationError = validateCartForCheckout()
    if (validationError) {
      setFeedback(validationError)
      setCheckingOut(false)
      return
    }

    if (isGuest) {
      const guestError = validateGuestForm()
      if (guestError) {
        setFeedback(guestError)
        setCheckingOut(false)
        return
      }

      try {
        const guestResults = await Promise.all(
          items.map((item) => api.post('/orders/guest', {
            menu_id: today.id,
            meal_id: item.id,
            quantity: item.quantity,
            guest_name: guestForm.name,
            guest_email: guestForm.email,
            guest_phone: guestForm.phone,
            delivery_info: guestForm.deliveryInfo,
          })),
        )

        if (guestResults.length !== items.length) {
          setFeedback('Some guest order items could not be submitted. Please try again.')
          setCheckingOut(false)
          return
        }

        dispatch(clearCart())
        setFeedback('Guest order received. An admin will process it manually.')
        setCheckingOut(false)
      } catch (err) {
        setFeedback(err.response?.data?.error || 'Could not submit guest order right now.')
        setCheckingOut(false)
      }
      return
    }

    try {
      const results = await Promise.all(
        items.map((item) => dispatch(placeOrder({ menu_id: today.id, meal_id: item.id, quantity: item.quantity }))),
      )

      const failed = results.filter((result) => placeOrder.rejected.match(result))

      if (failed.length > 0) {
        setFeedback('Some items could not be checked out. Please try again.')
        setCheckingOut(false)
        return
      }

      dispatch(clearCart())
      setFeedback('Checkout complete. Your order has been placed and is now pending.')
      setCheckingOut(false)
      navigate('/orders')
    } catch {
      setFeedback('Checkout failed. Please try again.')
      setCheckingOut(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-heading page-heading--row">
        <div>
          <h1>Checkout</h1>
          <p>{isGuest ? 'Guest checkout creates a temporary guest order for manual admin handling.' : 'Review your cart and confirm your order.'}</p>
        </div>
        <button type="button" className="button button--ghost button--small" onClick={() => navigate('/menu')}>
          Back to Menu
        </button>
      </div>

      {feedback && (
        <div className={`feedback ${feedback.toLowerCase().includes('complete') ? 'feedback--success' : 'feedback--error'}`}>
          {feedback}
        </div>
      )}

      {items.length === 0 ? (
        <div className="empty-state">Your cart is empty. Add meals from the menu to continue.</div>
      ) : (
        <div className="checkout-grid">
          <div className="panel checkout-items">
            {isGuest && (
              <div className="panel guest-checkout-form">
                <div className="section-heading">
                  <h2>Guest details</h2>
                  <p>These details help the admin process your guest order.</p>
                </div>
                <div className="detail-grid">
                  <label className="form-field">
                    <span>Name</span>
                    <input
                      type="text"
                      className="input"
                      value={guestForm.name}
                      onChange={(e) => setGuestForm((prev) => ({ ...prev, name: e.target.value }))}
                      placeholder="Your full name"
                    />
                  </label>
                  <label className="form-field">
                    <span>Email</span>
                    <input
                      type="email"
                      className="input"
                      value={guestForm.email}
                      onChange={(e) => setGuestForm((prev) => ({ ...prev, email: e.target.value }))}
                      placeholder="you@example.com"
                    />
                  </label>
                  <label className="form-field">
                    <span>Phone</span>
                    <input
                      type="tel"
                      className="input"
                      value={guestForm.phone}
                      onChange={(e) => setGuestForm((prev) => ({ ...prev, phone: e.target.value }))}
                      placeholder="07xxxxxxxx"
                    />
                  </label>
                  <label className="form-field">
                    <span>Delivery info (optional)</span>
                    <input
                      type="text"
                      className="input"
                      value={guestForm.deliveryInfo}
                      onChange={(e) => setGuestForm((prev) => ({ ...prev, deliveryInfo: e.target.value }))}
                      placeholder="Pickup or delivery note"
                    />
                  </label>
                </div>
              </div>
            )}

            {items.map((item) => (
              <article key={item.id} className="cart-row">
                <img
                  src={item.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1200&q=80'}
                  alt={item.name}
                  className="cart-row__image"
                />
                <div className="cart-row__details">
                  <h2>{item.name}</h2>
                  <p>{item.description || 'Meal item'}</p>
                  <span className="price-label">Ksh {item.price}</span>
                </div>
                <div className="cart-row__controls">
                  <div className="quantity-control">
                    <button
                      type="button"
                      className="button button--secondary button--small"
                      onClick={() => dispatch(updateCartQuantity({ id: item.id, quantity: item.quantity - 1 }))}
                    >
                      -
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      type="button"
                      className="button button--secondary button--small"
                      onClick={() => dispatch(updateCartQuantity({ id: item.id, quantity: item.quantity + 1 }))}
                    >
                      +
                    </button>
                  </div>
                  <button
                    type="button"
                    className="button button--ghost button--small"
                    onClick={() => dispatch(removeFromCart(item.id))}
                  >
                    Remove
                  </button>
                </div>
              </article>
            ))}
          </div>

          <aside className="panel checkout-summary">
            <div className="section-heading">
              <h2>Order Summary</h2>
              <p>{items.length} items in cart</p>
            </div>
            <p className="detail-label">Delivery / Collection: Standard pickup at your selected kitchen point.</p>
            <div className="checkout-total">
              <span>Total</span>
              <strong>Ksh {total}</strong>
            </div>
            <button
              type="button"
              className="button button--primary button--full"
              disabled={checkingOut}
              onClick={handleCheckout}
            >
              {checkingOut ? 'Processing checkout...' : isGuest ? 'Submit Guest Order' : 'Confirm Order'}
            </button>
          </aside>
        </div>
      )}
    </section>
  )
}

export default CheckoutPage
