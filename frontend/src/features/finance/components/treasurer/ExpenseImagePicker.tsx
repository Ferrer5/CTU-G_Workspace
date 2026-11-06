export default function ExpenseImagePicker() {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>Receipt Images</h3>
      <input type="file" multiple accept="image/png,image/jpeg,image/webp" />
    </div>
  );
}
