'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAccessToken, getStoredUserRole, getRoleBasedRedirectPath } from '@/lib/auth';
import { Shield, GraduationCap, Building2, CheckCircle2, Sparkles, Calendar, Lock, Cpu } from 'lucide-react';
import api from '@/lib/api';

interface ActiveOpportunity {
  id: string;
  title: string;
  company_name?: string;
  location?: string;
}

export default function HomePage() {
  const router = useRouter();
  const [activeJobs, setActiveJobs] = useState<ActiveOpportunity[]>([]);

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      router.replace(getRoleBasedRedirectPath(getStoredUserRole()));
      return;
    }

    api.get('/jobs/?limit=4').then((res) => {
      const raw = res.data;
      const list = Array.isArray(raw) ? raw : (raw.results || []);
      if (list.length > 0) {
        setActiveJobs(list);
      }
    }).catch(() => {
      // unauthenticated or no jobs yet
    });
  }, [router]);

  return (
    <main className="relative min-h-screen bg-slate-50 flex items-center justify-center overflow-hidden p-4 sm:p-8">
      {/* Background glowing blobs */}
      <div className="absolute top-[-10%] left-[-10%] h-96 w-96 rounded-full bg-indigo-300/40 blur-3xl" />
      <div className="absolute bottom-[-10%] right-[-10%] h-96 w-96 rounded-full bg-purple-300/40 blur-3xl" />
      <div className="absolute top-[20%] right-[10%] h-72 w-72 rounded-full bg-blue-200/40 blur-3xl" />

      {/* Main Card mimicking the design screen */}
      <div className="relative flex w-full max-w-[1200px] flex-col overflow-hidden rounded-[2rem] bg-white/60 p-6 shadow-2xl shadow-indigo-200/50 backdrop-blur-xl sm:p-10 lg:flex-row lg:items-center">
        
        {/* Left Content Area */}
        <div className="flex-1 space-y-8">
          {/* Header */}
          <header className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold leading-none text-slate-900">Placement</h1>
                <p className="text-sm font-semibold text-slate-600">OS</p>
              </div>
            </div>
            <Link href="/login" className="rounded-full bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-700">
              Login / Signup
            </Link>
          </header>

          {/* Hero Text */}
          <div className="space-y-4 pt-8">
            <h2 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Placement OS
            </h2>
            <p className="text-lg font-medium text-slate-600 sm:text-xl">
              India&apos;s Smartest Campus Placement Platform
            </p>
            <p className="max-w-lg text-sm text-slate-500">
              Streamline student placements with intelligent matching, real-time interview tracking, and outcomes analytics for colleges and recruiters.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-wrap gap-4 pt-2">
            <Link href="/signup" className="rounded-xl bg-indigo-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 hover:shadow-indigo-600/40">
              Get Started Free
            </Link>
            <Link href="/about" className="flex items-center justify-center gap-2 rounded-xl border-2 border-slate-200 bg-white px-8 py-3.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-white text-[10px]">▶</span>
              Book a Demo
            </Link>
          </div>

          {/* Stats Row */}
          <div className="flex flex-wrap gap-4 pt-6">
            <div className="flex items-center gap-4 rounded-2xl bg-white/80 p-4 shadow-sm backdrop-blur-sm border border-white">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                <GraduationCap className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xl font-bold text-slate-900">1000+</p>
                <p className="text-sm font-medium text-slate-500">Students</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 rounded-2xl bg-white/80 p-4 shadow-sm backdrop-blur-sm border border-white">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <Building2 className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xl font-bold text-slate-900">50+</p>
                <p className="text-sm font-medium text-slate-500">Companies</p>
              </div>
            </div>

            <div className="flex items-center gap-4 rounded-2xl bg-emerald-50 p-4 shadow-sm border border-emerald-100">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xl font-bold text-emerald-700">98%</p>
                <p className="text-sm font-medium text-emerald-600">Placement</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Floating Card Overlay */}
        <div className="mt-12 lg:ml-12 lg:mt-0 lg:w-[380px] shrink-0">
          <div className="relative overflow-hidden rounded-3xl border border-white bg-white/70 p-6 shadow-2xl backdrop-blur-md">
            <div className="mb-6 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">
                {activeJobs.length > 0 ? 'Active Opportunities' : 'Platform Capabilities'}
              </h3>
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-600">
                {activeJobs.length > 0 ? activeJobs.length : '4'}
              </span>
            </div>
            
            <div className="space-y-4">
              {activeJobs.length > 0 ? (
                activeJobs.map((job) => (
                  <div key={job.id} className="flex items-center gap-4 rounded-2xl bg-white p-3 shadow-sm transition hover:shadow-md border border-slate-100">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-indigo-600">
                      {job.company_name ? job.company_name.charAt(0).toUpperCase() : 'J'}
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h4 className="truncate font-semibold text-slate-900">{job.title}</h4>
                      <p className="truncate text-xs font-medium text-slate-500">{job.company_name || 'Hiring Company'} • {job.location || 'Flexible'}</p>
                    </div>
                  </div>
                ))
              ) : (
                <>
                  <div className="flex items-center gap-4 rounded-2xl bg-white p-3 shadow-sm transition hover:shadow-md border border-slate-100">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-indigo-600">
                      <Sparkles className="h-6 w-6" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h4 className="truncate font-semibold text-slate-900">AI ATS Scoring</h4>
                      <p className="truncate text-xs font-medium text-slate-500">Automated match & feedback</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 rounded-2xl bg-white p-3 shadow-sm transition hover:shadow-md border border-slate-100">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-blue-600">
                      <Calendar className="h-6 w-6" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h4 className="truncate font-semibold text-slate-900">Real-Time Interviews</h4>
                      <p className="truncate text-xs font-medium text-slate-500">Slot tracking & reminders</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 rounded-2xl bg-white p-3 shadow-sm transition hover:shadow-md border border-slate-100">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-emerald-600">
                      <Lock className="h-6 w-6" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h4 className="truncate font-semibold text-slate-900">Tenant Data Isolation</h4>
                      <p className="truncate text-xs font-medium text-slate-500">Enterprise security & MFA</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 rounded-2xl bg-white p-3 shadow-sm transition hover:shadow-md border border-slate-100">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-purple-600">
                      <Cpu className="h-6 w-6" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <h4 className="truncate font-semibold text-slate-900">TPO Verification</h4>
                      <p className="truncate text-xs font-medium text-slate-500">Official student marksheets</p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
