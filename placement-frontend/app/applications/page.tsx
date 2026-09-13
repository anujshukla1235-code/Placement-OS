'use client';

import React, { useEffect, useState } from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { toast } from 'sonner';

interface Application {
  id: string | number;
  company_name: string;
  job_title?: string;
  role?: string;
  status: string;
  applied_at?: string;
  date_applied?: string;
}

const JobApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await api.get('/jobs/my-applications/');
        const raw = response.data;
        const list: Application[] = Array.isArray(raw) ? raw : (raw.results || []);
        setApplications(list);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setError(msg);
        try { toast.error('Failed to load applications: ' + msg); } catch {}
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="space-y-4">
          <div className="h-24 bg-gray-100 rounded animate-pulse" />
          <div className="h-24 bg-gray-100 rounded animate-pulse" />
          <div className="h-24 bg-gray-100 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error loading applications: {error}</div>;
  }

  return (
    <ProtectedRoute requiredRole={['student', 'tpo']}>
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Your Job Applications</h1>
          <LogoutButton />
        </div>

        <div className="grid grid-cols-1 gap-6">
          {applications.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
              <p className="font-medium text-lg">No applications submitted yet.</p>
              <p className="text-sm text-slate-500 mt-1">Explore active job drives and apply to start tracking your applications.</p>
              <a href="/jobs" className="mt-4 inline-block rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">
                Browse Jobs
              </a>
            </div>
          ) : (
            applications.map((app) => {
              const roleTitle = app.job_title || app.role || 'Job Application';
              const dateVal = app.applied_at || app.date_applied;
              const formattedDate = dateVal ? new Date(dateVal).toLocaleDateString() : 'Recently';

              return (
                <div key={app.id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                  <h2 className="text-xl font-semibold mb-2 text-slate-900">{roleTitle} at {app.company_name}</h2>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                    <p><span className="font-semibold text-slate-700">Status:</span> <span className="rounded bg-indigo-50 px-2.5 py-1 font-bold text-indigo-700">{app.status}</span></p>
                    <p><span className="font-semibold text-slate-700">Date Applied:</span> {formattedDate}</p>
                  </div>
                  <a href={`/applications/${app.id}`} className="text-indigo-600 font-semibold hover:underline mr-4 text-sm">View Details</a>
                </div>
              );
            })
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default JobApplicationsPage;
