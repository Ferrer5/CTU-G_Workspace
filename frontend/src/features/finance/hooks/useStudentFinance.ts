import { useEffect, useState } from 'react';
import { ApiError } from '../../../services/apiClient';
import type { StudentAcademicProfile } from '../../student/services/studentService';
import { fetchAcademicProfile } from '../../student/services/studentService';
import { fetchStudentFinance } from '../services/financeService';
import type { StudentFinanceData } from '../types';

interface State {
  status: 'loading' | 'ready' | 'error';
  data: StudentFinanceData | null;
  academic: StudentAcademicProfile | null;
  academicError: string;
  error: string;
  errorStatus: number | null;
}

const INITIAL: State = {
  status: 'loading',
  data: null,
  academic: null,
  academicError: '',
  error: '',
  errorStatus: null,
};

export function useStudentFinance(loadAcademic: boolean): State {
  const [state, setState] = useState<State>(INITIAL);

  useEffect(() => {
    let active = true;
    const academicRequest = loadAcademic
      ? fetchAcademicProfile()
        .then((profile) => ({ profile, error: '' }))
        .catch((requestError: unknown) => {
          if (requestError instanceof ApiError && requestError.status === 401) throw requestError;
          return {
            profile: null,
            error: requestError instanceof Error ? requestError.message : 'Unable to load academic information.',
          };
        })
      : Promise.resolve({ profile: null, error: '' });

    Promise.all([
      fetchStudentFinance(),
      academicRequest,
    ])
      .then(([data, { profile: academic, error: academicError }]) => {
        if (active) setState({ status: 'ready', data, academic, academicError, error: '', errorStatus: null });
      })
      .catch((requestError: unknown) => {
        if (!active) return;
        setState({
          status: 'error',
          data: null,
          academic: null,
          academicError: '',
          error: requestError instanceof Error ? requestError.message : 'Unable to load finance records.',
          errorStatus: requestError instanceof ApiError ? requestError.status : null,
        });
      });
    return () => {
      active = false;
    };
  }, [loadAcademic]);

  return state;
}
