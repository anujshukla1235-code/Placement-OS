export type UserRole = "student" | "tpo" | "company" | "college";

export const AUTH_STORAGE_KEYS = {
  access: "accessToken",
  refresh: "refreshToken",
  role: "userRole",
} as const;

const isBrowser = typeof window !== "undefined";

function _getItem(key: string): string | null {
  return isBrowser ? window.localStorage.getItem(key) : null;
}

function _setItem(key: string, value: string): void {
  if (!isBrowser) return;
  window.localStorage.setItem(key, value);
}

function _removeItem(key: string): void {
  if (!isBrowser) return;
  window.localStorage.removeItem(key);
}

export function getAccessToken(): string | null {
  return _getItem(AUTH_STORAGE_KEYS.access) ?? _getItem("access_token");
}

export function getRefreshToken(): string | null {
  return _getItem(AUTH_STORAGE_KEYS.refresh) ?? _getItem("refresh_token");
}

export function clearAuthStorage(): void {
  _removeItem(AUTH_STORAGE_KEYS.access);
  _removeItem(AUTH_STORAGE_KEYS.refresh);
  _removeItem(AUTH_STORAGE_KEYS.role);
  _removeItem("access_token");
  _removeItem("refresh_token");
  _removeItem("userEmail");
}

export function normalizeRole(role?: string | null): UserRole | null {
  if (!role) return null;
  const normalized = role.toLowerCase();
  if (["admin", "tpo", "staff", "super_admin"].includes(normalized)) return "tpo";
  if (["student", "candidate"].includes(normalized)) return "student";
  if (["company", "employer"].includes(normalized)) return "company";
  if (["college", "campus"].includes(normalized)) return "college";
  return null;
}

export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    if (!isBrowser) {
      // Node environment
      return JSON.parse(Buffer.from(padded, "base64").toString("utf8"));
    }
    return JSON.parse(window.atob(padded));
  } catch {
    return null;
  }
}

export function getUserRoleFromToken(token: string | null): UserRole | null {
  if (!token) return null;
  const payload = decodeJwtPayload(token);
  if (!payload) return null;
  const candidate =
    (typeof payload.role === "string" && payload.role) ||
    (typeof payload.user_role === "string" && payload.user_role) ||
    (typeof payload.is_admin === "boolean" && payload.is_admin ? "tpo" : null) ||
    (typeof payload.is_staff === "boolean" && payload.is_staff ? "tpo" : null);
  return normalizeRole(candidate as string | null);
}

export function getStoredUserRole(): UserRole | null {
  const role = _getItem(AUTH_STORAGE_KEYS.role);
  return normalizeRole(role);
}

export function saveAuthSession(auth: { accessToken: string; refreshToken: string; role?: string | null }): void {
  _setItem(AUTH_STORAGE_KEYS.access, auth.accessToken);
  _setItem(AUTH_STORAGE_KEYS.refresh, auth.refreshToken);
  const resolvedRole = normalizeRole(auth.role ?? getUserRoleFromToken(auth.accessToken));
  if (resolvedRole) _setItem(AUTH_STORAGE_KEYS.role, resolvedRole);
  else _removeItem(AUTH_STORAGE_KEYS.role);
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export function logoutUser(router?: { replace: (path: string) => void }): void {
  clearAuthStorage();
  if (router) {
    router.replace("/login");
    return;
  }
  if (isBrowser) window.location.href = "/login";
}

export function getRoleBasedRedirectPath(role?: string | null): string {
  const normalized = normalizeRole(role ?? getStoredUserRole() ?? null);
  switch (normalized) {
    case 'student':
      return '/student-dashboard';
    case 'company':
      return '/company-dashboard';
    case 'college':
      return '/college-dashboard';
    case 'tpo':
      // Admin/TPO panel lives at /admin — /tpo route has no implementation yet.
      return '/admin';
    default:
      return '/login';
  }
}
