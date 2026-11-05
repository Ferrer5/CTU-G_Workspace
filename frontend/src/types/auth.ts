export interface AuthUser {
  school_id: string;
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  suffix_name: string | null;
  email: string | null;
  roles: string[];
  permissions: string[];
  services: AuthService[];
}

export interface AuthService {
  service_code: string;
  service_name: string;
}

export const ROLES = {
  Admin: 'Admin',
  Student: 'Student',
  SuperUser: 'SuperUser',
} as const;

export type RoleName = (typeof ROLES)[keyof typeof ROLES];

export interface CourseOption {
  course_id: number;
  course_code: string;
  course_name: string | null;
}

export interface RegisterPayload {
  school_id: string;
  password: string;
  confirm_password: string;
  email: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  course_id: number;
  year: string;
  section: string;
}
