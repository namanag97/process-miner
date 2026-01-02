const { NxAppRspackPlugin } = require('@nx/rspack/app-plugin');
const { NxReactRspackPlugin } = require('@nx/rspack/react-plugin');
const { join } = require('path');
const rspack = require('@rspack/core');
const dotenv = require('dotenv');

// Load environment variables from .env file
const envVars = dotenv.config().parsed || {};

console.log('[Rspack Config] Loaded env vars:', envVars);

// Build environment definitions for DefinePlugin
const envKeys = {};

// Add each env var as a separate property
Object.keys(envVars).forEach((key) => {
  envKeys[`import.meta.env.${key}`] = JSON.stringify(envVars[key]);
});

// Add standard Vite env vars
envKeys['import.meta.env.MODE'] = JSON.stringify(process.env.NODE_ENV || 'development');
envKeys['import.meta.env.DEV'] = JSON.stringify(process.env.NODE_ENV !== 'production');
envKeys['import.meta.env.PROD'] = JSON.stringify(process.env.NODE_ENV === 'production');
envKeys['import.meta.env.SSR'] = JSON.stringify(false);

console.log('[Rspack Config] DefinePlugin keys:', Object.keys(envKeys));

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
