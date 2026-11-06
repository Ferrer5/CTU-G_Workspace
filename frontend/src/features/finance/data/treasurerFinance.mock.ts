import type {
  ExemptionRecord,
  ExpenseRecord,
  FeeRecord,
  FinanceReport,
  OtherFundRecord,
  SchoolYearRecord,
  SignatureRecord,
  TreasurerFinanceData,
  TreasurerPayment,
  TreasurerStudentRow,
} from '../types';

const students: TreasurerStudentRow[] = [
  { user_id: 101, school_id: '2024-001', name: 'Marian Cruz', course_code: 'BSIT', year: 2, section: 'A', required: 4500, paid: 3200, balance: 1300, status: 'Partial' },
  { user_id: 102, school_id: '2024-002', name: 'Rafael Dela Cruz', course_code: 'BSCS', year: 3, section: 'B', required: 4500, paid: 4500, balance: 0, status: 'Paid' },
  { user_id: 103, school_id: '2024-003', name: 'Alyssa Santos', course_code: 'BSA', year: 1, section: 'C', required: 4500, paid: 0, balance: 4500, status: 'Unpaid' },
  { user_id: 104, school_id: '2024-004', name: 'Noah Tan', course_code: 'BSEd', year: 4, section: 'A', required: 4500, paid: 1700, balance: 2800, status: 'Partial' },
];

const payments: TreasurerPayment[] = [
  {
    payment_id: 1001,
    receipt_number: 'ORG-2024-001',
    semester: 'First',
    school_year: '2024-2025',
    amount: 3200,
    status: 'Partial',
    received_by: 'Treasurer Office',
    payment_date: '2024-09-10',
    year_level_at_payment: 2,
    section_at_payment: 'A',
    user_id: 101,
    student_name: 'Marian Cruz',
    school_id: '2024-001',
    course_code: 'BSIT',
    full_amount_id: 201,
    recorded_by_school_id: 'T-1001',
    created_at: '2024-09-10T08:15:00.000Z',
  },
  {
    payment_id: 1002,
    receipt_number: 'ORG-2024-002',
    semester: 'First',
    school_year: '2024-2025',
    amount: 4500,
    status: 'Paid',
    received_by: 'Treasurer Office',
    payment_date: '2024-09-12',
    year_level_at_payment: 3,
    section_at_payment: 'B',
    user_id: 102,
    student_name: 'Rafael Dela Cruz',
    school_id: '2024-002',
    course_code: 'BSCS',
    full_amount_id: 202,
    recorded_by_school_id: 'T-1002',
    created_at: '2024-09-12T09:20:00.000Z',
  },
];

const otherFunds: OtherFundRecord[] = [
  {
    fund_id: 301,
    source: 'Student Council',
    description: 'Leadership fundraiser',
    category: 'Fundraising',
    amount: 12500,
    received_by: 'Office',
    recorded_by_school_id: 'T-1001',
    received_date: '2024-09-14',
    created_at: '2024-09-14T09:00:00.000Z',
  },
];

const expenses: ExpenseRecord[] = [
  {
    expense_id: 401,
    description: 'Supply raffle prizes',
    amount: 3200,
    recorded_by: 'Treasurer',
    recorded_by_school_id: 'T-1001',
    expense_date: '2024-09-18',
    created_at: '2024-09-18T12:50:00.000Z',
    images: [],
  },
  {
    expense_id: 402,
    description: 'Event signage',
    amount: 1800,
    recorded_by: 'Treasurer',
    recorded_by_school_id: 'T-1002',
    expense_date: '2024-09-20',
    created_at: '2024-09-20T15:00:00.000Z',
    images: [],
  },
];

const schoolYears: SchoolYearRecord[] = [
  { period_id: 1, year_start: 2024, year_end: 2025, status: 'Current', first_start: '2024-08-01', first_end: '2024-12-15', second_start: '2025-01-15', second_end: '2025-05-30' },
];

const fees: FeeRecord[] = [
  { full_amount_id: 201, school_year: '2024-2025', semester: 'First', amount: 4500, status: 'Current' },
  { full_amount_id: 202, school_year: '2024-2025', semester: 'Second', amount: 4500, status: 'Current' },
];

const exemptions: ExemptionRecord[] = [
  { exemption_id: 501, user_id: 104, school_year: '2024-2025', semester: 'First' },
];

const signatures: SignatureRecord[] = [
  { signature_id: 601, school_id: 'T-1001', treasurer_name: 'Treasurer Office', created_at: '2024-09-01T10:00:00.000Z', is_active: true, signature_data: 'sample-signature' },
];

const reports: FinanceReport[] = [
  {
    report_id: 701,
    report_type: 'Semester',
    title: 'September Summary',
    school_year: '2024-2025',
    date_from: '2024-09-01',
    date_to: '2024-09-30',
    status: 'Draft',
    beginning_balance: 120000,
    total_revenue: 24500,
    total_expenses: 6200,
    running_balance: 128300,
    created_by: 'Treasurer Office',
    created_at: '2024-09-30T12:00:00.000Z',
    items: [
      { item_type: 'OrgFee', description: 'Student org fee collections', amount: 24500 },
      { item_type: 'Expense', description: 'Event signage', amount: 6200 },
    ],
  },
];

export const treasurerFinanceMock: TreasurerFinanceData = {
  students,
  payments,
  otherFunds,
  expenses,
  schoolYears,
  fees,
  exemptions,
  signatures,
  reports,
};
