'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LogoutButton } from '@/components/LogoutButton';
import api from '@/lib/api';

type Job = {
  id: string;
  title: string;
  description: string;
  company_name?: string;
  ctc?: string;
  location?: string;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [companies, setCompanies] = useState<{ id: string; company_name: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // filters
  const [q, setQ] = useState('');
  const [branch, setBranch] = useState('');
  const [company, setCompany] = useState('');
  const [ctcMin, setCtcMin] = useState('');
  const [ctcMax, setCtcMax] = useState('');

  const fetchCompanies = async () => {
    try {
      const res = await api.get('/companies/');
      setCompanies(res.data || []);
    } catch (err) {
      // ignore
    }
  };

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, any> = {};
      if (q) params.q = q;
      if (branch) params.branch = branch;
      if (company) params.company = company;
      if (ctcMin) params.ctc_min = ctcMin;
      if (ctcMax) params.ctc_max = ctcMax;

      // Real backend response (jobs/views.py JobListCreateView uses
      // StandardResultsSetPagination) is a paginated envelope, not a bare array.
      const res = await api.get<{ results: Job[]; count: number }>('/jobs/', { params });
      setJobs(res.data.results || []);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
    fetchJobs();
  }, []);

  const onSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    fetchJobs();
  };

  return (
    <ProtectedRoute requiredRole={["student", "tpo"]}>
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Jobs</h1>
          <LogoutButton />
        </div>

        <form onSubmit={onSearch} className="mb-4">
          <div className="flex space-x-2">
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search jobs by title or description" className="flex-1 p-2 border rounded" />
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Search</button>
          </div>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <aside className="md:col-span-1">
            <div className="bg-white p-4 rounded shadow mb-4">
              <h3 className="font-semibold mb-2">Filters</h3>
              <label className="block text-sm">Branch</label>
              <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full p-2 border rounded mb-2">
                <option value="">Any</option>
                <option value="CSE">CSE</option>
                <option value="ECE">ECE</option>
                <option value="ME">ME</option>
                <option value="CE">CE</option>
              </select>

              <label className="block text-sm">Company</label>
              <select value={company} onChange={(e) => setCompany(e.target.value)} className="w-full p-2 border rounded mb-2">
                <option value="">Any</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>{c.company_name}</option>
                ))}
              </select>

              <label className="block text-sm">CTC Min</label>
              <input value={ctcMin} onChange={(e) => setCtcMin(e.target.value)} className="w-full p-2 border rounded mb-2" />
              <label className="block text-sm">CTC Max</label>
              <input value={ctcMax} onChange={(e) => setCtcMax(e.target.value)} className="w-full p-2 border rounded mb-2" />

              <div className="flex space-x-2 mt-3">
                <button onClick={() => { setQ(''); setBranch(''); setCompany(''); setCtcMin(''); setCtcMax(''); fetchJobs(); }} className="px-3 py-1 bg-gray-200 rounded">Clear</button>
                <button onClick={(e) => { e.preventDefault(); fetchJobs(); }} className="px-3 py-1 bg-blue-600 text-white rounded">Apply</button>
              </div>
            </div>
          </aside>

          <main className="md:col-span-3">
            {loading && <p>Loading jobs...</p>}
            {error && <p className="text-red-600">{error}</p>}

            <div className="grid grid-cols-1 gap-4">
              {jobs.length === 0 && !loading ? <p>No jobs found.</p> : jobs.map((j) => (
                <div key={j.id} className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2">{j.title}</h2>
                  <p className="text-sm text-gray-600 mb-2">{j.company_name}</p>
                  <p className="text-gray-700 mb-2">{j.description?.slice(0, 200)}{j.description && j.description.length > 200 ? '...' : ''}</p>
                  <div className="flex items-center justify-between">
                    <a href={`/jobs/${j.id}`} className="text-blue-500 hover:underline">View Details</a>
                    <div className="text-sm text-gray-600">CTC: {j.ctc || '—'}</div>
                  </div>
                </div>
              ))}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
