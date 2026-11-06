import { useState } from 'react';
import '../../../../css/finance-treasurer.css';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import usePermissions from '../../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../../permissions';

export default function CollectPage() {
  const { hasPermission } = usePermissions();
  const [activeTab, setActiveTab] = useState<'org' | 'other'>('org');

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="Record Payment" subtitle="Capture student collections and other fund entries." />
      <div className="fin-tablist" role="tablist" aria-label="Payment options">
        <button className={`fin-tab ${activeTab === 'org' ? 'is-active' : ''}`} type="button" role="tab" aria-selected={activeTab === 'org'} onClick={() => setActiveTab('org')}>
          Org Fee payment
        </button>
        <button className={`fin-tab ${activeTab === 'other' ? 'is-active' : ''}`} type="button" role="tab" aria-selected={activeTab === 'other'} onClick={() => setActiveTab('other')}>
          Other Fund
        </button>
      </div>

      {activeTab === 'org' ? (
        <div className="fin-card">
          <div className="fin-form-grid">
            <div className="fin-field">
              <label className="fin-label">Student</label>
              <input className="fin-input" defaultValue="Marian Cruz" />
            </div>
            <div className="fin-field">
              <label className="fin-label">School Year</label>
              <select className="fin-select" defaultValue="2024-2025">
                <option value="2024-2025">2024-2025</option>
              </select>
            </div>
            <div className="fin-field">
              <label className="fin-label">Amount Paid</label>
              <input className="fin-input" type="number" defaultValue="1500" />
            </div>
            <div className="fin-field">
              <label className="fin-label">Receipt Number</label>
              <input className="fin-input" defaultValue="ORG-2024-014" />
            </div>
          </div>
          <div className="fin-summary">
            <div className="fin-muted">Status: Partial</div>
            {hasPermission(PERMISSIONS.financePaymentCreate) ? <button type="button" className="fin-btn">Save</button> : <button type="button" className="fin-btn-secondary" disabled>Save</button>}
          </div>
        </div>
      ) : (
        <div className="fin-card">
          <div className="fin-form-grid">
            <div className="fin-field">
              <label className="fin-label">Source</label>
              <input className="fin-input" defaultValue="Student Council" />
            </div>
            <div className="fin-field">
              <label className="fin-label">Category</label>
              <select className="fin-select" defaultValue="Fundraising">
                <option>Revenue</option>
                <option>Donation</option>
                <option>Grant</option>
                <option>Fundraising</option>
                <option>Event Proceeds</option>
                <option>Sponsorship</option>
                <option>Other</option>
              </select>
            </div>
            <div className="fin-field" style={{ gridColumn: '1 / -1' }}>
              <label className="fin-label">Description</label>
              <textarea className="fin-textarea" defaultValue="Campus sustainability campaign" />
            </div>
            <div className="fin-field">
              <label className="fin-label">Amount</label>
              <input className="fin-input" type="number" defaultValue="25000" />
            </div>
            <div className="fin-field">
              <label className="fin-label">Date Received</label>
              <input className="fin-input" type="date" defaultValue="2024-09-15" />
            </div>
          </div>
          <div className="fin-summary">
            <div className="fin-muted">Other funds are posted to the monthly overview.</div>
            {hasPermission(PERMISSIONS.financeOtherFundCreate) ? <button type="button" className="fin-btn">Save</button> : <button type="button" className="fin-btn-secondary" disabled>Save</button>}
          </div>
        </div>
      )}
    </section>
  );
}
