interface EditWindowBadgeProps {
  isOpen: boolean;
}

export default function EditWindowBadge({ isOpen }: EditWindowBadgeProps) {
  return (
    <span className="fin-badge-card" title={isOpen ? 'Can be edited within the allowed window.' : 'Edit window has expired.'}>
      {isOpen ? 'Editable' : 'Locked'}
    </span>
  );
}
