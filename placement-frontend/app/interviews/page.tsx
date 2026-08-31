'use client';

import React, { useEffect, useState } from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

interface Interview {
  id: number;
  company_name: string;
  role: string;
  date: string;
  time: string;
  status: string;
}

const InterviewSchedulePage: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const response = await api.get<Interview[]>('/interviews/');
        setInterviews(response.data);
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
            <p>No interviews scheduled.</p>
          ) : (
            interviews.map((interview) => (
              <div key={interview.id} className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">Interview with {interview.company_name}</h2>
                <p className="text-gray-700 mb-2">Role: {interview.role}</p>
                <p className="text-gray-700 mb-2">Date: {new Date(interview.date).toLocaleDateString()}</p>
                <p className="text-gray-700 mb-2">Time: {interview.time}</p>
                <p className="text-gray-700 mb-2">Status: {interview.status}</p>
                <a href={`/interviews/${interview.id}`} className="text-blue-500 hover:underline mr-4">View Details</a>
                {interview.status === 'Scheduled' && (
                  <button className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600">Reschedule</button>
                )}
                {interview.status === 'Pending Confirmation' && (
                  <button className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">Confirm</button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default InterviewSchedulePage;
