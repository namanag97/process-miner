import { StrictMode } from 'react';
import * as ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { luminaTheme } from '@lumina/design-system';
import { AuthProvider, SDKProvider } from './context';
import App from './app/App';
import './styles.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <StrictMode>
    <ConfigProvider theme={luminaTheme}>
      <SDKProvider>
        <AuthProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AuthProvider>
      </SDKProvider>
    </ConfigProvider>
  </StrictMode>
);
