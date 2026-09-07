import { Platform } from "react-native";

// In Android Emulator, host machine is 10.0.2.2; on iOS Simulator it's localhost
export const API_BASE_URL = Platform.OS === "android"
  ? "http://10.0.2.2:8000/api/v1"
  : "http://localhost:8000/api/v1";

export interface MobileApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  results?: T;
  code?: string;
  errors?: Record<string, any>;
}

let storedToken: string | null = null;
let storedRefreshToken: string | null = null;

export const setAuthTokens = (access: string | null, refresh: string | null = null) => {
  storedToken = access;
  if (refresh) storedRefreshToken = refresh;
};

export const getAuthToken = () => storedToken;

export async function mobileApiRequest<T = any>(
  endpoint: string,
  options: {
    method?: string;
    body?: any;
    headers?: Record<string, string>;
  } = {}
): Promise<T> {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (storedToken && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${storedToken}`;
  }

  const response = await fetch(url, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const contentType = response.headers.get("content-type");
  const isJson = contentType && contentType.includes("application/json");
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    const errorMsg = data?.message || data?.detail || `API request failed with HTTP ${response.status}`;
    throw new Error(errorMsg);
  }

  return data as T;
}
