'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { toast } from 'sonner';

interface CompanyProfile {
  company_name: string;
  hr_name: string;
  official_email: string;
  website?: string;
  is_approved: boolean;
}

const CompanyDashboardPage: React.FC = () => {
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Real endpoint: GET /companies/me/ (companies/urls.py -> CompanyMeView)
        const res = await api.get<CompanyProfile>('/companies/me/');
        setProfile(res.data);
      } catch (err) {
        toast.error('Unable to load your company profile.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <ProtectedRoute requiredRole="company">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Company Dashboard</h1>
          <LogoutButton />
        </div>

        {loading ? (
          <p className="text-gray-600">Loading...</p>
        ) : (
          <>
            {profile && !profile.is_approved && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded mb-6">
                Your company account is pending TPO/admin approval. You will be able to post jobs once approved.
              </div>
            )}

            {profile && (
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                <h2 className="text-xl font-semibold mb-3">{profile.company_name}</h2>
                <p className="text-gray-700">HR Contact: {profile.hr_name}</p>
                <p className="text-gray-700">Email: {profile.official_email}</p>
                {profile.website && <p className="text-gray-700">Website: {profile.website}</p>}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">Job Postings</h2>
                <p className="text-gray-700 mb-2">View and manage jobs you have posted.</p>
                <Link href="/jobs" className="text-blue-500 hover:underline">Go to Jobs</Link>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">Applications</h2>
                <p className="text-gray-700 mb-2">Review applicants and manage shortlisting.</p>
                <Link href="/applications" className="text-blue-500 hover:underline">View Applications</Link>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">Interviews</h2>
                <p className="text-gray-700 mb-2">Schedule and track candidate interviews.</p>
                <Link href="/interviews" className="text-blue-500 hover:underline">Manage Interviews</Link>
              </div>
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
};

export default CompanyDashboardPage;
