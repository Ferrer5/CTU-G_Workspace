import { CloseIcon, PrinterIcon } from '../../../components/common/DashboardIcons';
import { CAMPUS_NAME } from '../../../utils/constants';
import type { PaymentRecord } from '../types';
import { amountToWords, formatPeso, formatReceiptDate, formatYearSection } from '../utils/format';
import FinanceModal from './FinanceModal';

export interface ReceiptStudent {
  name: string;
  schoolId: string;
  courseCode: string;
  yearSection: string;
}

interface ReceiptModalProps {
  payment: PaymentRecord | null;
  student: ReceiptStudent;
  onClose: () => void;
}

function Field({ label, children }: { label: string; children: string }) {
  return (
    <div className="fin-rp-field">
      <span className="fin-rp-label">{label}</span>
      <span className="fin-rp-value">{children || '—'}</span>
    </div>
  );
}

export default function ReceiptModal({ payment, student, onClose }: ReceiptModalProps) {
  const handlePrint = () => {
    if (!payment) return;
    const previousTitle = document.title;
    const safeName = student.name.trim().replace(/\s+/g, '_');
    document.title = `${safeName}_${payment.receipt_number ?? 'receipt'}`;
    window.print();
    document.title = previousTitle;
  };

  // Use the year/section captured at payment time so old receipts never change as the student advances.
  const yearSection =
    payment && payment.year_level_at_payment !== null
      ? formatYearSection(String(payment.year_level_at_payment), payment.section_at_payment ?? '')
      : student.yearSection;
  const course = [student.courseCode, yearSection].filter(Boolean).join(' - ');

  return (
    <FinanceModal open={payment !== null} onClose={onClose} label="Official receipt">
      {payment && (
        <>
          <div className="fin-receipt-controls">
            <span className="fin-receipt-title">
              Receipt — {payment.school_year} {payment.semester} Semester
            </span>
            <button type="button" className="fin-pdf-btn" onClick={handlePrint}>
              <PrinterIcon width={13} height={13} /> Print / Save PDF
            </button>
            <button type="button" className="fin-close-btn" aria-label="Close receipt" onClick={onClose}>
              <CloseIcon width={14} height={14} />
            </button>
          </div>

          <div className="fin-receipt-paper">
            <div className="fin-rp-header">
              <div className="fin-rp-org">SUPREME STUDENT GOVERNMENT</div>
              <div className="fin-rp-campus">{CAMPUS_NAME}</div>
              <hr className="fin-rp-divider" />
              <div className="fin-rp-type">Organization Fee</div>
              <div className="fin-rp-copy">(Owner’s Copy)</div>
            </div>

            <div className="fin-rp-meta">
              <div>
                <span className="fin-rp-meta-label">Receipt No. </span>
                <span className="fin-rp-meta-value is-red">{payment.receipt_number ?? '—'}</span>
              </div>
              <div>
                <span className="fin-rp-meta-label">Date </span>
                <span className="fin-rp-meta-value">{formatReceiptDate(payment.payment_date)}</span>
              </div>
            </div>

            <div className="fin-rp-section">Acknowledgement Receipt</div>

            <Field label="Name:">{student.name}</Field>
            <Field label="ID Number:">{student.schoolId}</Field>
            <Field label="Course/Year/Section:">{course}</Field>
            <Field label="S.Y.-Semester:">{`${payment.school_year} – ${payment.semester} Semester`}</Field>
            <Field label="Amount Paid:">{formatPeso(payment.amount)}</Field>
            <Field label="Amount in words:">{amountToWords(payment.amount)}</Field>
            <Field label="Status:">{payment.status}</Field>

            <div className="fin-rp-signature">
              <div className="fin-rp-sig-block">
                <div className="fin-rp-sig-label">Received by:</div>
                <div className="fin-rp-sig-line">
                  <span className="fin-rp-sig-name">{(payment.received_by ?? '—').toUpperCase()}</span>
                </div>
                <div className="fin-rp-sig-caption">(Signature over Printed Name)</div>
              </div>
            </div>
          </div>
        </>
      )}
    </FinanceModal>
  );
}
