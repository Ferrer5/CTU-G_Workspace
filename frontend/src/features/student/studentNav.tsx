import type { ComponentType, SVGProps } from 'react';
import {
  ClipboardCheckIcon,
  MegaphoneIcon,
  UsersIcon,
  WalletIcon,
} from '../../components/common/Icons';

interface StudentServiceNavItem {
  label: string;
  Icon: ComponentType<SVGProps<SVGSVGElement>>;
}

export const studentServiceNavItems: StudentServiceNavItem[] = [
  { label: 'SSG Finance', Icon: WalletIcon },
  { label: 'Clearance', Icon: ClipboardCheckIcon },
  { label: 'Group Rating', Icon: UsersIcon },
  { label: 'Announcements', Icon: MegaphoneIcon },
];
