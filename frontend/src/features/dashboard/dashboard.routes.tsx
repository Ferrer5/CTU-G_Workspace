import { Navigate, Route } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import { PERMISSIONS } from '../../permissions';
import PermissionRoute from '../../routes/PermissionRoute';
import DashboardSidebar from './components/DashboardSidebar';
import DashboardIndexPage from './pages/DashboardIndexPage';
import ServicePage from './pages/ServicePage';
import FinancePage from '../finance/pages/FinancePage';
import StudentProfilePage from '../student/pages/StudentProfilePage';
import { dashboardServices } from './dashboardConfig';

const serviceRoute = (service: (typeof dashboardServices)[number]) => (
  <PermissionRoute requiredPermissions={service.permissions} mode="any">
    {service.serviceCode === 'finance' ? (
      <FinancePage title={service.label} description={service.description} />
    ) : (
      <ServicePage title={service.label} description={service.description} />
    )}
  </PermissionRoute>
);

export const dashboardRoutes = (
  <>
    <Route
      path="/dashboard"
      element={
        <PermissionRoute>
          <DashboardLayout sidebar={(props) => <DashboardSidebar {...props} />} />
        </PermissionRoute>
      }
    >
      <Route index element={<DashboardIndexPage />} />
      <Route
        path="profile"
        element={
          <PermissionRoute requiredPermissions={[PERMISSIONS.accountsProfileViewOwn]}>
            <StudentProfilePage />
          </PermissionRoute>
        }
      />
      {dashboardServices.map((service) => (
        <Route
          key={service.serviceCode}
          path={`${service.path.replace('/dashboard/', '')}/*`}
          element={serviceRoute(service)}
        />
      ))}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Route>
    <Route path="/student/profile" element={<Navigate to="/dashboard/profile" replace />} />
    <Route path="/student/*" element={<Navigate to="/dashboard" replace />} />
  </>
);
