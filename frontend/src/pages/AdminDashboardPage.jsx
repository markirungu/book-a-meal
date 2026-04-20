import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchAdminAnalytics, fetchAdminRevenue } from '../store/adminSlice'

function AdminDashboardPage() {
  const dispatch = useDispatch()
  const { revenue, analytics, loading, error } = useSelector((state) => state.admin)

  useEffect(() => {
    dispatch(fetchAdminRevenue({ fulfilled_only: true }))
    dispatch(fetchAdminAnalytics())
  }, [dispatch])

  return (
    <div style={{ maxWidth: '980px', margin: '20px auto' }}>
      <h1 style={{ color: '#0f172a', marginBottom: '6px' }}>Admin Dashboard</h1>
      <p style={{ color: '#475569' }}>Revenue, trends, and operational analytics for your caterer account.</p>

      {loading && <p>Loading analytics...</p>}
      {error && <p style={{ color: '#b91c1c' }}>{error}</p>}

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '12px', marginBottom: '14px' }}>
        <article style={{ background: '#fff', border: '1px solid #cbd5e1', borderRadius: '12px', padding: '14px' }}>
          <h3 style={{ margin: 0, color: '#1e3a8a' }}>Fulfilled Revenue</h3>
          <p style={{ fontSize: '1.6rem', margin: '10px 0 0', fontWeight: 800 }}>
            Ksh {revenue?.total_revenue?.toFixed ? revenue.total_revenue.toFixed(2) : revenue?.total_revenue || '0.00'}
          </p>
        </article>
      </section>

      <section style={{ display: 'grid', gap: '12px', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        <article style={{ background: '#fff', border: '1px solid #cbd5e1', borderRadius: '12px', padding: '14px' }}>
          <h3 style={{ marginTop: 0, color: '#1e3a8a' }}>Most Ordered Meals</h3>
          {(analytics?.top_meals || []).length === 0 ? <p>No trend data yet.</p> : (
            <ul>
              {analytics.top_meals.map((item) => (
                <li key={item.meal_name}>{item.meal_name} - {item.orders} orders</li>
              ))}
            </ul>
          )}
        </article>

        <article style={{ background: '#fff', border: '1px solid #cbd5e1', borderRadius: '12px', padding: '14px' }}>
          <h3 style={{ marginTop: 0, color: '#1e3a8a' }}>Peak Days</h3>
          {(analytics?.peak_days || []).length === 0 ? <p>No peak-day data yet.</p> : (
            <ul>
              {analytics.peak_days.map((item) => (
                <li key={item.day}>{item.day}: {item.orders} orders</li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </div>
  )
}

export default AdminDashboardPage
