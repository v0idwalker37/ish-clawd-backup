'use client';

import { useState } from 'react';
import { Settings, Bell, Shield, Trash2, AlertTriangle, Loader2 } from 'lucide-react';

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    email: true,
    reports: true,
    marketing: false,
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      const res = await fetch('/api/auth/my-data', {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail || 'Failed to delete account');
      }

      // Clear any local cookies/storage
      document.cookie = 'access_token=; Max-Age=0; path=/';
      document.cookie = 'refresh_token=; Max-Age=0; path=/';
      localStorage.clear();

      // Redirect to homepage
      window.location.href = '/';
    } catch (err: unknown) {
      setDeleteError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
      setIsDeleting(false);
    }
  };

  const handleNotificationChange = (key: keyof typeof notifications) => {
    setNotifications((prev) => ({ ...prev, [key]: !prev[key] }));
    // TODO: Save to backend
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your preferences</p>
      </div>

      {/* Notifications */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Bell className="w-5 h-5 text-primary-600" />
          Notifications
        </h2>

        <div className="space-y-4">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium text-gray-900">Email Notifications</p>
              <p className="text-sm text-gray-600">Receive updates about your account</p>
            </div>
            <input
              type="checkbox"
              checked={notifications.email}
              onChange={() => handleNotificationChange('email')}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium text-gray-900">Report Notifications</p>
              <p className="text-sm text-gray-600">Get notified when your reports are ready</p>
            </div>
            <input
              type="checkbox"
              checked={notifications.reports}
              onChange={() => handleNotificationChange('reports')}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="font-medium text-gray-900">Marketing Emails</p>
              <p className="text-sm text-gray-600">Tips, product updates, and offers</p>
            </div>
            <input
              type="checkbox"
              checked={notifications.marketing}
              onChange={() => handleNotificationChange('marketing')}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
          </label>
        </div>
      </div>

      {/* Privacy */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-600" />
          Privacy & Data
        </h2>

        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-green-800">Your Data is Protected</p>
                <p className="text-sm text-green-700 mt-1">
                  We never sell your data or share it with contractors. Your quotes and personal
                  information are encrypted and stored securely.
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Download Your Data</h3>
            <p className="text-sm text-gray-600 mb-3">
              Request a copy of all your data, including quotes and reports.
            </p>
            <button className="btn-secondary text-sm">Request Data Export</button>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="card border-red-200">
        <h2 className="text-xl font-bold text-red-600 mb-6 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Danger Zone
        </h2>

        <div className="space-y-4">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Delete Account</h3>
            <p className="text-sm text-gray-600 mb-3">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>

            {!showDeleteConfirm ? (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete Account
              </button>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700 mb-3">
                  This will permanently delete your account and all data. Type <strong>DELETE</strong> to confirm.
                </p>
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Type DELETE to confirm"
                  className="w-full px-3 py-2 border border-red-300 rounded-lg mb-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                  disabled={isDeleting}
                  autoFocus
                />
                {deleteError && (
                  <p className="text-sm text-red-600 mb-3">{deleteError}</p>
                )}
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeleteConfirmText('');
                      setDeleteError(null);
                    }}
                    disabled={isDeleting}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteAccount}
                    disabled={deleteConfirmText !== 'DELETE' || isDeleting}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isDeleting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                    {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
