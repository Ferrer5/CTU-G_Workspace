import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';
import usePermissions from '../hooks/usePermissions';

interface PermissionRouteProps {
  children: ReactNode;
  requiredPermissions?: readonly string[];
  mode?: 'all' | 'any';
}

export default function PermissionRoute({
  children,
  requiredPermissions = [],
  mode = 'all',
}: PermissionRouteProps) {
  const { user, status } = useAuth();
  const { hasAllPermissions, hasAnyPermission } = usePermissions();

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center" role="status" aria-label="Loading account">
        <LoadingSpinner className="h-8 w-8" />
      </div>
    );
  }

  if (!user) return <Navigate to="/" replace />;

  const allowed =
    requiredPermissions.length === 0 ||
    (mode === 'all'
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions));

  return allowed ? children : <Navigate to="/not-allowed" replace />;
}
