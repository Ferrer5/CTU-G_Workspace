import DashboardHeader from '../components/DashboardHeader';

export default function ServicePage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <section className="dash-page">
      <DashboardHeader title={title} subtitle={description} />
      <section className="dash-card" aria-label={`${title} service`}>
        <div className="dash-card-hdr">
          <h2 className="dash-card-title">{title}</h2>
        </div>
        <p className="dash-empty">
          You have permission to access this service. Its workspace will appear here as the service is connected.
        </p>
      </section>
    </section>
  );
}
