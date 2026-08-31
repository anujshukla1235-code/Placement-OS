'use client';

import React from 'react';

import { LogoutButton } from '@/components/LogoutButton';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const AdminPanelPage: React.FC = () => {
  return (
    <ProtectedRoute requiredRole="tpo">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Admin Panel</h1>
          <LogoutButton />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">User Management</h2>
            <p className="text-gray-700 mb-2">Manage student, company, and admin accounts.</p>
            <a href="/admin/users" className="text-blue-500 hover:underline">Go to Users</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Company Management</h2>
            <p className="text-gray-700 mb-2">Add, edit, or remove company listings.</p>
            <a href="/admin/companies" className="text-blue-500 hover:underline">Manage Companies</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Account Approvals</h2>
            <p className="text-gray-700 mb-2">Approve or reject company/college registrations.</p>
            <a href="/admin/approvals" className="text-blue-500 hover:underline">Pending Approvals</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Job Posting Management</h2>
            <p className="text-gray-700 mb-2">Oversee all job postings.</p>
            <a href="/admin/jobs" className="text-blue-500 hover:underline">Manage Jobs</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Interview Management</h2>
            <p className="text-gray-700 mb-2">Schedule and manage interviews.</p>
            <a href="/admin/interviews" className="text-blue-500 hover:underline">Manage Interviews</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">Analytics Dashboard</h2>
            <p className="text-gray-700 mb-2">View placement statistics and reports.</p>
            <a href="/admin/analytics" className="text-blue-500 hover:underline">View Analytics</a>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-3">System Settings</h2>
            <p className="text-gray-700 mb-2">Configure portal settings.</p>
            <a href="/admin/settings" className="text-blue-500 hover:underline">Configure Settings</a>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default AdminPanelPage;
