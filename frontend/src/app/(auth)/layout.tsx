/**
 * Auth Layout
 * Provides consistent styling and structure for all auth pages (login, signup)
 * Matches the dark theme used in login and signup pages
 */

import { ReactNode } from 'react';

export default function AuthLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center" style={{ background: '#0d0f14' }}>
      <div className="w-full max-w-md px-4">
        {/* App Icon and Title */}
        <div className="mb-8 text-center">
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 13,
            margin: '0 auto 14px',
            background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 18px rgba(99,102,241,0.35)',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                stroke="#fff"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-1" style={{ color: '#eef0f4' }}>
            Todo App
          </h1>
          <p style={{ color: '#6b7585', fontSize: 14, margin: 0 }}>
            AI-powered task management
          </p>
        </div>

        {/* Auth Page Content */}
        {children}
      </div>
    </div>
  );
}
