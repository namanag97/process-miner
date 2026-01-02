import { StrictMode } from 'react';
import * as ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
import { initTelemetry } from './lib/telemetry';
import { env, isDevelopment } from './config/env';

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
