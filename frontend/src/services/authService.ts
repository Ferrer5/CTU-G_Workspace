import { apiGet, apiPost, ApiError } from './apiClient';
import type { AuthUser } from '../types/auth';

export async function login(schoolId: string, password: string): Promise<AuthUser> {
  await apiPost<{ detail: string }>('/auth/login/', {
    school_id: schoolId,
    password,
  });
  return fetchMe();
}

export function logout(): Promise<{ detail: string }> {
  return apiPost('/auth/logout/', {});
}

export function fetchMe(): Promise<AuthUser> {
  return apiGet('/auth/me/');
}

export function getLoginErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return error instanceof Error && error.message
      ? error.message
      : 'Sign-in could not be completed. Please try again.';
  }

  if (error.status === 401) return 'Invalid school ID or password.';
  if (error.status === 403 && error.code === 'pending') {
    return 'Your registration is still pending approval.';
  }
  if (error.status === 403 && error.code === 'rejected') {
    return 'Your registration was rejected. Please contact the administrator.';
  }
  if (error.status === 403 && error.code === 'inactive') {
    return 'This account is inactive.';
  }
  if (error.status === 429) {
    return 'Too many attempts. Please wait a minute and try again.';
  }
  if (error.status === 0) return 'Cannot reach the server. Please try again.';
  return error.message || 'Sign-in could not be completed. Please try again.';
}
