const { NxAppRspackPlugin } = require('@nx/rspack/app-plugin');
const { NxReactRspackPlugin } = require('@nx/rspack/react-plugin');
const { join } = require('path');
const rspack = require('@rspack/core');
const dotenv = require('dotenv');

// Load environment variables from .env file
const envResult = dotenv.config();
const envVars = envResult.parsed || {};

if (envResult.error) {
  console.warn('[Rspack Config] Warning: Could not load .env file:', envResult.error.message);
} else {
  console.log('[Rspack Config] Loaded env vars:', Object.keys(envVars));
}

// Build the complete import.meta.env object
const importMetaEnv = {
  // Standard Vite env vars
  MODE: process.env.NODE_ENV || 'development',
  DEV: process.env.NODE_ENV !== 'production',
  PROD: process.env.NODE_ENV === 'production',
  SSR: false,
  // User env vars from .env file
  ...envVars,
};

// Build environment definitions for DefinePlugin
const envKeys = {
  // Define the entire import.meta.env object
  'import.meta.env': JSON.stringify(importMetaEnv),
};

console.log('[Rspack Config] Environment:', importMetaEnv);

module.exports = {
  output: {
    path: join(__dirname, 'dist/frontend-new'),
  },
  devServer: {
    port: 4200,
    historyApiFallback: {
      index: '/index.html',
      disableDotRule: true,
      htmlAcceptHeaders: ['text/html', 'application/xhtml+xml'],
    },
  },
  plugins: [
    new rspack.DefinePlugin(envKeys),
    new NxAppRspackPlugin({
      tsConfig: './tsconfig.app.json',
      main: './src/main.tsx',
      index: './src/index.html',
      baseHref: '/',
      assets: ['./src/favicon.ico', './src/assets'],
      styles: ['./src/styles.css'],
      outputHashing: process.env['NODE_ENV'] === 'production' ? 'all' : 'none',
      optimization: process.env['NODE_ENV'] === 'production',
    }),
    new NxReactRspackPlugin({
      // Uncomment this line if you don't want to use SVGR
      // See: https://react-svgr.com/
      // svgr: false
    }),
  ],
};
