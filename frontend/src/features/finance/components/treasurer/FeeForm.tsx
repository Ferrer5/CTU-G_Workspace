export default function FeeForm() {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>Fee</h3>
      <div className="fin-form-grid">
        <div className="fin-field"><label className="fin-label">Year</label><input className="fin-input" /></div>
        <div className="fin-field"><label className="fin-label">Amount</label><input className="fin-input" type="number" /></div>
      </div>
    </div>
  );
}
