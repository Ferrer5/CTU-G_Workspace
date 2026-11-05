import type { ReactNode } from 'react';
import '../css/theme.css';
import ThemeProvider from '../contexts/ThemeProvider';
import Navbar from '../components/navigation/Navbar';
import { GLASS } from '../utils/styles';
import campusImage from '../assets/campus-building.jpg';

interface AuthLayoutProps {
  children: ReactNode;
  maxWidth?: 'md' | 'xl';
}

export default function AuthLayout({ children, maxWidth = 'xl' }: AuthLayoutProps) {
  const widthClass = maxWidth === 'xl' ? 'max-w-3xl' : 'max-w-md';

  return (
    <ThemeProvider>
      <div className="app-bg relative isolate flex min-h-screen flex-col overflow-x-clip">
        <div aria-hidden className="site-bg">
          <div className="site-bg-photo" style={{ backgroundImage: `url(${campusImage})` }} />
          <div className="site-bg-overlay" />
        </div>

        <Navbar />

        <main className="flex flex-1 items-start justify-center px-4 py-10 sm:px-6">
          <div className={`${GLASS} w-full ${widthClass} rounded-2xl p-6 sm:p-8`}>{children}</div>
        </main>
      </div>
    </ThemeProvider>
  );
}
