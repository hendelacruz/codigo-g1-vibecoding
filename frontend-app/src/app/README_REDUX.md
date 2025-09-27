# Redux Store Configuration

## Overview
This Redux store is configured with Redux Toolkit and includes persistence for the auth state.

## Structure

### Store Configuration (`store.ts`)
- Uses `configureStore` from Redux Toolkit
- Includes `redux-persist` for state persistence
- Persists only the `auth` slice to localStorage
- Exports typed `RootState` and `AppDispatch`

### Root Reducer (`rootReducer.ts`)
- Combines all feature slices
- Currently includes: `auth`
- Ready for future slices: `inventory`, `sales`, `dashboard`

### Auth Slice (`features/auth/authSlice.ts`)
- Basic auth state management
- Includes: user, tokens, authentication status, loading, error
- Basic actions: `clearError`, `clearAuth`
- Will be fully implemented in Phase 1.7

## Usage

### In Components
```typescript
import { useAppSelector, useAppDispatch } from '@/shared/hooks/redux'
import { clearAuth } from '@/features/auth/authSlice'

const MyComponent = () => {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated } = useAppSelector(state => state.auth)
  
  const handleLogout = () => {
    dispatch(clearAuth())
  }
  
  return (
    <div>
      {isAuthenticated ? `Welcome ${user?.name}` : 'Please login'}
    </div>
  )
}
```

### Typed Hooks
Use the provided typed hooks for better TypeScript support:
- `useAppDispatch()` - Typed dispatch hook
- `useAppSelector()` - Typed selector hook
- `useAuth()` - Get entire auth state
- `useIsAuthenticated()` - Get authentication status
- `useAuthUser()` - Get current user
- `useAuthToken()` - Get auth token

### Provider Setup
The `ReduxProvider` is already configured with:
- Redux store provider
- Persistence gate with loading spinner
- Error boundaries (to be added in future phases)

## Next Steps (Future Phases)
1. Complete auth slice implementation (Phase 1.7)
2. Add inventory slice (Phase 2)
3. Add sales slice (Phase 3)
4. Add dashboard slice (Phase 4)
5. Add middleware for API calls
6. Add error handling middleware