'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { getStoredUserRole } from '@/lib/auth';

type CompanyDetail = {
  id: number;
  name?: string;
  description?: string;
  location?: string;
  industry?: string;
  website?: string;
  email?: string;
  phone?: string;
  contact_person?: string;
  status?: string;
};

export default function CompanyDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const companyId = params.id;

    if (!companyId) {
      setError('Company id is missing.');
      setLoading(false);
      return;
    }

    const fetchCompany = async () => {
      try {
        const response = await api.get<CompanyDetail>(`/companies/${companyId}/`);
        setCompany(response.data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load company details.');
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
  }, [params.id]);

  if (loading) {
    return <div className="container mx-auto p-4 text-center text-gray-700">Loading company details...</div>;
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error loading company: {error}</div>;
  }

  if (!company) {
    return <div className="container mx-auto p-4 text-center text-gray-700">Company not found.</div>;
  }

  const role = getStoredUserRole();
  const canEdit = role === 'company' || role === 'tpo';

  return (
    <ProtectedRoute requiredRole={['student', 'tpo', 'company']}>
      <div className="container mx-auto p-4">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-blue-600">Company</p>
            <h1 className="text-3xl font-bold text-gray-900">{company.name ?? 'Company Profile'}</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/companies" className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300">
              Back to Companies
            </Link>
            {canEdit && (
              <button
                type="button"
                onClick={() => router.push(`/companies/${company.id}/edit`)}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Profile overview</h2>
            <div className="space-y-3 text-gray-700">
              <p><span className="font-semibold">Name:</span> {company.name ?? 'Not provided'}</p>
              <p><span className="font-semibold">Location:</span> {company.location ?? 'Not provided'}</p>
              <p><span className="font-semibold">Industry:</span> {company.industry ?? 'Not provided'}</p>
              <p><span className="font-semibold">Status:</span> {company.status ?? 'Active'}</p>
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-md">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Contact information</h2>
            <div className="space-y-3 text-gray-700">
              <p><span className="font-semibold">Website:</span> {company.website ?? 'Not provided'}</p>
              <p><span className="font-semibold">Email:</span> {company.email ?? 'Not provided'}</p>
              <p><span className="font-semibold">Phone:</span> {company.phone ?? 'Not provided'}</p>
              <p><span className="font-semibold">Contact person:</span> {company.contact_person ?? 'Not provided'}</p>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-lg bg-white p-6 shadow-md">
          <h2 className="mb-3 text-xl font-semibold text-gray-900">About</h2>
          <p className="whitespace-pre-wrap text-gray-700">
            {company.description || 'No company description available.'}
          </p>
        </div>
      </div>
    </ProtectedRoute>
  );
}
