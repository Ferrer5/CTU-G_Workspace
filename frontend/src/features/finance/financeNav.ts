import { createElement, type ComponentType, type SVGProps } from 'react';
import { PERMISSIONS } from '../../permissions';

export interface FinanceNavItem {
  label: string;
  path: string;
  permissions: readonly string[];
  Icon: ComponentType<SVGProps<SVGSVGElement>>;
}

const makeIcon = (paths: string[]) => (props: SVGProps<SVGSVGElement>) =>
  createElement(
    'svg',
    {
      ...props,
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      strokeWidth: 1.8,
      strokeLinecap: 'round',
      strokeLinejoin: 'round',
      'aria-hidden': true,
    },
    ...paths.map((d) => createElement('path', { key: d, d })),
  );

const FinanceIcon = makeIcon(['M4 19V9', 'M10 19V5', 'M16 19v-7', 'M22 19V3']);
const CollectIcon = makeIcon(['M12 2v20', 'M17 5H9.5a3.5 3.5 0 0 0 0 7H14.5a3.5 3.5 0 0 1 0 7H6']);
const ExpenseIcon = makeIcon(['M7 7h10v10H7z', 'M7 12h10', 'M12 7v10']);
const HistoryIcon = makeIcon(['M3 12a9 9 0 1 0 3-6.7', 'M3 3v6h6', 'M12 7v5l3 2']);
const ReportIcon = makeIcon(['M7 3h8l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z', 'M15 3v5h5', 'M8 13h8M8 17h6']);
const SettingsIcon = makeIcon(['M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V20a2 2 0 1 1-4 0v-.2A1.7 1.7 0 0 0 9 18.4a1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H4a2 2 0 1 1 0-4h.2A1.7 1.7 0 0 0 5.6 9a1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.7 1.7 0 0 0 18.4 9a1.7 1.7 0 0 0 1.5 1H20a2 2 0 1 1 0 4h-.2a1.7 1.7 0 0 0-1.5 1Z']);

export const financeNavItems: FinanceNavItem[] = [
  { label: 'Overview', path: '/dashboard/finance', permissions: [PERMISSIONS.financeDashboardView], Icon: FinanceIcon },
  { label: 'Collect', path: '/dashboard/finance/collect', permissions: [PERMISSIONS.financePaymentCreate, PERMISSIONS.financeOtherFundCreate], Icon: CollectIcon },
  { label: 'Expenses', path: '/dashboard/finance/expenses', permissions: [PERMISSIONS.financeExpenseView], Icon: ExpenseIcon },
  { label: 'History', path: '/dashboard/finance/history', permissions: [PERMISSIONS.financePaymentViewAll], Icon: HistoryIcon },
  { label: 'Reports', path: '/dashboard/finance/reports', permissions: [PERMISSIONS.financeReportView], Icon: ReportIcon },
  { label: 'Settings', path: '/dashboard/finance/settings', permissions: [PERMISSIONS.financeSchoolYearView, PERMISSIONS.financeFeeView, PERMISSIONS.financeExemptionView, PERMISSIONS.financeSignatureManageOwn], Icon: SettingsIcon },
];
