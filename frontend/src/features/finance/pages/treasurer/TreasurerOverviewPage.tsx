import '../../../../css/finance-treasurer.css';
import { CheckIcon, ClockIcon, CoinIcon } from '../../../../components/common/DashboardIcons';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import usePermissions from '../../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../../permissions';
import StatCard from '../../../student/components/StatCard';
import { useTreasurerFinance } from '../../hooks/useTreasurerFinance';

export default function TreasurerOverviewPage() {
  const { hasPermission } = usePermissions();
  const { data, loading, error } = useTreasurerFinance();

  if (!hasPermission(PERMISSIONS.financeDashboardView)) {
    return (
      <section className="dash-page">
        <div className="dash-card"><p className="dash-empty">You do not have access to the treasurer dashboard.</p></div>
      </section>
    );
  }

  if (loading) {
    return <section className="dash-page"><div className="dash-card"><p className="dash-empty">Loading finance overview…</p></div></section>;
  }

  if (error || !data) {
    return <section className="dash-page"><div className="dash-card"><p className="dash-empty">{error ?? 'Unable to load finance overview.'}</p></div></section>;
  }

  const remaining = data.students.reduce((sum, student) => sum + student.balance, 0);
  const totalCollected = data.payments.reduce((sum, payment) => sum + payment.amount, 0);
  const expenses = data.expenses.reduce((sum, expense) => sum + expense.amount, 0);
  const collectable = data.students.filter((student) => student.status !== 'Paid').reduce((sum, student) => sum + student.balance, 0);

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="Dashboard" subtitle="Current school year and semester" />
      <div className="fin-subheader">
        <div className="fin-live">Live</div>
      </div>
      <div className="fin-grid">
        <StatCard label="Remaining Balance" value={`₱${remaining.toLocaleString()}`} trend="Cash on hand" tone="good" icon={<CoinIcon />} />
        <StatCard label="Total Collected" value={`₱${totalCollected.toLocaleString()}`} trend="This school year" tone="good" icon={<CheckIcon />} />
        <StatCard label="Expenses" value={`₱${expenses.toLocaleString()}`} trend="This school year" tone="warn" icon={<CoinIcon />} />
        <StatCard label="Collectable Org Fee" value={`₱${collectable.toLocaleString()}`} trend={`${data.students.filter((student) => student.status !== 'Paid').length} students`} tone={collectable > 0 ? 'warn' : 'good'} icon={<ClockIcon />} />
      </div>
      <div className="fin-card">
        <div className="fin-subheader">
          <h2 className="dash-page-title" style={{ fontSize: '18px' }}>Students</h2>
          <button type="button" className="fin-btn-secondary">Reset</button>
        </div>
        <table className="fin-table">
          <thead>
            <tr>
              <th>#</th>
              <th>CTU ID</th>
              <th>Name</th>
              <th>Course.Year.Section</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.students.map((student, index) => (
              <tr key={student.school_id}>
                <td>{index + 1}</td>
                <td>{student.school_id}</td>
                <td>{student.name}</td>
                <td>{`${student.course_code}.${student.year}.${student.section}`}</td>
                <td><span className="fin-badge-card">{student.status}</span></td>
                <td className="fin-muted">View ledger</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
