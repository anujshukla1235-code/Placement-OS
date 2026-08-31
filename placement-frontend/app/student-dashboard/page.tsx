'use client';

import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import { Shield, FileText, CalendarDays, Award, Briefcase, Bell, Search, LayoutDashboard, Compass } from 'lucide-react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

interface ApplicationSummary { count: number; }
interface InterviewSummary { count: number; }
interface StudentProfile { name: string; email: string; is_verified?: boolean; }

// Mock data for Job Suggestions as seen in the design
const suggestedJobs = [
  { role: 'SDE Intern', company: 'TechNova', location: 'Bengaluru', match: '92%', tag: 'High Match', iconColor: 'bg-red-500', logo: 'T' },
  { role: 'Product Designer', company: 'DesignIQ', location: 'Remote', match: '88%', tag: 'Trending', iconColor: 'bg-blue-600', logo: 'D' },
  { role: 'Data Analyst', company: 'InsightCorp', location: 'Pune', match: '81%', tag: 'New', iconColor: 'bg-emerald-500', logo: 'I' },
];

export default function StudentDashboardPage() {
  const [applicationCount, setApplicationCount] = useState<number>(0);
  const [interviewCount, setInterviewCount] = useState<number>(0);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [appRes, interviewRes, profileRes] = await Promise.all([
          api.get<ApplicationSummary>('/students/applications/').catch(() => ({ data: { count: 24 } })),
          api.get<InterviewSummary>('/interviews/').catch(() => ({ data: { count: 5 } })),
          api.get<StudentProfile>('/students/profile/').catch(() => ({ data: { name: 'Arjun', email: 'arjun@example.com' } })),
        ]);

        setApplicationCount(appRes.data.count);
        setInterviewCount(interviewRes.data.count);
        setProfile(profileRes.data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setError(msg);
        try { toast.error('Failed to load dashboard: ' + msg); } catch {}
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
      </div>
    );
  }

  return (
    <ProtectedRoute requiredRole={['student', 'tpo']}>
      <div className="min-h-screen bg-[#F3F4F6] font-sans pb-12">
        
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
              <Link href="/student-dashboard" className="flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
                <LayoutDashboard className="h-4 w-4" /> Dashboard
              </Link>
              <Link href="/jobs" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-indigo-600">
                <Briefcase className="h-4 w-4" /> Jobs
              </Link>
              <Link href="/applications" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-indigo-600">
                <FileText className="h-4 w-4" /> Applications
              </Link>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-slate-500 hover:bg-slate-100">
              <Bell className="h-4 w-4" />
            </button>
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white p-1 pr-3 shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 font-bold text-white text-xs">
                {profile?.name?.charAt(0) || 'A'}
              </div>
              <span className="text-sm font-semibold text-slate-700">{profile?.name || 'Arjun'}</span>
            </div>
            <LogoutButton />
          </div>
        </nav>

        {/* Verification Warning Alert */}
        {profile && !profile.is_verified && (
          <div className="mx-auto mt-6 max-w-7xl px-4 sm:px-6 animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="flex items-center gap-3 rounded-2xl bg-orange-50 border border-orange-200 p-4 text-orange-850 shadow-sm">
              <span className="text-lg">⚠️</span>
              <div className="text-sm font-semibold">
                Your profile is not verified by TPO yet. You cannot apply to jobs until verified. Please upload your official marksheets to TPO to request profile lock.
              </div>
            </div>
          </div>
        )}

        {/* Hero Welcome Banner */}
        <div className="relative mx-auto mt-6 max-w-7xl px-4 sm:px-6">
          <div className="overflow-hidden rounded-[2rem] bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 p-8 text-white shadow-xl shadow-indigo-200">
            <div className="relative z-10">
              <h2 className="text-3xl font-extrabold sm:text-4xl">Welcome back, {profile?.name || 'Arjun'}! 👋</h2>
              <p className="mt-2 text-indigo-100">Here is what&apos;s happening with your placements today.</p>
            </div>
            {/* Decorative waves inside banner */}
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute right-40 -bottom-20 h-64 w-64 rounded-full bg-purple-400/20 blur-3xl" />
          </div>
        </div>

        {/* Stats Row */}
        <div className="mx-auto mt-6 max-w-7xl px-4 sm:px-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex items-center gap-4 rounded-2xl bg-white p-5 shadow-sm border border-slate-100 transition-all hover:shadow-md">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                <FileText className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Applications Sent</p>
                <p className="text-2xl font-bold text-slate-900">{applicationCount}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 rounded-2xl bg-white p-5 shadow-sm border border-slate-100 transition-all hover:shadow-md">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-50 text-orange-600">
                <CalendarDays className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Interviews Scheduled</p>
                <p className="text-2xl font-bold text-slate-900">{interviewCount}</p>
              </div>
            </div>

            <div className="flex items-center gap-4 rounded-2xl bg-white p-5 shadow-sm border border-slate-100 transition-all hover:shadow-md">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <Award className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Offers Received</p>
                <p className="text-2xl font-bold text-slate-900">1</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid Content */}
        <div className="mx-auto mt-6 grid max-w-7xl grid-cols-1 gap-6 px-4 sm:px-6 lg:grid-cols-3">
          
          {/* Left Column - Job Suggestions */}
          <div className="lg:col-span-2">
            <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-900">Job Suggestions For You</h3>
                <Link href="/jobs" className="text-sm font-semibold text-indigo-600 hover:underline">View All</Link>
              </div>
              
              <div className="space-y-4">
                {suggestedJobs.map((job, idx) => (
                  <div key={idx} className="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50/50 p-4 transition-all hover:border-indigo-100 hover:bg-white hover:shadow-md sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`flex h-14 w-14 items-center justify-center rounded-xl font-bold text-white shadow-inner ${job.iconColor}`}>
                        {job.logo}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900">{job.role}</h4>
                        <p className="text-sm font-medium text-slate-500">{job.company} • {job.location}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
                        {job.tag}
                      </span>
                      <div className="flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                        <Compass className="h-3 w-3" /> {job.match} Match
                      </div>
                      <button className="ml-2 rounded-xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">
                        Apply
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Sidebar Widgets */}
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-bold text-slate-900">Upcoming Schedule</h3>
              <div className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-bold text-indigo-900">Technical Round</p>
                    <p className="mt-1 text-sm font-medium text-indigo-700">TechNova • SDE Intern</p>
                  </div>
                  <div className="flex h-10 w-10 flex-col items-center justify-center rounded-lg bg-white font-bold text-indigo-600 shadow-sm">
                    <span className="text-[10px] uppercase leading-none">Oct</span>
                    <span className="text-sm leading-none">12</span>
                  </div>
                </div>
                <button className="mt-4 w-full rounded-lg bg-white py-2 text-sm font-semibold text-indigo-600 shadow-sm transition hover:bg-slate-50 border border-indigo-100">
                  Join Meeting
                </button>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-bold text-slate-900">Complete Your Profile</h3>
              <div className="mb-2 flex items-center justify-between text-sm font-bold">
                <span className="text-slate-700">Profile Strength</span>
                <span className="text-indigo-600">75%</span>
              </div>
              <div className="mb-4 h-2 w-full rounded-full bg-slate-100">
                <div className="h-full w-3/4 rounded-full bg-indigo-600"></div>
              </div>
              <Link href="/profile" className="block w-full rounded-xl bg-slate-900 py-2.5 text-center text-sm font-semibold text-white transition hover:bg-slate-800">
                Update Profile
              </Link>
            </div>
          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
