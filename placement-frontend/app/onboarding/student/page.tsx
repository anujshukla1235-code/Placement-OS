'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { OnboardingStepper } from '@/components/OnboardingStepper';
import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { toast } from 'sonner';

function SkillsStep({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="block font-medium mb-2">Skills (comma separated)</label>
      <input
        className="w-full border rounded p-2"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. React, Django, SQL"
      />
    </div>
  );
}

function ResumeStep({ file, onChange }: { file: File | null; onChange: (f: File | null) => void }) {
  return (
    <div>
      <label className="block font-medium mb-2">Upload Resume (PDF only)</label>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => onChange(e.target.files ? e.target.files[0] : null)}
      />
      <p className="mt-1 text-xs text-gray-500">Backend accepts PDF files only.</p>
      {file && <p className="mt-2 text-sm">Selected: {file.name}</p>}
    </div>
  );
}

const steps = ['Skills', 'Resume', 'Review'];

export default function StudentOnboardingPage() {
  const router = useRouter();
  const [current, setCurrent] = useState(0);
  const [skills, setSkills] = useState('');
  const [resume, setResume] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const next = () => setCurrent((s) => Math.min(steps.length - 1, s + 1));
  const prev = () => setCurrent((s) => Math.max(0, s - 1));

  const submit = async () => {
    setLoading(true);
    setError(null);

    try {
      // Real endpoint + method: PUT /students/me/ (students/urls.py -> StudentMeView.put)
      await api.put('/students/me/', { skills: skills.split(',').map((s) => s.trim()).filter(Boolean) });

      if (resume) {
        const fd = new FormData();
        fd.append('resume', resume);
        // Real endpoint: POST /students/resume/upload/ (students/urls.py -> ResumeUploadView), PDF only.
        await api.post('/students/resume/upload/', fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      // On success, navigate to student dashboard
    try { toast.success('Profile updated successfully'); } catch {}
    router.replace('/student-dashboard');
    } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Failed to complete onboarding';
    setError(msg);
    try { toast.error(msg); } catch {}
    } finally {
    setLoading(false);
    }
  };

  return (
    <ProtectedRoute requiredRole="student">
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold">Complete Your Student Profile</h1>
            <LogoutButton />
          </div>

          <OnboardingStepper steps={steps} current={current} />

          <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
          {current === 0 && <SkillsStep value={skills} onChange={setSkills} />}
          {current === 1 && <ResumeStep file={resume} onChange={setResume} />}

          {current === 2 && (
            <div>
              <h3 className="font-semibold mb-2">Review</h3>
              <p className="mb-2"><strong>Skills:</strong> {skills || '—'}</p>
              <p className="mb-2"><strong>Resume:</strong> {resume ? resume.name : 'Not uploaded'}</p>
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
