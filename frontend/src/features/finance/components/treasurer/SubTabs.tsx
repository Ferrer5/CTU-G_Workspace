interface SubTabItem<T extends string> {
  id: T;
  label: string;
}

interface SubTabsProps<T extends string> { tabs: SubTabItem<T>[]; active: T; onChange: (id: T) => void; }

export default function SubTabs<T extends string>({ tabs, active, onChange }: SubTabsProps<T>) {
  return (
    <div className="fin-tablist" role="tablist">
      {tabs.map((tab) => (
        <button key={tab.id} type="button" role="tab" aria-selected={active === tab.id} className={`fin-tab ${active === tab.id ? 'is-active' : ''}`} onClick={() => onChange(tab.id)}>
          {tab.label}
        </button>
      ))}
    </div>
  );
}
