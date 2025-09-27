import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '../../app/store'

// Typed hooks for Redux
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()

// Auth selector hooks
export const useAuth = () => useAppSelector((state) => state.auth)
export const useAuthUser = () => useAppSelector((state) => state.auth.user)
export const useIsAuthenticated = () => useAppSelector((state) => state.auth.isAuthenticated)
export const useAuthToken = () => useAppSelector((state) => state.auth.token)
export const useAuthLoading = () => useAppSelector((state) => state.auth.isLoading)
export const useAuthError = () => useAppSelector((state) => state.auth.error)

// Entities selector hooks
export const useEntitiesState = () => useAppSelector((state) => state.entities)
export const useClientesState = () => useAppSelector((state) => state.entities.clientes)
export const useUnidadesState = () => useAppSelector((state) => state.entities.unidades)
export const useProveedoresState = () => useAppSelector((state) => state.entities.proveedores)