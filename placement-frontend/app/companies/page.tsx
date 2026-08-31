'use client';

import React, { useEffect, useState } from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { toast } from 'sonner';

interface Company {
  id: string;
  company_name: string;
  hr_name?: string;
  website?: string;
}

const CompanyListPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompanies = async (search = '') => {
      try {
        // Real backend endpoint (companies/views.py CompanyListView) returns a plain
        // array, not a paginated {results: [...]} envelope — no default pagination class
        // is configured for it.
        const response = await api.get<Company[]>('/companies/', { params: search ? { q: search } : {} });
        setCompanies(response.data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setError(msg);
        try { toast.error('Failed to load companies: ' + msg); } catch {}
      } finally {
        setLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="grid grid-cols-1 gap-6">
          <div className="p-6 rounded shadow bg-gray-100 animate-pulse h-28" />
          <div className="p-6 rounded shadow bg-gray-100 animate-pulse h-28" />
          <div className="p-6 rounded shadow bg-gray-100 animate-pulse h-28" />
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error loading companies: {error}</div>;
  }

  return (
    <ProtectedRoute requiredRole={['student', 'company', 'tpo']}>
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Company Listings</h1>
          <LogoutButton />
        </div>

        <div className="mb-4">
          <input placeholder="Search companies by name or website" onChange={(e) => {
            const q = e.target.value;
            setLoading(true);
            api.get<Company[]>('/companies/', { params: q ? { q } : {} }).then((res) => {
              setCompanies(res.data);
            }).catch((err) => {
              setError(err?.message || 'Failed to search');
            }).finally(() => setLoading(false));
          }} className="w-full p-2 border rounded" />
        </div>

        <div className="grid grid-cols-1 gap-6">
          {companies.length === 0 ? (
            <p>No companies found.</p>
          ) : (
            companies.map((company) => (
              <div key={company.id} className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">{company.company_name}</h2>
                <p className="text-gray-700 mb-2">{company.website}</p>
                {company.hr_name && <p className="text-gray-700 mb-2">HR Contact: {company.hr_name}</p>}
                <a href={`/companies/${company.id}`} className="text-blue-500 hover:underline">View Details</a>
              </div>
            ))
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default CompanyListPage;
