import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../../../services/apiClient';
import { useAuth } from '../../../hooks/useAuth';
import type { StudentAcademicProfile } from '../services/studentService';
import { fetchAcademicProfile } from '../services/studentService';

function fullName(first: string | null, middle: string | null, last: string | null, suffix: string | null) {
  const middleInitial = middle?.trim().charAt(0);
  return [first, middleInitial ? `${middleInitial}.` : null, last, suffix]
    .filter((part): part is string => Boolean(part?.trim()))
    .join(' ') || 'Student';
}

function initials(first: string | null, last: string | null, fallback: string) {
  const nameInitials = `${first?.trim().charAt(0) ?? ''}${last?.trim().charAt(0) ?? ''}`;
  return nameInitials || fallback.slice(0, 2).toUpperCase();
}

export default function StudentProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [academic, setAcademic] = useState<StudentAcademicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const name = fullName(user?.first_name ?? null, user?.middle_name ?? null, user?.last_name ?? null, user?.suffix_name ?? null);
  const avatarInitials = initials(user?.first_name ?? null, user?.last_name ?? null, user?.school_id ?? 'ST');

  useEffect(() => {
    let active = true;
    fetchAcademicProfile()
      .then((profile) => {
        if (active) setAcademic(profile);
      })
      .catch((requestError: unknown) => {
        if (!active) return;
        if (requestError instanceof ApiError && (requestError.status === 401 || requestError.status === 403)) {
          void logout()
            .catch(() => undefined)
            .finally(() => navigate('/', { replace: true }));
          return;
        }
        setError(requestError instanceof Error ? requestError.message : 'Unable to load academic information.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [logout, navigate]);

  return (
    <section className="dash-page">
      <header className="dash-page-hdr">
        <div>
          <h1 className="dash-page-title">My Profile</h1>
          <p className="dash-page-sub">Your personal and academic information.</p>
        </div>
      </header>

      <section className="dash-card" aria-label="Student profile">
        <div className="dash-profile-hero">
          <div className="dash-avatar" aria-hidden="true">{avatarInitials}</div>
          <h2 className="dash-profile-name">{name}</h2>
          <div className="dash-profile-role">Student</div>
        </div>
        <div className="dash-fields">
          <div className="dash-field">
            <span className="dash-field-label">School ID</span>
            <span className="dash-field-value dash-mono">{user?.school_id ?? '—'}</span>
          </div>
          <div className="dash-field is-full">
            <span className="dash-field-label">Email</span>
            <span className="dash-field-value">{user?.email || '—'}</span>
          </div>
          {loading && <div className="dash-field-value" role="status">Loading academic information…</div>}
          {error && <div className="dash-field-value" role="alert">{error}</div>}
          {academic && (
            <>
              <div className="dash-field">
                <span className="dash-field-label">Course</span>
                <span className="dash-field-value">
                  {academic.course_code}{academic.course_name ? ` — ${academic.course_name}` : ''}
                </span>
              </div>
              <div className="dash-field">
                <span className="dash-field-label">Year &amp; Section</span>
                <span className="dash-field-value">{academic.year} - {academic.section}</span>
              </div>
              <div className="dash-field">
                <span className="dash-field-label">School Year</span>
                <span className="dash-field-value dash-mono">{academic.school_year}</span>
              </div>
              <div className="dash-field">
                <span className="dash-field-label">Status</span>
                <span className="dash-field-value">{academic.academic_status}</span>
              </div>
            </>
          )}
        </div>
      </section>
    </section>
  );
}
