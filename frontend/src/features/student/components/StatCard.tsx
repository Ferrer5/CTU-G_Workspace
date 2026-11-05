import type { ReactNode } from 'react';

interface StatCardProps {
  label: string;
  value: string;
  trend: string;
  tone: 'good' | 'warn' | 'bad';
  icon: ReactNode;
}

export default function StatCard({ label, value, trend, tone, icon }: StatCardProps) {
  const iconTone = tone === 'good' ? 'is-g' : tone === 'warn' ? 'is-y' : 'is-r';
  const trendTone = tone === 'warn' ? 'is-warn' : '';

  return (
    <article className="dash-stat-card">
      <div className="dash-stat-lbl">{label}</div>
      <div className="dash-stat-row">
        <div className="dash-stat-val is-amount">{value}</div>
        <div className={`dash-stat-icon ${iconTone}`}>{icon}</div>
      </div>
      <div className={`dash-stat-trend ${trendTone}`}>{trend}</div>
    </article>
  );
}
