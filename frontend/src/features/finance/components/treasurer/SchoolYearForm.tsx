export default function SchoolYearForm() {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>School Year</h3>
      <div className="fin-form-grid">
        <div className="fin-field"><label className="fin-label">Year</label><input className="fin-input" /></div>
        <div className="fin-field"><label className="fin-label">Status</label><select className="fin-select"><option>Current</option><option>Ended</option></select></div>
      </div>
    </div>
  );
}
