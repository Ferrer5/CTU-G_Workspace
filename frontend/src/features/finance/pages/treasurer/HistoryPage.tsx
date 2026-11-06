import '../../../../css/finance-treasurer.css';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import { useTreasurerFinance } from '../../hooks/useTreasurerFinance';

export default function HistoryPage() {
  const { data, loading, error } = useTreasurerFinance();

  if (loading) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">Loading history…</p></div></section>;
  if (error || !data) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">{error ?? 'No finance history.'}</p></div></section>;

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="History" subtitle="Transactions across org fees, other funds, and expenses." />
      <div className="fin-card">
        <table className="fin-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Description</th>
              <th>Semester</th>
              <th>From</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.payments.map((payment) => (
              <tr key={payment.payment_id}>
                <td>Org Fee</td>
                <td>{payment.student_name}</td>
                <td>{payment.semester}</td>
                <td>{payment.received_by ?? 'Office'}</td>
                <td>₱{payment.amount.toLocaleString()}</td>
                <td><span className="fin-badge-card">{payment.status}</span></td>
              </tr>
            ))}
            {data.expenses.map((expense) => (
              <tr key={`expense-${expense.expense_id}`}>
                <td>Expense</td>
                <td>{expense.description}</td>
                <td>—</td>
                <td>{expense.recorded_by}</td>
                <td>₱{expense.amount.toLocaleString()}</td>
                <td><span className="fin-badge-card">Posted</span></td>
              </tr>
            ))}
            {data.otherFunds.map((fund) => (
              <tr key={`fund-${fund.fund_id}`}>
                <td>Other Fund</td>
                <td>{fund.description}</td>
                <td>—</td>
                <td>{fund.source}</td>
                <td>₱{fund.amount.toLocaleString()}</td>
                <td><span className="fin-badge-card">Posted</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
