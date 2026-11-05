import { apiGet } from '../../../services/apiClient';
import { studentFinanceMock } from '../data/studentFinance.mock';
import type { PaymentRecord, SemesterFee, StudentFinanceData } from '../types';

/** Flip to false once GET /api/finance/me/ exists on the backend. */
const USE_MOCK = true;
export const IS_SAMPLE_DATA = USE_MOCK;

// Django DecimalField values are serialized as strings by DRF.
type Money = number | string;
interface RawFee extends Omit<SemesterFee, 'required_amount' | 'paid_amount'> {
  required_amount: Money;
  paid_amount: Money;
}
interface RawPayment extends Omit<PaymentRecord, 'amount'> {
  amount: Money;
}
interface RawFinanceData {
  fees: RawFee[];
  payments: RawPayment[];
}

export async function fetchStudentFinance(): Promise<StudentFinanceData> {
  if (USE_MOCK) return studentFinanceMock;

  const raw = await apiGet<RawFinanceData>('/finance/me/');
  return {
    fees: raw.fees.map((fee) => ({
      ...fee,
      required_amount: Number(fee.required_amount),
      paid_amount: Number(fee.paid_amount),
    })),
    payments: raw.payments.map((payment) => ({ ...payment, amount: Number(payment.amount) })),
  };
}
