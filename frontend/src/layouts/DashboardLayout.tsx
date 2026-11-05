import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { MenuIcon } from '../components/common/DashboardIcons';
import '../css/dashboard.css';

export interface DashboardSidebarProps {
  open: boolean;
  onClose: () => void;
}

interface DashboardLayoutProps {
  sidebar: (props: DashboardSidebarProps) => ReactNode;
}

function DashboardShell({ sidebar }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!sidebarOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSidebarOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen]);

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="dash-root">
      <div className="dash-top-accent" />
      <button
        type="button"
        className="dash-menu-btn"
        aria-label="Open dashboard menu"
        aria-expanded={sidebarOpen}
        onClick={() => setSidebarOpen(true)}
      >
        <MenuIcon />
      </button>
      <button
        type="button"
        className={`dash-overlay ${sidebarOpen ? 'is-open' : ''}`}
        aria-label="Close dashboard menu"
        onClick={closeSidebar}
      />
      {sidebar({ open: sidebarOpen, onClose: closeSidebar })}
      <main className="dash-main">
        <Outlet />
      </main>
    </div>
  );
}

export default function DashboardLayout({ sidebar }: DashboardLayoutProps) {
  const location = useLocation();
  return <DashboardShell key={location.pathname} sidebar={sidebar} />;
}