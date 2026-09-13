'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useState } from 'react';
import { type AxiosError } from 'axios';
import api from '@/lib/api';
import { toast } from 'sonner';
import OtpInput from '@/components/OtpInput';

type Role = 'student' | 'company' | 'college';
type FormData = {
  name: string;
  email: string;
  mobile: string;
  password: string;
  role: Role | '';
  org_name: string;
  consent: boolean;
};
type FormErrors = Partial<Record<keyof FormData, string>>;

const roleOptions: { key: Role; title: string }[] = [
  { key: 'student', title: 'Student / Candidate' },
  { key: 'company', title: 'TA/HR Team' },
  { key: 'college', title: 'TPO (Training & Placement Officer)' },
];

function validateCredentials(data: FormData): FormErrors {
  const errors: FormErrors = {};
  if (!data.name.trim()) errors.name = 'Name is required.';
  if (!data.email.trim()) errors.email = 'Email is required.';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) errors.email = 'Enter a valid email address.';
  if (!data.password) errors.password = 'Password is required.';
  else if (data.password.length < 8) errors.password = 'Password must be at least 8 characters.';
  if (!data.role) errors.role = 'Please select your role.';
  if (data.role && data.role !== 'student' && !data.org_name.trim()) {
    errors.org_name = 'Organization/Company name is required.';
  }
  if (!data.consent) {
    errors.consent = 'You must agree to the terms and privacy policy.';
  }
  return errors;
}

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    mobile: '',
    password: '',
    role: '',
    org_name: '',
    consent: false,
  });
  const [errors, setErrors] = useState<FormErrors>({});

  // OTP Step States
  const [otpStep, setOtpStep] = useState(false);
  const [otp, setOtp] = useState('');
  const [userId, setUserId] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState<number>(0);

  useEffect(() => {
    let t: number | undefined;
    if (resendCooldown > 0) {
      t = window.setTimeout(() => setResendCooldown((s) => Math.max(0, s - 1)), 1000);
    }
    return () => {
      if (t) window.clearTimeout(t);
    };
  }, [resendCooldown]);

  const startResendCooldown = () => setResendCooldown(30);

  const updateField = (key: keyof FormData, value: any) => {
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

    // Split name into first and last name
    const nameParts = formData.name.trim().split(' ');
    const first_name = nameParts[0] || '';
    const last_name = nameParts.slice(1).join(' ') || '.'; // default last name if not provided

    const payload = {
      first_name,
      last_name,
      email: formData.email,
      mobile: formData.mobile || undefined,
      password: formData.password,
      role: formData.role.toUpperCase(),
      consent_student_clause7: formData.role === 'student' ? formData.consent : undefined,
      consent_tenant_clause8: formData.role !== 'student' ? formData.consent : undefined,
      org_name: formData.role !== 'student' ? formData.org_name : undefined,
    };

    try {
      const { data } = await api.post('/accounts/register/', payload);
      setUserId(data.user_id);
      setOtpStep(true);
      startResendCooldown();
      if (data.dev_otp) {
        setOtp(data.dev_otp);
        toast.info(`Dev Mode OTP: ${data.dev_otp}`);
      } else {
        toast.success('Registration successful! OTP sent to your email.');
      }
    } catch (err: any) {
      const axiosError = err as AxiosError<any>;
      const serverError = axiosError.response?.data;
      if (serverError && typeof serverError === 'object') {
        const fieldErrors: FormErrors = {};
        Object.keys(serverError).forEach((key) => {
          fieldErrors[key as keyof FormData] = Array.isArray(serverError[key])
            ? serverError[key][0]
            : serverError[key];
        });
        setErrors(fieldErrors);
      } else {
        toast.error(axiosError.response?.data?.error || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      await api.post('/accounts/verify-otp/', {
        user_id: userId,
        otp,
        purpose: 'REGISTER',
      });
      toast.success('Email verified successfully! Please log in.');
      router.replace('/login');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resendOtp = async () => {
    if (!userId) return;
    try {
      const res = await api.post('/accounts/resend-otp/', { user_id: userId, purpose: 'REGISTER' });
      startResendCooldown();
      if (res.data?.dev_otp) {
        setOtp(res.data.dev_otp);
        toast.info(`Dev Mode OTP: ${res.data.dev_otp}`);
      } else {
        toast.success('OTP resent successfully.');
      }
    } catch (e) {
      toast.error('Unable to resend OTP.');
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-10 relative overflow-hidden">
      {/* Background glowing blobs */}
      <div className="absolute top-[0%] left-[20%] h-[500px] w-[500px] rounded-full bg-indigo-300/30 blur-[100px]" />
      
      <div className="mx-auto w-full max-w-md relative z-10 rounded-[2rem] border border-white bg-white/70 p-8 shadow-2xl shadow-indigo-100/50 backdrop-blur-xl">
        
        {otpStep ? (
          <div>
            <div className="mb-8 text-center">
              <h1 className="text-2xl font-extrabold text-slate-900">Verify your Email</h1>
              <p className="mt-2 text-sm text-slate-500">We have sent a 6-digit OTP to {formData.email}</p>
            </div>
            
            <div className="mb-6 flex justify-center">
              <OtpInput value={otp} onChange={setOtp} length={6} autoFocus />
            </div>

            <div className="space-y-4">
              <button
                onClick={verifyOtp}
                disabled={loading || otp.replace(/\s/g, '').length < 6}
                className="w-full rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? 'Verifying...' : 'Verify Email'}
              </button>

              <button
                onClick={resendOtp}
                disabled={resendCooldown > 0}
                className="w-full rounded-xl border border-slate-200 bg-white py-3 text-sm font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                {resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : 'Resend OTP'}
              </button>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => { setOtpStep(false); setOtp(''); setUserId(null); }}
                className="text-sm font-bold text-indigo-600 hover:underline"
              >
                Back to registration
              </button>
            </div>
          </div>
        ) : (
          <form className="space-y-5" onSubmit={completeSignup} noValidate>
            <div className="mb-6 text-center">
              <h1 className="text-2xl font-extrabold text-slate-900">Create your account</h1>
              <p className="mt-2 text-sm text-slate-500">Join Placement OS today</p>
            </div>
            
            <div className="space-y-4">
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

              {/* Conditionally render Organization Name if role is Company or College */}
              {formData.role && formData.role !== 'student' && (
                <InputField
                  label={formData.role === 'company' ? 'Company Name' : 'College Name'}
                  value={formData.org_name}
                  onChange={(value) => updateField('org_name', value)}
                  error={errors.org_name}
                  placeholder={formData.role === 'company' ? 'Zenith Technologies' : 'LNCT College'}
                />
              )}

              <InputField label="Full Name" value={formData.name} onChange={(value) => updateField('name', value)} error={errors.name} placeholder="John Doe" />
              <InputField label="Email Address" type="email" value={formData.email} onChange={(value) => updateField('email', value)} error={errors.email} placeholder="john@example.com" />
              <InputField label="Phone Number (Optional)" value={formData.mobile} onChange={(value) => updateField('mobile', value)} error={errors.mobile} placeholder="+919876543210" />
              <InputField label="Password" type="password" value={formData.password} onChange={(value) => updateField('password', value)} error={errors.password} placeholder="••••••••" />

              {/* GDPR / Legal Consent Box */}
              <label className="flex items-start gap-3 mt-4 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.consent}
                  onChange={(e) => updateField('consent', e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-500 leading-normal">
                  {formData.role === 'student' ? (
                    <>I agree to the <Link href="/terms" className="text-indigo-600 font-semibold hover:underline">Student Placement Agreement (Clause 7)</Link> and privacy terms.</>
                  ) : (
                    <>I agree to the <Link href="/terms" className="text-indigo-600 font-semibold hover:underline">Placement OS Tenant Agreement (Clause 8)</Link> and platform conditions.</>
                  )}
                </span>
              </label>
              {errors.consent && <p className="mt-1.5 text-xs font-semibold text-red-600">{errors.consent}</p>}
            </div>
            
            <div className="mt-6">
              <button type="submit" disabled={loading} className="w-full rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50">
                {loading ? 'Creating account...' : 'Complete Signup'}
              </button>
            </div>
            
            <p className="mt-6 text-center text-sm font-medium text-slate-600">
              Already have an account? <Link href="/login" className="text-indigo-600 hover:underline font-bold">Login</Link>
            </p>
          </form>
        )}
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
