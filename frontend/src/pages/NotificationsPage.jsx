import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import api from '../api'

const fallbackNotifications = [
  {
    id: 'offline-1',
    title: "Today's menu is ready",
    message: 'Browse new meals and add your favorites to cart.',
    notification_type: 'menu',
    is_read: false,
    created_at: new Date().toISOString(),
  },
  {
    id: 'offline-2',
    title: 'Order updates',
    message: 'You can still explore DishDash while backend services restart.',
    notification_type: 'order',
    is_read: true,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
]

const NotificationsPage = () => {
  const { user } = useSelector((state) => state.auth)
  
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [meta, setMeta] = useState({ unread_count: 0 })
  const [page, setPage] = useState(1)
  const [showAll, setShowAll] = useState(false)
  const [offlineMode, setOfflineMode] = useState(false)

  const buildOfflineMeta = (list) => ({
    unread_count: list.filter((item) => !item.is_read).length,
    pages: 1,
  })

  const isNetworkError = (err) => err?.code === 'ERR_NETWORK' || !err?.response

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const response = await api.get('/notifications', {
        params: { page, per_page: 10, show_all: showAll }
      })
      setNotifications(response.data.data)
      setMeta(response.data.meta)
      setOfflineMode(false)
      setError(null)
    } catch (err) {
      if (isNetworkError(err)) {
        setNotifications(fallbackNotifications)
        setMeta(buildOfflineMeta(fallbackNotifications))
        setOfflineMode(true)
        setError('Backend is currently unreachable. Showing local preview notifications.')
      } else {
        setError('Failed to load notifications')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [user, page, showAll])

  const markAsRead = async (id) => {
    if (offlineMode) {
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      )
      setMeta(prev => ({ ...prev, unread_count: Math.max(0, prev.unread_count - 1) }))
      return
    }

    try {
      await api.patch(`/notifications/${id}/read`, {})
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      )
      setMeta(prev => ({ ...prev, unread_count: Math.max(0, prev.unread_count - 1) }))
    } catch {
      setError('Could not mark notification as read.')
    }
  }

  const markAllAsRead = async () => {
    if (offlineMode) {
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true }))
      )
      setMeta(prev => ({ ...prev, unread_count: 0 }))
      return
    }

    try {
      await api.patch('/notifications/read-all', {})
      setNotifications(prev =>
        prev.map(n => ({ ...n, is_read: true }))
      )
      setMeta(prev => ({ ...prev, unread_count: 0 }))
    } catch {
      setError('Could not mark all notifications as read.')
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'menu': return 'Menu'
      case 'order': return 'Order'
      default: return 'Alert'
    }
  }

  if (loading && notifications.length === 0) {
    return (
      <section className="page-section">
        <div className="page-heading">
          <h1>Notifications</h1>
          <p>Loading your latest updates.</p>
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

  return (
    <section className="page-section">
      <div className="page-heading page-heading--row">
        <div>
          <h1>Notifications</h1>
          <p>
            {meta.unread_count > 0
              ? `${meta.unread_count} unread notification${meta.unread_count !== 1 ? 's' : ''}`
              : 'Stay up to date with menu and order activity.'}
          </p>
        </div>
        <div className="button-row">
          <button
            onClick={() => setShowAll(!showAll)}
            className="button button--ghost button--small"
          >
            {showAll ? 'Show unread' : 'Show all'}
          </button>

          {meta.unread_count > 0 && (
            <button
              onClick={markAllAsRead}
              className="button button--secondary button--small"
            >
              Mark all read
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="feedback feedback--error">
          {error}
        </div>
      )}

      <div className="stack-list">
        {notifications.length === 0 ? (
          <div className="empty-state">No notifications yet</div>
        ) : (
          notifications.map((notification) => (
            <article
              key={notification.id}
              className={`panel notification-card ${notification.is_read ? '' : 'notification-card--unread'}`}
            >
              <div className="notification-card__label">{getNotificationIcon(notification.notification_type)}</div>
              <div className="notification-card__body">
                <div className="panel__header">
                  <div>
                    <h3>{notification.title || "Today's menu is ready"}</h3>
                    <p>{notification.message}</p>
                  </div>
                  {!notification.is_read && <span className="tag">Unread</span>}
                </div>
                <div className="notification-card__footer">
                  <span className="detail-label">{formatDate(notification.created_at)}</span>
                  {!notification.is_read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="button button--ghost button--small"
                    >
                      Mark read
                    </button>
                  )}
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {meta.pages > 1 && (
        <div className="pagination-row">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="button button--ghost button--small"
          >
            Previous
          </button>

          <span className="pagination-copy">
            Page {page} of {meta.pages}
          </span>

          <button
            onClick={() => setPage(p => Math.min(meta.pages, p + 1))}
            disabled={page === meta.pages}
            className="button button--ghost button--small"
          >
            Next
          </button>
        </div>
      )}
    </section>
  )
}

export default NotificationsPage