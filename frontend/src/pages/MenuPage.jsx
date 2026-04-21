import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { fetchTodayMenu } from '../store/menuSlice'
import { addToCart } from '../store/cartSlice'

function MenuPage() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { today, loading, error } = useSelector((state) => state.menu)
  const { items: cartItems } = useSelector((state) => state.cart)
  const [feedback, setFeedback] = useState('')
  const [activeFilter, setActiveFilter] = useState('All')
  const token = sessionStorage.getItem('token')
  const role = sessionStorage.getItem('role')
  const isGuest = !token || role === 'guest'
  const mealFallbackImages = useMemo(() => ([
    'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1511690743698-d9d85f2fbf38?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1625944230945-1b7dd3b949ab?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=1200&q=80',
  ]), [])

  const guestMeals = useMemo(() => ([
    {
      id: 'guest-1',
      name: 'Chicken Rice Bowl',
      description: 'Guest preview meal with chicken, vegetables, and rice.',
      price: 520,
      image_url: 'https://images.unsplash.com/photo-1604908554027-1b6f2b2f3f8b?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Rice', 'Seasonal vegetables'],
      is_special: true,
    },
    {
      id: 'guest-2',
      name: 'Beef Stew Plate',
      description: 'Slow-cooked beef stew served with ugali and greens.',
      price: 580,
      image_url: 'https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Tomatoes', 'Greens'],
      is_special: false,
    },
    {
      id: 'guest-3',
      name: 'Veggie Pasta',
      description: 'Fresh pasta with a light vegetable sauce.',
      price: 470,
      image_url: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Pasta', 'Tomatoes', 'Herbs'],
      is_special: false,
    },
    {
      id: 'guest-4',
      name: 'Spicy Chicken Wrap',
      description: 'Grilled spicy chicken wrapped with crisp lettuce and sauce.',
      price: 430,
      image_url: 'https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Tortilla', 'Lettuce'],
      is_special: false,
    },
    {
      id: 'guest-5',
      name: 'BBQ Beef Burger',
      description: 'Juicy beef burger with smoky barbecue glaze and onions.',
      price: 540,
      image_url: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Bun', 'BBQ sauce'],
      is_special: true,
    },
    {
      id: 'guest-6',
      name: 'Lemon Garlic Fish',
      description: 'Pan-seared fish served with lemon garlic butter.',
      price: 620,
      image_url: 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Fish fillet', 'Lemon', 'Garlic'],
      is_special: false,
    },
    {
      id: 'guest-7',
      name: 'Creamy Mushroom Pasta',
      description: 'Pasta tossed in creamy mushroom sauce and parmesan.',
      price: 500,
      image_url: 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Pasta', 'Mushroom', 'Cream'],
      is_special: false,
    },
    {
      id: 'guest-8',
      name: 'Veggie Stir Fry',
      description: 'Mixed vegetables stir-fried with sesame and soy.',
      price: 410,
      image_url: 'https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Carrot', 'Broccoli', 'Soy sauce'],
      is_special: false,
    },
    {
      id: 'guest-9',
      name: 'Chicken Alfredo',
      description: 'Tender chicken and fettuccine in creamy alfredo.',
      price: 590,
      image_url: 'https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Fettuccine', 'Cream'],
      is_special: true,
    },
    {
      id: 'guest-10',
      name: 'Roasted Beef Plate',
      description: 'Slow roasted beef served with seasonal sides.',
      price: 650,
      image_url: 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Potatoes', 'Carrots'],
      is_special: false,
    },
    {
      id: 'guest-11',
      name: 'Chicken Caesar Salad',
      description: 'Romaine, grilled chicken, croutons and parmesan.',
      price: 470,
      image_url: 'https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Romaine', 'Parmesan'],
      is_special: false,
    },
    {
      id: 'guest-12',
      name: 'Classic Beef Tacos',
      description: 'Three tacos filled with seasoned beef and salsa.',
      price: 520,
      image_url: 'https://images.unsplash.com/photo-1565299585323-38174c4a6471?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Taco shells', 'Salsa'],
      is_special: false,
    },
    {
      id: 'guest-13',
      name: 'Grilled Chicken Skewers',
      description: 'Marinated chicken skewers with charred peppers.',
      price: 560,
      image_url: 'https://images.unsplash.com/photo-1608039755401-742074f0548d?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Bell pepper', 'Spices'],
      is_special: false,
    },
    {
      id: 'guest-14',
      name: 'Pepper Steak',
      description: 'Tender beef strips in black pepper sauce.',
      price: 680,
      image_url: 'https://images.unsplash.com/photo-1615937657715-bc7b4b7962c1?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Pepper', 'Onion'],
      is_special: true,
    },
    {
      id: 'guest-15',
      name: 'Chicken Biryani',
      description: 'Fragrant rice cooked with spiced chicken pieces.',
      price: 610,
      image_url: 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Basmati rice', 'Spices'],
      is_special: false,
    },
    {
      id: 'guest-16',
      name: 'Beef Noodle Bowl',
      description: 'Asian-inspired noodle bowl with sliced beef.',
      price: 590,
      image_url: 'https://images.unsplash.com/photo-1585032226651-759b368d7246?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Noodles', 'Greens'],
      is_special: false,
    },
    {
      id: 'guest-17',
      name: 'Chicken Curry Plate',
      description: 'Mildly spiced chicken curry with steamed rice.',
      price: 570,
      image_url: 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Curry sauce', 'Rice'],
      is_special: false,
    },
    {
      id: 'guest-18',
      name: 'Veggie Pizza Slice',
      description: 'Thin-crust pizza topped with fresh vegetables.',
      price: 450,
      image_url: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Dough', 'Cheese', 'Vegetables'],
      is_special: false,
    },
    {
      id: 'guest-19',
      name: 'Chicken Shawarma Plate',
      description: 'Sliced chicken shawarma served with fries and dip.',
      price: 530,
      image_url: 'https://images.unsplash.com/photo-1529563021893-cc83c992d75d?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Pita', 'Garlic dip'],
      is_special: false,
    },
    {
      id: 'guest-20',
      name: 'Beef Meatballs',
      description: 'Beef meatballs in tomato basil sauce.',
      price: 600,
      image_url: 'https://images.unsplash.com/photo-1529042410759-befb1204b468?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Tomato', 'Basil'],
      is_special: false,
    },
    {
      id: 'guest-21',
      name: 'Chicken Fried Rice',
      description: 'Wok-fried rice with egg, chicken and vegetables.',
      price: 490,
      image_url: 'https://images.unsplash.com/photo-1516684732162-798a0062be99?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Rice', 'Chicken', 'Egg'],
      is_special: false,
    },
    {
      id: 'guest-22',
      name: 'Beef Burrito Bowl',
      description: 'Seasoned beef, beans, and rice with fresh toppings.',
      price: 560,
      image_url: 'https://images.unsplash.com/photo-1562967916-eb82221dfb92?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Beef', 'Beans', 'Rice'],
      is_special: false,
    },
    {
      id: 'guest-23',
      name: 'Chicken Parmesan',
      description: 'Breaded chicken topped with cheese and tomato sauce.',
      price: 640,
      image_url: 'https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?auto=format&fit=crop&w=1200&q=80',
      ingredients: ['Chicken', 'Cheese', 'Tomato sauce'],
      is_special: true,
    },
  ]), [])

  const meals = useMemo(() => (isGuest ? guestMeals : (today?.meals || [])), [guestMeals, isGuest, today])
  const specials = useMemo(() => meals.filter((meal) => meal.is_special), [meals])
  const filters = useMemo(() => {
    const available = ['All', 'Specials']
    const names = meals.map((meal) => meal.name || '')
    if (names.some((name) => /chicken/i.test(name))) {
      available.push('Chicken')
    }
    if (names.some((name) => /beef/i.test(name))) {
      available.push('Beef')
    }
    return available
  }, [meals])
  const visibleMeals = useMemo(() => {
    if (activeFilter === 'All') {
      return meals
    }
    if (activeFilter === 'Specials') {
      return meals.filter((meal) => meal.is_special)
    }
    return meals.filter((meal) => (meal.name || '').toLowerCase().includes(activeFilter.toLowerCase()))
  }, [activeFilter, meals])
  const cartCount = useMemo(
    () => cartItems.reduce((total, item) => total + item.quantity, 0),
    [cartItems],
  )

  useEffect(() => {
    if (!isGuest) {
      dispatch(fetchTodayMenu())
    }
  }, [dispatch, isGuest])

  const handleAddToCart = (meal) => {
    dispatch(addToCart({
      id: meal.id,
      name: meal.name,
      price: meal.price,
      image_url: meal.image_url,
      description: meal.description,
      quantity: 1,
    }))

    setFeedback(`${meal.name} added to cart.`)
  }

  if (loading && !isGuest) {
    return (
      <section className="page-section">
        <div className="page-heading">
          <h1>Today&apos;s Menu</h1>
          <p>Loading meals for today.</p>
        </div>
        <div className="meal-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="meal-card skeleton-card">
              <div className="skeleton skeleton-image" />
              <div className="meal-card__body">
                <div className="skeleton skeleton-line skeleton-line--title" />
                <div className="skeleton skeleton-line" />
                <div className="skeleton skeleton-line skeleton-line--short" />
              </div>
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
          <h1>Today&apos;s Menu</h1>
          <p>We could not load the menu right now.</p>
        </div>
        <div className="empty-state empty-state--error">{error}</div>
      </section>
    )
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <h1>Today&apos;s Menu</h1>
        <p>{isGuest ? 'You are browsing as a guest. Add meals to cart and checkout as guest or login for full order history.' : 'Choose from the meals prepared for today and add them to cart for checkout.'}</p>
      </div>
      {feedback && <div className={`feedback ${feedback.toLowerCase().includes('success') ? 'feedback--success' : 'feedback--error'}`}>{feedback}</div>}

      <div className="button-row">
        <button
          type="button"
          className="button button--secondary button--small"
          onClick={() => navigate('/checkout')}
        >
          Go to Checkout ({cartCount})
        </button>
      </div>

      {today?.cutoff_time && (
        <p className="info-strip">
          Order cutoff: {new Date(today.cutoff_time).toLocaleString()}
        </p>
      )}

      <div className="filter-bar" role="tablist" aria-label="Menu filters">
        {filters.map((filter) => (
          <button
            key={filter}
            type="button"
            className={`filter-chip ${activeFilter === filter ? 'filter-chip--active' : ''}`}
            onClick={() => setActiveFilter(filter)}
          >
            {filter}
          </button>
        ))}
      </div>

      {specials.length > 0 && (
        <section className="section-block section-block--compact">
          <div className="section-heading">
            <h2>Special Items Today</h2>
            <p>Quick picks from the caterer.</p>
          </div>
          <div className="special-grid">
            {specials.map((meal) => (
              <article key={`special-${meal.id}`} className="special-card">
                <div className="meal-card__top">
                  <strong>{meal.name}</strong>
                  <span className="tag">Special</span>
                </div>
                <p>{meal.description || 'Chef special item.'}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {meals.length === 0 ? (
        <div className="empty-state">
          No meals available today.
        </div>
      ) : (
        <div className="meal-grid">
          {visibleMeals.map((meal, index) => (
            <article key={meal.id} className="meal-card">
              <img
                src={meal.image_url || mealFallbackImages[index % mealFallbackImages.length]}
                alt={meal.name}
                className="meal-card__image"
              />
              <div className="meal-card__body">
                <div className="meal-card__top">
                  <h2>{meal.name}</h2>
                  <div className="tag-list">
                    {meal.is_special && <span className="tag">Special</span>}
                    {!meal.is_special && <span className="tag tag--muted">Popular</span>}
                  </div>
                </div>
                <p>{meal.description || 'No description available.'}</p>
              {meal.ingredients?.length > 0 && (
                <p className="meal-card__meta">
                  Ingredients: {meal.ingredients.slice(0, 4).join(', ')}
                </p>
              )}
                <div className="meal-card__footer">
                  <span className="price-label">Ksh {meal.price}</span>
                  <button
                    type="button"
                    onClick={() => handleAddToCart(meal)}
                    className="button button--primary button--small"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

export default MenuPage