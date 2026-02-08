/**
 * Login Page
 * Public route for user authentication
 * Header/branding is provided by (auth)/layout.tsx
 */

import LoginForm from '@/components/auth/LoginForm';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="w-full">
      <LoginForm />

      {/* Signup Link */}
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <p style={{ color: '#6b7585', fontSize: 13, margin: 0 }}>
          Don't have an account?{' '}
          <Link href="/signup" style={{ color: '#a78bfa', fontWeight: 600, textDecoration: 'none' }}>
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
}
