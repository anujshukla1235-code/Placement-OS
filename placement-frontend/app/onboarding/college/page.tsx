'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

import api from '@/lib/api';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { OnboardingStepper } from '@/components/OnboardingStepper';
import { toast } from 'sonner';

const steps = ['College Info', 'Review'];

export default function CollegeOnboardingPage() {
  const router = useRouter();
  const [current, setCurrent] = useState(0);
  // Fields match companies/college_views.py CollegeMeView.put exactly.
  const [payload, setPayload] = useState({ college_name: '', tpo_name: '', tpo_phone: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const next = () => setCurrent((s) => Math.min(steps.length - 1, s + 1));
  const prev = () => setCurrent((s) => Math.max(0, s - 1));

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      // Real endpoint + method: PUT /college/me/ (companies/urls_college.py -> CollegeMeView.put)
      await api.put('/college/me/', payload);
      toast.success('College profile updated');
      router.replace('/college-dashboard');
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Unable to save. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute requiredRole="college">
      <div className="min-h-screen bg-gray-100 py-10">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold">Complete Your College Profile</h1>
          </div>

          <OnboardingStepper steps={steps} current={current} />

          <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
            {current === 0 && (
              <div>
                <label className="block font-medium mb-2">College Name</label>
                <input
                  className="w-full border rounded p-2 mb-3"
                  value={payload.college_name}
                  onChange={(e) => setPayload((p) => ({ ...p, college_name: e.target.value }))}
                />

                <label className="block font-medium mb-2">TPO Name</label>
                <input
                  className="w-full border rounded p-2 mb-3"
                  value={payload.tpo_name}
                  onChange={(e) => setPayload((p) => ({ ...p, tpo_name: e.target.value }))}
                />

                <label className="block font-medium mb-2">TPO Phone</label>
                <input
                  className="w-full border rounded p-2"
                  value={payload.tpo_phone}
                  onChange={(e) => setPayload((p) => ({ ...p, tpo_phone: e.target.value }))}
                />
              </div>
            )}

            {current === 1 && (
              <div>
                <h3 className="font-semibold mb-2">Review</h3>
                <p className="mb-2"><strong>College Name:</strong> {payload.college_name || '—'}</p>
                <p className="mb-2"><strong>TPO Name:</strong> {payload.tpo_name || '—'}</p>
                <p className="mb-2"><strong>TPO Phone:</strong> {payload.tpo_phone || '—'}</p>
              </div>
            )}

            {error && <p className="mt-4 text-red-600">{error}</p>}

            <div className="mt-6 flex justify-between">
              <button onClick={prev} disabled={current === 0 || loading} className="px-4 py-2 bg-gray-200 rounded">
                Back
              </button>

              {current < steps.length - 1 ? (
                <button onClick={next} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">
                  Next
                </button>
              ) : (
                <button onClick={submit} disabled={loading} className="px-4 py-2 bg-green-600 text-white rounded">
                  {loading ? 'Saving...' : 'Finish & Go to Dashboard'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
