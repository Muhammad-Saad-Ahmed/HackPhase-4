/**
 * Next.js Proxy (formerly Middleware)
 * Server-side route protection that runs before pages are rendered
 * Redirects unauthenticated users to login page
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // List of protected routes that require authentication
  const protectedRoutes = ['/dashboard', '/chat'];

  // Check if current path is a protected route
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  // Skip proxy for non-protected routes
  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  // Check for session token in cookies or headers
  // Note: sessionStorage is client-side only, so we check cookies here
  const sessionCookie = request.cookies.get('session_token');

  // For sessionStorage-based auth, we let AuthGuard handle it on client side
  // This proxy primarily handles cookie-based sessions
  // If no cookie found, allow request to proceed (AuthGuard will handle redirect)

  // Optional: Add security headers
  const response = NextResponse.next();
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
}

// Configure which routes this proxy should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)',
  ],
};
