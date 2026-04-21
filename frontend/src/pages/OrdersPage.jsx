import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import api from '../api'
import { fetchOrderHistory, fetchOrders, updateOrder } from '../store/orderSlice'
import { addToCart } from '../store/cartSlice'

function OrdersPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { active, history, loading, error } = useSelector((state) => state.orders)
  const role = sessionStorage.getItem('role')
  const [feedback, setFeedback] = useState('')
  const currentOrder = active.find((order) => ['pending', 'preparing'].includes(order.status)) || active[0] || null
  const historyOrders = currentOrder ? history.filter((order) => order.id !== currentOrder.id) : history

  useEffect(() => {
    dispatch(fetchOrders())
    dispatch(fetchOrderHistory())
  }, [dispatch])

  const handleStatus = async (orderId, status) => {
    const result = await dispatch(updateOrder({ orderId, payload: { status } }))
    if (updateOrder.fulfilled.match(result)) {
      setFeedback('Order status updated.')
      dispatch(fetchOrderHistory())
    } else {
      setFeedback(result.payload || 'Failed to update order')
    }
  }

  const handleRefund = async (orderId) => {
    try {
      await api.post(`/orders/${orderId}/refund`, { penalty_percent: 10 })
      setFeedback('Refund processed with penalty deduction.')
      dispatch(fetchOrders())
      dispatch(fetchOrderHistory())
    } catch (err) {
      setFeedback(err.response?.data?.error || 'Refund failed')
    }
  }

  const handleReorder = (order) => {
    const mealId = order.meal_id || order.meal?.id

    if (!mealId) {
      setFeedback('Reorder unavailable for this item because meal details are missing.')
      return
    }

    const quantity = Number(order.quantity) || 1
    const totalPrice = Number(order.total_price) || 0
    const unitPrice = quantity > 0 ? totalPrice / quantity : totalPrice

    dispatch(addToCart({
      id: mealId,
      name: order.meal_name || order.meal?.name || `Meal ${mealId}`,
      price: unitPrice,
      image_url: order.meal?.image_url || '',
      description: order.meal?.description || 'Reordered from your history.',
      quantity,
    }))

    setFeedback('Meal added to cart. Continue in checkout.')
    navigate('/checkout')
  }

  if (loading) {
    return (
      <section className="page-section">
        <div className="page-heading">
          <h1>My Orders</h1>
          <p>Loading your order activity.</p>
        </div>
        <div className="stack-list">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="panel skeleton-panel">
              <div className="skeleton skeleton-line skeleton-line--title" />
              <div className="skeleton skeleton-line" />
              <div className="skeleton skeleton-line skeleton-line--short" />
            </div>
          ))}
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="page-section">
        <div className="page-heading">
          <h1>My Orders</h1>
          <p>We could not load your orders.</p>
        </div>
        <div className="empty-state empty-state--error">{error}</div>
      </section>
    )
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <h1>My Orders</h1>
        <p>Track your meal choices and current order status.</p>
      </div>
      {feedback && <div className={`feedback ${feedback.toLowerCase().includes('failed') ? 'feedback--error' : 'feedback--success'}`}>{feedback}</div>}

      <div className="section-heading section-heading--spaced">
        <h2>Current active order</h2>
        <p>Your latest pending or in-progress order appears here.</p>
      </div>

      {!currentOrder ? (
        <div className="empty-state">You have no orders yet.</div>
      ) : (
        <div className="stack-list">
          <article className="panel order-panel">
            <div className="panel__header">
              <div>
                <h3>Order #{currentOrder.id}</h3>
                <p>{currentOrder.meal_name || currentOrder.meal?.name || 'N/A'}</p>
              </div>
              <span className={`status-pill status-pill--${currentOrder.status}`}>{currentOrder.status}</span>
            </div>

            <div className="detail-grid">
              <div>
                <span className="detail-label">Time ordered</span>
                <strong>{new Date(currentOrder.created_at).toLocaleString()}</strong>
              </div>
              <div>
                <span className="detail-label">Total</span>
                <strong>Ksh {currentOrder.total_price}</strong>
              </div>
            </div>

            {role === 'admin' && (
              <div className="button-row">
                <button onClick={() => handleStatus(currentOrder.id, 'preparing')} className="button button--secondary button--small">Preparing</button>
                <button onClick={() => handleStatus(currentOrder.id, 'completed')} className="button button--primary button--small">Completed</button>
                <button onClick={() => handleStatus(currentOrder.id, 'cancelled')} className="button button--ghost button--small">Cancel</button>
              </div>
            )}

            {role !== 'admin' && currentOrder.status !== 'completed' && (
              <div className="button-row">
                <button onClick={() => handleRefund(currentOrder.id)} className="button button--secondary button--small">
                  Change Order
                </button>
                <button onClick={() => handleReorder(currentOrder)} className="button button--primary button--small">
                  Reorder
                </button>
              </div>
            )}
          </article>
        </div>
      )}

      <div className="section-heading section-heading--spaced">
        <h2>Order history</h2>
        <p>Past orders with meal, date, price, and status.</p>
      </div>

      <div className="stack-list">
        {historyOrders.length === 0 ? (
          <div className="empty-state">You have no order history yet.</div>
        ) : (
          historyOrders.map((order) => (
            <article key={`h-${order.id}`} className="panel history-row">
              <div>
                <strong>#{order.id}</strong>
                <p>{order.meal_name || 'Meal unavailable'}</p>
                {order.is_guest_order && (
                  <p className="detail-label">
                    Guest: {order.guest_name || 'N/A'} {order.guest_phone ? `(${order.guest_phone})` : ''}
                  </p>
                )}
              </div>
              <div>
                <span className="detail-label">Date</span>
                <strong>{new Date(order.created_at).toLocaleDateString()}</strong>
              </div>
              <div>
                <span className="detail-label">Price</span>
                <strong>Ksh {order.total_price}</strong>
              </div>
              {order.is_guest_order && (
                <div>
                  <span className="detail-label">Guest email</span>
                  <strong>{order.guest_email || 'N/A'}</strong>
                </div>
              )}
              <div className="button-row">
                <span className={`status-pill status-pill--${order.status}`}>{order.status}</span>
                {!order.is_guest_order && (
                  <button
                    type="button"
                    onClick={() => handleReorder(order)}
                    className="button button--secondary button--small"
                  >
                    Reorder
                  </button>
                )}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  )
}

export default OrdersPage