import { CloseIcon } from '../../../components/common/DashboardIcons';
import type { SemesterFee } from '../types';
import { formatPeso, semShort } from '../utils/format';
import FinanceModal from './FinanceModal';

interface PayInfoModalProps {
  fee: SemesterFee | null;
  onClose: () => void;
}

export default function PayInfoModal({ fee, onClose }: PayInfoModalProps) {
  const balance = fee ? Math.max(fee.required_amount - fee.paid_amount, 0) : 0;

  return (
    <FinanceModal open={fee !== null} onClose={onClose} label="How to pay">
      {fee && (
        <div className="fin-dialog">
          <div className="fin-dialog-hdr">
            <div>
              <h2 className="fin-dialog-title">Pay Fee</h2>
              <p className="fin-dialog-sub">{fee.school_year} · {semShort(fee.semester)} Semester</p>
            </div>
            <button type="button" className="fin-close-btn" aria-label="Close" onClick={onClose}>
              <CloseIcon width={16} height={16} />
            </button>
          </div>
          <div className="fin-balance-box">
            <span className="fin-balance-lbl">Org Fee Balance</span>
            <strong className="fin-balance-val">{formatPeso(balance)}</strong>
          </div>
          <p className="fin-dialog-text">
            To process your payment, please proceed to the SSG Finance office with this information.
            Online payment integration is coming soon.
          </p>
          <div className="fin-dialog-actions">
            <button type="button" className="fin-ghost-btn" onClick={onClose}>Close</button>
          </div>
        </div>
      )}
    </FinanceModal>
  );
}
