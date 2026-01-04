import { StrictMode } from 'react';
import * as ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
import { initTelemetry } from './lib/telemetry';
import { env, isDevelopment } from './config/env';

// Suppress harmless ResizeObserver errors (common with React Flow)
// This error occurs when the browser's ResizeObserver can't deliver notifications fast enough
// It's completely harmless and only appears in development mode
window.addEventListener('error', (e: ErrorEvent) => {
  if (e.message && e.message.includes('ResizeObserver')) {
    e.stopImmediatePropagation();
    e.stopPropagation();
    e.preventDefault();
  }
});

// Also suppress in console
const originalConsoleError = console.error;
console.error = (...args: unknown[]) => {
  const stringified = args.join(' ');
  if (stringified.includes('ResizeObserver')) {
    // Suppress ResizeObserver errors
    return;
  }
  originalConsoleError.apply(console, args);
};

// Initialize telemetry (check browser console for errors)
initTelemetry({
  enabled: isDevelopment,
  serviceName: 'process-mining-frontend',
  serviceVersion: env.APP_VERSION,
  backendUrl: env.API_BASE_URL,
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
);
root.render(
  <StrictMode>
    <App />
  </StrictMode>,
);
