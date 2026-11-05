import { Navigate, Route, Routes } from 'react-router-dom';
import HomePage from '../features/home/pages/HomePage';
import PublicLayout from '../layouts/PublicLayout';
import { studentRoutes } from '../features/student/student.routes';

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
      {studentRoutes}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
