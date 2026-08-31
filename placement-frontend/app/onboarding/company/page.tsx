'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { OnboardingStepper } from '@/components/OnboardingStepper';
import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { toast } from 'sonner';

function InfoStep({ companyName, hrName, website, gstin, onChange }: any) {
  return (
    <div>
      <label className="block font-medium mb-2">Company Name</label>
      <input className="w-full border rounded p-2 mb-3" value={companyName} onChange={(e) => onChange({ company_name: e.target.value })} />

      <label className="block font-medium mb-2">HR Contact Name</label>
      <input className="w-full border rounded p-2 mb-3" value={hrName} onChange={(e) => onChange({ hr_name: e.target.value })} />

      <label className="block font-medium mb-2">Website</label>
      <input className="w-full border rounded p-2 mb-3" value={website} onChange={(e) => onChange({ website: e.target.value })} />

      <label className="block font-medium mb-2">GSTIN (optional)</label>
      <input className="w-full border rounded p-2" value={gstin} onChange={(e) => onChange({ gstin: e.target.value })} />
    </div>
  );
}

// NOTE: the backend Company model (companies/models.py) has no logo field yet — only
// accounts.CompanyProfile does, and that's a separate, currently-unused profile model
// (see the earlier architecture audit re: Company vs CompanyProfile duplication).
// Logo upload is intentionally left out here until that's consolidated, so we don't
// promise a save that silently does nothing.

const steps = ['Company Info', 'Review'];

export default function CompanyOnboardingPage() {
  const router = useRouter();
  const [current, setCurrent] = useState(0);
  const [payload, setPayload] = useState({ company_name: '', hr_name: '', website: '', gstin: '' });
  const [loading, setLoading] = useState(false); // logo upload deferred until backend model supports it
  const [error, setError] = useState<string | null>(null);

  const next = () => setCurrent((s) => Math.min(steps.length - 1, s + 1));
  const prev = () => setCurrent((s) => Math.max(0, s - 1));

  const submit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Real endpoint + method: PUT /companies/me/ (companies/urls.py -> CompanyMeView.put)
      await api.put('/companies/me/', payload);

    try { toast.success('Company profile updated'); } catch {}
    router.replace('/company-dashboard');
    } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Failed to complete onboarding';
    setError(msg);
    try { toast.error(msg); } catch {}
    } finally {
    setLoading(false);
    }
  };

  return (
    <ProtectedRoute requiredRole="company">
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold">Complete Your Company Profile</h1>
            <LogoutButton />
          </div>

          <OnboardingStepper steps={steps} current={current} />

          <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
          {current === 0 && (
            <InfoStep
              companyName={payload.company_name}
              hrName={payload.hr_name}
              website={payload.website}
              gstin={payload.gstin}
              onChange={(next: any) => setPayload((p) => ({ ...p, ...next }))}
            />
          )}

          {current === 1 && (
            <div>
              <h3 className="font-semibold mb-2">Review</h3>
              <p className="mb-2"><strong>Company Name:</strong> {payload.company_name || '—'}</p>
              <p className="mb-2"><strong>HR Contact:</strong> {payload.hr_name || '—'}</p>
              <p className="mb-2"><strong>Website:</strong> {payload.website || '—'}</p>
              <p className="mb-2"><strong>GSTIN:</strong> {payload.gstin || '—'}</p>
            </div>
          )}

          {error && <p className="mt-4 text-red-600">{error}</p>}

          <div className="mt-6 flex justify-between">
            <button onClick={prev} disabled={current === 0 || loading} className="px-4 py-2 bg-gray-200 rounded">
              Back
            </button>

            {current < steps.length - 1 ? (
              <button
                onClick={next}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded"
              >
                Next
              </button>
            ) : (
              <button
                onClick={submit}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded"
              >
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
