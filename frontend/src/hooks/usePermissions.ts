import { useCallback, useMemo } from 'react';
import { useAuth } from './useAuth';

export default function usePermissions() {
  const { user } = useAuth();
  const permissions = useMemo(() => new Set(user?.permissions ?? []), [user?.permissions]);
  const services = useMemo(
    () => new Set(user?.services.map((service) => service.service_code) ?? []),
    [user?.services],
  );
  const hasPermission = useCallback(
    (permission: string) => permissions.has(permission),
    [permissions],
  );
  const hasAnyPermission = useCallback(
    (required: readonly string[]) => required.some((permission) => permissions.has(permission)),
    [permissions],
  );
  const hasAllPermissions = useCallback(
    (required: readonly string[]) => required.every((permission) => permissions.has(permission)),
    [permissions],
  );
  const hasService = useCallback(
    (serviceCode: string) => services.has(serviceCode),
    [services],
  );

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasService,
  };
}
