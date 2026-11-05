import { NavLink, useNavigate } from 'react-router-dom';
import logo from '../../../assets/logo.png';
import {
  CloseIcon,
  GridIcon,
  LogoutIcon,
} from '../../../components/common/DashboardIcons';
import { BRAND_NAME } from '../../../utils/constants';
import { useAuth } from '../../../hooks/useAuth';
import type { DashboardSidebarProps } from '../../../layouts/DashboardLayout';
import { studentServiceNavItems } from '../studentNav';

function displayName(first: string | null, middle: string | null, last: string | null, suffix: string | null) {
  const middleInitial = middle?.trim().charAt(0);
  return [first, middleInitial ? `${middleInitial}.` : null, last, suffix]
    .filter((part): part is string => Boolean(part?.trim()))
    .join(' ') || 'Student';
}

function initials(first: string | null, last: string | null, fallback: string) {
  const nameInitials = `${first?.trim().charAt(0) ?? ''}${last?.trim().charAt(0) ?? ''}`;
  return nameInitials || fallback.slice(0, 2).toUpperCase();
}

export default function StudentSidebar({ open, onClose }: DashboardSidebarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const name = displayName(user?.first_name ?? null, user?.middle_name ?? null, user?.last_name ?? null, user?.suffix_name ?? null);
  const avatarInitials = initials(user?.first_name ?? null, user?.last_name ?? null, user?.school_id ?? 'ST');

  const handleSignOut = async () => {
    try {
      await logout();
    } catch {
      // Local authentication state is cleared by logout even if the request fails.
    } finally {
      navigate('/', { replace: true });
    }
  };

  return (
    <aside className={`dash-sidebar ${open ? 'is-open' : ''}`} aria-label="Student dashboard">
      <button type="button" className="dash-sb-close" aria-label="Close navigation" onClick={onClose}>
        <CloseIcon />
      </button>
      <div className="dash-brand">
        <div className="dash-logo"><img src={logo} alt="" /></div>
        <div>
          <div className="dash-brand-name">{BRAND_NAME}</div>
          <div className="dash-brand-sub">Student Portal</div>
        </div>
      </div>
      <nav aria-label="Student navigation">
        <div className="dash-sb-label">Main</div>
        <NavLink
          to="/student"
          end
          className={({ isActive }) => `dash-nav-item ${isActive ? 'is-active' : ''}`}
        >
          <GridIcon /> Overview
        </NavLink>
        <div className="dash-sb-label">Services</div>
        {studentServiceNavItems.map(({ label, Icon }) => (
          <span key={label} className="dash-nav-item is-disabled" aria-disabled="true">
            <Icon /> {label}<span className="dash-soon">Soon</span>
          </span>
        ))}
      </nav>
      <div className="dash-spacer" />
      <div className="dash-sb-user">
        <NavLink
          to="/student/profile"
          className={({ isActive }) => `dash-user-card ${isActive ? 'is-active' : ''}`}
        >
          <div className="dash-user-av">{avatarInitials}</div>
          <div>
            <div className="dash-user-name">{name}</div>
            <div className="dash-user-role">Student</div>
          </div>
        </NavLink>
        <button type="button" className="dash-signout" onClick={handleSignOut}>
          <LogoutIcon /> Sign Out
        </button>
      </div>
    </aside>
  );
}
