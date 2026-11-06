import '../../../../css/finance-treasurer.css';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import { useTreasurerFinance } from '../../hooks/useTreasurerFinance';

export default function ReportsPage() {
  const { data, loading, error } = useTreasurerFinance();

  if (loading) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">Loading reports…</p></div></section>;
  if (error || !data) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">{error ?? 'No reports available.'}</p></div></section>;

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="Reports" subtitle="Monthly overview and generated reports." />
      <div className="fin-card">
        <h2 className="dash-page-title" style={{ fontSize: '18px' }}>Monthly Overview</h2>
        <div className="fin-chart" aria-label="Monthly overview chart">
          {[52, 78, 91, 58, 84, 66].map((value, index) => (
            <div key={value + index} style={{ height: `${value}%`, width: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'end', alignItems: 'center', gap: 6 }}>
              <div className="fin-chart-bar" style={{ width: '100%', height: `${value}%` }} />
              <span className="fin-muted">M{index + 1}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="fin-card">
        <h2 className="dash-page-title" style={{ fontSize: '18px' }}>All Reports</h2>
        <table className="fin-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Title</th>
              <th>Status</th>
              <th>School Year</th>
              <th>Created By</th>
            </tr>
          </thead>
          <tbody>
            {data.reports.map((report) => (
              <tr key={report.report_id}>
                <td>{report.report_type}</td>
                <td>{report.title}</td>
                <td>{report.status}</td>
                <td>{report.school_year}</td>
                <td>{report.created_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
