/**
 * Signup Page
 * Public route for user registration
 * Header/branding is provided by (auth)/layout.tsx
 */

import SignupForm from '@/components/auth/SignupForm';
import Link from 'next/link';

export default function SignupPage() {
  return (
    <div className="w-full">
      <SignupForm />

      {/* Login Link */}
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <p style={{ color: '#6b7585', fontSize: 13, margin: 0 }}>
          Already have an account?{' '}
          <Link href="/login" style={{ color: '#a78bfa', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
