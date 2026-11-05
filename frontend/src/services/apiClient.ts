const API_BASE = '/api';
const CSRF_COOKIE = 'csrftoken';
const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export class ApiError extends Error {
  status: number;
  code?: string;
  data?: unknown;

  constructor(message: string, status: number, code?: string, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function readCookie(name: string): string | null {
  const cookie = document.cookie
    .split('; ')
    .find((entry) => entry.startsWith(`${name}=`));
  if (!cookie) return null;

  const value = cookie.slice(name.length + 1);
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

async function fetchResponse(path: string, init: RequestInit): Promise<Response> {
  try {
    return await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: 'same-origin',
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Network request failed.';
    throw new ApiError(message, 0, undefined, error);
  }
}

async function ensureCsrfCookie(): Promise<string> {
  let token = readCookie(CSRF_COOKIE);
  if (token) return token;

  await request('/auth/csrf/', { method: 'GET' });
  token = readCookie(CSRF_COOKIE);
  if (!token) {
    throw new ApiError('Unable to obtain a CSRF token.', 0);
  }
  return token;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  headers.set('Content-Type', 'application/json');

  if (MUTATING_METHODS.has(method)) {
    headers.set('X-CSRFToken', await ensureCsrfCookie());
  }

  const response = await fetchResponse(path, { ...init, method, headers });
  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const message = isRecord(data) && typeof data.detail === 'string'
      ? data.detail
      : `Request failed with status ${response.status}.`;
    const code = isRecord(data) && typeof data.code === 'string' ? data.code : undefined;
    throw new ApiError(message, response.status, code, data);
  }

  return data as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
