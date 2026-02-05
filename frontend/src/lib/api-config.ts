/**
 * API Configuration Validator
 * Validates environment variables at build time with clear error messages
 */

export interface ApiConfig {
  apiURL: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

/**
 * Validate and return API configuration
 * Throws error if required environment variables are missing
 */
export function getApiConfig(): ApiConfig {
  const apiURL = process.env.NEXT_PUBLIC_API_URL;

  if (!apiURL) {
    throw new Error(
      'Missing required environment variable: NEXT_PUBLIC_API_URL\n' +
      'Please set it in your .env.local file.\n' +
      'Example: NEXT_PUBLIC_API_URL=http://localhost:8000'
    );
  }

  // Validate URL format
  try {
    new URL(apiURL);
  } catch (error) {
    throw new Error(
      `Invalid NEXT_PUBLIC_API_URL: "${apiURL}"\n` +
      'Must be a valid URL (e.g., http://localhost:8000 or https://api.example.com)'
    );
  }

  return {
    apiURL,
    isDevelopment: process.env.NODE_ENV === 'development',
    isProduction: process.env.NODE_ENV === 'production',
  };
}

// Validate on import (will throw at build time if missing)
export const apiConfig = getApiConfig();
