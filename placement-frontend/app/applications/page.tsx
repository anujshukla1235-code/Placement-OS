'use client';

import React, { useEffect, useState } from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { toast } from 'sonner';

interface Application {
  id: number;
  company_name: string;
  role: string;
  status: string;
  date_applied: string;
}

const JobApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await api.get<Application[]>('/students/applications/');
        setApplications(response.data);
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
            <p>No applications found.</p>
          ) : (
            applications.map((app) => (
              <div key={app.id} className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">{app.role} at {app.company_name}</h2>
                <p className="text-gray-700 mb-2">Status: {app.status}</p>
                <p className="text-gray-700 mb-2">Date Applied: {new Date(app.date_applied).toLocaleDateString()}</p>
                <a href={`/applications/${app.id}`} className="text-blue-500 hover:underline mr-4">View Details</a>
                <button className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">Withdraw Application</button>
              </div>
            ))
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default JobApplicationsPage;
