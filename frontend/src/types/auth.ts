export interface AuthUser {
  school_id: string;
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  suffix_name: string | null;
  email: string | null;
  roles: string[];
}

export const ROLES = {
  Admin: 'Admin',
  Student: 'Student',
} as const;

export type RoleName = (typeof ROLES)[keyof typeof ROLES];
