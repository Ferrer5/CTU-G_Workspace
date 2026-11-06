import type { SVGProps } from 'react';

const base: SVGProps<SVGSVGElement> = {
  width: 20,
  height: 20,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
};

type IconProps = SVGProps<SVGSVGElement>;

export const PlusIcon = (props: IconProps) => <svg {...base} {...props}><path d="M12 5v14M5 12h14" /></svg>;
export const SearchIcon = (props: IconProps) => <svg {...base} {...props}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.35-4.35" /></svg>;
export const EditIcon = (props: IconProps) => <svg {...base} {...props}><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></svg>;
export const TrashIcon = (props: IconProps) => <svg {...base} {...props}><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14" /></svg>;
