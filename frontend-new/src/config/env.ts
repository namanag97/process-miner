/**
 * Environment Configuration
 *
 * Validates and types environment variables at startup.
 * Fails fast if required variables are missing.
 *
 * Usage:
 * ```tsx
 * import { env } from '@/config/env';
 * console.log(env.API_BASE_URL);
 * ```
 */
import { z } from 'zod';

// ============================================
// Environment Schema
// ============================================

const envSchema = z.object({
  // API Configuration
  API_BASE_URL: z
    .string()
    .url()
    .default('http://localhost:8001'),

  // Authentication
  USE_REAL_AUTH: z
    .enum(['true', 'false'])
    .default('false')
    .transform((val) => val === 'true'),

  AUTH_API_URL: z
    .string()
    .url()
    .optional()
    .default('http://localhost:8001/auth'),

  // Feature Flags
  ENABLE_DEV_TOOLS: z
    .enum(['true', 'false'])
    .default('true')
    .transform((val) => val === 'true'),

  ENABLE_MOCK_DATA: z
    .enum(['true', 'false'])
    .default('false')
    .transform((val) => val === 'true'),

  // Error Tracking (optional)
  SENTRY_DSN: z.string().optional(),

  // Environment
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development'),

  // App Info
  APP_VERSION: z.string().optional().default('0.0.0'),
});

// Infer the type from the schema
export type Env = z.infer<typeof envSchema>;

// ============================================
// Environment Parsing
// ============================================

function parseEnv(): Env {
  // Map Vite env vars to our schema
  const rawEnv = {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    USE_REAL_AUTH: import.meta.env.VITE_USE_REAL_AUTH,
    AUTH_API_URL: import.meta.env.VITE_AUTH_API_URL,
    ENABLE_DEV_TOOLS: import.meta.env.VITE_ENABLE_DEV_TOOLS,
    ENABLE_MOCK_DATA: import.meta.env.VITE_ENABLE_MOCK_DATA,
    SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
    NODE_ENV: import.meta.env.MODE,
    APP_VERSION: import.meta.env.VITE_APP_VERSION,
  };

  // Parse and validate
  const result = envSchema.safeParse(rawEnv);

  if (!result.success) {
    const errors = result.error.issues
      .map((issue) => `  - ${issue.path.join('.')}: ${issue.message}`)
      .join('\n');

    console.error(
      `[Env] Invalid environment configuration:\n${errors}\n\nProvided values:`,
      rawEnv
    );

    // In development, show detailed error
    if (import.meta.env.DEV) {
      throw new Error(`Invalid environment configuration:\n${errors}`);
    }

    // In production, fail silently with defaults
    // This prevents exposing configuration details
    console.warn('[Env] Using default configuration due to validation errors');
    return envSchema.parse({});
  }

  return result.data;
}

// ============================================
// Export Validated Environment
// ============================================

export const env = parseEnv();

// Log environment in development (excluding sensitive values)
if (env.NODE_ENV === 'development') {
  console.log('[Env] Configuration loaded:', {
    API_BASE_URL: env.API_BASE_URL,
    USE_REAL_AUTH: env.USE_REAL_AUTH,
    ENABLE_DEV_TOOLS: env.ENABLE_DEV_TOOLS,
    ENABLE_MOCK_DATA: env.ENABLE_MOCK_DATA,
    NODE_ENV: env.NODE_ENV,
    APP_VERSION: env.APP_VERSION,
    // Sensitive values hidden
    SENTRY_DSN: env.SENTRY_DSN ? '[CONFIGURED]' : '[NOT SET]',
    AUTH_API_URL: '[HIDDEN]',
  });
}

// ============================================
// Helper Functions
// ============================================

/** Check if running in development mode */
export const isDevelopment = env.NODE_ENV === 'development';

/** Check if running in production mode */
export const isProduction = env.NODE_ENV === 'production';

/** Check if running in test mode */
export const isTest = env.NODE_ENV === 'test';

/** Check if real authentication is enabled */
export const useRealAuth = env.USE_REAL_AUTH;

/** Check if dev tools should be enabled */
export const enableDevTools = env.ENABLE_DEV_TOOLS && isDevelopment;

export default env;
