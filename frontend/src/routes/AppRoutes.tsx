import { Navigate, Route, Routes } from 'react-router-dom';
import HomePage from '../features/home/pages/HomePage';
import PublicLayout from '../layouts/PublicLayout';
import { authRoutes } from '../features/auth/auth.routes';
import { dashboardRoutes } from '../features/dashboard/dashboard.routes';
import NotAllowedPage from '../features/dashboard/pages/NotAllowedPage';
import ThemeProvider from '../contexts/ThemeProvider';

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicLayout>
            <HomePage />
          </PublicLayout>
        }
      />
      {authRoutes}
      {dashboardRoutes}
      <Route
        path="/not-allowed"
        element={<ThemeProvider><NotAllowedPage /></ThemeProvider>}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
