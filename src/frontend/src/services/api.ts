import axios from "axios";

/**
 * Base URL for the API. When empty (the default in development) requests go to
 * the current origin and Vite proxies `/api` to the backend. Production builds
 * can set `VITE_API_URL` to the deployed API origin.
 */
const API_ORIGIN = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");

export const api = axios.create({
  baseURL: `${API_ORIGIN}/api/v1`,
  withCredentials: true,
  headers: { Accept: "application/json" },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error?.response?.status === 401 &&
      localStorage.getItem("token") &&
      !window.location.pathname.startsWith("/login")
    ) {
      localStorage.removeItem("token");
      window.location.assign("/login?expired=1");
    }
    return Promise.reject(error);
  },
);

/** Turn an unknown Axios/JS error into a user-facing message. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item: { loc?: Array<string | number>; msg?: string }) => {
          const field = item.loc?.filter((part) => part !== "body").join(".");
          return field ? `${field}: ${item.msg}` : item.msg;
        })
        .filter(Boolean);
      if (messages.length) {
        return messages.join("; ");
      }
    }
    if (error.code === "ERR_NETWORK") {
      return "Unable to reach the API. Check that the backend is running.";
    }
    return error.message || "The request failed. Please try again.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred.";
}

export default api;
