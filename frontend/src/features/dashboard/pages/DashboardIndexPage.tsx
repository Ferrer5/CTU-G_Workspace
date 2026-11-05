import { Navigate } from 'react-router-dom';
import usePermissions from '../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../permissions';
import DashboardPage from './DashboardPage';

export default function DashboardIndexPage() {
  const { hasPermission } = usePermissions();
  return hasPermission(PERMISSIONS.financePaymentViewOwn)
    ? <Navigate to="/dashboard/finance" replace />
    : <DashboardPage />;
}
