'use client';

import React from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const TPOPage: React.FC = () => {
  return (
    <ProtectedRoute requiredRole="tpo">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">TPO Dashboard</h1>
          <LogoutButton />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Approval Queue</h2>
            <p className="text-gray-700 mb-2">Review and approve pending company and college registrations.</p>
            <a href="/tpo/approvals" className="text-blue-500 hover:underline">View Approvals</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Placement Overview</h2>
            <p className="text-gray-700 mb-2">Monitor student activity, offers, and campus placements.</p>
            <a href="/admin" className="text-blue-500 hover:underline">Open Admin Panel</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Job Controls</h2>
            <p className="text-gray-700 mb-2">Manage active job postings and applicant flow.</p>
            <a href="/jobs" className="text-blue-500 hover:underline">Browse Jobs</a>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default TPOPage;
