import usePermissions from '../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../permissions';
import ServicePage from '../../dashboard/pages/ServicePage';
import TreasurerFinanceRoutes from './treasurer/TreasurerFinanceRoutes';
import StudentFinancePage from './StudentFinancePage';

/**
 * Picks the Finance workspace from effective permissions (never from role names).
 * Treasurer/Admin branches live before the student branch.
 */
export default function FinancePage({ title, description }: { title: string; description: string }) {
  const { hasPermission, hasAnyPermission } = usePermissions();

  const hasTreasurerAccess = hasAnyPermission([
    PERMISSIONS.financePaymentCreate,
    PERMISSIONS.financeFeeSetAmount,
    PERMISSIONS.financeReportCreate,
  ]);

  if (hasTreasurerAccess) {
    // Admin also has payment.create, so they land here until a dedicated Admin branch exists.
    return <TreasurerFinanceRoutes />;
  }

  const hasStaffAccess = hasAnyPermission([
    PERMISSIONS.financePaymentViewAll,
    PERMISSIONS.financeDashboardView,
  ]);
  if (hasStaffAccess) return <ServicePage title={title} description={description} />;

  if (hasPermission(PERMISSIONS.financePaymentViewOwn)) return <StudentFinancePage />;

  return <ServicePage title={title} description={description} />;
}
