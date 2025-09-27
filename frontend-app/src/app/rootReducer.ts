import { combineReducers } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import { inventoryReducer } from '../features/inventory'
import entitiesReducer from '../features/entities/entitiesSlice'

export const rootReducer = combineReducers({
  auth: authReducer,
  inventory: inventoryReducer, // Fase 2 ✅
  entities: entitiesReducer,   // Entidades ✅
  // sales: salesReducer,         // Fase 3
  // dashboard: dashboardReducer, // Fase 4
})