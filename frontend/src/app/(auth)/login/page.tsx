/**
 * Login Page
 * Public route for user authentication
 * FR-001: Login page with Better Auth integration
 */

import LoginForm from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center" style={{ background: '#0d0f14' }}>
      <div className="w-full max-w-md px-4">
        <div className="mb-8 text-center">
          <div style={{
            width: 48, height: 48, borderRadius: 13, margin: '0 auto 14px',
            background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 18px rgba(99,102,241,0.35)',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-1" style={{ color: '#eef0f4' }}>
            ChatKit
          </h1>
          <p style={{ color: '#6b7585', fontSize: 14, margin: 0 }}>
            Sign in to continue to your conversations
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
