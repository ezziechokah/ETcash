import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import App from './App.jsx';
import { useThemeInit } from './hooks/useTheme.js';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30000, refetchOnWindowFocus: false }
  }
});

function Root() {
  useThemeInit();
  return (
    <>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--toast-bg)',
            color: 'var(--toast-fg)',
            border: '1px solid var(--toast-border)',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: 'var(--toast-bg)' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: 'var(--toast-bg)' } },
        }}
      />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Root />
    </QueryClientProvider>
  </React.StrictMode>
);
