export type FinanceTab = 'overview' | 'fees' | 'history';

interface FinanceTabsProps {
  active: FinanceTab;
  onChange: (tab: FinanceTab) => void;
  pendingCount: number;
  paymentCount: number;
}

export default function FinanceTabs({ active, onChange, pendingCount, paymentCount }: FinanceTabsProps) {
  const tabs: { id: FinanceTab; label: string; count?: number }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'fees', label: 'Current Fees', count: pendingCount },
    { id: 'history', label: 'Payment History', count: paymentCount },
  ];

  return (
    <div className="fin-tabs" role="tablist" aria-label="Finance sections">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          id={`fin-tab-${tab.id}`}
          aria-selected={active === tab.id}
          aria-controls={`fin-panel-${tab.id}`}
          className={`fin-tab ${active === tab.id ? 'is-active' : ''}`}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
          {tab.count !== undefined && <span className="fin-tab-count">{tab.count}</span>}
        </button>
      ))}
    </div>
  );
}
