import { useEffect, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from '../../layouts/AuthLayout';
import Input from '../../components/common/Input';
import Select from '../../components/common/Select';
import Button from '../../components/common/Button';
import Banner from '../../components/common/Banner';
import { EyeIcon, EyeOffIcon } from '../../components/common/Icons';
import { fetchCourses } from '../../services/academicsService';
import {
  getSignupCodeErrorMessage,
  parseRegisterError,
  registerAccount,
  sendSignupCode,
  verifySignupCode,
} from '../../services/authService';
import type { CourseOption, RegisterPayload } from '../../types/auth';
import { PASSWORD_RULES, isPasswordValid } from '../../utils/passwordRules';
import VerifyEmailPage from './VerifyEmailPage';
import RequestStatusPage from './RequestStatusPage';

const RESEND_SECONDS = 60;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface FormValues {
  schoolId: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  middleInitial: string;
  lastName: string;
  email: string;
  courseId: string;
  year: string;
  section: string;
}

type FieldKey = keyof FormValues;
type FieldErrors = Partial<Record<FieldKey, string>>;
type Step = 'form' | 'verify' | 'done';
type BannerState = { type: 'error' | 'success'; text: string } | null;

const INITIAL_VALUES: FormValues = {
  schoolId: '',
  password: '',
  confirmPassword: '',
  firstName: '',
  middleInitial: '',
  lastName: '',
  email: '',
  courseId: '',
  year: '',
  section: '',
};

const FIELD_IDS: Record<FieldKey, string> = {
  schoolId: 'reg-school-id',
  password: 'reg-password',
  confirmPassword: 'reg-confirm-password',
  firstName: 'reg-first-name',
  middleInitial: 'reg-middle-initial',
  lastName: 'reg-last-name',
  email: 'reg-email',
  courseId: 'reg-course',
  year: 'reg-year',
  section: 'reg-section',
};

const FIELD_ORDER: FieldKey[] = [
  'schoolId',
  'password',
  'confirmPassword',
  'firstName',
  'middleInitial',
  'lastName',
  'email',
  'courseId',
  'year',
  'section',
];

const SERVER_FIELD_MAP: Record<string, FieldKey> = {
  school_id: 'schoolId',
  password: 'password',
  confirm_password: 'confirmPassword',
  first_name: 'firstName',
  middle_name: 'middleInitial',
  last_name: 'lastName',
  email: 'email',
  course_id: 'courseId',
  year: 'year',
  section: 'section',
};

const YEAR_OPTIONS = [
  { value: '1', label: '1st Year' },
  { value: '2', label: '2nd Year' },
  { value: '3', label: '3rd Year' },
  { value: '4', label: '4th Year' },
];

const SECTION_OPTIONS = ['A', 'B', 'C', 'D'].map((section) => ({
  value: section,
  label: `Section ${section}`,
}));

function formatMiddleInitial(raw: string, previous: string): string {
  if (raw.length < previous.length) return '';
  const letter = raw.match(/[A-Za-z]/)?.[0];
  return letter ? `${letter.toUpperCase()}.` : '';
}

function validate(values: FormValues): FieldErrors {
  const errors: FieldErrors = {};
  if (!values.schoolId.trim()) errors.schoolId = 'CTU ID is required.';
  if (!values.firstName.trim()) errors.firstName = 'First name is required.';
  if (!values.lastName.trim()) errors.lastName = 'Last name is required.';
  if (!values.email.trim()) errors.email = 'Email is required.';
  else if (!EMAIL_RE.test(values.email.trim())) errors.email = 'Enter a valid email address.';
  if (!values.password) errors.password = 'Password is required.';
  else if (!isPasswordValid(values.password)) errors.password = 'Password does not meet all requirements.';
  if (!values.confirmPassword) errors.confirmPassword = 'Please confirm your password.';
  else if (values.password !== values.confirmPassword) errors.confirmPassword = 'Passwords do not match.';
  if (!values.courseId) errors.courseId = 'Select a course.';
  if (!values.year) errors.year = 'Select a year level.';
  if (!values.section) errors.section = 'Select a section.';
  return errors;
}

function focusFirstInvalid(errors: FieldErrors) {
  const first = FIELD_ORDER.find((key) => errors[key]);
  if (first) document.getElementById(FIELD_IDS[first])?.focus();
}

function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <h2
      className="fg-accent mb-4 mt-6 border-b pb-1.5 text-xs font-semibold uppercase tracking-wide"
      style={{ borderColor: 'var(--accent-soft)' }}
    >
      {children}
    </h2>
  );
}

function PasswordToggle({ visible, label, onToggle }: { visible: boolean; label: string; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={`${visible ? 'Hide' : 'Show'} ${label}`}
      className="icon-btn rounded-md p-1.5"
    >
      {visible ? <EyeOffIcon width={18} height={18} /> : <EyeIcon width={18} height={18} />}
    </button>
  );
}

export default function RegisterPage() {
  const [step, setStep] = useState<Step>('form');
  const [values, setValues] = useState<FormValues>(INITIAL_VALUES);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [banner, setBanner] = useState<BannerState>(null);
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<CourseOption[]>([]);
  const [coursesFailed, setCoursesFailed] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [code, setCode] = useState('');
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [verifyNotice, setVerifyNotice] = useState<string | null>(null);
  const [resendIn, setResendIn] = useState(0);

  const busy = useRef(false);
  const normalizedEmail = values.email.trim().toLowerCase();

  useEffect(() => {
    let active = true;
    fetchCourses()
      .then((list) => {
        if (active) setCourses(list);
      })
      .catch(() => {
        if (active) setCoursesFailed(true);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (resendIn <= 0) return;
    const timer = setTimeout(() => setResendIn((seconds) => seconds - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendIn]);

  function setField(key: FieldKey, value: string) {
    setValues((previous) => ({ ...previous, [key]: value }));
    setErrors((previous) => (previous[key] ? { ...previous, [key]: undefined } : previous));
  }

  function buildPayload(): RegisterPayload {
    return {
      school_id: values.schoolId.trim(),
      password: values.password,
      confirm_password: values.confirmPassword,
      email: normalizedEmail,
      first_name: values.firstName.trim(),
      middle_name: values.middleInitial.trim(),
      last_name: values.lastName.trim(),
      course_id: Number(values.courseId),
      year: values.year,
      section: values.section,
    };
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy.current) return;
    setBanner(null);

    const found = validate(values);
    if (Object.keys(found).length > 0) {
      setErrors(found);
      setBanner({ type: 'error', text: 'Please fill in all required fields correctly.' });
      focusFirstInvalid(found);
      return;
    }

    busy.current = true;
    setLoading(true);
    try {
      await sendSignupCode(normalizedEmail);
      setCode('');
      setVerifyError(null);
      setVerifyNotice(null);
      setResendIn(RESEND_SECONDS);
      setStep('verify');
    } catch (error) {
      setBanner({ type: 'error', text: getSignupCodeErrorMessage(error) });
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }

  async function handleVerify(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy.current) return;
    if (!/^\d{6}$/.test(code)) {
      setVerifyError('Enter the 6-digit code.');
      return;
    }

    busy.current = true;
    setLoading(true);
    setVerifyError(null);
    setVerifyNotice(null);
    let verified = false;
    try {
      await verifySignupCode(normalizedEmail, code);
      verified = true;
      await registerAccount(buildPayload());
      setStep('done');
    } catch (error) {
      if (!verified) {
        setVerifyError(getSignupCodeErrorMessage(error));
      } else {
        const info = parseRegisterError(error);
        const mapped: FieldErrors = {};
        for (const [serverKey, message] of Object.entries(info.fields)) {
          const key = SERVER_FIELD_MAP[serverKey];
          if (key) mapped[key] = message;
        }
        setErrors(mapped);
        const hasFields = Object.keys(mapped).length > 0;
        setBanner({
          type: 'error',
          text: hasFields
            ? 'Please correct the highlighted fields. A new code will be sent when you submit again.'
            : (info.message ?? 'Registration could not be completed. Please try again.'),
        });
        setStep('form');
      }
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }

  async function handleResend() {
    if (busy.current || resendIn > 0) return;
    busy.current = true;
    setLoading(true);
    setVerifyError(null);
    try {
      await sendSignupCode(normalizedEmail);
      setResendIn(RESEND_SECONDS);
      setVerifyNotice('A new code was sent to your email.');
    } catch (error) {
      setVerifyError(getSignupCodeErrorMessage(error));
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }

  function handleBack() {
    setVerifyError(null);
    setVerifyNotice(null);
    setBanner(null);
    setStep('form');
  }

  if (step === 'done') {
    return (
      <AuthLayout maxWidth="md">
        <RequestStatusPage />
      </AuthLayout>
    );
  }

  if (step === 'verify') {
    return (
      <AuthLayout maxWidth="md">
        <VerifyEmailPage
          email={normalizedEmail}
          code={code}
          onCodeChange={(value) => {
            setCode(value.replace(/\D/g, '').slice(0, 6));
            setVerifyError(null);
          }}
          error={verifyError}
          notice={verifyNotice}
          loading={loading}
          resendIn={resendIn}
          onSubmit={handleVerify}
          onResend={handleResend}
          onBack={handleBack}
        />
      </AuthLayout>
    );
  }

  const courseOptions = courses.map((course) => ({
    value: String(course.course_id),
    label: course.course_name ? `${course.course_code} – ${course.course_name}` : course.course_code,
  }));

  return (
    <AuthLayout maxWidth="xl">
      <h1 className="fg-strong text-xl font-semibold sm:text-2xl">Create Account</h1>
      <p className="fg-muted mt-1 text-xs">Fill in the details below to create your student account.</p>

      <form onSubmit={handleSubmit} noValidate className="mt-2">
        <SectionTitle>Login Credentials</SectionTitle>
        <div className="grid items-start gap-4 sm:grid-cols-3">
          <Input
            label="CTU ID"
            id={FIELD_IDS.schoolId}
            requiredMark
            autoComplete="username"
            placeholder="Enter your CTU ID"
            value={values.schoolId}
            error={errors.schoolId}
            onChange={(event) => setField('schoolId', event.target.value)}
          />
          <div>
            <Input
              label="Password"
              id={FIELD_IDS.password}
              requiredMark
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="Create a password"
              value={values.password}
              error={errors.password}
              onFocus={() => setShowRules(true)}
              onChange={(event) => setField('password', event.target.value)}
              rightAdornment={
                <PasswordToggle visible={showPassword} label="password" onToggle={() => setShowPassword((value) => !value)} />
              }
            />
            {showRules && (
              <ul className="mt-2 space-y-0.5 text-[11.5px] leading-relaxed" aria-live="polite">
                {PASSWORD_RULES.map((rule) => {
                  const ok = rule.test(values.password);
                  return (
                    <li key={rule.id} className={ok ? 'fg-accent' : 'fg-muted'}>
                      {ok ? '✓' : '•'} {rule.label}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          <Input
            label="Confirm Password"
            id={FIELD_IDS.confirmPassword}
            requiredMark
            type={showConfirm ? 'text' : 'password'}
            autoComplete="new-password"
            placeholder="Re-enter your password"
            value={values.confirmPassword}
            error={errors.confirmPassword}
            onChange={(event) => setField('confirmPassword', event.target.value)}
            rightAdornment={
              <PasswordToggle visible={showConfirm} label="confirm password" onToggle={() => setShowConfirm((value) => !value)} />
            }
          />
        </div>

        <SectionTitle>Personal Information</SectionTitle>
        <div className="grid items-start gap-4 sm:grid-cols-[1fr_84px_1fr]">
          <Input
            label="First Name"
            id={FIELD_IDS.firstName}
            requiredMark
            autoComplete="given-name"
            placeholder="First name"
            value={values.firstName}
            error={errors.firstName}
            onChange={(event) => setField('firstName', event.target.value)}
          />
          <Input
            label="M. I."
            id={FIELD_IDS.middleInitial}
            maxLength={2}
            placeholder="M.I."
            value={values.middleInitial}
            error={errors.middleInitial}
            onChange={(event) => setField('middleInitial', formatMiddleInitial(event.target.value, values.middleInitial))}
          />
          <Input
            label="Last Name"
            id={FIELD_IDS.lastName}
            requiredMark
            autoComplete="family-name"
            placeholder="Last name"
            value={values.lastName}
            error={errors.lastName}
            onChange={(event) => setField('lastName', event.target.value)}
          />
        </div>
        <div className="mt-4 sm:w-1/2 sm:pr-2">
          <Input
            label="Email"
            id={FIELD_IDS.email}
            requiredMark
            type="email"
            autoComplete="email"
            placeholder="name@example.com"
            value={values.email}
            error={errors.email}
            onChange={(event) => setField('email', event.target.value)}
          />
        </div>

        <SectionTitle>School Information</SectionTitle>
        <div className="grid items-start gap-4 sm:grid-cols-3">
          <Select
            label="Course"
            id={FIELD_IDS.courseId}
            requiredMark
            placeholder="Select a course"
            options={courseOptions}
            value={values.courseId}
            error={errors.courseId}
            onChange={(event) => setField('courseId', event.target.value)}
          />
          <Select
            label="Year Level"
            id={FIELD_IDS.year}
            requiredMark
            placeholder="Select year"
            options={YEAR_OPTIONS}
            value={values.year}
            error={errors.year}
            onChange={(event) => setField('year', event.target.value)}
          />
          <Select
            label="Section"
            id={FIELD_IDS.section}
            requiredMark
            placeholder="Select section"
            options={SECTION_OPTIONS}
            value={values.section}
            error={errors.section}
            onChange={(event) => setField('section', event.target.value)}
          />
        </div>

        <div className="mt-6">
          {coursesFailed && <Banner type="error">Courses could not be loaded. Please refresh the page.</Banner>}
          {banner && <Banner type={banner.type}>{banner.text}</Banner>}
          <Button type="submit" fullWidth loading={loading} disabled={coursesFailed}>
            {loading ? 'Sending code…' : 'Submit'}
          </Button>
        </div>
      </form>

      <p className="fg-muted mt-5 text-center text-xs">
        Already have an account?{' '}
        <Link to="/" className="link-accent font-medium">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
