import axios, { type AxiosError, type AxiosRequestConfig } from 'axios';

import {
  clearAuthStorage,
  getAccessToken,
  getRefreshToken,
  getStoredUserRole,
  getUserRoleFromToken,
  saveAuthSession,
} from '@/lib/auth';

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

const notifyRefreshSubscribers = (token: string): void => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

const refreshAccessToken = async (): Promise<string> => {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error('No refresh token available.');
  }

  const response = await axios.post<{ access?: string; access_token?: string; accessToken?: string; refresh?: string }>(
    `${API_BASE_URL}/token/refresh/`,
    { refresh: refreshToken },
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  const nextAccessToken = response.data.access ?? response.data.access_token ?? response.data.accessToken;

  if (!nextAccessToken) {
    throw new Error('Refresh token response did not include a new access token.');
  }

  const currentRole = getStoredUserRole() ?? getUserRoleFromToken(getAccessToken());

  // SIMPLE_JWT has ROTATE_REFRESH_TOKENS=True + BLACKLIST_AFTER_ROTATION=True — every
  // refresh call invalidates the old refresh token and issues a new one. Previously this
  // new refresh token was discarded, so the *second* silent refresh would always fail
  // (using an already-blacklisted token), forcing a logout one refresh cycle later than
  // expected. Persist whatever refresh token comes back, falling back to the old one only
  // if the backend didn't rotate it.
  saveAuthSession({
    accessToken: nextAccessToken,
    refreshToken: response.data.refresh ?? refreshToken,
    role: currentRole ?? undefined,
  });

  return nextAccessToken;
};

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (AxiosRequestConfig & {
      _retry?: boolean;
      headers?: Record<string, string>;
    }) | undefined;

    if (!originalRequest || error.response?.status !== 401 || originalRequest.url?.includes('/token/refresh/')) {
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshSubscribers.push((token: string) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }

          api(originalRequest)
            .then(resolve)
            .catch(reject);
        });
      });
    }

    isRefreshing = true;

    try {
      const newAccessToken = await refreshAccessToken();
      notifyRefreshSubscribers(newAccessToken);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      }

      return await api(originalRequest);
    } catch (refreshError) {
      clearAuthStorage();

      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }

      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
      refreshSubscribers = [];
    }
  }
);

export default api;
