import { useState, useEffect } from 'react'
import api from '../api'

function AdminMealsPage() {
  const [meals, setMeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [ingredients, setIngredients] = useState('')
  const [recipeQuery, setRecipeQuery] = useState('')
  const [recipeResults, setRecipeResults] = useState([])

  useEffect(() => {
    api.get('/meals')
      .then(response => {
        setMeals(response.data)
        setLoading(false)
      })
      .catch(() => {
        setError('Could not load meals. Please try again later.')
        setLoading(false)
      })
  }, [])

  const handleAddMeal = async (e) => {
    e.preventDefault()
    try {
      await api.post('/meals', {
        name,
        description,
        price,
        ingredients: ingredients.split(',').map((x) => x.trim()).filter(Boolean),
      })
      setName('')
      setDescription('')
      setPrice('')
      setIngredients('')
      const response = await api.get('/meals')
      setMeals(response.data)
    } catch {
      setError('Could not add meal. Please try again.')
    }
  }

  const handleRecipeSearch = async () => {
    if (!recipeQuery.trim()) {
      return
    }
    try {
      const response = await api.get('/meals/recipes/search', { params: { q: recipeQuery } })
      setRecipeResults(response.data.results || [])
    } catch {
      setError('Recipe search failed.')
    }
  }

  const importRecipe = (recipe) => {
    setName(recipe.name || '')
    setDescription(recipe.description || '')
    setIngredients((recipe.ingredients || []).join(', '))
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/meals/${id}`)
      setMeals(meals.filter(meal => meal.id !== id))
    } catch {
      setError('Could not delete meal. Please try again.')
    }
  }

  if (loading) return <p style={{ textAlign: 'center', marginTop: '100px' }}>Loading meals...</p>

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px' }}>
      <h1>Admin — Manage Meals</h1>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <h2>Add New Meal</h2>
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        <input
          type="text"
          value={recipeQuery}
          onChange={(e) => setRecipeQuery(e.target.value)}
          placeholder="Search public recipe API..."
          style={{ flex: 1, minWidth: '220px', padding: '8px', border: '1px solid #94a3b8', borderRadius: '6px' }}
        />
        <button onClick={handleRecipeSearch} type="button" style={{ padding: '8px 14px', border: 'none', borderRadius: '6px', background: '#0f766e', color: '#fff', cursor: 'pointer' }}>
          Search Recipes
        </button>
      </div>

      {recipeResults.length > 0 && (
        <div style={{ marginBottom: '14px', display: 'grid', gap: '8px' }}>
          {recipeResults.slice(0, 5).map((recipe) => (
            <div key={recipe.external_id} style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '10px', background: '#fff' }}>
              <strong>{recipe.name}</strong>
              <p style={{ margin: '4px 0' }}>{recipe.description}</p>
              <button type="button" onClick={() => importRecipe(recipe)} style={{ padding: '6px 10px', border: 'none', borderRadius: '6px', background: '#1d4ed8', color: '#fff', cursor: 'pointer' }}>
                Use Recipe
              </button>
            </div>
          ))}
        </div>
      )}

      <form onSubmit={handleAddMeal}>
        <div style={{ marginBottom: '10px' }}>
          <label>Meal Name</label><br />
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Description</label><br />
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Ingredients (comma separated)</label><br />
          <input
            type="text"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Price (Ksh)</label><br />
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <button
          type="submit"
          style={{ padding: '10px 20px', backgroundColor: 'green', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Add Meal
        </button>
      </form>

      <h2 style={{ marginTop: '40px' }}>All Meals</h2>
      {meals.length === 0 ? (
        <p>No meals added yet.</p>
      ) : (
        meals.map(meal => (
          <div key={meal.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '15px', borderRadius: '8px' }}>
            <h3>{meal.name}</h3>
            <p>{meal.description}</p>
            <p><strong>Price:</strong> Ksh {meal.price}</p>
            <button
              onClick={() => handleDelete(meal.id)}
              style={{ padding: '6px 15px', backgroundColor: 'red', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Delete
            </button>
          </div>
        ))
      )}
    </div>
  )
}

export default AdminMealsPage