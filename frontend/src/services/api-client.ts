/**
 * API Client
 * Centralized HTTP client with retry logic, error handling, and auth header injection
 */

'use client';

// Define error types inline to avoid Turbopack module resolution issues
export type ApiErrorCode =
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'SERVER_ERROR'
  | 'VALIDATION_ERROR';

export interface ApiError {
  message: string;
  code: ApiErrorCode;
  details?: Record<string, any>;
}

// Type guard for ApiError
function isApiError(error: any): error is ApiError {
  return (
    error &&
    typeof error === 'object' &&
    'code' in error &&
    'message' in error &&
    typeof error.message === 'string'
  );
}

interface RequestConfig extends RequestInit {
  maxRetries?: number;
  retryDelay?: number;
}

class ApiClient {
  private baseURL: string;
  private defaultMaxRetries = 3;
  private defaultRetryDelay = 1000; // ms

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
      ...config,
    });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...config,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...config,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      ...config,
    });
  }

  /**
   * Core request method with retry logic and error handling
   */
  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const {
      maxRetries = this.defaultMaxRetries,
      retryDelay = this.defaultRetryDelay,
      ...fetchConfig
    } = config;

    let lastError: ApiError | null = null;

    // Retry loop
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await this.makeRequest<T>(endpoint, fetchConfig);
        return response;
      } catch (error) {
        lastError = error as ApiError;

        // Don't retry on auth errors or validation errors
        if (
          lastError.code === 'UNAUTHORIZED' ||
          lastError.code === 'FORBIDDEN' ||
          lastError.code === 'VALIDATION_ERROR'
        ) {
          throw lastError;
        }

        // If this was the last attempt, throw the error
        if (attempt === maxRetries) {
          throw lastError;
        }

        // Exponential backoff
        const delay = retryDelay * Math.pow(2, attempt);
        await this.sleep(delay);

        // Log retry attempt (in development only)
        if (process.env.NODE_ENV === 'development') {
          console.log(`Retrying request to ${endpoint} (attempt ${attempt + 1}/${maxRetries})`);
        }
      }
    }

    // Fallback (should never reach here)
    throw lastError || this.createError('NETWORK_ERROR', 'Request failed after retries');
  }

  /**
   * Make the actual HTTP request
   */
  private async makeRequest<T>(
    endpoint: string,
    config: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Inject auth header
    const headers = this.injectAuthHeader(config.headers);

    try {
      const response = await fetch(url, {
        ...config,
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
      });

      // Handle HTTP errors
      if (!response.ok) {
        throw await this.handleHttpError(response);
      }

      // Parse JSON response
      const data = await response.json();
      return data as T;

    } catch (error) {
      // Network errors or fetch failures
      if (isApiError(error)) {
        throw error;
      }

      throw this.createError(
        'NETWORK_ERROR',
        error instanceof Error ? error.message : 'Network request failed'
      );
    }
  }

  /**
   * Inject Authorization header with session token
   * FR-007: Include authentication token in Authorization header for all API requests
   */
  private injectAuthHeader(headers?: HeadersInit): HeadersInit {
    const token = this.getSessionToken();

    const headersObj: Record<string, string> = {};

    // Convert HeadersInit to plain object
    if (headers) {
      if (headers instanceof Headers) {
        headers.forEach((value, key) => {
          headersObj[key] = value;
        });
      } else if (Array.isArray(headers)) {
        headers.forEach(([key, value]) => {
          headersObj[key] = value;
        });
      } else {
        Object.assign(headersObj, headers);
      }
    }

    // Add Authorization header if token exists
    if (token) {
      headersObj['Authorization'] = `Bearer ${token}`;
    }

    return headersObj;
  }

  /**
   * Get session token from storage
   * Note: In production, this should read from HTTP-only cookie via backend
   * For now, using localStorage as a fallback
   */
  private getSessionToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    // Try to get from sessionStorage first (better security than localStorage)
    return sessionStorage.getItem('session_token') || null;
  }

  /**
   * Handle HTTP error responses
   */
  private async handleHttpError(response: Response): Promise<ApiError> {
    let message = 'An error occurred';
    let details: Record<string, any> | undefined;

    try {
      const errorData = await response.json();
      // Backend returns errors in detail object: { detail: { error, message } }
      if (errorData.detail) {
        message = errorData.detail.message || errorData.detail.error || message;
        details = errorData.detail;
      } else {
        message = errorData.message || errorData.error || message;
        details = errorData.details;
      }
    } catch {
      // Failed to parse error response
      message = response.statusText || message;
    }

    // Map HTTP status to error code
    let code: ApiErrorCode;
    switch (response.status) {
      case 401:
        code = 'UNAUTHORIZED';
        break;
      case 403:
        code = 'FORBIDDEN';
        break;
      case 404:
        code = 'NOT_FOUND';
        break;
      case 400:
        code = 'VALIDATION_ERROR';
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        code = 'SERVER_ERROR';
        break;
      default:
        code = 'NETWORK_ERROR';
    }

    return this.createError(code, message, details);
  }

  /**
   * Create an ApiError object
   */
  private createError(
    code: ApiErrorCode,
    message: string,
    details?: Record<string, any>
  ): ApiError {
    return {
      code,
      message,
      details,
    };
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Create and export a singleton instance
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export const apiClient = new ApiClient(apiBaseURL);
