'use client';

import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

import { getAccessToken, getStoredUserRole, getUserRoleFromToken, getRoleBasedRedirectPath, type UserRole } from '@/lib/auth';
import api from '@/lib/api';

type ProtectedRouteProps = {
  children: ReactNode;
  requiredRole?: UserRole | UserRole[];
  fallbackPath?: string;
};

export function ProtectedRoute({
  children,
  requiredRole,
  fallbackPath = '/login',
}: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const token = getAccessToken();

    if (!token) {
      if (pathname !== fallbackPath) {
        router.replace(fallbackPath);
      }
      return;
    }

    const role = getStoredUserRole() ?? getUserRoleFromToken(token);
    const requiredRoles = Array.isArray(requiredRole) ? requiredRole : requiredRole ? [requiredRole] : [];

    if (requiredRoles.length > 0 && (!role || !requiredRoles.includes(role))) {
      const redirectTo = role ? getRoleBasedRedirectPath(role) : fallbackPath;
      if (pathname !== redirectTo) {
        router.replace(redirectTo);
      }
      return;
    }

    // If student or company, ensure onboarding is complete by checking profile fields
    const checkProfileAndAuthorize = async () => {
      try {
        if (role === 'student') {
          // Real endpoint: GET /students/me/ (StudentProfile). See students/urls.py.
          const res = await api.get('/students/me/');
          const profile = res.data as any;
          const hasSkills = Array.isArray(profile?.skills) && profile.skills.length > 0;
          const hasResume = Boolean(profile?.resume);

          if (!hasSkills || !hasResume) {
            if (pathname !== '/onboarding/student') {
              router.replace('/onboarding/student');
              return;
            } else {
              setIsAuthorized(true);
              return;
            }
          }
        }

        if (role === 'company') {
          // Real endpoint: GET /companies/me/. See companies/urls.py.
          try {
            const res = await api.get('/companies/me/');
            const profile = res.data as any;
            const hasName = Boolean(profile?.company_name);

            if (!hasName) {
              if (pathname !== '/onboarding/company') {
                router.replace('/onboarding/company');
                return;
              } else {
                setIsAuthorized(true);
                return;
              }
            }

            const isApproved = Boolean(profile?.is_approved);
            if (!isApproved) {
              setPendingApproval(true);
              setIsAuthorized(true);
              return;
            }
          } catch (e) {
            if (pathname !== '/onboarding/company') {
              router.replace('/onboarding/company');
              return;
            } else {
              setIsAuthorized(true);
              return;
            }
          }
        }

        if (role === 'college') {
          // Real endpoint: GET /college/me/ (companies/urls_college.py -> CollegeMeView)
          try {
            const res = await api.get('/college/me/');
            const profile = res.data as any;
            const hasName = Boolean(profile?.college_name);

            if (!hasName) {
              if (pathname !== '/onboarding/college') {
                router.replace('/onboarding/college');
                return;
              } else {
                setIsAuthorized(true);
                return;
              }
            }

            const isApproved = Boolean(profile?.is_approved);
            if (!isApproved) {
              setPendingApproval(true);
              setIsAuthorized(true);
              return;
            }
          } catch (e) {
            if (pathname !== '/onboarding/college') {
              router.replace('/onboarding/college');
              return;
            } else {
              setIsAuthorized(true);
              return;
            }
          }
          setIsAuthorized(true);
          return;
        }

        setIsAuthorized(true);
      } catch (err) {
        // If profile endpoint fails, treat as incomplete and redirect to onboarding for non-admins
        if (role === 'student') {
          if (pathname !== '/onboarding/student') {
            router.replace('/onboarding/student');
            return;
          }
        }
        if (role === 'company') {
          if (pathname !== '/onboarding/company') {
            router.replace('/onboarding/company');
            return;
          }
        }
        if (role === 'college') {
          if (pathname !== '/onboarding/college') {
            router.replace('/onboarding/college');
            return;
          }
        }
        // Fallback to allow access (e.g., admin or unknown issue)
        setIsAuthorized(true);
      }
    };

    checkProfileAndAuthorize();
  }, [fallbackPath, requiredRole, router, pathname]);

  if (!isAuthorized) {
    return null;
  }

  if (pendingApproval) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-md max-w-xl text-center">
          <h2 className="text-2xl font-semibold mb-2">Account Verification Pending</h2>
          <p className="text-gray-700 mb-4">Your account is currently pending verification by the campus TPO / admin. You will be notified by email once your account is approved.</p>
          <p className="text-sm text-gray-500">If you have questions, contact support or your campus TPO.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

