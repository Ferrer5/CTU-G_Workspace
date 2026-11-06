import { Fragment } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import logo from '../../../assets/logo.png';
import {
  CloseIcon,
  GridIcon,
  LogoutIcon,
  UserIcon,
} from '../../../components/common/DashboardIcons';
import { useAuth } from '../../../hooks/useAuth';
import usePermissions from '../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../permissions';
import { BRAND_NAME } from '../../../utils/constants';
import type { DashboardSidebarProps } from '../../../layouts/DashboardLayout';
import { financeNavItems } from '../../finance/financeNav';
import { dashboardNavigation } from '../dashboardConfig';

function displayName(first: string | null, last: string | null) {
  return [first, last].filter(Boolean).join(' ') || 'Campus User';
}

export default function DashboardSidebar({ open, onClose }: DashboardSidebarProps) {
  const { user, logout } = useAuth();
  const { hasAnyPermission, hasPermission } = usePermissions();
  const navigate = useNavigate();
  const navItems = dashboardNavigation.filter((item) => {
    // NOTE: the existing filter hides "Overview" for financePaymentViewOwn users.
    // Keep that behaviour; treasurer users should land in the Finance workspace.
    if (item.path === '/dashboard' && hasPermission(PERMISSIONS.financePaymentViewOwn)) {
      return false;
    }
    return item.permissions.length === 0 || hasAnyPermission(item.permissions);
  });
  const financeLinks = financeNavItems.filter(
    (item) => item.permissions.length === 0 || hasAnyPermission(item.permissions),
  );
  const name = displayName(user?.first_name ?? null, user?.last_name ?? null);
  const initials = `${user?.first_name?.trim().charAt(0) ?? ''}${user?.last_name?.trim().charAt(0) ?? ''}`
    || user?.school_id.slice(0, 2).toUpperCase()
    || 'CU';
  const roles = user?.roles.join(', ') || 'No role assigned';

  const handleSignOut = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Unable to complete server sign-out.', error);
    } finally {
      navigate('/', { replace: true });
    }
  };

  return (
    <aside className={`dash-sidebar ${open ? 'is-open' : ''}`} aria-label="Workspace dashboard">
      <button type="button" className="dash-sb-close" aria-label="Close navigation" onClick={onClose}>
        <CloseIcon />
      </button>
      <div className="dash-brand">
        <div className="dash-logo"><img src={logo} alt="" /></div>
        <div>
          <div className="dash-brand-name">{BRAND_NAME}</div>
          <div className="dash-brand-sub">Campus Workspace</div>
        </div>
      </div>
      <nav aria-label="Dashboard navigation">
        <div className="dash-sb-label">Services</div>
        {navItems.map((item, index) => (
          <Fragment key={item.path}>
            <NavLink
              to={item.path}
              end={item.path === '/dashboard'}
              onClick={onClose}
              className={({ isActive }) => `dash-nav-item ${isActive ? 'is-active' : ''}`}
            >
              {index === 0 ? <GridIcon /> : item.label === 'My Profile' ? <UserIcon /> : <GridIcon />}
              {item.label}
            </NavLink>
            {item.path === '/dashboard/finance' && financeLinks.length > 0 && (
              <div className="dash-sb-group">
                {financeLinks.map((link) => (
                  <NavLink
                    key={link.path}
                    to={link.path}
                    end={link.path === '/dashboard/finance'}
                    onClick={onClose}
                    className={({ isActive }) => `dash-nav-item dash-nav-sub ${isActive ? 'is-active' : ''}`}
                  >
                    <link.Icon />
                    {link.label}
                  </NavLink>
                ))}
              </div>
            )}
          </Fragment>
        ))}
      </nav>
      <div className="dash-spacer" />
      <div className="dash-sb-user">
        <div className="dash-user-card">
          <div className="dash-user-av">{initials}</div>
          <div className="min-w-0">
            <div className="dash-user-name truncate">{name}</div>
            <div className="dash-user-role truncate" title={roles}>{roles}</div>
          </div>
        </div>
        <button type="button" className="dash-signout" onClick={handleSignOut}>
          <LogoutIcon /> Sign Out
        </button>
      </div>
    </aside>
  );
}
