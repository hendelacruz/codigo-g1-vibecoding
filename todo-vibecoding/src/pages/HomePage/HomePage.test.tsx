/**
 * HomePage Component Tests
 * Tests for the main home page component with strict typing
 */

import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router'
import { HomePage } from './HomePage'
import { describe, it, expect } from '@jest/globals'

/**
 * Helper function to render components with Router context
 * @returns JSX element wrapped with BrowserRouter
 */
const renderWithRouter = (): void => {
  render(
    <BrowserRouter>
      <HomePage />
    </BrowserRouter>
  )
}

describe('HomePage Component', () => {
  it('should render the main heading', () => {
    renderWithRouter()
    
    const heading = screen.getByText('Lista de Tareas')
    expect(heading).toBeTruthy()
  })

  it('should render the subtitle', () => {
    renderWithRouter()
    
    const subtitle = screen.getByText('Gestiona tus tareas de manera eficiente')
    expect(subtitle).toBeTruthy()
  })

  it('should render the create todo link', () => {
    renderWithRouter()
    
    const createLink = screen.getByRole('link', { name: /crear todo/i })
    expect(createLink).toBeTruthy()
    expect(createLink.getAttribute('href')).toBe('/crear-todo')
  })

  it('should render navigation links', () => {
    renderWithRouter()
    
    const homeLink = screen.getByRole('link', { name: /inicio/i })
    const createLink = screen.getByRole('link', { name: /crear todo/i })
    
    expect(homeLink).toBeTruthy()
    expect(createLink).toBeTruthy()
  })

  it('should render the navigation link with proper styling', () => {
    renderWithRouter()
    
    const createLink = screen.getByRole('link', { name: /crear todo/i })
    const classList = Array.from(createLink.classList)
    expect(classList).toContain('bg-green-500')
    expect(classList).toContain('text-white')
  })

  it('should have navigation structure', () => {
    renderWithRouter()
    
    const navigation = screen.getByRole('navigation')
    expect(navigation).toBeTruthy()
    
    const links = screen.getAllByRole('link')
    expect(links.length).toBeGreaterThan(0)
  })
})