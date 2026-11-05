export type FeeStatus = 'Paid' | 'Partial' | 'Pending' | 'Overdue';
export type PaymentStatus = 'Paid' | 'Partial';

/** One semester's org fee for the signed-in student. */
export interface SemesterFee {
  full_amount_id: number;
  semester: string;
  school_year: string;
  required_amount: number;
  paid_amount: number;
  status: FeeStatus;
}

/** One payment transaction (maps to org_fee_payments + receipts). */
export interface PaymentRecord {
  payment_id: number;
  receipt_number: string | null;
  semester: string;
  school_year: string;
  amount: number;
  status: PaymentStatus;
  received_by: string | null;
  payment_date: string | null;
  year_level_at_payment: number | null;
  section_at_payment: string | null;
}

export interface StudentFinanceData {
  fees: SemesterFee[];
  payments: PaymentRecord[];
}
