'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LogoutButton } from '@/components/LogoutButton';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Check, X, Shield, Briefcase, MapPin, Award, CheckCircle, HelpCircle, GraduationCap } from 'lucide-react';
import Link from 'next/link';

type Job = {
  id: string;
  title: string;
  description: string;
  company_name?: string;
  ctc?: string;
  location?: string;
  min_cgpa?: number;
  eligibility_branch?: string[];
};

type StudentProfile = {
  cgpa: number;
  branch: string;
  is_verified: boolean;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [companies, setCompanies] = useState<{ id: string; company_name: string }[]>([]);
  const [student, setStudent] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [applying, setApplying] = useState(false);

  // filters
  const [q, setQ] = useState('');
  const [branch, setBranch] = useState('');
  const [company, setCompany] = useState('');
  const [ctcMin, setCtcMin] = useState('');
  const [ctcMax, setCtcMax] = useState('');

  const fetchStudentProfile = async () => {
    try {
      const res = await api.get<StudentProfile>('/students/profile/');
      setStudent(res.data);
    } catch (err) {
      console.error('Failed to load student profile for eligibility check', err);
    }
  };

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

      const res = await api.get<{ results: Job[]; count: number }>('/jobs/', { params });
      setJobs(res.data.results || []);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentProfile();
    fetchCompanies();
    fetchJobs();
  }, []);

  const onSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    fetchJobs();
  };

  // Eligibility Evaluation
  const checkEligibility = (job: Job) => {
    if (!student) return { eligible: false, reasons: { cgpa: false, branch: false, verified: false } };

    const cgpaOk = Number(student.cgpa) >= (job.min_cgpa ?? 0);
    
    let branchOk = true;
    if (job.eligibility_branch && job.eligibility_branch.length > 0) {
      const allowed = job.eligibility_branch.map(b => b.trim().toUpperCase());
      branchOk = allowed.includes(student.branch.trim().toUpperCase());
    }

    const verifiedOk = student.is_verified;

    return {
      eligible: cgpaOk && branchOk && verifiedOk,
      reasons: {
        cgpa: cgpaOk,
        branch: branchOk,
        verified: verifiedOk
      }
    };
  };

  const handleApply = async (jobId: string) => {
    setApplying(true);
    try {
      await api.post(`/jobs/${jobId}/apply/`);
      toast.success('Applied successfully! ATS scoring is in progress.');
      setSelectedJob(null);
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to apply to this job');
    } finally {
      setApplying(false);
    }
  };

  return (
    <ProtectedRoute requiredRole={["student", "tpo"]}>
      <div className="min-h-screen bg-[#F3F4F6] pb-12 font-sans">
        
        {/* Top Navbar */}
        <nav className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-indigo-100 bg-white px-6 shadow-sm">
          <div className="flex items-center gap-10">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-md">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-sm font-bold leading-tight text-slate-900">Placement</h1>
                <p className="text-[10px] font-semibold text-slate-500">OS</p>
              </div>
            </Link>
            
            <div className="hidden items-center gap-6 md:flex">
              <Link href="/student-dashboard" className="text-sm font-medium text-slate-600 hover:text-indigo-600">
                Dashboard
              </Link>
              <Link href="/jobs" className="flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
                <Briefcase className="h-4 w-4" /> Jobs
              </Link>
              <Link href="/applications" className="text-sm font-medium text-slate-600 hover:text-indigo-600">
                Applications
              </Link>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <LogoutButton />
          </div>
        </nav>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <h2 className="text-2xl font-extrabold text-slate-900">Available Jobs</h2>
            
            <form onSubmit={onSearch} className="flex w-full max-w-md items-center gap-2 sm:w-auto">
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search jobs by title or description..." className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-indigo-500" />
              <button type="submit" className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700">Search</button>
            </form>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
            
            {/* Sidebar Filters */}
            <aside className="lg:col-span-1">
              <div className="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Filters</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="mb-1.5 block text-xs font-bold text-slate-600">Branch</label>
                    <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full rounded-xl border border-slate-200 p-2.5 text-sm outline-none">
                      <option value="">Any</option>
                      <option value="CSE">CSE</option>
                      <option value="ECE">ECE</option>
                      <option value="ME">ME</option>
                      <option value="CE">CE</option>
                    </select>
                  </div>

                  <div>
                    <label className="mb-1.5 block text-xs font-bold text-slate-600">Company</label>
                    <select value={company} onChange={(e) => setCompany(e.target.value)} className="w-full rounded-xl border border-slate-200 p-2.5 text-sm outline-none">
                      <option value="">Any</option>
                      {companies.map((c) => (
                        <option key={c.id} value={c.id}>{c.company_name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="mb-1.5 block text-xs font-bold text-slate-600">CTC Range</label>
                    <div className="flex gap-2">
                      <input value={ctcMin} onChange={(e) => setCtcMin(e.target.value)} placeholder="Min" className="w-full rounded-xl border border-slate-200 p-2 text-xs outline-none" />
                      <input value={ctcMax} onChange={(e) => setCtcMax(e.target.value)} placeholder="Max" className="w-full rounded-xl border border-slate-200 p-2 text-xs outline-none" />
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <button onClick={() => { setQ(''); setBranch(''); setCompany(''); setCtcMin(''); setCtcMax(''); fetchJobs(); }} className="w-full rounded-xl bg-slate-100 py-2.5 text-xs font-bold text-slate-600 hover:bg-slate-200">Clear</button>
                    <button onClick={(e) => { e.preventDefault(); fetchJobs(); }} className="w-full rounded-xl bg-indigo-600 py-2.5 text-xs font-bold text-white hover:bg-indigo-700">Apply</button>
                  </div>
                </div>
              </div>
            </aside>

            {/* Jobs List */}
            <main className="lg:col-span-3">
              {loading && (
                <div className="flex h-40 items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600" />
                </div>
              )}
              {error && <p className="rounded-xl bg-red-50 p-4 text-sm font-semibold text-red-600">{error}</p>}

              <div className="grid grid-cols-1 gap-4">
                {jobs.length === 0 && !loading ? (
                  <div className="rounded-3xl bg-white p-12 text-center shadow-sm">
                    <p className="text-slate-500 font-medium">No active jobs matched your criteria.</p>
                  </div>
                ) : (
                  jobs.map((j) => (
                    <div key={j.id} className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm transition hover:shadow-md">
                      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">{j.title}</h3>
                          <p className="text-sm font-medium text-indigo-600 mb-3">{j.company_name}</p>
                          <p className="text-sm text-slate-500 line-clamp-2 max-w-2xl">{j.description}</p>
                        </div>
                        <div className="text-right">
                          <span className="inline-block rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                            CTC: {j.ctc || '—'}
                          </span>
                          <p className="mt-2 text-xs font-medium text-slate-400">{j.location || 'Remote'}</p>
                        </div>
                      </div>
                      <div className="mt-6 flex items-center justify-between border-t border-slate-50 pt-4">
                        <button onClick={() => setSelectedJob(j)} className="rounded-xl border border-slate-200 bg-white px-5 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50">
                          View Details & Eligibility
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </main>
          </div>
        </div>

        {/* Job Details & Eligibility Checklist Modal */}
        {selectedJob && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-3xl border border-white bg-white/95 p-6 shadow-2xl animate-in fade-in zoom-in duration-300">
              
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-slate-900">{selectedJob.title}</h3>
                  <p className="text-sm font-semibold text-indigo-600">{selectedJob.company_name}</p>
                </div>
                <button onClick={() => setSelectedJob(null)} className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200">
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Job Metadata */}
              <div className="grid grid-cols-2 gap-4 rounded-2xl bg-slate-50 p-4 mb-6">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-slate-400" />
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Location</p>
                    <p className="text-xs font-bold text-slate-700">{selectedJob.location || 'Remote'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="h-4 w-4 text-emerald-500" />
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">CTC Package</p>
                    <p className="text-xs font-bold text-emerald-700">{selectedJob.ctc || '—'}</p>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="mb-6">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Job Description</h4>
                <p className="text-sm text-slate-600 max-h-40 overflow-y-auto leading-relaxed">{selectedJob.description}</p>
              </div>

              {/* Transparent Eligibility Checklist (Reddit/Quora Pain Point Solution) */}
              <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Transparent Eligibility Check</h4>
                
                <div className="space-y-3">
                  
                  {/* CGPA Check */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <GraduationCap className="h-4 w-4 text-slate-400" />
                      <span className="text-sm text-slate-600 font-medium">Minimum CGPA: {selectedJob.min_cgpa ?? 0}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-slate-400 mr-2">(Your CGPA: {student?.cgpa || '0'})</span>
                      {checkEligibility(selectedJob).reasons.cgpa ? (
                        <Check className="h-5 w-5 text-emerald-600 bg-emerald-50 rounded-full p-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-red-600 bg-red-50 rounded-full p-0.5" />
                      )}
                    </div>
                  </div>

                  {/* Branch Check */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4 text-slate-400" />
                      <span className="text-sm text-slate-600 font-medium">Branch: {selectedJob.eligibility_branch?.join(', ') || 'Any'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-slate-400 mr-2">(Your Branch: {student?.branch || 'N/A'})</span>
                      {checkEligibility(selectedJob).reasons.branch ? (
                        <Check className="h-5 w-5 text-emerald-600 bg-emerald-50 rounded-full p-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-red-600 bg-red-50 rounded-full p-0.5" />
                      )}
                    </div>
                  </div>

                  {/* Profile Verification Check */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-slate-400" />
                      <span className="text-sm text-slate-600 font-medium">TPO Verification Lock</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-slate-400 mr-2">{student?.is_verified ? 'Verified' : 'Unverified'}</span>
                      {checkEligibility(selectedJob).reasons.verified ? (
                        <Check className="h-5 w-5 text-emerald-600 bg-emerald-50 rounded-full p-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-red-600 bg-red-50 rounded-full p-0.5" />
                      )}
                    </div>
                  </div>

                </div>

                {!student?.is_verified && (
                  <div className="mt-4 rounded-xl bg-orange-50 p-3 text-xs text-orange-700">
                    Your profile is currently unverified. Please upload your official marksheets to TPO and request profile verification.
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button onClick={() => setSelectedJob(null)} className="w-full rounded-xl bg-slate-100 py-3 text-sm font-semibold text-slate-600 hover:bg-slate-200">
                  Cancel
                </button>
                <button
                  disabled={applying || !checkEligibility(selectedJob).eligible}
                  onClick={() => handleApply(selectedJob.id)}
                  className="w-full rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {applying ? 'Applying...' : checkEligibility(selectedJob).eligible ? 'Apply to Job' : 'Not Eligible'}
                </button>
              </div>

            </div>
          </div>
        )}

      </div>
    </ProtectedRoute>
  );
}
