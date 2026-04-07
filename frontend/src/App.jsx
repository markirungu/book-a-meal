import { useEffect, useMemo, useState } from 'react'

function App() {
  const [apiBase, setApiBase] = useState('http://127.0.0.1:5000')
  const [token, setToken] = useState('')
  const [menus, setMenus] = useState([])
  const [meals, setMeals] = useState([])
  const [todayMenu, setTodayMenu] = useState(null)
  const [status, setStatus] = useState('Set API URL and JWT, then click Refresh Data.')
  const [busy, setBusy] = useState(false)

  const [newMenuDate, setNewMenuDate] = useState('')
  const [newMenuMealIds, setNewMenuMealIds] = useState([])

  const [editingMenuId, setEditingMenuId] = useState(null)
  const [editDate, setEditDate] = useState('')
  const [editMealIds, setEditMealIds] = useState([])

  useEffect(() => {
    document.body.style.margin = '0'
    document.body.style.background = '#f1f5f9'
    document.body.style.color = '#0f172a'
    document.body.style.fontFamily = 'ui-sans-serif, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'
  }, [])

  const styles = useMemo(
    () => ({
      page: {
        minHeight: '100vh',
        background: 'radial-gradient(circle at top left, #e2e8f0, #f8fafc 48%, #e2e8f0)',
        padding: '24px 14px 40px'
      },
      container: {
        maxWidth: '1180px',
        margin: '0 auto',
        display: 'grid',
        gap: '16px'
      },
      titleCard: {
        background: '#0f172a',
        color: '#f8fafc',
        borderRadius: '16px',
        padding: '22px',
        boxShadow: '0 12px 24px rgba(15, 23, 42, 0.2)'
      },
      title: {
        margin: '0',
        fontSize: 'clamp(1.4rem, 2.5vw, 2rem)'
      },
      subtitle: {
        margin: '8px 0 0',
        color: '#cbd5e1'
      },
      card: {
        background: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '16px',
        padding: '16px',
        boxShadow: '0 8px 18px rgba(15, 23, 42, 0.08)'
      },
      cardTitle: {
        margin: '0 0 12px',
        fontSize: '1.05rem'
      },
      row: {
        display: 'grid',
        gap: '10px',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))'
      },
      input: {
        width: '100%',
        boxSizing: 'border-box',
        border: '1px solid #94a3b8',
        borderRadius: '10px',
        padding: '10px 12px',
        fontSize: '0.95rem',
        background: '#fff'
      },
      label: {
        display: 'block',
        marginBottom: '6px',
        color: '#334155',
        fontSize: '0.86rem',
        fontWeight: 600
      },
      button: {
        border: 'none',
        borderRadius: '10px',
        padding: '10px 14px',
        fontWeight: 700,
        cursor: 'pointer'
      },
      buttonPrimary: {
        background: '#1d4ed8',
        color: '#ffffff'
      },
      buttonSecondary: {
        background: '#e2e8f0',
        color: '#0f172a'
      },
      buttonDanger: {
        background: '#b91c1c',
        color: '#ffffff'
      },
      status: {
        marginTop: '10px',
        color: '#1e293b'
      },
      mealGrid: {
        display: 'grid',
        gap: '8px',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        marginTop: '8px'
      },
      checkbox: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px',
        border: '1px solid #e2e8f0',
        borderRadius: '10px',
        background: '#f8fafc'
      },
      sectionHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap'
      },
      menuList: {
        display: 'grid',
        gap: '12px'
      },
      menuItem: {
        border: '1px solid #cbd5e1',
        borderRadius: '12px',
        padding: '12px',
        background: '#f8fafc'
      },
      mealTagWrap: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '7px',
        marginTop: '8px'
      },
      mealTag: {
        background: '#dbeafe',
        border: '1px solid #93c5fd',
        color: '#1e3a8a',
        borderRadius: '999px',
        padding: '4px 10px',
        fontSize: '0.85rem'
      },
      buttonRow: {
        marginTop: '10px',
        display: 'flex',
        gap: '8px',
        flexWrap: 'wrap'
      }
    }),
    []
  )

  const parseError = async (response) => {
    try {
      const payload = await response.json()
      return payload.error || payload.message || 'Request failed'
    } catch {
      return `Request failed: ${response.status}`
    }
  }

  const request = async (path, options = {}) => {
    const response = await fetch(`${apiBase}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
      }
    })

    if (!response.ok) {
      throw new Error(await parseError(response))
    }

    if (response.status === 204) {
      return null
    }

    return response.json()
  }

  const refreshData = async () => {
    if (!token.trim()) {
      setStatus('JWT token is required to call the API.')
      return
    }

    setBusy(true)
    setStatus('Loading meals and menus...')

    try {
      const [menuData, mealData] = await Promise.all([request('/menus'), request('/meals')])
      setMenus(menuData)
      setMeals(mealData)

      try {
        const today = await request('/menus/today')
        setTodayMenu(today)
      } catch {
        setTodayMenu(null)
      }

      setStatus('Loaded menu and meal data successfully.')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setBusy(false)
    }
  }

  const toggleMeal = (mealId, selectedMealIds, setter) => {
    if (selectedMealIds.includes(mealId)) {
      setter(selectedMealIds.filter((id) => id !== mealId))
      return
    }
    setter([...selectedMealIds, mealId])
  }

  const createMenu = async () => {
    if (!newMenuDate || newMenuMealIds.length === 0) {
      setStatus('Select a date and at least one meal for the new menu.')
      return
    }

    setBusy(true)
    setStatus('Creating menu...')

    try {
      await request('/menus', {
        method: 'POST',
        body: JSON.stringify({
          date: newMenuDate,
          meal_ids: newMenuMealIds
        })
      })
      setNewMenuDate('')
      setNewMenuMealIds([])
      await refreshData()
      setStatus('Menu created successfully.')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setBusy(false)
    }
  }

  const beginEdit = (menu) => {
    setEditingMenuId(menu.id)
    setEditDate(menu.date)
    setEditMealIds(menu.meals.map((meal) => meal.id))
  }

  const saveEdit = async () => {
    if (!editingMenuId) {
      return
    }
    if (!editDate || editMealIds.length === 0) {
      setStatus('Edited menu must have a date and at least one meal.')
      return
    }

    setBusy(true)
    setStatus('Updating menu...')

    try {
      await request(`/menus/${editingMenuId}`, {
        method: 'PUT',
        body: JSON.stringify({
          date: editDate,
          meal_ids: editMealIds
        })
      })
      setEditingMenuId(null)
      setEditDate('')
      setEditMealIds([])
      await refreshData()
      setStatus('Menu updated successfully.')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setBusy(false)
    }
  }

  const removeMenu = async (menuId) => {
    setBusy(true)
    setStatus('Deleting menu...')
    try {
      await request(`/menus/${menuId}`, { method: 'DELETE' })
      await refreshData()
      setStatus('Menu deleted successfully.')
    } catch (error) {
      setStatus(error.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main style={styles.page}>
      <div style={styles.container}>
        <section style={styles.titleCard}>
          <h1 style={styles.title}>Book A Meal - Menu Management</h1>
          <p style={styles.subtitle}>Create, edit, view, and delete daily menus from one screen.</p>
        </section>

        <section style={styles.card}>
          <h2 style={styles.cardTitle}>API Connection</h2>
          <div style={styles.row}>
            <div>
              <label style={styles.label}>Backend URL</label>
              <input
                style={styles.input}
                value={apiBase}
                onChange={(event) => setApiBase(event.target.value.trim())}
                placeholder="http://127.0.0.1:5000"
              />
            </div>
            <div>
              <label style={styles.label}>JWT Token</label>
              <input
                style={styles.input}
                value={token}
                onChange={(event) => setToken(event.target.value)}
                placeholder="Paste access token"
                type="password"
              />
            </div>
          </div>
          <div style={styles.buttonRow}>
            <button style={{ ...styles.button, ...styles.buttonPrimary }} onClick={refreshData} disabled={busy}>
              {busy ? 'Working...' : 'Refresh Data'}
            </button>
          </div>
          <p style={styles.status}>{status}</p>
        </section>

        <section style={styles.card}>
          <div style={styles.sectionHeader}>
            <h2 style={styles.cardTitle}>Today&apos;s Menu</h2>
          </div>
          {!todayMenu && <p>No menu has been set for today.</p>}
          {todayMenu && (
            <div style={styles.menuItem}>
              <strong>{todayMenu.date}</strong>
              <div style={styles.mealTagWrap}>
                {todayMenu.meals.map((meal) => (
                  <span style={styles.mealTag} key={meal.id}>
                    {meal.name} - KES {Number(meal.price).toFixed(2)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        <section style={styles.card}>
          <h2 style={styles.cardTitle}>Create Menu</h2>
          <div style={styles.row}>
            <div>
              <label style={styles.label}>Menu Date</label>
              <input
                style={styles.input}
                type="date"
                value={newMenuDate}
                onChange={(event) => setNewMenuDate(event.target.value)}
              />
            </div>
          </div>
          <div style={styles.mealGrid}>
            {meals.map((meal) => (
              <label key={meal.id} style={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={newMenuMealIds.includes(meal.id)}
                  onChange={() => toggleMeal(meal.id, newMenuMealIds, setNewMenuMealIds)}
                />
                <span>
                  {meal.name} - KES {Number(meal.price).toFixed(2)}
                </span>
              </label>
            ))}
          </div>
          <div style={styles.buttonRow}>
            <button style={{ ...styles.button, ...styles.buttonPrimary }} onClick={createMenu} disabled={busy}>
              Create Menu
            </button>
          </div>
        </section>

        <section style={styles.card}>
          <div style={styles.sectionHeader}>
            <h2 style={styles.cardTitle}>All Menus</h2>
            <span>{menus.length} record(s)</span>
          </div>
          <div style={styles.menuList}>
            {menus.map((menu) => (
              <article key={menu.id} style={styles.menuItem}>
                <strong>{menu.date}</strong>
                <div style={styles.mealTagWrap}>
                  {menu.meals.map((meal) => (
                    <span style={styles.mealTag} key={meal.id}>
                      {meal.name}
                    </span>
                  ))}
                </div>

                {editingMenuId === menu.id ? (
                  <div style={{ marginTop: '12px' }}>
                    <label style={styles.label}>Edit Date</label>
                    <input style={styles.input} type="date" value={editDate} onChange={(event) => setEditDate(event.target.value)} />
                    <div style={styles.mealGrid}>
                      {meals.map((meal) => (
                        <label key={`edit-${menu.id}-${meal.id}`} style={styles.checkbox}>
                          <input
                            type="checkbox"
                            checked={editMealIds.includes(meal.id)}
                            onChange={() => toggleMeal(meal.id, editMealIds, setEditMealIds)}
                          />
                          <span>{meal.name}</span>
                        </label>
                      ))}
                    </div>
                    <div style={styles.buttonRow}>
                      <button style={{ ...styles.button, ...styles.buttonPrimary }} onClick={saveEdit} disabled={busy}>
                        Save
                      </button>
                      <button
                        style={{ ...styles.button, ...styles.buttonSecondary }}
                        onClick={() => {
                          setEditingMenuId(null)
                          setEditDate('')
                          setEditMealIds([])
                        }}
                        disabled={busy}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div style={styles.buttonRow}>
                    <button style={{ ...styles.button, ...styles.buttonSecondary }} onClick={() => beginEdit(menu)} disabled={busy}>
                      Edit
                    </button>
                    <button style={{ ...styles.button, ...styles.buttonDanger }} onClick={() => removeMenu(menu.id)} disabled={busy}>
                      Delete
                    </button>
                  </div>
                )}
              </article>
            ))}
            {menus.length === 0 && <p>No menus available. Create one above.</p>}
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
