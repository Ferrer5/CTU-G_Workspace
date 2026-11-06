interface SummaryStatsProps {
  items: Array<{ label: string; value: string; tone?: 'good' | 'warn' | 'bad' }>;
}

export default function SummaryStats({ items }: SummaryStatsProps) {
  return (
    <div className="fin-grid">
      {items.map((item) => (
        <article key={item.label} className="fin-card">
          <div className="fin-muted">{item.label}</div>
          <div className="dash-stat-val is-amount" style={{ marginTop: 8 }}>{item.value}</div>
        </article>
      ))}
    </div>
  );
}
