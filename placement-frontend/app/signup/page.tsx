'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useMemo, useState } from 'react';

type Role = 'student' | 'company' | 'college';
type FormData = { name: string; email: string; password: string; role: Role | '' };
type FormErrors = Partial<Record<keyof FormData, string>>;

const roleOptions: { key: Role; title: string }[] = [
  { key: 'student', title: 'Student / Candidate' },
  { key: 'company', title: 'TA/HR Team' },
  { key: 'college', title: 'TPO (Training & Placement Officer)' },
];

const roleDashboardRoute: Record<Role, string> = {
  student: '/student-dashboard',
  company: '/company-dashboard',
  college: '/college-dashboard',
};

function validateCredentials(data: FormData): FormErrors {
  const errors: FormErrors = {};
  if (!data.name.trim()) errors.name = 'Name is required.';
  if (!data.email.trim()) errors.email = 'Email is required.';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) errors.email = 'Enter a valid email address.';
  if (!data.password) errors.password = 'Password is required.';
  else if (data.password.length < 8) errors.password = 'Password must be at least 8 characters.';
  if (!data.role) errors.role = 'Please select your role.';
  return errors;
}

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({ name: '', email: '', password: '', role: '' });
  const [errors, setErrors] = useState<FormErrors>({});

  const updateField = (key: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const completeSignup = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextErrors = validateCredentials(formData);
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setLoading(true);
    try {
      const destination = roleDashboardRoute[formData.role as Role];
      router.replace(destination);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-10 relative overflow-hidden">
      {/* Background glowing blobs */}
      <div className="absolute top-[0%] left-[20%] h-[500px] w-[500px] rounded-full bg-indigo-300/30 blur-[100px]" />
      
      <div className="mx-auto w-full max-w-md relative z-10 rounded-[2rem] border border-white bg-white/70 p-8 shadow-2xl shadow-indigo-100/50 backdrop-blur-xl">
        
        <form className="space-y-6" onSubmit={completeSignup} noValidate>
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-extrabold text-slate-900">Create your account</h1>
            <p className="mt-2 text-sm text-slate-500">Join Placement OS today</p>
          </div>
          
          <div className="space-y-5">
            {/* Role Dropdown */}
            <label className="block">
              <span className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">I am a</span>
              <div className="relative">
                <select
                  value={formData.role}
                  onChange={(e) => updateField('role', e.target.value)}
                  className={`w-full appearance-none rounded-xl border-2 bg-white/50 px-4 py-3.5 text-sm font-medium text-slate-900 outline-none transition ${
                    errors.role ? 'border-red-400 focus:border-red-500 focus:bg-white' : 'border-slate-200 focus:border-indigo-500 focus:bg-white hover:border-slate-300'
                  }`}
                >
                  <option value="" disabled>Select your role</option>
                  {roleOptions.map((opt) => (
                    <option key={opt.key} value={opt.key}>{opt.title}</option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
                  <svg className="h-4 w-4 fill-current" viewBox="0 0 20 20">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                  </svg>
                </div>
              </div>
              {errors.role && <p className="mt-1.5 text-xs font-semibold text-red-600">{errors.role}</p>}
            </label>

            <InputField label="Full Name" value={formData.name} onChange={(value) => updateField('name', value)} error={errors.name} placeholder="John Doe" />
            <InputField label="Email Address" type="email" value={formData.email} onChange={(value) => updateField('email', value)} error={errors.email} placeholder="john@example.com" />
            <InputField label="Password" type="password" value={formData.password} onChange={(value) => updateField('password', value)} error={errors.password} placeholder="••••••••" />
          </div>
          
          <div className="mt-8">
            <button type="submit" disabled={loading} className="w-full rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50">
              {loading ? 'Creating account...' : 'Complete Signup'}
            </button>
          </div>
          
          <p className="mt-6 text-center text-sm font-medium text-slate-600">
            Already have an account? <Link href="/login" className="text-indigo-600 hover:underline font-bold">Login</Link>
          </p>
        </form>
      </div>
    </main>
  );
}

function InputField({ label, value, onChange, error, type = 'text', placeholder }: { label: string; value: string; onChange: (value: string) => void; error?: string; type?: string; placeholder?: string }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className={`w-full rounded-xl border-2 bg-white/50 px-4 py-3.5 text-sm font-medium text-slate-900 outline-none transition placeholder:text-slate-400 ${
          error ? 'border-red-400 focus:border-red-500 focus:bg-white' : 'border-slate-200 focus:border-indigo-500 focus:bg-white hover:border-slate-300'
        }`}
      />
      {error && <p className="mt-1.5 text-xs font-semibold text-red-600">{error}</p>}
    </label>
  );
}
