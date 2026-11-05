import { useNavigate } from 'react-router-dom';
import Button from '../../components/common/Button';

export default function RequestStatusPage() {
  const navigate = useNavigate();

  return (
    <div className="text-center">
      <div className="chip-accent mx-auto flex h-14 w-14 items-center justify-center rounded-full">
        <svg
          className="fg-accent h-7 w-7"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 className="fg-strong mt-5 text-xl font-semibold sm:text-2xl">Registration Submitted</h1>
      <p className="fg-body mt-2 text-sm">
        Your account is pending approval by an administrator. You will be able to sign in once it is approved.
      </p>
      <Button className="mt-6" fullWidth onClick={() => navigate('/')}>
        Back to Home
      </Button>
    </div>
  );
}
