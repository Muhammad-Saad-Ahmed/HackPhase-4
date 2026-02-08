/**
 * Auth Guard Component
 * Wraps protected pages and redirects to login if not authenticated
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { session, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for auth state to load
    if (isLoading) {
      return;
    }

    // Redirect to login if not authenticated
    if (!session || !session.is_authenticated) {
      const currentPath = window.location.pathname;
      // Use window.location for more reliable redirect
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
    }
  }, [session, isLoading]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading state while redirecting if not authenticated
  if (!session || !session.is_authenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // Render protected content
  return <>{children}</>;
}
