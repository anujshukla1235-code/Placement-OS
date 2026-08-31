'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import api from '@/lib/api';
import OtpInput from '@/components/OtpInput';
import { toast } from 'sonner';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState('');
  const [userId, setUserId] = useState<string | null>(null);
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const requestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Real endpoint: POST /accounts/forgot-password/ { email }
      const res = await api.post('/accounts/forgot-password/', { email });
      // Backend intentionally doesn't reveal whether the email exists — user_id is only
      // present when it does. Either way we move to the OTP step; a non-existent email
      // will just fail at the reset step with an invalid-OTP error.
      setUserId(res.data?.user_id ?? null);
      setStep(2);
      toast.success('If that email exists, an OTP has been sent.');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) {
      toast.error('Session expired — please request a new OTP.');
      setStep(1);
      return;
    }
    setLoading(true);
    try {
      // Real endpoint: POST /accounts/reset-password/ { user_id, otp, new_password }
      await api.post('/accounts/reset-password/', { user_id: userId, otp, new_password: newPassword });
      toast.success('Password updated. Please log in.');
      router.push('/login');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Unable to reset password. Check your OTP.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Reset Password</h2>

        {step === 1 && (
          <form onSubmit={requestOtp}>
            <label className="block text-gray-700 text-sm font-bold mb-2">Email</label>
            <input
              type="email"
              className="w-full border rounded py-2 px-3 mb-4"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={resetPassword}>
            <p className="mb-4 text-sm text-gray-600">Enter the OTP sent to <strong>{email}</strong> and your new password.</p>
            <div className="mb-4 flex justify-center">
              <OtpInput value={otp} onChange={setOtp} length={6} autoFocus />
            </div>
            <label className="block text-gray-700 text-sm font-bold mb-2">New Password</label>
            <input
              type="password"
              className="w-full border rounded py-2 px-3 mb-4"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              required
            />
            <button
              type="submit"
              disabled={loading || otp.replace(/\s/g, '').length < 6}
              className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              {loading ? 'Updating...' : 'Reset Password'}
            </button>
          </form>
        )}

        <p className="mt-4 text-center text-sm text-gray-600">
          Remembered your password? <Link href="/login" className="text-blue-600 hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
