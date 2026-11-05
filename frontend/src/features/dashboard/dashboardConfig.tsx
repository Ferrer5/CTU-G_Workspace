import type { ComponentType, SVGProps } from 'react';
import {
  ClipboardCheckIcon,
  MegaphoneIcon,
  MonitorIcon,
  UsersIcon,
  WalletIcon,
} from '../../components/common/Icons';
import { PERMISSIONS } from '../../permissions';

type DashboardIcon = ComponentType<SVGProps<SVGSVGElement>>;

export interface DashboardService {
  serviceCode: string;
  label: string;
  description: string;
  path: string;
  permissions: readonly string[];
  icon: DashboardIcon;
}

export const dashboardServices: DashboardService[] = [
  {
    serviceCode: 'accounts',
    label: 'Account Administration',
    description: 'Review account requests and manage privileged roles.',
    path: '/dashboard/accounts',
    permissions: [
      PERMISSIONS.accountsRegistrationReview,
      PERMISSIONS.accountsRoleManage,
    ],
    icon: UsersIcon,
  },
  {
    serviceCode: 'academics',
    label: 'Academic Profile',
    description: 'Review your course, year level, section, and school year.',
    path: '/dashboard/academics',
    permissions: [PERMISSIONS.academicsProfileViewOwn],
    icon: MonitorIcon,
  },
  {
    serviceCode: 'clearance',
    label: 'Clearance',
    description: 'View, submit, and review clearance requests.',
    path: '/dashboard/clearance',
    permissions: [
      PERMISSIONS.clearanceViewOwn,
      PERMISSIONS.clearanceCreate,
      PERMISSIONS.clearanceViewAll,
      PERMISSIONS.clearanceApprove,
    ],
    icon: ClipboardCheckIcon,
  },
  {
    serviceCode: 'finance',
    label: 'Finance',
    description: 'Access finance transactions and reports.',
    path: '/dashboard/finance',
    permissions: [
      PERMISSIONS.financeTransactionView,
      PERMISSIONS.financeTransactionCreate,
      PERMISSIONS.financeReportView,
    ],
    icon: WalletIcon,
  },
  {
    serviceCode: 'group_rating',
    label: 'Group Rating',
    description: 'Access rating sheets and criteria.',
    path: '/dashboard/group-rating',
    permissions: [
      PERMISSIONS.groupRatingSheetViewOwn,
      PERMISSIONS.groupRatingSheetSubmit,
      PERMISSIONS.groupRatingCriteriaManage,
    ],
    icon: UsersIcon,
  },
  {
    serviceCode: 'announcements',
    label: 'Announcements',
    description: 'Read campus announcements.',
    path: '/dashboard/announcements',
    permissions: [PERMISSIONS.announcementsPostView],
    icon: MegaphoneIcon,
  },
];

export const dashboardNavigation = [
  {
    label: 'Overview',
    path: '/dashboard',
    permissions: [] as readonly string[],
  },
  {
    label: 'My Profile',
    path: '/dashboard/profile',
    permissions: [PERMISSIONS.accountsProfileViewOwn],
  },
  ...dashboardServices.map(({ label, path, permissions }) => ({
    label,
    path,
    permissions,
  })),
];
