import { useMemo } from 'react';
import usePermissions from '../../../hooks/usePermissions';
import { dashboardServices } from '../dashboardConfig';
import ServiceCard from './ServiceCard';

export default function AvailableServices() {
  const { hasAnyPermission, hasService } = usePermissions();
  const available = useMemo(
    () =>
      dashboardServices.filter(
        (service) =>
          hasService(service.serviceCode) &&
          hasAnyPermission(service.permissions),
      ),
    [hasAnyPermission, hasService],
  );

  return (
    <section className="dash-card" aria-labelledby="available-services-heading">
      <div className="dash-card-hdr">
        <h2 className="dash-card-title" id="available-services-heading">Available Services</h2>
        <span className="dash-service-count">{available.length}</span>
      </div>
      {available.length ? (
        <div className="dash-service-grid">
          {available.map((service) => (
            <ServiceCard key={service.serviceCode} service={service} />
          ))}
        </div>
      ) : (
        <p className="dash-empty">No services are assigned to your account yet.</p>
      )}
    </section>
  );
}
