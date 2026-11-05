import type { FormEvent } from 'react';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';

interface VerifyEmailPageProps {
  email: string;
  code: string;
  onCodeChange: (value: string) => void;
  error: string | null;
  notice: string | null;
  loading: boolean;
  resendIn: number;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onResend: () => void;
  onBack: () => void;
}

export default function VerifyEmailPage({
  email,
  code,
  onCodeChange,
  error,
  notice,
  loading,
  resendIn,
  onSubmit,
  onResend,
  onBack,
}: VerifyEmailPageProps) {
  return (
    <>
      <h1 className="fg-strong text-xl font-semibold sm:text-2xl">Verify Your Email</h1>
      <p className="fg-muted mt-1 text-xs">
        A 6-digit code was sent to <strong className="fg-strong">{email}</strong>. Enter it below.
      </p>

      <form onSubmit={onSubmit} noValidate className="mt-5 space-y-4">
        <Input
          label="Verification Code"
          id="reg-code"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          placeholder="Enter 6-digit code"
          value={code}
          error={error ?? undefined}
          onChange={(event) => onCodeChange(event.target.value)}
        />
        {notice && <p className="fg-accent text-xs">{notice}</p>}
        <Button type="submit" fullWidth loading={loading}>
          {loading ? 'Please wait…' : 'Verify & Create Account'}
        </Button>
      </form>

      <p className="fg-muted mt-5 text-center text-xs">
        Didn’t receive a code?{' '}
        <button
          type="button"
          onClick={onResend}
          disabled={resendIn > 0 || loading}
          className="link-accent font-medium disabled:cursor-not-allowed disabled:no-underline disabled:opacity-60"
        >
          {resendIn > 0 ? `Resend (${resendIn}s)` : 'Resend'}
        </button>{' '}
        ·{' '}
        <button type="button" onClick={onBack} className="link-muted font-medium">
          Back
        </button>
      </p>
    </>
  );
}
