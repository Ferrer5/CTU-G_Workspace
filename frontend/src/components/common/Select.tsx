import { forwardRef } from 'react';
import type { SelectHTMLAttributes } from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label: string;
  id: string;
  placeholder: string;
  options: SelectOption[];
  error?: string;
  requiredMark?: boolean;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, id, placeholder, options, error, requiredMark = false, className = '', ...rest },
  ref,
) {
  return (
    <div>
      <label htmlFor={id} className="fg-body mb-1.5 block text-xs font-medium">
        {label}
        {requiredMark && <span className="fg-error ml-0.5" aria-hidden="true">*</span>}
      </label>
      <div className="relative">
        <select
          ref={ref}
          id={id}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${id}-error` : undefined}
          className={`field w-full appearance-none rounded-lg px-3 py-2.5 pr-9 text-sm ${error ? 'field-error' : ''} ${className}`}
          {...rest}
        >
          <option value="">{placeholder}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <svg
          className="fg-muted pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M7 10l5 5 5-5z" />
        </svg>
      </div>
      {error && (
        <p id={`${id}-error`} role="alert" className="fg-error mt-1 text-xs">
          {error}
        </p>
      )}
    </div>
  );
});

export default Select;
