/**
 * Auth Context and Hook
 * Provides authentication state and methods to all components
 */

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '@/services/auth-service';
import { AuthContextValue, UserSession } from '@/types/auth';

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<UserSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load session on mount
  useEffect(() => {
    loadSession();
  }, []);

  /**
   * Load existing session from storage
   */
  const loadSession = () => {
    try {
      if (authService.isAuthenticated()) {
        const userId = authService.getUserId();
        const email = authService.getUserEmail();

        if (userId && email) {
          setSession({
            user_id: userId,
            email: email,
            session_token: '', // Token is in sessionStorage
            expires_at: '', // TODO: Get from storage
            is_authenticated: true,
          });
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Failed to load session');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login with email and password
   */
  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login(email, password);

      setSession({
        user_id: response.user.user_id,
        email: response.user.email,
        session_token: response.session_token,
        expires_at: response.expires_at,
        is_authenticated: true,
      });

      // Redirect to chat page after successful login
      if (typeof window !== 'undefined') {
        const redirect = new URLSearchParams(window.location.search).get('redirect');
        window.location.href = redirect || '/chat';
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Login failed. Please check your credentials.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Signup with email and password
   */
  const signup = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.signup(email, password);

      setSession({
        user_id: response.user.user_id,
        email: response.user.email,
        session_token: response.session_token,
        expires_at: response.expires_at,
        is_authenticated: true,
      });

      // Redirect to chat page after successful signup
      if (typeof window !== 'undefined') {
        window.location.href = '/chat';
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Signup failed. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout current user
   */
  const logout = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await authService.logout();
      setSession(null);
    } catch (err: any) {
      console.error('Logout error:', err);
      // Still clear session even if logout request fails
      setSession(null);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextValue = {
    session,
    login,
    signup,
    logout,
    isLoading,
    error,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 * Must be used within AuthProvider
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
