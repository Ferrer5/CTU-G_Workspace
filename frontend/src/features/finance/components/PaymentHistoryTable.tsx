import { ReceiptIcon } from '../../../components/common/DashboardIcons';
import type { PaymentRecord } from '../types';
import { formatDate, formatPeso, semShort } from '../utils/format';
import StatusBadge from './StatusBadge';

interface PaymentHistoryTableProps {
  payments: PaymentRecord[];
  canViewReceipts: boolean;
  onViewReceipt: (payment: PaymentRecord) => void;
}

export default function PaymentHistoryTable({ payments, canViewReceipts, onViewReceipt }: PaymentHistoryTableProps) {
  const columnCount = canViewReceipts ? 8 : 7;
  const label = `${payments.length} record${payments.length === 1 ? '' : 's'}`;

  return (
    <section className="dash-card" aria-labelledby="fin-history-title">
      <div className="dash-card-hdr">
        <h2 className="dash-card-title" id="fin-history-title">All Transactions</h2>
        <span className="dash-badge dash-badge-ok">{label}</span>
      </div>
      <div className="dash-tbl-wrap fin-scroll">
        <table className="dash-table">
          <thead>
            <tr>
              <th scope="col" className="fin-hide-sm">#</th>
              <th scope="col">Semester</th>
              <th scope="col">School Year</th>
              <th scope="col">Paid Amount</th>
              <th scope="col">Status</th>
              <th scope="col">Received By</th>
              <th scope="col">Date of Payment</th>
              {canViewReceipts && <th scope="col">Receipt</th>}
            </tr>
          </thead>
          <tbody>
            {payments.length === 0 ? (
              <tr><td colSpan={columnCount} className="fin-empty-cell">No payment history available.</td></tr>
            ) : (
              payments.map((payment, index) => (
                <tr key={payment.payment_id}>
                  <td className="dash-mono dash-td-m fin-hide-sm">{index + 1}</td>
                  <td className="dash-td-m"><strong>{semShort(payment.semester)}</strong></td>
                  <td className="dash-mono dash-td-m">{payment.school_year}</td>
                  <td className="dash-mono">{formatPeso(payment.amount)}</td>
                  <td><StatusBadge status={payment.status} /></td>
                  <td className="dash-td-m">{payment.received_by || '—'}</td>
                  <td className="dash-mono dash-td-m">{formatDate(payment.payment_date)}</td>
                  {canViewReceipts && (
                    <td>
                      <button
                        type="button"
                        className="fin-icon-btn is-receipt"
                        title="View receipt"
                        aria-label={`View receipt ${payment.receipt_number ?? ''}`.trim()}
                        onClick={() => onViewReceipt(payment)}
                      >
                        <ReceiptIcon width={14} height={14} />
                      </button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
