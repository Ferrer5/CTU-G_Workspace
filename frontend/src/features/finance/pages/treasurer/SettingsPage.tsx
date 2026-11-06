import { useState } from 'react';
import '../../../../css/finance-treasurer.css';
import DashboardHeader from '../../../dashboard/components/DashboardHeader';
import usePermissions from '../../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../../permissions';

export default function SettingsPage() {
  const { hasPermission } = usePermissions();
  const [activeTab, setActiveTab] = useState<'school-years' | 'fees' | 'exemptions' | 'signature'>('school-years');

  const schoolYearsAllowed = hasPermission(PERMISSIONS.financeSchoolYearView);
  const feesAllowed = hasPermission(PERMISSIONS.financeFeeView);
  const exemptionAllowed = hasPermission(PERMISSIONS.financeExemptionView);
  const signatureAllowed = hasPermission(PERMISSIONS.financeSignatureManageOwn);

  const tabs = [
    schoolYearsAllowed ? { id: 'school-years', label: 'School Years' } : null,
    feesAllowed ? { id: 'fees', label: 'Fees' } : null,
    exemptionAllowed ? { id: 'exemptions', label: 'Exemptions & Payment Start' } : null,
    signatureAllowed ? { id: 'signature', label: 'Signature' } : null,
  ].filter(Boolean) as Array<{ id: 'school-years' | 'fees' | 'exemptions' | 'signature'; label: string }>;

  if (tabs.length === 0) {
    return <section className="dash-page"><div className="dash-card"><p className="dash-empty">No settings tabs are available for your current permissions.</p></div></section>;
  }

  return (
    <section className="dash-page fin-workspace">
      <DashboardHeader title="Settings" subtitle="Manage finance configuration and signatures." />
      <div className="fin-tablist" role="tablist" aria-label="Finance settings tabs">
        {tabs.map((tab) => (
          <button key={tab.id} className={`fin-tab ${activeTab === tab.id ? 'is-active' : ''}`} type="button" role="tab" aria-selected={activeTab === tab.id} onClick={() => setActiveTab(tab.id)}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'school-years' && (
        <div className="fin-card">
          <div className="fin-summary">
            <div className="fin-muted">School year settings</div>
            {hasPermission(PERMISSIONS.financeSchoolYearCreate) && <button type="button" className="fin-btn">Add</button>}
          </div>
          <table className="fin-table">
            <thead><tr><th>Academic Year</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr><td>2024-2025</td><td>Current</td><td className="fin-muted">Edit / Delete</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'fees' && (
        <div className="fin-card">
          <div className="fin-summary">
            <div className="fin-muted">Fee schedules</div>
            {hasPermission(PERMISSIONS.financeFeeSetAmount) && <button type="button" className="fin-btn">Set Amount</button>}
          </div>
          <table className="fin-table">
            <thead><tr><th>School year</th><th>Semester</th><th>Amount</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td>2024-2025</td><td>First</td><td>₱4,500</td><td>Current</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'exemptions' && (
        <div className="fin-card">
          <div className="fin-summary">
            <div className="fin-muted">Exemptions and payment start</div>
            {hasPermission(PERMISSIONS.financeExemptionAdd) && <button type="button" className="fin-btn">Add Exemption</button>}
          </div>
          <table className="fin-table">
            <thead><tr><th>Student</th><th>Semester</th><th>Action</th></tr></thead>
            <tbody>
              <tr><td>Noah Tan</td><td>First</td><td className="fin-muted">Remove</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'signature' && (
        <div className="fin-card">
          <div className="fin-summary">
            <div className="fin-muted">Treasurer signature</div>
            {hasPermission(PERMISSIONS.financeSignatureManageOwn) && <button type="button" className="fin-btn">Save Signature</button>}
          </div>
          <p className="fin-muted">Signature capture and history are available to the signing treasurer.</p>
        </div>
      )}
    </section>
  );
}
