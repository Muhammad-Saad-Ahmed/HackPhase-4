/**
 * User Session Types
 * Defines authentication state and session management interfaces
 */

export interface UserSession {
  user_id: string;
  email: string;
  session_token: string; // Stored in HTTP-only cookie
  expires_at: string; // ISO 8601 timestamp
  is_authenticated: boolean;
}

export interface AuthContextValue {
  session: UserSession | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: {
    user_id: string;
    email: string;
  };
  session_token: string;
  expires_at: string;
}
