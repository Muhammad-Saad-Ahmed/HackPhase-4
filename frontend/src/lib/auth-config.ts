/**
 * Auth Configuration
 * Better Auth configuration with email/password provider
 *
 * Note: This is a placeholder configuration.
 * Replace with actual Better Auth setup when the package is available.
 */

export interface AuthConfig {
  secret: string;
  baseURL: string;
  providers: {
    email: {
      enabled: boolean;
      requireEmailVerification: boolean;
    };
  };
  session: {
    expiresIn: number; // seconds
    updateAge: number; // seconds
  };
}

// Get auth configuration from environment variables
export const authConfig: AuthConfig = {
  secret: process.env.BETTER_AUTH_SECRET || '',
  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',
  providers: {
    email: {
      enabled: true,
      requireEmailVerification: false, // For MVP, disable email verification
    },
  },
  session: {
    expiresIn: 7 * 24 * 60 * 60, // 7 days in seconds
    updateAge: 24 * 60 * 60, // Update session every 24 hours
  },
};

// Validate auth configuration
export function validateAuthConfig(): void {
  if (!authConfig.secret || authConfig.secret.length < 32) {
    throw new Error(
      'BETTER_AUTH_SECRET must be set and at least 32 characters long. ' +
      'Set it in your .env.local file.'
    );
  }

  if (!authConfig.baseURL) {
    throw new Error(
      'BETTER_AUTH_URL must be set. ' +
      'Set it in your .env.local file (e.g., http://localhost:3000).'
    );
  }
}

// Validate on import (in development)
if (process.env.NODE_ENV !== 'production') {
  try {
    validateAuthConfig();
  } catch (error) {
    console.warn('Auth configuration warning:', error);
  }
}
