interface BannerProps {
  type: 'error' | 'success';
  children: string;
}

export default function Banner({ type, children }: BannerProps) {
  return (
    <p
      role="alert"
      className={`mb-4 rounded-lg px-3 py-2 text-xs ${type === 'error' ? 'fg-error' : 'fg-accent'}`}
      style={{
        background:
          type === 'error' ? 'color-mix(in srgb, var(--fg-error) 12%, transparent)' : 'var(--accent-soft)',
      }}
    >
      {children}
    </p>
  );
}
