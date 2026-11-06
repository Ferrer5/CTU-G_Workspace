interface ConfirmDeleteModalProps {
  open: boolean;
  message: string;
}

export default function ConfirmDeleteModal({ open, message }: ConfirmDeleteModalProps) {
  if (!open) return null;
  return (
    <div className="fin-portal">
      <div className="fin-backdrop" />
      <div className="fin-dialog">
        <h3 className="fin-dialog-title">Confirm delete</h3>
        <p className="fin-dialog-text">{message}</p>
      </div>
    </div>
  );
}
