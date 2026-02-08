'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '../../lib/auth';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // Password validation checks
  const [passwordChecks, setPasswordChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    digit: false,
    specialChar: false,
  });

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);

    // Update password validation checks
    setPasswordChecks({
      length: newPassword.length >= 8,
      uppercase: /[A-Z]/.test(newPassword),
      lowercase: /[a-z]/.test(newPassword),
      digit: /\d/.test(newPassword),
      specialChar: /[!@#$%^&*(),.?":{}|<>]/.test(newPassword),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await auth.register(email, password, name);

      if (result.success) {
        // Redirect to dashboard on successful registration
        router.push('/dashboard');
        router.refresh();
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (err) {
      setError('An error occurred during registration');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Check if all password requirements are met
  const isPasswordValid = Object.values(passwordChecks).every(check => check);

  // Function to get class names based on validation status
  const getValidationClass = (isValid: boolean) => {
    return isValid ? 'text-green-600' : 'text-red-600';
  };

  const getIndicatorClass = (isValid: boolean) => {
    return isValid ? 'text-green-500' : 'text-gray-400';
  };

  // Button class based on validation
  const buttonClass = "group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 " +
    (isPasswordValid
      ? 'bg-indigo-600 hover:bg-indigo-700'
      : 'bg-gray-400 cursor-not-allowed');

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          )}
          <input type="hidden" name="remember" defaultValue="true" />
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="name" className="sr-only">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Full Name"
              />
            </div>
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={handlePasswordChange}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          {/* Password requirements */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Password must contain:</p>
            <div className="grid grid-cols-1 gap-2">
              <div className={"flex items-center p-2 rounded " + (passwordChecks.length ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                <span className="mr-2 font-bold">{passwordChecks.length ? '✓' : '○'}</span>
                <span className="text-sm">At least 8 characters</span>
              </div>
              <div className={"flex items-center p-2 rounded " + (passwordChecks.uppercase ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                <span className="mr-2 font-bold">{passwordChecks.uppercase ? '✓' : '○'}</span>
                <span className="text-sm">At least one uppercase letter (A-Z)</span>
              </div>
              <div className={"flex items-center p-2 rounded " + (passwordChecks.lowercase ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                <span className="mr-2 font-bold">{passwordChecks.lowercase ? '✓' : '○'}</span>
                <span className="text-sm">At least one lowercase letter (a-z)</span>
              </div>
              <div className={"flex items-center p-2 rounded " + (passwordChecks.digit ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                <span className="mr-2 font-bold">{passwordChecks.digit ? '✓' : '○'}</span>
                <span className="text-sm">At least one digit (0-9)</span>
              </div>
              <div className={"flex items-center p-2 rounded " + (passwordChecks.specialChar ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                <span className="mr-2 font-bold">{passwordChecks.specialChar ? '✓' : '○'}</span>
                <span className="text-sm">At least one special character (!@#$%^&*)</span>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !isPasswordValid}
              className={buttonClass}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </div>
        </form>
        <div className="text-center">
          <p className="mt-2 text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}