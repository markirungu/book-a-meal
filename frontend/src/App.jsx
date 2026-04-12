import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import MenuPage from './pages/MenuPage'
import OrdersPage from './pages/OrdersPage'
import AdminMealsPage from './pages/AdminMealsPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public pages - anyone can visit */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Customer pages - must be logged in */}
        <Route path="/menu" element={
          <ProtectedRoute>
            <MenuPage />
          </ProtectedRoute>
        } />
        <Route path="/orders" element={
          <ProtectedRoute>
            <OrdersPage />
          </ProtectedRoute>
        } />

        {/* Admin pages - must be logged in AND be an admin */}
        <Route path="/admin/meals" element={
          <ProtectedRoute adminOnly={true}>
            <AdminMealsPage />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}

export default App