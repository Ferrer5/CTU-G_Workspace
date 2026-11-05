import { HelpIcon } from '../../../components/common/DashboardIcons';
import type { SemesterFee } from '../types';
import { formatPeso, semShort } from '../utils/format';
import StatusBadge from './StatusBadge';

interface FeesTableProps {
  fees: SemesterFee[];
  onPay: (fee: SemesterFee) => void;
}

export default function FeesTable({ fees, onPay }: FeesTableProps) {
  return (
    <section className="dash-card" aria-labelledby="fin-fees-title">
      <div className="dash-card-hdr">
        <h2 className="dash-card-title" id="fin-fees-title">Fee Breakdown</h2>
        <span className="dash-badge dash-badge-warn">{fees.length} pending</span>
      </div>
      <div className="dash-tbl-wrap fin-scroll">
        <table className="dash-table">
          <thead>
            <tr>
              <th scope="col" className="fin-hide-sm">#</th>
              <th scope="col">Semester</th>
              <th scope="col">School Year</th>
              <th scope="col">Org Fee Balance</th>
              <th scope="col">Paid Amount</th>
              <th scope="col">Status</th>
              <th scope="col">To Pay</th>
            </tr>
          </thead>
          <tbody>
            {fees.length === 0 ? (
              <tr><td colSpan={7} className="fin-empty-cell">No unpaid fees. You’re all settled.</td></tr>
            ) : (
              fees.map((fee, index) => {
                const balance = Math.max(fee.required_amount - fee.paid_amount, 0);
                const tone = balance <= 0 ? 'is-ok' : fee.paid_amount > 0 ? 'is-warn' : 'is-bad';
                return (
                  <tr key={fee.full_amount_id}>
                    <td className="dash-mono dash-td-m fin-hide-sm">{index + 1}</td>
                    <td className="dash-td-m"><strong>{semShort(fee.semester)}</strong></td>
                    <td className="dash-mono dash-td-m">{fee.school_year}</td>
                    <td className={`dash-mono fin-money ${tone}`}>{formatPeso(balance)}</td>
                    <td className="dash-mono">{formatPeso(fee.paid_amount)}</td>
                    <td><StatusBadge status={fee.status} /></td>
                    <td>
                      <button
                        type="button"
                        className="fin-icon-btn is-pay"
                        title="How to pay"
                        aria-label={`How to pay ${fee.school_year} ${semShort(fee.semester)} semester`}
                        onClick={() => onPay(fee)}
                      >
                        <HelpIcon width={14} height={14} />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
