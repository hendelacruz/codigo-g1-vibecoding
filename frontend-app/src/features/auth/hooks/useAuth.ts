import { useSelector, useDispatch } from 'react-redux'
import { useCallback } from 'react'
import type { RootState, AppDispatch } from '../../../app/store'
import { loginUser, logoutUser, checkAuthStatus, clearError } from '../authSlice'
import type { LoginCredentials } from '../authTypes'

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>()
  const auth = useSelector((state: RootState) => state.auth)

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const result = await dispatch(loginUser(credentials))
      return result
    },
    [dispatch]
  )

  const logout = useCallback(async () => {
    await dispatch(logoutUser())
  }, [dispatch])

  const checkStatus = useCallback(async () => {
    if (auth.token) {
      await dispatch(checkAuthStatus(auth.token))
    }
  }, [dispatch, auth.token])

  const clearAuthError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  return {
    ...auth,
    login,
    logout,
    checkStatus,
    clearError: clearAuthError,
  }
}