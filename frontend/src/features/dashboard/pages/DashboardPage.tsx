import { useAuth } from '../../../hooks/useAuth';
import DashboardHeader from '../components/DashboardHeader';
import AvailableServices from '../components/AvailableServices';

export default function DashboardPage() {
  const { user } = useAuth();
  return (
    <section className="dash-page">
      <DashboardHeader
        title="Dashboard"
        subtitle="Your campus services and account access."
      />
      <section className="dash-overview" aria-label="Account overview">
        <article className="dash-stat-card">
          <span className="dash-stat-lbl">Assigned roles</span>
          <strong className="dash-stat-val">{user?.roles.length ?? 0}</strong>
          <span className="dash-stat-trend">Access is based on effective permissions</span>
        </article>
        <article className="dash-stat-card">
          <span className="dash-stat-lbl">Available permissions</span>
          <strong className="dash-stat-val">{user?.permissions.length ?? 0}</strong>
          <span className="dash-stat-trend">Resolved from roles, grants, and denies</span>
        </article>
      </section>
      <AvailableServices />
    </section>
  );
}
