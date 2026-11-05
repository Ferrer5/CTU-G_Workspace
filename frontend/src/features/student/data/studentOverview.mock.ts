export interface StudentOverviewStat {
  label: string;
  value: string;
  trend: string;
  tone: 'good' | 'warn' | 'bad';
}

export interface StudentPaymentMock {
  item: string;
  amount: string;
  date: string;
  status: 'Paid' | 'Pending';
}

// Sample finance values only; no finance backend is connected.
export const studentOverviewStats: StudentOverviewStat[] = [
  { label: 'Org Fee Balance', value: '₱1,250.00', trend: 'Amount due', tone: 'warn' },
  { label: 'Paid This School Year', value: '₱3,750.00', trend: 'Sample figures', tone: 'good' },
  { label: 'Upcoming Assessment', value: '₱500.00', trend: 'Sample amount', tone: 'bad' },
];

export const studentPaymentsMock: StudentPaymentMock[] = [
  { item: 'Organization Fee', amount: '₱500.00', date: '2026-10-28', status: 'Paid' },
  { item: 'SSG Contribution', amount: '₱1,000.00', date: '2026-10-15', status: 'Paid' },
  { item: 'Campus Activity Fee', amount: '₱500.00', date: '2026-09-30', status: 'Pending' },
];
