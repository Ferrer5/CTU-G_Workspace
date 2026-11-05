const TONE: Record<string, string> = {
  Paid: 'dash-badge-ok',
  Partial: 'dash-badge-warn',
  Pending: 'dash-badge-warn',
  Overdue: 'dash-badge-bad',
};

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`dash-badge ${TONE[status] ?? 'dash-badge-warn'}`}>{status}</span>;
}
