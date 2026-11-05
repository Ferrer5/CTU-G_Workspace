import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { focusLoginForm, scrollToSection } from '../utils/scroll';

interface ArrivalState {
  scrollTo?: string;
  focusLogin?: boolean;
}

export function useScrollOnArrival() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const state = location.state as ArrivalState | null;
    if (!state?.scrollTo) return;
    const { scrollTo, focusLogin } = state;
    const timer = window.setTimeout(() => {
      if (focusLogin) focusLoginForm();
      else scrollToSection(scrollTo);
      navigate(location.pathname, { replace: true, state: null });
    }, 60);
    return () => window.clearTimeout(timer);
  }, [location.pathname, location.state, navigate]);
}
