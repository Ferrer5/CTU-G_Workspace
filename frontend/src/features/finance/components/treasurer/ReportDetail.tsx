interface ReportDetailProps {
  title: string;
}

export default function ReportDetail({ title }: ReportDetailProps) {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>{title}</h3>
      <p className="fin-muted">Detailed report preview.</p>
    </div>
  );
}
