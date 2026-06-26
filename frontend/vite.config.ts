import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// During `vite dev` the backend runs separately on :8000, so proxy /api to it.
// In the Docker image the build is static and nginx handles the /api proxy.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
