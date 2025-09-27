import React from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

// Layout component placeholder
// This component will be implemented later in the layout system
export const Layout: React.FC<LayoutProps> = ({ children, showSidebar = true }) => {
  return (
    <div className="layout">
      <Header />
      <div className="layout-body">
        {showSidebar && <Sidebar />}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};