const peso = new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' });

export const formatPeso = (amount: number) => peso.format(amount);

export function formatDate(iso: string | null): string {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('en-PH', { month: 'short', day: '2-digit', year: 'numeric' }).format(date);
}

export function formatReceiptDate(iso: string | null): string {
  const date = iso ? new Date(iso) : new Date();
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('en-PH', { month: '2-digit', day: '2-digit', year: '2-digit' }).format(date);
}

/** "First" -> "1st", "Second" -> "2nd". */
export function semShort(semester: string | null | undefined): string {
  if (!semester?.trim()) return '-';
  const value = semester.trim().toLowerCase();
  if (value.startsWith('first') || value.startsWith('1')) return '1st';
  if (value.startsWith('second') || value.startsWith('2')) return '2nd';
  return semester;
}

/** Year level 5 means the 4-year program is completed. */
export function formatYearSection(year: string, section: string): string {
  return year === '5' ? '4 Completed' : `${year}${section}`;
}

const ONES = [
  '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
  'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen',
];
const TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];

function say(n: number): string {
  if (n < 20) return ONES[n];
  if (n < 100) return TENS[Math.floor(n / 10)] + (n % 10 ? ` ${ONES[n % 10]}` : '');
  if (n < 1000) return `${ONES[Math.floor(n / 100)]} Hundred${n % 100 ? ` ${say(n % 100)}` : ''}`;
  if (n < 1_000_000) return `${say(Math.floor(n / 1000))} Thousand${n % 1000 ? ` ${say(n % 1000)}` : ''}`;
  return String(n);
}

export function amountToWords(amount: number): string {
  const total = Math.round(amount * 100);
  const pesos = Math.floor(total / 100);
  const cents = total % 100;
  if (pesos === 0 && cents === 0) return 'Zero Pesos Only';
  const parts: string[] = [];
  if (pesos > 0) parts.push(`${say(pesos)} Peso${pesos === 1 ? '' : 's'}`);
  if (cents > 0) parts.push(`${say(cents)} Centavo${cents === 1 ? '' : 's'}`);
  return `${parts.join(' and ')} Only`;
}
