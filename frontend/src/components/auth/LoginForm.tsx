/**
 * Login Form Component
 * Email/password login form with validation
 * FR-001: Login page with Better Auth integration
 */

'use client';

import { useState, FormEvent } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function LoginForm() {
  const { login, isLoading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setValidationError('');

    // Client-side validation
    if (!email || !email.includes('@')) {
      setValidationError('Please enter a valid email address');
      return;
    }

    if (!password || password.length < 6) {
      setValidationError('Password must be at least 6 characters');
      return;
    }

    try {
      await login(email, password);
      // Redirect happens in useAuth
    } catch (err) {
      // Error is handled by useAuth context
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div style={{ background: '#161923', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 16, padding: '32px 28px' }}>
        <h2 style={{ fontSize: 21, fontWeight: 700, color: '#eef0f4', textAlign: 'center', margin: '0 0 24px' }}>
          Sign In
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Email Field */}
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="email" style={{ display: 'block', color: '#6b7585', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              style={{
                width: '100%', padding: '10px 14px', borderRadius: 10, boxSizing: 'border-box',
                border: '1px solid rgba(255,255,255,0.1)', background: '#1e2233',
                color: '#eef0f4', fontSize: 14, outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
              onFocus={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.25)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
              required
            />
          </div>

          {/* Password Field */}
          <div style={{ marginBottom: 22 }}>
            <label htmlFor="password" style={{ display: 'block', color: '#6b7585', fontSize: 13, fontWeight: 600, marginBottom: 6 }}>
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              style={{
                width: '100%', padding: '10px 14px', borderRadius: 10, boxSizing: 'border-box',
                border: '1px solid rgba(255,255,255,0.1)', background: '#1e2233',
                color: '#eef0f4', fontSize: 14, outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s',
              }}
              onFocus={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.25)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
              required
            />
          </div>

          {/* Error Messages */}
          {(validationError || error) && (
            <div style={{ marginBottom: 16, padding: '10px 14px', borderRadius: 10, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', color: '#fca5a5', fontSize: 13 }}>
              {validationError || error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%', padding: '11px', borderRadius: 10, border: 'none',
              background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
              color: '#fff', fontSize: 15, fontWeight: 600,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.55 : 1,
              boxShadow: '0 2px 12px rgba(99,102,241,0.35)',
              transition: 'opacity 0.2s, box-shadow 0.2s',
            }}
          >
            {isLoading ? 'Signing In…' : 'Sign In'}
          </button>
        </form>

        {/* Signup Link */}
        <div style={{ marginTop: 20, textAlign: 'center' }}>
          <p style={{ color: '#6b7585', fontSize: 13, margin: 0 }}>
            Don't have an account?{' '}
            <a href="/signup" style={{ color: '#a78bfa', fontWeight: 600, textDecoration: 'none' }}>
              Sign Up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
