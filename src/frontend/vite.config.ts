import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxyTarget =
    env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const proxy = {
    "/api": {
      target: proxyTarget,
      changeOrigin: true,
    },
  };

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 5173,
      watch: {
        usePolling: true,
      },
      proxy,
    },
    // `vite preview` is a local smoke-test server for the production bundle.
    // Real deployments should reverse-proxy /api to the backend instead.
    preview: {
      host: "0.0.0.0",
      port: 4173,
      proxy,
    },
  };
});
