import { useState, useEffect } from 'react'
import api from '../api'

function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/orders')
      .then(response => {
        setOrders(response.data)
        setLoading(false)
      })
      .catch(() => {
        setError('Could not load orders. Please try again later.')
        setLoading(false)
      })
  }, [])

  if (loading) return <p style={{ textAlign: 'center', marginTop: '100px' }}>Loading orders...</p>
  if (error) return <p style={{ textAlign: 'center', color: 'red', marginTop: '100px' }}>{error}</p>

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px' }}>
      <h1>My Orders</h1>

      {orders.length === 0 ? (
        <p>You have no orders yet.</p>
      ) : (
        <div>
          {orders.map(order => (
            <div key={order.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '15px', borderRadius: '8px' }}>
              <h2>Order #{order.id}</h2>
              <p><strong>Meal:</strong> {order.meal_name}</p>
              <p><strong>Status:</strong> {order.status}</p>
              <p><strong>Date:</strong> {new Date(order.created_at).toLocaleDateString('en-KE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default OrdersPage