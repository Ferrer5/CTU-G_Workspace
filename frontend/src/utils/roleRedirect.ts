import { ROLES } from '../types/auth';

export function getDashboardPath(roles: string[]): string | null {
  if (roles.includes(ROLES.Student)) return '/student';
  return null;
}
