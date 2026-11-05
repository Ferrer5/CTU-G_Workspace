import { apiGet } from '../../../services/apiClient';

export interface StudentAcademicProfile {
  course_code: string;
  course_name: string | null;
  year: string;
  section: string;
  school_year: string;
  academic_status: string;
}

export function fetchAcademicProfile(): Promise<StudentAcademicProfile> {
  return apiGet('/academics/me/');
}
