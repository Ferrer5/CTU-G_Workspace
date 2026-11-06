interface ReportCreateModalProps {
  open: boolean;
}

export default function ReportCreateModal({ open }: ReportCreateModalProps) {
  if (!open) return null;

  return (
    <div className="fin-portal">
      <div className="fin-backdrop" />
      <div className="fin-dialog">
        <h3 className="fin-dialog-title">Create report</h3>
        <p className="fin-dialog-text">This is a preview placeholder for the treasurer reporting modal.</p>
      </div>
    </div>
  );
}
