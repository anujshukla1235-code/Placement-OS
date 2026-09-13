'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAccessToken, getStoredUserRole, getRoleBasedRedirectPath } from '@/lib/auth';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace('/login');
      return;
    }
    const role = getStoredUserRole();
    router.replace(getRoleBasedRedirectPath(role));
  }, [router]);

  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-6 lg:p-8">
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
          <p className="text-sm font-medium text-slate-500">Redirecting to your dashboard...</p>
        </div>
      </div>
    </main>
  );
}
