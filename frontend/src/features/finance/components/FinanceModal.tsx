import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface FinanceModalProps {
  open: boolean;
  onClose: () => void;
  label: string;
  children: ReactNode;
}

/** Portal modal: closes on Escape and backdrop click. Rendered on document.body so it can be printed alone. */
export default function FinanceModal({ open, onClose, label, children }: FinanceModalProps) {
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="fin-portal" role="dialog" aria-modal="true" aria-label={label}>
      <button type="button" className="fin-backdrop" aria-label="Close dialog" onClick={onClose} />
      <div className="fin-modal-inner">{children}</div>
    </div>,
    document.body,
  );
}
