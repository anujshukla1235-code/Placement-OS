'use client';

import { type AxiosError } from 'axios';
import React, { useState, useEffect, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

import api from '@/lib/api';
import { getUserRoleFromToken, saveAuthSession, getRoleBasedRedirectPath } from '@/lib/auth';
import OtpInput from '@/components/OtpInput';
import { toast } from 'sonner';

type LoginResponse = {
  access?: string;
  access_token?: string;
  accessToken?: string;
  refresh?: string;
  refresh_token?: string;
  refreshToken?: string;
  role?: string;
  userRole?: string;
  user_role?: string;
  error?: string;
  message?: string;
  mfa_required?: boolean;
  user_id?: string;
};

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [mfaStep, setMfaStep] = useState(false);
  const [otp, setOtp] = useState('');
  // Backend identifies the MFA challenge by user_id, not a separate mfa token.
  const [userId, setUserId] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState<number>(0);

  const router = useRouter();

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

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data } = await api.post<LoginResponse>('/accounts/login/', {
        email,
        password,
      });

      // If backend indicates MFA required, enter MFA step
      // Contract: LoginView returns { mfa_required: true, user_id, ... } (see accounts/views.py)
      if (data.mfa_required) {
        setMfaStep(true);
        setUserId((data as any).user_id ?? null);
        startResendCooldown();
        setLoading(false);
        try { toast.success('OTP sent. Check your email.'); } catch {}
        return;
      }

      const accessToken = data.accessToken ?? data.access_token ?? data.access;
      const refreshToken = data.refreshToken ?? data.refresh_token ?? data.refresh;

      if (!accessToken || !refreshToken) {
        setError('Authentication response was incomplete.');
        try { toast.error('Authentication response incomplete.'); } catch {}
        setLoading(false);
        return;
      }

      const role = data.role ?? data.userRole ?? data.user_role ?? getUserRoleFromToken(accessToken) ?? undefined;
      saveAuthSession({ accessToken, refreshToken, role });

      // If backend indicates pending approval, redirect to pending page
      if ((data as any).pending_approval) {
        router.push('/pending-verification');
        return;
      }

      try { toast.success('Logged in successfully'); } catch {}
      router.push(getRoleBasedRedirectPath(role));
    } catch (err) {
      const axiosError = err as AxiosError<LoginResponse>;
      const serverMessage = axiosError.response?.data?.error ?? axiosError.response?.data?.message;
      setError(serverMessage ?? 'Invalid credentials');
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    if (!userId) {
      setError('Session expired. Please log in again.');
      setMfaStep(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Real endpoint + payload contract: POST /accounts/login/verify-mfa/ { user_id, otp }
      const resp = await api.post<LoginResponse>('/accounts/login/verify-mfa/', { user_id: userId, otp });
      const resData = resp.data;

      const accessToken = resData.accessToken ?? resData.access_token ?? resData.access;
      const refreshToken = resData.refreshToken ?? resData.refresh_token ?? resData.refresh;

      if (!accessToken || !refreshToken) {
        setError('Verification did not return tokens.');
        try { toast.error('Verification did not return tokens.'); } catch {}
        setLoading(false);
        return;
      }

      const role = resData.role ?? resData.userRole ?? resData.user_role ?? getUserRoleFromToken(accessToken) ?? undefined;
      saveAuthSession({ accessToken, refreshToken, role });

      if ((resData as any).pending_approval) {
        router.push('/pending-verification');
        return;
      }

      try { toast.success('Logged in successfully'); } catch {}
      router.push(getRoleBasedRedirectPath(role));
    } catch (err) {
      const axiosError = err as AxiosError<LoginResponse>;
      const serverMessage = axiosError.response?.data?.error ?? axiosError.response?.data?.message;
      setError(serverMessage ?? 'OTP verification failed');
      setLoading(false);
    }
  };

  const resendOtp = async () => {
    if (!userId) return;
    setError(null);
    try {
      // Real endpoint + payload contract: POST /accounts/resend-otp/ { user_id, purpose }
      await api.post('/accounts/resend-otp/', { user_id: userId, purpose: 'LOGIN' });
      startResendCooldown();
      try { toast.success('OTP resent'); } catch {}
    } catch (e) {
      setError('Unable to resend OTP.');
      try { toast.error('Unable to resend OTP.'); } catch {}
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}
        {mfaStep ? (
          <div>
            <p className="mb-4 text-gray-700">Enter the 6-digit OTP sent to your email for {email}.</p>
            <div className="mb-4 flex justify-center">
              <OtpInput value={otp} onChange={setOtp} length={6} autoFocus />
            </div>
            <div className="flex gap-2 mb-4">
              <button
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex-1"
                onClick={async (e) => { e.preventDefault(); await verifyOtp(); }}
                disabled={loading || otp.replace(/\s/g,'').length < 6}
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
              <button
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                onClick={(e) => { e.preventDefault(); resendOtp(); }}
                disabled={resendCooldown > 0}
              >
                {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP'}
              </button>
            </div>
            <div className="text-center">
              <button
                className="text-sm text-blue-600 hover:underline"
                onClick={(e) => { e.preventDefault(); setMfaStep(false); setOtp(''); setUserId(null); }}
              >Back to password login</button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                Email
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                Password
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>
            <div className="flex items-center justify-between">
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
                type="submit"
                disabled={loading}
              >
                {loading ? 'Logging in...' : 'Sign In'}
              </button>
            </div>
          </form>
        )}
          <p className="mt-2 text-center text-sm"><Link href="/forgot-password" className="text-blue-600 hover:underline">Forgot password?</Link></p>
          <p className="mt-4 text-center text-sm text-gray-600">Don't have an account? <Link href="/signup" className="text-blue-600 hover:underline">Sign up</Link></p>
      </div>
    </div>
  );
};

export default LoginPage;
