import { apiGet } from './apiClient';
import type { CourseOption } from '../types/auth';

export function fetchCourses(): Promise<CourseOption[]> {
  return apiGet<CourseOption[]>('/academics/courses/');
}
