import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'

function HomePage() {
  const token = sessionStorage.getItem('token')
  const role = sessionStorage.getItem('role')
  const isAdmin = token && role === 'admin'
  const isCustomer = token && (role === 'user' || role === 'customer')
  const { items } = useSelector((state) => state.cart)
  const cartCount = items.reduce((total, item) => total + item.quantity, 0)
  const featuredMeals = [
    {
      title: 'Herb Chicken Bowl',
      description: 'Grilled chicken, rice, and fresh greens for a balanced lunch.',
      tag: 'Popular',
      image: 'https://images.unsplash.com/photo-1604908554027-1b6f2b2f3f8b?auto=format&fit=crop&w=1200&q=80',
    },
    {
      title: 'Beef Pilau',
      description: 'Slow-cooked beef with warm spices and a rich pilau finish.',
      tag: 'Today',
      image: 'https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80',
    },
    {
      title: 'Fresh Veggie Plate',
      description: 'A lighter option with roasted vegetables and house dressing.',
      tag: 'Light',
      image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80',
    },
    {
      title: 'Chef Special Pasta',
      description: 'A rotating daily special with simple ingredients and bold flavor.',
      tag: 'Special',
      image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80',
    },
  ]

  return (
    <div className="landing-page">
      <header className="site-header">
        <div className="site-header__inner">
          <Link to="/" className="site-logo">DishDash</Link>
          <nav className="site-nav" aria-label="Main navigation">
            <Link to="/" className="site-nav__link">Home</Link>
            <Link to="/menu" className="site-nav__link">Menu</Link>
            
            {/* ✅ Cart - Only for customers, not admin */}
            {isCustomer && (
              <Link to="/checkout" className="site-nav__link site-nav__link--cart">
                Cart
                <span className="cart-badge" aria-label={`${cartCount} items in cart`}>
                  {cartCount}
                </span>
              </Link>
            )}
            
            {/* ✅ Orders & Notifications - Only when logged in */}
            {token && <Link to="/orders" className="site-nav__link">Orders</Link>}
            {token && <Link to="/notifications" className="site-nav__link">Notifications</Link>}
            
            {isAdmin && <Link to="/admin/dashboard" className="site-nav__link">Dashboard</Link>}
            {isAdmin && <Link to="/admin/meals" className="site-nav__link">Manage Meals</Link>}
            
            {!token && <Link to="/login" className="site-nav__link">Login</Link>}
            {!token && <Link to="/register" className="button button--primary button--small">Register</Link>}
            
            {token && (
              <button
                onClick={() => {
                  sessionStorage.removeItem('token')
                  sessionStorage.removeItem('role')
                  window.location.href = '/login'
                }}
                className="button button--secondary button--small"
              >
                Logout
              </button>
            )}
          </nav>
        </div>
      </header>

      <main className="landing-content">
        <section className="hero hero--solid">
          <div className="hero__content">
            <p className="eyebrow">Fast meal ordering</p>
            <h1 className="hero__title">Order your daily meals</h1>
            <p className="hero__text">
              A simple way to browse today&apos;s meals, select what you want, and keep track of every order.
            </p>
            <div className="button-row">
              <Link to="/menu" className="button button--primary">View Menu</Link>
              <Link to={token ? '/orders' : '/register'} className="button button--secondary">Get Started</Link>
            </div>
          </div>
          <div className="hero__panel">
            <div className="hero-stat">
              <span className="hero-stat__label">Today</span>
              <strong className="hero-stat__value">Fresh meals ready</strong>
            </div>
            <div className="hero-stat">
              <span className="hero-stat__label">Flow</span>
              <strong className="hero-stat__value">Browse, select, order</strong>
            </div>
          </div>
        </section>

        <section className="section-block">
          <div className="section-heading">
            <h2>Featured meals</h2>
            <p>A clean preview of what customers can expect today.</p>
          </div>
          <div className="meal-grid">
            {featuredMeals.map((meal) => (
              <article key={meal.title} className="meal-card">
                <img src={meal.image} alt={meal.title} className="meal-card__image" />
                <div className="meal-card__body">
                  <div className="meal-card__top">
                    <h3>{meal.title}</h3>
                    <span className="tag">{meal.tag}</span>
                  </div>
                  <p>{meal.description}</p>
                  <div className="meal-card__footer">
                    <span className="price-label">From Ksh 450</span>
                    <Link to="/menu" className="button button--secondary button--small">View</Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section-block">
          <div className="section-heading">
            <h2>How it works</h2>
            <p>Three quick steps from browsing to checkout.</p>
          </div>
          <div className="steps-grid">
            <article className="step-card">
              <span className="step-card__number">1</span>
              <h3>Browse menu</h3>
              <p>Open the daily menu and review featured meals, categories, and specials.</p>
            </article>
            <article className="step-card">
              <span className="step-card__number">2</span>
              <h3>Select meal</h3>
              <p>Compare price, description, and tags before making your choice.</p>
            </article>
            <article className="step-card">
              <span className="step-card__number">3</span>
              <h3>Place order</h3>
              <p>Submit your order and track updates from confirmation to completion.</p>
            </article>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-footer__inner">
          <div>
            <p className="site-footer__title">Contact</p>
            <p className="site-footer__text">support@dishdash.app</p>
          </div>
          <nav className="site-footer__nav" aria-label="Footer navigation">
            <Link to="/" className="site-footer__link">Home</Link>
            <Link to="/menu" className="site-footer__link">Menu</Link>
            
            {isCustomer && <Link to="/checkout" className="site-footer__link">Checkout</Link>}
            {token && <Link to="/orders" className="site-footer__link">Orders</Link>}
            {token && <Link to="/notifications" className="site-footer__link">Notifications</Link>}
            
            {isAdmin && <Link to="/admin/dashboard" className="site-footer__link">Dashboard</Link>}
            {isAdmin && <Link to="/admin/meals" className="site-footer__link">Manage Meals</Link>}
            
            {!token && <Link to="/login" className="site-footer__link">Login</Link>}
            {!token && <Link to="/register" className="site-footer__link">Register</Link>}
          </nav>
          <p className="site-footer__text">© 2026 DishDash</p>
        </div>
      </footer>
    </div>
  )
}

export default HomePage