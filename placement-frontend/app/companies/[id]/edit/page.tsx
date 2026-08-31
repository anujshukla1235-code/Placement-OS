'use client';

import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

type CompanyFormState = {
  name: string;
  description: string;
  location: string;
  industry: string;
  website: string;
  email: string;
  phone: string;
  contact_person: string;
};

export default function CompanyEditPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [form, setForm] = useState<CompanyFormState>({
    name: '',
    description: '',
    location: '',
    industry: '',
    website: '',
    email: '',
    phone: '',
    contact_person: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
        const response = await api.get<CompanyFormState>(`/companies/${companyId}/`);
        setForm({
          name: response.data.name ?? '',
          description: response.data.description ?? '',
          location: response.data.location ?? '',
          industry: response.data.industry ?? '',
          website: response.data.website ?? '',
          email: response.data.email ?? '',
          phone: response.data.phone ?? '',
          contact_person: response.data.contact_person ?? '',
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load company profile.');
      } finally {
        setLoading(false);
      }
    };

    fetchCompany();
  }, [params.id]);

  const handleChange = (field: keyof CompanyFormState, value: string) => {
    setForm((previous) => ({ ...previous, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await api.patch(`/companies/${params.id}/`, form);
      router.push(`/companies/${params.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to save company profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="container mx-auto p-4 text-center text-gray-700">Loading company profile...</div>;
  }

  return (
    <ProtectedRoute requiredRole={['company', 'tpo']}>
      <div className="container mx-auto max-w-3xl p-4">
        <div className="mb-6 flex items-center justify-between gap-3">
          <h1 className="text-3xl font-bold text-gray-900">Edit Company Profile</h1>
          <button
            type="button"
            onClick={() => router.push(`/companies/${params.id}`)}
            className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 rounded-lg bg-white p-6 shadow-md">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Company name</label>
            <input
              className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
              value={form.name}
              onChange={(event) => handleChange('name', event.target.value)}
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="min-h-28 w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
              value={form.description}
              onChange={(event) => handleChange('description', event.target.value)}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Location</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.location}
                onChange={(event) => handleChange('location', event.target.value)}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Industry</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.industry}
                onChange={(event) => handleChange('industry', event.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Website</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.website}
                onChange={(event) => handleChange('website', event.target.value)}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.email}
                onChange={(event) => handleChange('email', event.target.value)}
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Phone</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.phone}
                onChange={(event) => handleChange('phone', event.target.value)}
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">Contact person</label>
              <input
                className="w-full rounded-md border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
                value={form.contact_person}
                onChange={(event) => handleChange('contact_person', event.target.value)}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
            >
              {saving ? 'Saving...' : 'Save changes'}
            </button>
          </div>
        </form>
      </div>
    </ProtectedRoute>
  );
}
