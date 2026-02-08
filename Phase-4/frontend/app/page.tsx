'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '../lib/auth';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    if (auth.isAuthenticated()) {
      // Redirect to dashboard if authenticated
      router.push('/dashboard');
    } else {
      // Redirect to login if not authenticated
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Todo Web Application</h1>
        <p className="text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}