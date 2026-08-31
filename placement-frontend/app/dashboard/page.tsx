'use client';

type Job = { title: string; company: string; match: number; location: string };
type Interview = { role: string; company: string; date: string; time: string };

const jobs: Job[] = [
  { title: 'Frontend Developer Intern', company: 'TechNova', match: 92, location: 'Bengaluru' },
  { title: 'React Engineer', company: 'CloudAxis', match: 88, location: 'Remote' },
  { title: 'UI Developer', company: 'PixelForge', match: 84, location: 'Hyderabad' },
];
const interviews: Interview[] = [
  { role: 'SDE Intern', company: 'TechNova', date: '28 Aug 2026', time: '10:30 AM' },
  { role: 'Frontend Intern', company: 'CloudAxis', date: '30 Aug 2026', time: '02:00 PM' },
];

const score = 84;
const circumference = 2 * Math.PI * 42;
const dashOffset = circumference - (score / 100) * circumference;

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-6 lg:p-8">
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: 'Applications Sent', value: '34' },
          { label: 'Interviews Scheduled', value: '7' },
          { label: 'Offers', value: '2' },
        ].map((metric) => (
          <div key={metric.label} className="rounded-2xl border border-indigo-100 bg-white p-5 shadow-sm shadow-indigo-100/30">
            <p className="text-sm text-slate-500">{metric.label}</p>
            <p className="mt-2 text-3xl font-bold text-indigo-700">{metric.value}</p>
          </div>
        ))}
      </section>

      <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-12">
        <aside className="space-y-6 xl:col-span-3">
          <div className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm shadow-indigo-100/30">
            <div className="flex items-center gap-4">
              <img src="https://i.pravatar.cc/120?img=32" alt="Student" className="h-14 w-14 rounded-full object-cover" />
              <div>
                <h2 className="font-semibold text-slate-900">Aarav Sharma</h2>
                <p className="text-sm text-slate-500">B.Tech CSE • Final Year</p>
              </div>
            </div>
            <div className="mt-5 rounded-xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Skills</p>
              <p className="mt-1 text-sm font-medium text-slate-700">React, Next.js, Node.js, SQL</p>
            </div>
          </div>

          <div className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm shadow-indigo-100/30">
            <p className="text-sm text-slate-500">ATS Resume Score</p>
            <div className="mt-4 flex items-center justify-center">
              <div className="relative h-28 w-28">
                <svg className="h-28 w-28 -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" stroke="#e2e8f0" strokeWidth="9" fill="none" />
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    stroke="#4f46e5"
                    strokeWidth="9"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashOffset}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-indigo-700">{score}%</div>
              </div>
            </div>
            <p className="mt-3 text-center text-sm text-slate-500">Great profile strength. Keep improving projects.</p>
          </div>
        </aside>

        <section className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm shadow-indigo-100/30 xl:col-span-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Job Suggestions for You</h3>
            <span className="text-sm font-medium text-indigo-600">AI Matched</span>
          </div>
          <div className="space-y-4">
            {jobs.map((job) => (
              <article key={job.title + job.company} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="font-semibold text-slate-900">{job.title}</h4>
                    <p className="text-sm text-slate-500">{job.company} • {job.location}</p>
                  </div>
                  <span className="rounded-full bg-indigo-100 px-3 py-1 text-sm font-semibold text-indigo-700">{job.match}% Match</span>
                </div>
                <button className="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700">
                  View Job
                </button>
              </article>
            ))}
          </div>
        </section>

        <aside className="space-y-6 xl:col-span-3">
          <div className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm shadow-indigo-100/30">
            <h3 className="text-lg font-semibold text-slate-900">Interview Tips</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>• Prepare 2 project stories with impact metrics.</li>
              <li>• Revise DSA patterns: arrays, graphs, DP basics.</li>
              <li>• Practice concise STAR-format answers.</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-indigo-100 bg-white p-6 shadow-sm shadow-indigo-100/30">
            <h3 className="text-lg font-semibold text-slate-900">Upcoming Interviews</h3>
            <div className="mt-3 space-y-3">
              {interviews.map((item) => (
                <div key={item.role + item.company} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                  <p className="font-medium text-slate-900">{item.role}</p>
                  <p className="text-sm text-slate-500">{item.company}</p>
                  <p className="mt-1 text-xs font-medium text-indigo-600">{item.date} • {item.time}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
