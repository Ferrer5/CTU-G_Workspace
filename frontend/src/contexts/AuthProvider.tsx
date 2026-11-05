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

  const refresh = useCallback(async () => {
    setStatus('loading');
    try {
      const currentUser = await authService.fetchMe();
      setUser(currentUser);
      setStatus('authenticated');
    } catch (error) {
      setUser(null);
      setStatus('unauthenticated');
      if (!(error instanceof ApiError && (error.status === 401 || error.status === 403))) {
        throw error;
      }
    }
  }, []);

  const login = useCallback(async (schoolId: string, password: string) => {
    setStatus('loading');
    try {
      const currentUser = await authService.login(schoolId, password);
      setUser(currentUser);
      setStatus('authenticated');
      return currentUser;
    } catch (error) {
      setUser(null);
      setStatus('unauthenticated');
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setStatus('unauthenticated');
    }
  }, []);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    void refresh().catch(() => {
      setUser(null);
      setStatus('unauthenticated');
    });
  }, [refresh]);

  const value = useMemo(
    () => ({ user, status, login, logout, refresh }),
    [user, status, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
