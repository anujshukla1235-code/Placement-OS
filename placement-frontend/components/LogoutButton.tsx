'use client';

import { useRouter } from 'next/navigation';

import { logoutUser } from '@/lib/auth';

type LogoutButtonProps = {
  className?: string;
  label?: string;
};

export function LogoutButton({ className = '', label = 'Logout' }: LogoutButtonProps) {
  const router = useRouter();

  return (
    <button
      type="button"
      className={className || 'bg-red-500 hover:bg-red-600 text-white font-medium px-4 py-2 rounded-md transition-colors'}
      onClick={() => logoutUser(router)}
    >
      {label}
    </button>
  );
}
