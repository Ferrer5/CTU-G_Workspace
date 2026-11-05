import { useAuth } from '../../../hooks/useAuth';

export default function DashboardHeader({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  const { user } = useAuth();
  const name = [user?.first_name, user?.last_name].filter(Boolean).join(' ');

  return (
    <header className="dash-page-hdr">
      <div>
        <h1 className="dash-page-title">{title}</h1>
        <p className="dash-page-sub">
          {subtitle}
          {name ? ` · ${name}` : ''}
        </p>
        {user?.roles.length ? (
          <div className="dash-role-list" aria-label="Your roles">
            {user.roles.map((role) => (
              <span className="dash-role-chip" key={role}>{role}</span>
            ))}
          </div>
        ) : null}
      </div>
    </header>
  );
}
