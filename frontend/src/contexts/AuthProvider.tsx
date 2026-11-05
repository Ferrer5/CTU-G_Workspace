import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import * as authService from '../services/authService';
import { ApiError } from '../services/apiClient';
import { AuthContext } from './authContext';
import type { AuthStatus } from './authContext';
import type { AuthUser } from '../types/auth';

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');
  const initialized = useRef(false);
  const hasAuthenticatedUser = useRef(false);
  const refreshing = useRef(false);

  const refresh = useCallback(async () => {
    if (refreshing.current) return;
    refreshing.current = true;
    if (!hasAuthenticatedUser.current) setStatus('loading');
    try {
      const currentUser = await authService.fetchMe();
      setUser(currentUser);
      hasAuthenticatedUser.current = true;
      setStatus('authenticated');
    } catch (error) {
      if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
        setUser(null);
        hasAuthenticatedUser.current = false;
        setStatus('unauthenticated');
      }
      throw error;
    } finally {
      refreshing.current = false;
    }
  }, []);

  const login = useCallback(async (schoolId: string, password: string) => {
    setStatus('loading');
    try {
      const currentUser = await authService.login(schoolId, password);
      setUser(currentUser);
      hasAuthenticatedUser.current = true;
      setStatus('authenticated');
      return currentUser;
    } catch (error) {
      setUser(null);
      hasAuthenticatedUser.current = false;
      setStatus('unauthenticated');
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
      hasAuthenticatedUser.current = false;
      setStatus('unauthenticated');
    }
  }, []);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    void refresh().catch(() => {
      setUser(null);
      hasAuthenticatedUser.current = false;
      setStatus('unauthenticated');
    });
  }, [refresh]);

  useEffect(() => {
    const handleFocus = () => {
      if (document.visibilityState === 'visible') {
        void refresh().catch((error: unknown) => {
          console.error('Unable to refresh the authenticated session.', error);
        });
      }
    };
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refresh]);

  const value = useMemo(
    () => ({ user, status, login, logout, refresh }),
    [user, status, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
