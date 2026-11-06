import '../../../../css/finance-treasurer.css';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import usePermissions from '../../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../../permissions';
import { useTreasurerFinance } from '../../hooks/useTreasurerFinance';

export default function ExpensesPage() {
  const { hasPermission } = usePermissions();
  const { data, loading, error } = useTreasurerFinance();

  if (loading) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">Loading expenses…</p></div></section>;
  if (error || !data) return <section className="dash-page"><div className="dash-card"><p className="dash-empty">{error ?? 'No expenses available.'}</p></div></section>;

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="Expenses" subtitle="Track expenses and attach supporting receipts." />
      <div className="fin-card">
        <div className="fin-form-grid">
          <div className="fin-field" style={{ gridColumn: '1 / -1' }}>
            <label className="fin-label">Description</label>
            <input className="fin-input" defaultValue="Event signage" />
          </div>
          <div className="fin-field">
            <label className="fin-label">Amount</label>
            <input className="fin-input" type="number" defaultValue="1800" />
          </div>
          <div className="fin-field">
            <label className="fin-label">Date</label>
            <input className="fin-input" type="date" defaultValue="2024-09-20" />
          </div>
        </div>
        <div className="fin-summary">
          <div className="fin-muted">Receipt images can be attached by the treasurer.</div>
          {hasPermission(PERMISSIONS.financeExpenseCreate) ? <button type="button" className="fin-btn">Add Expense</button> : <button type="button" className="fin-btn-secondary" disabled>Add Expense</button>}
        </div>
      </div>

      <div className="fin-card">
        <h2 className="dash-page-title" style={{ fontSize: '18px' }}>Expense list</h2>
        <table className="fin-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Recorded by</th>
            </tr>
          </thead>
          <tbody>
            {data.expenses.map((expense) => (
              <tr key={expense.expense_id}>
                <td>{expense.description}</td>
                <td>₱{expense.amount.toLocaleString()}</td>
                <td>{expense.expense_date}</td>
                <td>{expense.recorded_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
