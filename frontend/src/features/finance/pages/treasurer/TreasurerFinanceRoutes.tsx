import { Navigate, Route, Routes } from 'react-router-dom';
import { PERMISSIONS } from '../../../../permissions';
import PermissionRoute from '../../../../routes/PermissionRoute';
import CollectPage from './CollectPage';
import ExpensesPage from './ExpensesPage';
import HistoryPage from './HistoryPage';
import ReportsPage from './ReportsPage';
import SettingsPage from './SettingsPage';
import TreasurerOverviewPage from './TreasurerOverviewPage';

export default function TreasurerFinanceRoutes() {
  return (
    <Routes>
      <Route index element={<PermissionRoute requiredPermissions={[PERMISSIONS.financeDashboardView]}><TreasurerOverviewPage /></PermissionRoute>} />
      <Route path="collect" element={<PermissionRoute requiredPermissions={[PERMISSIONS.financePaymentCreate, PERMISSIONS.financeOtherFundCreate]} mode="any"><CollectPage /></PermissionRoute>} />
      <Route path="expenses" element={<PermissionRoute requiredPermissions={[PERMISSIONS.financeExpenseView]}><ExpensesPage /></PermissionRoute>} />
      <Route path="history" element={<PermissionRoute requiredPermissions={[PERMISSIONS.financePaymentViewAll]}><HistoryPage /></PermissionRoute>} />
      <Route path="reports" element={<PermissionRoute requiredPermissions={[PERMISSIONS.financeReportView]}><ReportsPage /></PermissionRoute>} />
      <Route path="settings" element={<PermissionRoute requiredPermissions={[PERMISSIONS.financeSchoolYearView, PERMISSIONS.financeFeeView, PERMISSIONS.financeExemptionView, PERMISSIONS.financeSignatureManageOwn]} mode="any"><SettingsPage /></PermissionRoute>} />
      <Route path="*" element={<Navigate to="/dashboard/finance" replace />} />
    </Routes>
  );
}
