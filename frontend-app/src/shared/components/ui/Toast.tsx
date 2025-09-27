import React from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  onClose?: () => void;
}

// Toast component placeholder
// This component will be implemented later with proper toast system
export const Toast: React.FC<ToastProps> = ({ message, type = 'info', onClose }) => {
  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
      {onClose && <button onClick={onClose}>×</button>}
    </div>
  );
};