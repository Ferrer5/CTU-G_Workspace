interface PaymentStartModalProps {
  open: boolean;
}

export default function PaymentStartModal({ open }: PaymentStartModalProps) {
  if (!open) return null;
  return (
    <div className="fin-portal">
      <div className="fin-backdrop" />
      <div className="fin-dialog"><h3 className="fin-dialog-title">Payment start</h3><p className="fin-dialog-text">Configure the payment start date for the selected school year.</p></div>
    </div>
  );
}
