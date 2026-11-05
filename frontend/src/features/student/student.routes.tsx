import { Route } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import ProtectedRoute from '../../routes/ProtectedRoute';
import { ROLES } from '../../types/auth';
import StudentSidebar from './components/StudentSidebar';
import StudentOverviewPage from './pages/StudentOverviewPage';
import StudentProfilePage from './pages/StudentProfilePage';

export const studentRoutes = (
  <Route
    path="/student"
    element={
      <ProtectedRoute allowedRoles={[ROLES.Student]}>
        <DashboardLayout sidebar={(props) => <StudentSidebar {...props} />} />
      </ProtectedRoute>
    }
  >
    <Route index element={<StudentOverviewPage />} />
    <Route path="profile" element={<StudentProfilePage />} />
  </Route>
);
