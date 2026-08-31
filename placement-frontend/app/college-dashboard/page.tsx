'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';
import { toast } from 'sonner';

interface CollegeStudent {
  id: string;
  name: string;
  email: string;
  enrollment_number: string;
  branch: string;
  cgpa: string;
  is_placed: boolean;
}

interface CollegeDashboardData {
  college_name: string;
  is_approved: boolean;
  total_students: number;
  placed_count: number;
  students: CollegeStudent[];
}

const CollegeDashboardPage: React.FC = () => {
  const [data, setData] = useState<CollegeDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadDashboard = async () => {
    try {
      // Real endpoint: GET /college/dashboard/ (companies/urls_college.py -> CollegeDashboardView)
      const res = await api.get<CollegeDashboardData>('/college/dashboard/');
      setData(res.data);
    } catch (err) {
      toast.error('Unable to load college dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      // Real endpoint: POST /college/bulk-upload/ — CSV columns: first_name,last_name,email,enrollment_number,branch,cgpa
      const res = await api.post('/college/bulk-upload/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success(res.data?.message || 'Students uploaded');
      await loadDashboard();
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Upload failed. Check CSV format.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <ProtectedRoute requiredRole="college">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">College Dashboard</h1>
          <LogoutButton />
        </div>

        {loading ? (
          <p className="text-gray-600">Loading...</p>
        ) : (
          <>
            {data && !data.is_approved && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded mb-6">
                Your college account is pending admin approval.
              </div>
            )}

            {data && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div className="bg-white p-4 rounded shadow">
                  <p className="text-gray-500 text-sm">College</p>
                  <p className="text-lg font-semibold">{data.college_name}</p>
                </div>
                <div className="bg-white p-4 rounded shadow">
                  <p className="text-gray-500 text-sm">Total Students</p>
                  <p className="text-lg font-semibold">{data.total_students}</p>
                </div>
                <div className="bg-white p-4 rounded shadow">
                  <p className="text-gray-500 text-sm">Placed</p>
                  <p className="text-lg font-semibold">{data.placed_count}</p>
                </div>
              </div>
            )}

            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h2 className="text-xl font-semibold mb-3">Bulk Upload Students (CSV)</h2>
              <p className="text-sm text-gray-600 mb-2">
                Columns required: first_name, last_name, email, enrollment_number, branch, cgpa.
                New accounts get the default password <code>College@123</code>.
              </p>
              <input type="file" accept=".csv" onChange={handleUpload} disabled={uploading} />
              {uploading && <p className="text-sm text-gray-500 mt-2">Uploading...</p>}
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h2 className="text-xl font-semibold mb-3">Students</h2>
              {data && data.students.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 border-b">
                        <th className="py-2 pr-4">Name</th>
                        <th className="py-2 pr-4">Enrollment No.</th>
                        <th className="py-2 pr-4">Branch</th>
                        <th className="py-2 pr-4">CGPA</th>
                        <th className="py-2 pr-4">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.students.map((s) => (
                        <tr key={s.id} className="border-b last:border-0">
                          <td className="py-2 pr-4">{s.name}</td>
                          <td className="py-2 pr-4">{s.enrollment_number}</td>
                          <td className="py-2 pr-4">{s.branch}</td>
                          <td className="py-2 pr-4">{s.cgpa}</td>
                          <td className="py-2 pr-4">{s.is_placed ? 'Placed' : 'Not placed'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-600">No students yet — upload a CSV to get started.</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-3">Jobs on Campus</h2>
                <p className="text-gray-700 mb-2">Browse jobs currently open to your students.</p>
                <Link href="/jobs" className="text-blue-500 hover:underline">View Jobs</Link>
              </div>
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
};

export default CollegeDashboardPage;
