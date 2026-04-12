import { useState, useEffect } from 'react'
import api from '../api'

function MenuPage() {
  const [meals, setMeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/menus/today')
      .then(response => {
        setMeals(response.data)
        setLoading(false)
      })
      .catch(() => {
        setError("Could not load today's menu. Please try again later.")
        setLoading(false)
      })
  }, [])

  if (loading) return <p style={{ textAlign: 'center', marginTop: '100px' }}>Loading menu...</p>
  if (error) return <p style={{ textAlign: 'center', color: 'red', marginTop: '100px' }}>{error}</p>

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px' }}>
      <h1>Today's Menu</h1>

      {meals.length === 0 ? (
        <p>No meals available today.</p>
      ) : (
        <div>
          {meals.map(meal => (
            <div key={meal.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '15px', borderRadius: '8px' }}>
              <h2>{meal.name}</h2>
              <p>{meal.description}</p>
              <p><strong>Price:</strong> Ksh {meal.price}</p>
              <button style={{ padding: '8px 20px', backgroundColor: 'blue', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Order Now
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MenuPage