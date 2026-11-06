import { treasurerFinanceMock } from '../data/treasurerFinance.mock';
import type { TreasurerFinanceData } from '../types';

const USE_MOCK_TREASURER = true;
export const IS_SAMPLE_TREASURER_DATA = USE_MOCK_TREASURER;

type Money = number | string;

export async function fetchTreasurerFinance(): Promise<TreasurerFinanceData> {
  if (USE_MOCK_TREASURER) return treasurerFinanceMock;
  return treasurerFinanceMock;
}

export function getTreasurerFinanceData(): Promise<TreasurerFinanceData> {
  return fetchTreasurerFinance().then(
    (data): TreasurerFinanceData => ({
      ...data,
      students: data.students.map((student) => ({
        ...student,
        required: Number(student.required),
        paid: Number(student.paid),
        balance: Number(student.balance),
      })),
      payments: data.payments.map((payment) => ({
        ...payment,
        amount: Number(payment.amount),
      })),
      otherFunds: data.otherFunds.map((record) => ({
        ...record,
        amount: Number(record.amount),
      })),
      expenses: data.expenses.map((expense) => ({
        ...expense,
        amount: Number(expense.amount),
      })),
      fees: data.fees.map((fee) => ({
        ...fee,
        amount: Number(fee.amount),
      })),
      reports: data.reports.map((report) => ({
        ...report,
        beginning_balance: Number(report.beginning_balance),
        total_revenue: Number(report.total_revenue),
        total_expenses: Number(report.total_expenses),
        running_balance: Number(report.running_balance),
        items: report.items.map((item) => ({
          ...item,
          amount: Number(item.amount),
        })),
      })),
    }),
  );
}

export function convertMoneyValue(value: Money): number {
  return typeof value === 'number' ? value : Number(value);
}
