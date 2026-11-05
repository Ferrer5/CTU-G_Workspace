import { Link } from 'react-router-dom';
import type { DashboardService } from '../dashboardConfig';

export default function ServiceCard({ service }: { service: DashboardService }) {
  const Icon = service.icon;
  return (
    <Link className="dash-service-card" to={service.path}>
      <span className="dash-service-icon"><Icon /></span>
      <span className="dash-service-title">{service.label}</span>
      <span className="dash-service-description">{service.description}</span>
      <span className="dash-service-link">Open service <span aria-hidden="true">→</span></span>
    </Link>
  );
}
