/**
 * Dashboard Layout
 * Wraps all dashboard routes (/dashboard, /chat) with authentication protection
 * Ensures users must be logged in to access any dashboard features
 */

'use client';

import AuthGuard from '@/components/auth/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      {children}
    </AuthGuard>
  );
}
