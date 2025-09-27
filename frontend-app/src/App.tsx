import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LoginForm } from './features/auth/components/LoginForm'
import { ProtectedRoute } from './features/auth/components/ProtectedRoute'
import type { RootState } from './app/store'

import { DashboardPage } from './pages/DashboardPage'
import { UnauthorizedPage } from './pages/UnauthorizedPage'
import { UsersPage } from './pages/UsersPage'
import { GPSDevicesPage } from './features/inventory/components/GPSDevicesPage'
import { OtrosProductosPage } from './features/inventory/components/OtrosProductosPage'

import './index.css'

// Componente interno que maneja la lógica de redirección
const AppRoutes: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { token, isAuthenticated } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    const isLoginPage = location.pathname === '/login'
    const isUnauthorizedPage = location.pathname === '/unauthorized'
    
    // Si no hay token y no estamos en login o unauthorized, redirigir a login
    if (!token && !isAuthenticated && !isLoginPage && !isUnauthorizedPage) {
      console.log('No authentication found, redirecting to login')
      navigate('/login', { replace: true })
    }
  }, [navigate, location.pathname, token, isAuthenticated])

  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/users" 
        element={
          <ProtectedRoute>
            <UsersPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/gps-devices" 
        element={
          <ProtectedRoute>
            <GPSDevicesPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/inventory/gps" 
        element={
          <ProtectedRoute>
            <GPSDevicesPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/otros-productos" 
        element={
          <ProtectedRoute>
            <OtrosProductosPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/inventory/otros-productos" 
        element={
          <ProtectedRoute>
            <OtrosProductosPage />
          </ProtectedRoute>
        } 
      />

      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

// Crear QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
