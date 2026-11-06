export default function OtherFundForm() {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>Other Fund</h3>
      <div className="fin-form-grid">
        <div className="fin-field"><label className="fin-label">Source</label><input className="fin-input" /></div>
        <div className="fin-field"><label className="fin-label">Category</label><select className="fin-select"><option>Revenue</option></select></div>
      </div>
    </div>
  );
}
