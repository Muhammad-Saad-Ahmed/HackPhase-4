/**
 * Auth Service
 * Handles authentication operations: login, signup, logout
 */

'use client';

import { apiClient } from './api-client';
import { AuthResponse, LoginRequest, SignupRequest } from '@/types/auth';

class AuthService {
  /**
   * Login user with email and password
   * Sets session token in sessionStorage
   * FR-001, SC-001: Email/password authentication
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const request: LoginRequest = { email, password };

      // Call backend auth endpoint
      // Note: baseURL already includes /api prefix
      const response = await apiClient.post<AuthResponse>('/v1/auth/login', request, {
        maxRetries: 1, // Don't retry auth requests
      });

      // Store session token in both sessionStorage and cookies
      // Cookie allows middleware to validate session server-side
      // In production, this should be an HTTP-only cookie set by the server
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('session_token', response.session_token);
        sessionStorage.setItem('user_id', response.user.user_id);
        sessionStorage.setItem('user_email', response.user.email);

        // Set cookie for middleware (expires in 7 days)
        document.cookie = `session_token=${response.session_token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
      }

      return response;
    } catch (error) {
      // Clear any existing session on login failure
      this.clearSession();
      throw error;
    }
  }

  /**
   * Signup new user with email and password
   * Auto-logs in after successful signup
   */
  async signup(email: string, password: string): Promise<AuthResponse> {
    try {
      const request: SignupRequest = { email, password };

      // Call backend signup endpoint
      // Note: baseURL already includes /api prefix
      const response = await apiClient.post<AuthResponse>('/v1/auth/signup', request, {
        maxRetries: 1,
      });

      // Store session token (auto-login after signup)
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('session_token', response.session_token);
        sessionStorage.setItem('user_id', response.user.user_id);
        sessionStorage.setItem('user_email', response.user.email);

        // Set cookie for middleware (expires in 7 days)
        document.cookie = `session_token=${response.session_token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
      }

      return response;
    } catch (error) {
      this.clearSession();
      throw error;
    }
  }

  /**
   * Logout user
   * Clears session token and redirects to login
   * FR-016: Logout functionality
   */
  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint (optional, to invalidate server-side session)
      // Note: baseURL already includes /api prefix
      await apiClient.post('/v1/auth/logout', {}, {
        maxRetries: 0, // Don't retry logout
      });
    } catch (error) {
      // Continue with client-side logout even if server request fails
      console.warn('Logout request failed:', error);
    } finally {
      // Always clear client-side session
      this.clearSession();

      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  }

  /**
   * Check if user is authenticated
   * Validates session token exists and hasn't expired
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') {
      return false;
    }

    const token = sessionStorage.getItem('session_token');
    if (!token) {
      return false;
    }

    // TODO: Add expiration check here
    // const expiresAt = sessionStorage.getItem('expires_at');
    // if (expiresAt && new Date(expiresAt) < new Date()) {
    //   this.clearSession();
    //   return false;
    // }

    return true;
  }

  /**
   * Get current user ID
   */
  getUserId(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    return sessionStorage.getItem('user_id');
  }

  /**
   * Get current user email
   */
  getUserEmail(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    return sessionStorage.getItem('user_email');
  }

  /**
   * Clear session data from storage and cookies
   */
  private clearSession(): void {
    if (typeof window === 'undefined') {
      return;
    }

    sessionStorage.removeItem('session_token');
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('user_email');
    sessionStorage.removeItem('expires_at');

    // Clear the session_token cookie
    document.cookie = 'session_token=; path=/; max-age=0; SameSite=Lax';
  }
}

// Export singleton instance
export const authService = new AuthService();
