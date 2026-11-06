import { useEffect, useState } from 'react';
import { getTreasurerFinanceData } from '../services/treasurerFinanceService';
import type { TreasurerFinanceData } from '../types';

export function useTreasurerFinance() {
  const [data, setData] = useState<TreasurerFinanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    void getTreasurerFinanceData()
      .then((result) => {
        if (!isMounted) return;
        setData(result);
        setError(null);
      })
      .catch((caughtError: unknown) => {
        if (!isMounted) return;
        setError(caughtError instanceof Error ? caughtError.message : 'Unable to load treasurer finance data.');
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return { data, loading, error };
}
