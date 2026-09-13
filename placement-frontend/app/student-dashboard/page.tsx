'use client';

import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import { Shield, FileText, CalendarDays, Award, Briefcase, Bell, Search, LayoutDashboard, Compass } from 'lucide-react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import api from '@/lib/api';

interface StudentProfile {
  name?: string;
  email?: string;
  enrollment_number?: string;
  branch?: string;
  cgpa?: number | string;
  is_verified?: boolean;
  resume?: string | null;
}

interface Job {
  id: string;
  title: string;
  company_name?: string;
  location?: string;
  ctc?: string;
  min_cgpa?: number;
}

interface Interview {
  id: string;
  company_name?: string;
  role?: string;
  date?: string;
  time?: string;
  scheduled_at?: string;
  mode?: string;
  status?: string;
}

export default function StudentDashboardPage() {
  const [applicationCount, setApplicationCount] = useState<number>(0);
  const [interviewCount, setInterviewCount] = useState<number>(0);
  const [offersCount, setOffersCount] = useState<number>(0);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [suggestedJobs, setSuggestedJobs] = useState<Job[]>([]);
  const [upcomingInterview, setUpcomingInterview] = useState<Interview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, appsRes, interviewRes, jobsRes] = await Promise.allSettled([
          api.get<StudentProfile>('/students/me/'),
          api.get('/jobs/my-applications/'),
          api.get<Interview[]>('/interviews/'),
          api.get('/jobs/?limit=3'),
        ]);

        if (profileRes.status === 'fulfilled' && profileRes.value.data) {
          setProfile(profileRes.value.data);
        }

        if (appsRes.status === 'fulfilled' && appsRes.value.data) {
          const raw = appsRes.value.data;
          const list: any[] = Array.isArray(raw) ? raw : (raw.results || []);
          setApplicationCount(raw.count ?? list.length);
          const offers = list.filter((a) => a.status === 'OFFER' || a.status === 'HIRED').length;
          setOffersCount(offers);
        }

        if (interviewRes.status === 'fulfilled' && interviewRes.value.data) {
          const rawInterviews = Array.isArray(interviewRes.value.data) ? interviewRes.value.data : [];
          setInterviewCount(rawInterviews.length);
          if (rawInterviews.length > 0) {
            setUpcomingInterview(rawInterviews[0]);
          }
        }

        if (jobsRes.status === 'fulfilled' && jobsRes.value.data) {
          const rawJobs = jobsRes.value.data;
          const list: Job[] = Array.isArray(rawJobs) ? rawJobs : (rawJobs.results || []);
          setSuggestedJobs(list.slice(0, 3));
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
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
              <Link href="/interviews" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-indigo-600">
                <CalendarDays className="h-4 w-4" /> Interviews
              </Link>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-slate-500 hover:bg-slate-100">
              <Bell className="h-4 w-4" />
            </button>
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white p-1 pr-3 shadow-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 font-bold text-white text-xs">
                {(profile?.name || profile?.email || 'S').charAt(0).toUpperCase()}
              </div>
              <span className="text-sm font-semibold text-slate-700">
                {profile?.name || profile?.email?.split('@')[0] || 'Student'}
              </span>
            </div>
            <LogoutButton />
          </div>
        </nav>

        {/* Verification Warning Alert */}
        {profile && !profile.is_verified && (
          <div className="mx-auto mt-6 max-w-7xl px-4 sm:px-6 animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="flex items-center gap-3 rounded-2xl bg-orange-50 border border-orange-200 p-4 text-orange-800 shadow-sm">
              <span className="text-lg">⚠️</span>
              <div className="text-sm font-semibold">
                Your profile is not verified by TPO yet. You cannot apply to jobs until verified. Please upload your official marksheets to TPO to request profile verification.
              </div>
            </div>
          </div>
        )}

        {/* Hero Welcome Banner */}
        <div className="relative mx-auto mt-6 max-w-7xl px-4 sm:px-6">
          <div className="overflow-hidden rounded-[2rem] bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 p-8 text-white shadow-xl shadow-indigo-200">
            <div className="relative z-10">
              <h2 className="text-3xl font-extrabold sm:text-4xl">
                Welcome back, {profile?.name || profile?.email?.split('@')[0] || 'Student'}! 👋
              </h2>
              <p className="mt-2 text-indigo-100">Here is real-time tracking of your placement applications and drives.</p>
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
                <p className="text-2xl font-bold text-slate-900">{offersCount}</p>
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
              
              {suggestedJobs.length === 0 ? (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-8 text-center">
                  <Briefcase className="h-10 w-10 text-slate-400 mb-2" />
                  <p className="font-semibold text-slate-700">No active job openings available right now.</p>
                  <p className="text-xs text-slate-500 mt-1 max-w-sm">When companies post eligible drives or openings for your batch, they will appear right here.</p>
                  <Link href="/jobs" className="mt-4 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow transition hover:bg-indigo-700">
                    Browse All Jobs
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {suggestedJobs.map((job) => (
                    <div key={job.id} className="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50/50 p-4 transition-all hover:border-indigo-100 hover:bg-white hover:shadow-md sm:flex-row sm:items-center sm:justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-xl font-bold text-white shadow-inner bg-indigo-600">
                          {job.company_name ? job.company_name.charAt(0).toUpperCase() : 'J'}
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-900">{job.title}</h4>
                          <p className="text-sm font-medium text-slate-500">
                            {job.company_name || 'Hiring Company'} • {job.location || 'Location Flexible'}
                          </p>
                          {job.ctc && (
                            <p className="text-xs font-semibold text-emerald-600 mt-0.5">CTC: {job.ctc}</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <Link href="/jobs" className="rounded-xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">
                          View & Apply
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Sidebar Widgets */}
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-bold text-slate-900">Upcoming Schedule</h3>
              {upcomingInterview ? (
                <div className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-bold text-indigo-900">{upcomingInterview.role || 'Interview'}</p>
                      <p className="mt-1 text-sm font-medium text-indigo-700">
                        {upcomingInterview.company_name || 'Company'} • {upcomingInterview.mode || 'Online'}
                      </p>
                    </div>
                    {upcomingInterview.date && (
                      <div className="flex h-10 w-10 flex-col items-center justify-center rounded-lg bg-white font-bold text-indigo-600 shadow-sm">
                        <span className="text-[10px] uppercase leading-none">Day</span>
                        <span className="text-sm leading-none">{upcomingInterview.date.slice(-2)}</span>
                      </div>
                    )}
                  </div>
                  <Link href="/interviews" className="mt-4 block text-center w-full rounded-lg bg-white py-2 text-sm font-semibold text-indigo-600 shadow-sm transition hover:bg-slate-50 border border-indigo-100">
                    View Interview Details
                  </Link>
                </div>
              ) : (
                <div className="rounded-2xl border border-slate-100 bg-slate-50 p-6 text-center">
                  <CalendarDays className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-700">No interviews scheduled</p>
                  <p className="text-xs text-slate-500 mt-1">Once recruiters shortlist your application, interviews will appear here.</p>
                </div>
              )}
            </div>

            <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-bold text-slate-900">Your Profile Status</h3>
              {(() => {
                let strength = 20;
                if (profile?.name && profile.name.trim() !== '') strength += 20;
                if (profile?.branch && profile?.enrollment_number) strength += 20;
                if (profile?.cgpa && Number(profile.cgpa) > 0) strength += 20;
                if (profile?.resume || profile?.is_verified) strength += 20;
                const score = Math.min(100, strength);
                return (
                  <>
                    <div className="mb-2 flex items-center justify-between text-sm font-bold">
                      <span className="text-slate-700">Profile Strength</span>
                      <span className="text-indigo-600">{score}%</span>
                    </div>
                    <div className="mb-4 h-2 w-full rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-indigo-600 transition-all duration-500" style={{ width: `${score}%` }}></div>
                    </div>
                  </>
                );
              })()}
              <Link href="/onboarding/student" className="block w-full rounded-xl bg-slate-900 py-2.5 text-center text-sm font-semibold text-white transition hover:bg-slate-800">
                Update Profile
              </Link>
            </div>
          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
