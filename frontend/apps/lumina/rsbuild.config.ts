import { pluginReact } from '@rsbuild/plugin-react';
import { defineConfig } from '@rsbuild/core';

export default defineConfig({
  html: {
    template: './src/index.html',
  },
  plugins: [pluginReact()],

  source: {
    entry: {
      index: './src/main.tsx',
    },
    tsconfigPath: './tsconfig.app.json',
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(
        process.env.VITE_API_URL || 'http://localhost:8001'
      ),
      'import.meta.env.VITE_MOCK': JSON.stringify(
        process.env.VITE_MOCK || 'false'
      ),
      'import.meta.env.VITE_DEV_PANEL': JSON.stringify(
        process.env.VITE_DEV_PANEL || 'true'
      ),
    },
  },
  server: {
    port: 4300,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  output: {
    target: 'web',
    distPath: {
      root: 'dist',
    },
  },
});
