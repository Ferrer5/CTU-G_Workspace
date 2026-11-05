import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../../css/finance.css';
import {
  CheckIcon,
  ClockIcon,
  CoinIcon,
  InfoIcon,
} from '../../../components/common/DashboardIcons';
import { useAuth } from '../../../hooks/useAuth';
import usePermissions from '../../../hooks/usePermissions';
import { PERMISSIONS } from '../../../permissions';
import DashboardHeader from '../../dashboard/components/DashboardHeader';
import StatCard from '../../student/components/StatCard';
import FeesTable from '../components/FeesTable';
import FinanceTabs, { type FinanceTab } from '../components/FinanceTabs';
import PayInfoModal from '../components/PayInfoModal';
import PaymentHistoryTable from '../components/PaymentHistoryTable';
import ReceiptModal from '../components/ReceiptModal';
import { useStudentFinance } from '../hooks/useStudentFinance';
import { IS_SAMPLE_DATA } from '../services/financeService';
import type { PaymentRecord, SemesterFee } from '../types';
import { formatPeso, formatYearSection } from '../utils/format';

export default function StudentFinancePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { hasPermission } = usePermissions();
  const canViewReceipts = hasPermission(PERMISSIONS.financeReceiptViewOwn);
  const canViewAcademic = hasPermission(PERMISSIONS.academicsProfileViewOwn);
  const { status, data, academic, academicError, error, errorStatus } = useStudentFinance(canViewAcademic);

  const [tab, setTab] = useState<FinanceTab>('overview');
  const [payFee, setPayFee] = useState<SemesterFee | null>(null);
  const [receiptPayment, setReceiptPayment] = useState<PaymentRecord | null>(null);

  useEffect(() => {
    if (errorStatus !== 401) return;
    void logout()
      .catch(() => undefined)
      .finally(() => navigate('/', { replace: true }));
  }, [errorStatus, logout, navigate]);

  const summary = useMemo(() => {
    const fees = data?.fees ?? [];
    const payments = data?.payments ?? [];
    return {
      unpaid: fees.filter((fee) => fee.status !== 'Paid'),
      balance: fees.reduce((sum, fee) => sum + Math.max(fee.required_amount - fee.paid_amount, 0), 0),
      totalPaid: payments.reduce((sum, payment) => sum + payment.amount, 0),
      history: [...payments].sort(
        (a, b) =>
          (Date.parse(b.payment_date ?? '') || 0) - (Date.parse(a.payment_date ?? '') || 0) ||
          b.payment_id - a.payment_id,
      ),
    };
  }, [data]);

  const student = {
    name: [user?.first_name, user?.last_name].filter(Boolean).join(' ').toUpperCase() || 'STUDENT',
    schoolId: user?.school_id ?? '',
    courseCode: academic?.course_code ?? '',
    yearSection: academic ? formatYearSection(academic.year, academic.section) : '',
  };

  const pendingCount = summary.unpaid.length;

  return (
    <section className="dash-page">
      <DashboardHeader title="Finance" subtitle="Your organization fees, balances, and receipts." />

      {IS_SAMPLE_DATA && (
        <div className="dash-notice" role="note">
          <InfoIcon />
          <p className="dash-notice-text">
            The finance figures below are sample data until the finance service is connected.
          </p>
        </div>
      )}

      {status === 'loading' && (
        <section className="dash-card"><p className="dash-empty" role="status">Loading your finance records…</p></section>
      )}
      {status === 'error' && (
        <section className="dash-card"><p className="dash-empty" role="alert">{error}</p></section>
      )}

      {status === 'ready' && academicError && (
        <div className="dash-notice" role="alert">
          <InfoIcon />
          <p className="dash-notice-text">{academicError}</p>
        </div>
      )}

      {status === 'ready' && data && (
        <>
          <FinanceTabs
            active={tab}
            onChange={setTab}
            pendingCount={pendingCount}
            paymentCount={summary.history.length}
          />

          {tab === 'overview' && (
            <div role="tabpanel" id="fin-panel-overview" aria-labelledby="fin-tab-overview">
              <div className="dash-stat-grid">
                <StatCard
                  label="Org Fee Balance"
                  value={formatPeso(summary.balance)}
                  trend={summary.balance > 0 ? 'Amount due' : 'Fully settled'}
                  tone={summary.balance > 0 ? 'warn' : 'good'}
                  icon={<CoinIcon />}
                />
                <StatCard
                  label="Total Paid Amount"
                  value={formatPeso(summary.totalPaid)}
                  trend="All confirmed payments"
                  tone="good"
                  icon={<CheckIcon />}
                />
                <StatCard
                  label="Pending Semesters"
                  value={String(pendingCount)}
                  trend={pendingCount > 0 ? 'Semesters not yet fully paid' : 'All semesters paid'}
                  tone={pendingCount > 0 ? 'warn' : 'good'}
                  icon={<ClockIcon />}
                />
              </div>
              <div className="dash-notice" role="note">
                <InfoIcon />
                <p className="dash-notice-text">
                  This page is <strong>view-only</strong>. Contact your SSG office to update payment records or dispute a balance.
                </p>
              </div>
            </div>
          )}

          {tab === 'fees' && (
            <div role="tabpanel" id="fin-panel-fees" aria-labelledby="fin-tab-fees">
              <FeesTable fees={summary.unpaid} onPay={setPayFee} />
            </div>
          )}

          {tab === 'history' && (
            <div role="tabpanel" id="fin-panel-history" aria-labelledby="fin-tab-history">
              <PaymentHistoryTable
                payments={summary.history}
                canViewReceipts={canViewReceipts}
                onViewReceipt={setReceiptPayment}
              />
            </div>
          )}
        </>
      )}

      <PayInfoModal fee={payFee} onClose={() => setPayFee(null)} />
      <ReceiptModal payment={receiptPayment} student={student} onClose={() => setReceiptPayment(null)} />
    </section>
  );
}
