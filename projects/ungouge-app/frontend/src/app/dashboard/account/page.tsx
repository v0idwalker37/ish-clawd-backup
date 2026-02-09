'use client';

import { useState, useEffect } from 'react';
import { User, Mail, Calendar, Shield, Save, AlertCircle, Lock, CheckCircle, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface UserData {
  name: string;
  email: string;
  created_at?: string;
}

interface MFAStatus {
  mfa_enabled: boolean;
  email: string;
}

export default function AccountPage() {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // MFA State
  const [mfaStatus, setMfaStatus] = useState<MFAStatus | null>(null);
  const [mfaLoading, setMfaLoading] = useState(false);
  const [mfaStep, setMfaStep] = useState<'idle' | 'verify' | 'disable'>('idle');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaPassword, setMfaPassword] = useState('');
  const [mfaMessage, setMfaMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userData, mfaData] = await Promise.all([
          api.get('/api/auth/me'),
          api.get('/api/auth/mfa/status'),
        ]);
        setUser(userData);
        setMfaStatus(mfaData);
        setFormData((prev) => ({ ...prev, name: userData.name }));
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await api.put('/api/auth/me', { name: formData.name });
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setUser((prev) => prev ? { ...prev, name: formData.name } : null);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    if (formData.newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters.' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      await api.post('/api/auth/change-password', {
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
      });
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setFormData((prev) => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      }));
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to change password. Check your current password.' });
    } finally {
      setSaving(false);
    }
  };

  // MFA Handlers
  const handleEnableMFA = async () => {
    if (!mfaPassword) {
      setMfaMessage({ type: 'error', text: 'Please enter your password.' });
      return;
    }

    setMfaLoading(true);
    setMfaMessage(null);

    try {
      await api.post('/api/auth/mfa/enable', { password: mfaPassword });
      setMfaStep('verify');
      setMfaPassword('');
      setMfaMessage({ type: 'success', text: 'Verification code sent to your email!' });
    } catch (error: any) {
      setMfaMessage({ 
        type: 'error', 
        text: error?.message || 'Failed to send verification code. Check your password.' 
      });
    } finally {
      setMfaLoading(false);
    }
  };

  const handleVerifyMFA = async () => {
    if (mfaCode.length !== 6) {
      setMfaMessage({ type: 'error', text: 'Please enter the 6-digit code.' });
      return;
    }

    setMfaLoading(true);
    setMfaMessage(null);

    try {
      await api.post('/api/auth/mfa/verify-enable', { code: mfaCode });
      setMfaStatus((prev) => prev ? { ...prev, mfa_enabled: true } : null);
      setMfaStep('idle');
      setMfaCode('');
      setMfaMessage({ type: 'success', text: 'Two-factor authentication enabled!' });
    } catch (error: any) {
      setMfaMessage({ 
        type: 'error', 
        text: error?.message || 'Invalid or expired code. Please try again.' 
      });
    } finally {
      setMfaLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    if (!mfaPassword) {
      setMfaMessage({ type: 'error', text: 'Please enter your password.' });
      return;
    }

    setMfaLoading(true);
    setMfaMessage(null);

    try {
      await api.post('/api/auth/mfa/disable', { password: mfaPassword });
      setMfaStatus((prev) => prev ? { ...prev, mfa_enabled: false } : null);
      setMfaStep('idle');
      setMfaPassword('');
      setMfaMessage({ type: 'success', text: 'Two-factor authentication disabled.' });
    } catch (error: any) {
      setMfaMessage({ 
        type: 'error', 
        text: error?.message || 'Failed to disable 2FA. Check your password.' 
      });
    } finally {
      setMfaLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading account...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Account</h1>
        <p className="text-gray-600 mt-1">Manage your account settings</p>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {message.text}
        </div>
      )}

      {/* Profile Info */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <User className="w-5 h-5 text-primary-600" />
          Profile Information
        </h2>

        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
              <Mail className="w-4 h-4" />
              {user?.email}
            </div>
            <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
          </div>

          {user?.created_at && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Member Since
              </label>
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
                <Calendar className="w-4 h-4" />
                {new Date(user.created_at).toLocaleDateString()}
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      {/* Two-Factor Authentication */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Lock className="w-5 h-5 text-primary-600" />
          Two-Factor Authentication
        </h2>

        {/* MFA Message */}
        {mfaMessage && (
          <div
            className={`p-4 rounded-lg flex items-center gap-3 mb-6 ${
              mfaMessage.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {mfaMessage.type === 'success' ? (
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            {mfaMessage.text}
          </div>
        )}

        {/* Current Status */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg mb-6">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${mfaStatus?.mfa_enabled ? 'bg-green-500' : 'bg-gray-400'}`} />
            <div>
              <p className="font-medium text-gray-900">
                {mfaStatus?.mfa_enabled ? 'Enabled' : 'Disabled'}
              </p>
              <p className="text-sm text-gray-600">
                {mfaStatus?.mfa_enabled 
                  ? 'Your account is protected with email verification' 
                  : 'Add an extra layer of security to your account'}
              </p>
            </div>
          </div>
        </div>

        {/* Enable MFA Flow */}
        {!mfaStatus?.mfa_enabled && mfaStep === 'idle' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              When enabled, you&apos;ll receive a verification code via email each time you log in.
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm your password to enable
              </label>
              <input
                type="password"
                value={mfaPassword}
                onChange={(e) => setMfaPassword(e.target.value)}
                placeholder="Enter your current password"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <button
              onClick={handleEnableMFA}
              disabled={mfaLoading || !mfaPassword}
              className="btn-primary flex items-center gap-2"
            >
              {mfaLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Lock className="w-4 h-4" />
              )}
              {mfaLoading ? 'Sending code...' : 'Enable Two-Factor Authentication'}
            </button>
          </div>
        )}

        {/* Verify Code Step */}
        {!mfaStatus?.mfa_enabled && mfaStep === 'verify' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              We sent a 6-digit code to your email. Enter it below to complete setup.
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Verification Code
              </label>
              <input
                type="text"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Enter 6-digit code"
                maxLength={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-center text-2xl tracking-widest font-mono"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleVerifyMFA}
                disabled={mfaLoading || mfaCode.length !== 6}
                className="btn-primary flex items-center gap-2"
              >
                {mfaLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
                {mfaLoading ? 'Verifying...' : 'Verify & Enable'}
              </button>
              <button
                onClick={() => {
                  setMfaStep('idle');
                  setMfaCode('');
                  setMfaMessage(null);
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Disable MFA */}
        {mfaStatus?.mfa_enabled && mfaStep === 'idle' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              To disable two-factor authentication, enter your password below.
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm your password
              </label>
              <input
                type="password"
                value={mfaPassword}
                onChange={(e) => setMfaPassword(e.target.value)}
                placeholder="Enter your current password"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <button
              onClick={handleDisableMFA}
              disabled={mfaLoading || !mfaPassword}
              className="px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
            >
              {mfaLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Lock className="w-4 h-4" />
              )}
              {mfaLoading ? 'Disabling...' : 'Disable Two-Factor Authentication'}
            </button>
          </div>
        )}
      </div>

      {/* Change Password */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-600" />
          Change Password
        </h2>

        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              value={formData.currentPassword}
              onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              value={formData.newPassword}
              onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
              minLength={8}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="btn-secondary flex items-center gap-2"
          >
            <Shield className="w-4 h-4" />
            {saving ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>
    </div>
  );
}
