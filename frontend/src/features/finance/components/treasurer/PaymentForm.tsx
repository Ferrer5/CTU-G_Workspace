interface PaymentFormProps {
  title: string;
}

export default function PaymentForm({ title }: PaymentFormProps) {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>{title}</h3>
      <div className="fin-form-grid">
        <div className="fin-field"><label className="fin-label">Student</label><input className="fin-input" /></div>
        <div className="fin-field"><label className="fin-label">Amount</label><input className="fin-input" type="number" /></div>
      </div>
    </div>
  );
}
