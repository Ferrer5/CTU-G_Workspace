import { apiGet, apiPost, ApiError } from './apiClient';
import type { AuthUser, RegisterPayload } from '../types/auth';

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

export function sendSignupCode(email: string): Promise<{ detail: string }> {
  return apiPost('/auth/signup/send-code/', { email });
}

export function verifySignupCode(email: string, code: string): Promise<{ detail: string }> {
  return apiPost('/auth/signup/verify-code/', { email, code });
}

export function registerAccount(
  payload: RegisterPayload,
): Promise<{ account_id: number; request_status: string }> {
  return apiPost('/auth/register/', payload);
}

export function getSignupCodeErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) return 'Something went wrong. Please try again.';
  if (error.status === 0) return 'Cannot reach the server. Please try again.';
  if (error.status === 429) return 'Too many attempts. Please try again later.';
  if (error.message.startsWith('Request failed')) return 'Please check your input and try again.';
  return error.message;
}

export interface RegisterErrorInfo {
  fields: Record<string, string>;
  message: string | null;
  emailNotVerified: boolean;
}

export function parseRegisterError(error: unknown): RegisterErrorInfo {
  const info: RegisterErrorInfo = { fields: {}, message: null, emailNotVerified: false };

  if (!(error instanceof ApiError)) {
    info.message = 'Registration could not be completed. Please try again.';
    return info;
  }
  if (error.status === 0) {
    info.message = 'Cannot reach the server. Please try again.';
    return info;
  }
  if (error.status === 429) {
    info.message = 'Too many attempts. Please try again later.';
    return info;
  }
  if (error.code === 'email_not_verified') {
    info.emailNotVerified = true;
    info.message = 'Please verify your email again.';
    return info;
  }

  if (isRecord(error.data)) {
    for (const [key, value] of Object.entries(error.data)) {
      if (key === 'detail' || key === 'code') continue;
      const text = Array.isArray(value) ? String(value[0] ?? '') : typeof value === 'string' ? value : '';
      if (!text) continue;
      if (key === 'non_field_errors') {
        info.message = info.message ?? text;
      } else {
        info.fields[key] = text;
      }
    }
  }

  if (!info.message && Object.keys(info.fields).length === 0) {
    info.message = error.message || 'Registration could not be completed. Please try again.';
  }
  return info;
}
