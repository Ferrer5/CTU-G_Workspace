import { useAuth } from '../../../hooks/useAuth';
import {
  CheckIcon,
  ClockIcon,
  CoinIcon,
  InfoIcon,
} from '../../../components/common/DashboardIcons';
import StatCard from '../components/StatCard';
import { studentOverviewStats, studentPaymentsMock } from '../data/studentOverview.mock';

export default function StudentOverviewPage() {
  const { user } = useAuth();
  const firstName = user?.first_name?.trim() || 'Student';
  const today = new Intl.DateTimeFormat('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date());
  const icons = [<CoinIcon key="coin" />, <CheckIcon key="check" />, <ClockIcon key="clock" />];

  return (
    <section className="dash-page">
      <header className="dash-page-hdr">
        <div>
          <h1 className="dash-page-title">Welcome, {firstName}</h1>
          <p className="dash-page-sub">Here’s your student portal overview.</p>
        </div>
        <div className="dash-date-badge">{today}</div>
      </header>

      <div className="dash-notice" role="note">
        <InfoIcon />
        <p className="dash-notice-text">
          The finance figures below are sample data and are not connected to a live account.
        </p>
      </div>

      <div className="dash-stat-grid">
        {studentOverviewStats.map((stat, index) => (
          <StatCard key={stat.label} {...stat} icon={icons[index]} />
        ))}
      </div>

      <section className="dash-card" aria-labelledby="student-payments-title">
        <div className="dash-card-hdr">
          <h2 className="dash-card-title" id="student-payments-title">Recent Payments</h2>
          <span className="dash-badge dash-badge-warn">Sample data</span>
        </div>
        <div className="dash-tbl-wrap">
          <table className="dash-table">
            <thead>
              <tr><th scope="col">Item</th><th scope="col">Amount</th><th scope="col">Date</th><th scope="col">Status</th></tr>
            </thead>
            <tbody>
              {studentPaymentsMock.map((payment) => (
                <tr key={payment.item}>
                  <td>{payment.item}</td>
                  <td className="dash-mono">{payment.amount}</td>
                  <td className="dash-td-m dash-mono">{payment.date}</td>
                  <td>
                    <span className={`dash-badge ${payment.status === 'Paid' ? 'dash-badge-ok' : 'dash-badge-warn'}`}>
                      {payment.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
