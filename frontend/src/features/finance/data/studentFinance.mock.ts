import type { StudentFinanceData } from '../types';

// Sample values only, used while USE_MOCK is true in financeService.ts.
export const studentFinanceMock: StudentFinanceData = {
  fees: [
    { full_amount_id: 1, semester: 'First', school_year: '2025-2026', required_amount: 500, paid_amount: 500, status: 'Paid' },
    { full_amount_id: 2, semester: 'Second', school_year: '2025-2026', required_amount: 500, paid_amount: 300, status: 'Partial' },
    { full_amount_id: 3, semester: 'First', school_year: '2026-2027', required_amount: 500, paid_amount: 0, status: 'Pending' },
  ],
  payments: [
    {
      payment_id: 1, receipt_number: '25-01-0007', semester: 'First', school_year: '2025-2026',
      amount: 500, status: 'Paid', received_by: 'Maria Santos', payment_date: '2025-09-18T09:30:00+08:00',
      year_level_at_payment: 1, section_at_payment: 'A',
    },
    {
      payment_id: 2, receipt_number: '26-02-0011', semester: 'Second', school_year: '2025-2026',
      amount: 300, status: 'Partial', received_by: 'Maria Santos', payment_date: '2026-02-10T14:05:00+08:00',
      year_level_at_payment: 1, section_at_payment: 'A',
    },
  ],
};
