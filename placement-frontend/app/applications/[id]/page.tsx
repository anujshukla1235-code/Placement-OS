'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

type ApplicationDetail = {
  id: string | number;
  company_name?: string;
  company?: { id?: number; name?: string } | null;
  job_title?: string;
  role?: string;
  status?: string;
  applied_at?: string;
  date_applied?: string;
  ats_score?: number;
  rejection_reason?: string;
  cover_letter?: string | null;
  notes?: string | null;
};

export default function ApplicationDetailPage() {
  const params = useParams<{ id: string }>();
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const applicationId = params.id;

    if (!applicationId) {
      setError('Application id is missing.');
      setLoading(false);
      return;
    }

    const fetchApplication = async () => {
      try {
        const response = await api.get<ApplicationDetail>(`/jobs/applications/${applicationId}/`);
        setApplication(response.data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load application details.');
      } finally {
        setLoading(false);
      }
    };

    fetchApplication();
  }, [params.id]);

  if (loading) {
    return <div className="container mx-auto p-4 text-center text-gray-700">Loading application details...</div>;
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error loading application: {error}</div>;
  }

  if (!application) {
    return <div className="container mx-auto p-4 text-center text-gray-700">Application not found.</div>;
  }

  const companyName = application.company_name ?? application.company?.name ?? 'Unknown company';

  return (
    <ProtectedRoute requiredRole={['student', 'tpo']}>
      <div className="container mx-auto p-4">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-blue-600">Application</p>
            <h1 className="text-3xl font-bold text-gray-900">{application.job_title ?? application.role ?? 'Job Application'}</h1>
          </div>
          <Link href="/applications" className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300">
            Back to Applications
          </Link>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Application overview</h2>
            <div className="space-y-3 text-gray-700">
              <p><span className="font-semibold">Company:</span> {companyName}</p>
              <p><span className="font-semibold">Role:</span> {application.job_title ?? application.role ?? 'Not provided'}</p>
              <p><span className="font-semibold">Status:</span> <span className="rounded bg-indigo-50 px-2 py-0.5 font-bold text-indigo-700">{application.status ?? 'Unknown'}</span></p>
              <p><span className="font-semibold">Date applied:</span> {(application.applied_at || application.date_applied) ? new Date(application.applied_at || application.date_applied!).toLocaleDateString() : 'Not available'}</p>
              {typeof application.ats_score === 'number' && application.ats_score > 0 && (
                <p><span className="font-semibold">ATS Match Score:</span> {application.ats_score}%</p>
              )}
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-md">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Application Details & Notes</h2>
            {application.rejection_reason && (
              <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-red-700 text-sm">
                <span className="font-semibold">Reason for rejection:</span> {application.rejection_reason}
              </div>
            )}
            <p className="whitespace-pre-wrap text-gray-700">
              {application.cover_letter || application.notes || 'No additional notes provided.'}
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
