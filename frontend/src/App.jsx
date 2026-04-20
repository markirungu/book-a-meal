import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useSelector } from 'react-redux'
import LoginPage from './pages/LoginPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import NotificationsPage from './pages/NotificationsPage'
import MenuPage from './pages/MenuPage'
import CheckoutPage from './pages/CheckoutPage'
import OrdersPage from './pages/OrdersPage'
import AdminMealsPage from './pages/AdminMealsPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import HomePage from './pages/HomePage'
import ProtectedRoute from './components/ProtectedRoute'

function AppShell({ children }) {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  const isAdmin = token && role === 'admin'
  const { items } = useSelector((state) => state.cart)
  const cartCount = items.reduce((total, item) => total + item.quantity, 0)

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="site-header__inner">
          <Link to="/" className="site-logo">DishDash</Link>
          <nav className="site-nav" aria-label="Main navigation">
            <Link to="/" className="site-nav__link">Home</Link>
            <Link to="/menu" className="site-nav__link">Menu</Link>
            <Link to="/checkout" className="site-nav__link site-nav__link--cart">
              Cart
              <span className="cart-badge" aria-label={`${cartCount} items in cart`}>
                {cartCount}
              </span>
            </Link>
            <Link to="/orders" className="site-nav__link">Orders</Link>
            <Link to="/notifications" className="site-nav__link">Notifications</Link>
            {isAdmin && <Link to="/admin/dashboard" className="site-nav__link">Dashboard</Link>}
            {isAdmin && <Link to="/admin/meals" className="site-nav__link">Manage Meals</Link>}
            <Link to="/login" className="site-nav__link">Login</Link>
            <Link to="/register" className="site-nav__link">Register</Link>
            {token && (
              <button
                onClick={() => {
                  localStorage.removeItem('token')
                  localStorage.removeItem('role')
                  window.location.href = '/login'
                }}
                className="button button--primary button--small"
              >
                Logout
              </button>
            )}
          </nav>
        </div>
      </header>
      <main className="app-content">{children}</main>
      <footer className="site-footer">
        <div className="site-footer__inner">
          <div>
            <p className="site-footer__title">DishDash</p>
            <p className="site-footer__text">Fast daily ordering for customers and caterers.</p>
          </div>
          <nav className="site-footer__nav" aria-label="Footer navigation">
            <Link to="/" className="site-footer__link">Home</Link>
            <Link to="/menu" className="site-footer__link">Menu</Link>
            <Link to="/checkout" className="site-footer__link">Checkout</Link>
            <Link to="/orders" className="site-footer__link">Orders</Link>
            <Link to="/notifications" className="site-footer__link">Notifications</Link>
            {isAdmin && <Link to="/admin/dashboard" className="site-footer__link">Dashboard</Link>}
            {isAdmin && <Link to="/admin/meals" className="site-footer__link">Manage Meals</Link>}
            <Link to="/login" className="site-footer__link">Login</Link>
            <Link to="/register" className="site-footer__link">Register</Link>
          </nav>
        </div>
      </footer>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public pages */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify/:token" element={<VerifyEmailPage />} />
        <Route path="/auth/verify/:token" element={<VerifyEmailPage />} />

        {/* Customer pages */}
        <Route path="/menu" element={
          <ProtectedRoute allowGuest>
            <AppShell>
              <MenuPage />
            </AppShell>
          </ProtectedRoute>
        } />
        <Route path="/checkout" element={
          <ProtectedRoute allowGuest>
            <AppShell>
              <CheckoutPage />
            </AppShell>
          </ProtectedRoute>
        } />
        <Route path="/orders" element={
          <ProtectedRoute>
            <AppShell>
              <OrdersPage />
            </AppShell>
          </ProtectedRoute>
        } />
        <Route path="/notifications" element={
          <ProtectedRoute>
            <AppShell>
              <NotificationsPage />
            </AppShell>
          </ProtectedRoute>
        } />

        {/* Admin pages */}
        <Route path="/admin/dashboard" element={
          <ProtectedRoute adminOnly>
            <AppShell>
              <AdminDashboardPage />
            </AppShell>
          </ProtectedRoute>
        } />
        <Route path="/admin/meals" element={
          <ProtectedRoute adminOnly>
            <AppShell>
              <AdminMealsPage />
            </AppShell>
          </ProtectedRoute>
        } />

        <Route path="/" element={<HomePage />} />

        <Route path="*" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App