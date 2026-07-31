import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  cacheDir: ".vite-cache",
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    }
  },
  test: {
    environment: "jsdom",
    exclude: ["tests/e2e/**", "node_modules/**", "dist/**"],
    setupFiles: "./vitest.setup.ts",
    globals: true
  }
});
