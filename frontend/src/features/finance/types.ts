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

export type PayStatus = 'Paid' | 'Partial' | 'Unpaid' | 'Exempt';
export type SemesterName = 'First' | 'Second';
export type ActionResult = { ok: boolean; message: string };

export interface TreasurerStudent {
  user_id: number;
  school_id: string;
  name: string;
  course_code: string;
  year: number;
  section: string;
}

export interface TreasurerStudentRow extends TreasurerStudent {
  required: number;
  paid: number;
  balance: number;
  status: PayStatus;
}

export interface TreasurerPayment extends PaymentRecord {
  user_id: number;
  student_name: string;
  school_id: string;
  course_code: string;
  full_amount_id: number;
  recorded_by_school_id: string;
  created_at: string;
}

export interface OtherFundRecord {
  fund_id: number;
  source: string;
  description: string;
  category: string;
  amount: number;
  received_by: string;
  recorded_by_school_id: string;
  received_date: string;
  created_at: string;
}

export interface ExpenseRecord {
  expense_id: number;
  description: string;
  amount: number;
  recorded_by: string;
  recorded_by_school_id: string;
  expense_date: string;
  created_at: string;
  images: string[];
}

export interface SchoolYearRecord {
  period_id: number;
  year_start: number;
  year_end: number;
  status: 'Current' | 'Ended';
  first_start: string;
  first_end: string;
  second_start: string;
  second_end: string;
}

export interface FeeRecord {
  full_amount_id: number;
  school_year: string;
  semester: SemesterName;
  amount: number;
  status: 'Current' | 'Ended';
}

export interface ExemptionRecord {
  exemption_id: number;
  user_id: number;
  school_year: string;
  semester: SemesterName;
}

export interface PaymentStartRecord {
  school_year: string;
  semester: SemesterName;
}

export interface SignatureRecord {
  signature_id: number;
  school_id: string;
  treasurer_name: string;
  created_at: string;
  is_active: boolean;
  signature_data: string;
}

export type ReportType = 'Event' | 'Semester' | 'Annual';

export interface ReportItemRecord {
  item_type: 'OrgFee' | 'OtherFund' | 'Expense';
  description: string;
  amount: number;
}

export interface FinanceReport {
  report_id: number;
  report_type: ReportType;
  title: string;
  school_year: string;
  date_from: string;
  date_to: string;
  status: 'Draft' | 'Final';
  beginning_balance: number;
  total_revenue: number;
  total_expenses: number;
  running_balance: number;
  created_by: string;
  created_at: string;
  items: ReportItemRecord[];
}

export interface TreasurerFinanceData {
  students: TreasurerStudentRow[];
  payments: TreasurerPayment[];
  otherFunds: OtherFundRecord[];
  expenses: ExpenseRecord[];
  schoolYears: SchoolYearRecord[];
  fees: FeeRecord[];
  exemptions: ExemptionRecord[];
  signatures: SignatureRecord[];
  reports: FinanceReport[];
}
