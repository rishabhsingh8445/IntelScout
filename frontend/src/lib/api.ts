import axios, { AxiosRequestConfig } from "axios";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export async function buildAuthConfig(
  getToken: (options?: { template?: string }) => Promise<string | null>,
  config: AxiosRequestConfig = {}
): Promise<AxiosRequestConfig> {
  const token = await getToken();
  const headers = { ...(config.headers || {}) } as Record<string, string>;
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return { ...config, headers };
}

export async function apiGet<T>(
  getToken: (options?: { template?: string }) => Promise<string | null>,
  path: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const authConfig = await buildAuthConfig(getToken, config);
  const res = await axios.get<T>(`${API_BASE}${path}`, authConfig);
  return res.data;
}

export async function apiPost<T>(
  getToken: (options?: { template?: string }) => Promise<string | null>,
  path: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const authConfig = await buildAuthConfig(getToken, config);
  const res = await axios.post<T>(`${API_BASE}${path}`, data, authConfig);
  return res.data;
}

export async function apiDelete<T>(
  getToken: (options?: { template?: string }) => Promise<string | null>,
  path: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const authConfig = await buildAuthConfig(getToken, config);
  const res = await axios.delete<T>(`${API_BASE}${path}`, authConfig);
  return res.data;
}
