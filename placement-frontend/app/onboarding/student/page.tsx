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
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-extrabold text-slate-900">What are your superpowers?</h2>
        <p className="mt-2 text-sm text-slate-500">Add your top skills to stand out to recruiters.</p>
      </div>
      <label className="block">
        <span className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">Your Skills</span>
        <input
          className="w-full rounded-xl border-2 border-slate-200 bg-white/50 px-4 py-3.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white hover:border-slate-300"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="e.g. React, Python, Machine Learning..."
        />
      </label>
      <div className="mt-4 flex flex-wrap gap-2">
        {['React', 'Django', 'SQL', 'Python', 'Java'].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => {
              const currentSkills = value.split(',').map(s => s.trim()).filter(Boolean);
              if (!currentSkills.includes(suggestion)) {
                onChange(currentSkills.length > 0 ? `${value}, ${suggestion}` : suggestion);
              }
            }}
            className="rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-100"
          >
            + {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}

function ResumeStep({ file, onChange }: { file: File | null; onChange: (f: File | null) => void }) {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-extrabold text-slate-900">Upload your Resume</h2>
        <p className="mt-2 text-sm text-slate-500">Let companies see your complete background.</p>
      </div>
      
      <div className="relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-indigo-200 bg-indigo-50/50 p-12 text-center transition hover:bg-indigo-50">
        <input
          type="file"
          accept="application/pdf"
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          onChange={(e) => onChange(e.target.files ? e.target.files[0] : null)}
        />
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 mb-4">
          <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <p className="text-sm font-semibold text-slate-700">
          {file ? file.name : 'Click or drag PDF here to upload'}
        </p>
        {!file && (
          <span className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow">
            Browse Files
          </span>
        )}
        <p className="mt-4 text-xs text-slate-500">Maximum file size: 5MB (PDF only)</p>
      </div>
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
      await api.put('/students/me/', { skills: skills.split(',').map((s) => s.trim()).filter(Boolean) });

      if (resume) {
        const fd = new FormData();
        fd.append('resume', resume);
        await api.post('/students/resume/upload/', fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

    try { toast.success('Profile updated successfully! Welcome aboard 🚀'); } catch {}
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
      <main className="min-h-screen bg-slate-50 relative overflow-hidden flex flex-col">
        <style dangerouslySetInnerHTML={{__html: `
          @keyframes float {
            0% { transform: translate(0px, 0px) scale(1); }
            33% { transform: translate(30px, -50px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.9); }
            100% { transform: translate(0px, 0px) scale(1); }
          }
          .animate-float {
            animation: float 12s ease-in-out infinite;
          }
          .animate-float-delayed {
            animation: float 14s ease-in-out infinite;
            animation-delay: 2s;
          }
          .animate-float-slow {
            animation: float 16s ease-in-out infinite;
            animation-delay: 1s;
          }
        `}} />

        {/* Large background glows */}
        <div className="absolute top-[-10%] left-[-10%] h-[500px] w-[500px] rounded-full bg-blue-300/20 blur-[100px] animate-float pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-fuchsia-300/20 blur-[100px] animate-float-delayed pointer-events-none" />
        <div className="absolute top-[40%] right-[20%] h-[300px] w-[300px] rounded-full bg-indigo-300/20 blur-[80px] animate-float-slow pointer-events-none" />
        
        {/* Floating Bubble/Orchid Particles */}
        <div className="absolute top-[20%] left-[15%] h-32 w-32 rounded-full bg-fuchsia-400/20 blur-[20px] animate-float-slow pointer-events-none" />
        <div className="absolute bottom-[30%] left-[25%] h-24 w-24 rounded-full bg-pink-400/20 blur-[15px] animate-float pointer-events-none" />
        <div className="absolute top-[30%] right-[15%] h-40 w-40 rounded-full bg-purple-400/20 blur-[25px] animate-float-delayed pointer-events-none" />
        <div className="absolute bottom-[15%] right-[35%] h-20 w-20 rounded-full bg-blue-400/20 blur-[10px] animate-float-slow pointer-events-none" />
        <div className="absolute top-[10%] right-[40%] h-16 w-16 rounded-full bg-fuchsia-500/15 blur-[8px] animate-float pointer-events-none" />
        <div className="absolute bottom-[40%] right-[5%] h-28 w-28 rounded-full bg-indigo-400/20 blur-[15px] animate-float-delayed pointer-events-none" />

        {/* Header */}
        <header className="relative z-20 w-full px-6 py-4 flex items-center justify-between border-b border-slate-200/50 bg-white/50 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-lg" />
            <h1 className="text-xl font-bold tracking-tight text-slate-900">Placement OS</h1>
          </div>
          <LogoutButton />
        </header>

        <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-4">
          <div className="w-full max-w-2xl mb-8">
            <OnboardingStepper steps={steps} current={current} />
          </div>

          <div className="w-full max-w-lg rounded-[2rem] border border-white bg-white/70 p-8 shadow-2xl shadow-indigo-100/50 backdrop-blur-xl">
            {current === 0 && <SkillsStep value={skills} onChange={setSkills} />}
            {current === 1 && <ResumeStep file={resume} onChange={setResume} />}

            {current === 2 && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 text-center">
                <div className="mb-6">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-600">
                    <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-extrabold text-slate-900">You're all set!</h2>
                  <p className="mt-2 text-sm text-slate-500">Review your details before jumping into the dashboard.</p>
                </div>
                
                <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 text-left space-y-3">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Skills</span>
                    <p className="mt-1 font-medium text-slate-900">{skills || 'None provided'}</p>
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Resume</span>
                    <p className="mt-1 font-medium text-slate-900">{resume ? resume.name : 'Not uploaded'}</p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-medium text-red-600 border border-red-100 text-center">
                {error}
              </div>
            )}

            <div className="mt-8 flex gap-4">
              <button
                onClick={prev}
                disabled={current === 0 || loading}
                className="flex-1 rounded-xl border border-slate-200 bg-white py-3.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Back
              </button>

              {current < steps.length - 1 ? (
                <button
                  onClick={next}
                  disabled={loading || (current === 0 && !skills) || (current === 1 && !resume)}
                  className="flex-[2] rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue
                </button>
              ) : (
                <button
                  onClick={submit}
                  disabled={loading}
                  className="flex-[2] rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Taking off...' : 'Go to Dashboard 🚀'}
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </ProtectedRoute>
  );
}
