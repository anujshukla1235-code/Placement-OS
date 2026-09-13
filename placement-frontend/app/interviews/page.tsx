'use client';

import React, { useEffect, useState } from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

interface Interview {
  id: string | number;
  company_name?: string;
  role?: string;
  date?: string;
  time?: string;
  scheduled_at?: string;
  mode?: string;
  status: string;
}

const InterviewSchedulePage: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const response = await api.get('/interviews/');
        const list = Array.isArray(response.data) ? response.data : [];
        setInterviews(list);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchInterviews();
  }, []);

  if (loading) {
    return <div className="container mx-auto p-4 text-center">Loading interviews...</div>;
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error loading interviews: {error}</div>;
  }

  return (
    <ProtectedRoute requiredRole={['student', 'tpo']}>
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Interview Schedule</h1>
          <LogoutButton />
        </div>

        <div className="grid grid-cols-1 gap-6">
          {interviews.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
              <p className="font-medium text-lg">No interviews scheduled yet.</p>
              <p className="text-sm text-slate-500 mt-1">Once recruiters shortlist your application, interview invitations will appear here.</p>
            </div>
          ) : (
            interviews.map((interview) => {
              const displayDate = interview.date
                ? interview.date
                : (interview.scheduled_at ? new Date(interview.scheduled_at).toLocaleDateString() : 'Scheduled');

              return (
                <div key={interview.id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                  <h2 className="text-xl font-semibold mb-3">Interview with {interview.company_name || 'Hiring Company'}</h2>
                  <p className="text-gray-700 mb-1"><span className="font-semibold text-slate-900">Role:</span> {interview.role || 'Not specified'}</p>
                  <p className="text-gray-700 mb-1"><span className="font-semibold text-slate-900">Date:</span> {displayDate}</p>
                  {interview.time && <p className="text-gray-700 mb-1"><span className="font-semibold text-slate-900">Time:</span> {interview.time}</p>}
                  <p className="text-gray-700 mb-2"><span className="font-semibold text-slate-900">Mode:</span> {interview.mode || 'Online'}</p>
                  <p className="text-gray-700 mb-3"><span className="font-semibold text-slate-900">Status:</span> <span className="rounded bg-indigo-50 px-2.5 py-0.5 font-bold text-indigo-700">{interview.status}</span></p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default InterviewSchedulePage;
