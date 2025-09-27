import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { ReduxProvider } from './ReduxProvider'
import { QueryProvider } from './QueryProvider'

interface AppProvidersProps {
  children: React.ReactNode
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <ReduxProvider>
      <QueryProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryProvider>
    </ReduxProvider>
  )
}