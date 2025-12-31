/// <reference types="vite/client" />

interface ImportMetaEnv {
  // API Configuration
  readonly VITE_API_BASE_URL?: string;

  // Authentication
  readonly VITE_USE_REAL_AUTH?: 'true' | 'false';
  readonly VITE_AUTH_API_URL?: string;

  // Feature Flags
  readonly VITE_ENABLE_DEV_TOOLS?: 'true' | 'false';
  readonly VITE_ENABLE_MOCK_DATA?: 'true' | 'false';

  // Error Tracking
  readonly VITE_SENTRY_DSN?: string;

  // App Info
  readonly VITE_APP_VERSION?: string;

  // Vite built-in
  readonly MODE: 'development' | 'production' | 'test';
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly SSR: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
