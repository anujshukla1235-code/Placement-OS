'use client';

import React, { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LogoutButton } from '@/components/LogoutButton';
import api from '@/lib/api';
import { toast } from 'sonner';

type PendingItem = {
  profile_id: string;
  user_id: string;
  role: 'COMPANY' | 'COLLEGE';
  email: string;
  company_name?: string;
  college_name?: string;
  website?: string;
  logo?: string;
};

export default function TPOApprovalsPage() {
  const [items, setItems] = useState<PendingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<PendingItem[]>('/auth/approvals/');
      setItems(res.data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load pending approvals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const performAction = async (userId: string, action: 'approve' | 'reject') => {
    setActionLoading((s) => ({ ...s, [userId]: true }));
    try {
      await api.post(`/auth/approvals/${userId}/action/`, { action });
      toast.success('Action completed');
      await fetchItems();
    } catch (err: any) {
      const msg = err?.response?.data?.error || err?.message || 'Action failed';
      toast.error(msg);
      alert(msg);
    } finally {
      setActionLoading((s) => ({ ...s, [userId]: false }));
    }
  };

  return (
    <ProtectedRoute requiredRole="tpo">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Pending Account Approvals</h1>
          <LogoutButton />
        </div>

        {loading && <p>Loading pending approvals...</p>}
        {error && <p className="text-red-600">{error}</p>}
        {!loading && items.length === 0 && <p>No pending approvals.</p>}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {items.map((it) => (
            <div key={it.user_id} className="bg-white p-4 rounded shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{it.role === 'COMPANY' ? it.company_name || 'Company' : it.college_name || 'College'}</h3>
                  <p className="text-sm text-gray-600">{it.email}</p>
                  {it.website && <p className="text-sm text-gray-600">{it.website}</p>}
                </div>
                {it.logo && <img src={it.logo} alt="logo" className="w-16 h-16 object-contain" />}
              </div>

              <div className="mt-4 flex space-x-2">
                <button onClick={() => performAction(it.user_id, 'approve')} disabled={!!actionLoading[it.user_id]} className="px-3 py-1 bg-green-600 text-white rounded">{actionLoading[it.user_id] ? 'Working...' : 'Approve'}</button>
                <button onClick={() => {
                  const reason = prompt('Optional rejection reason:') || '';
                  if (reason || confirm('Reject this account?')) {
                    performAction(it.user_id, 'reject');
                  }
                }} disabled={!!actionLoading[it.user_id]} className="px-3 py-1 bg-red-600 text-white rounded">{actionLoading[it.user_id] ? 'Working...' : 'Reject'}</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </ProtectedRoute>
  );
}
