/**
 * Next.js Middleware for Session Validation
 * Runs on every request to validate authentication state
 * FR-005, FR-017: Session validation and redirect to login
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Public routes that don't require authentication
const publicRoutes = ['/login', '/signup', '/'];

// Protected routes that require authentication
const protectedRoutes = ['/dashboard', '/chat', '/conversations', '/profile'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the route is protected
  const isProtectedRoute = protectedRoutes.some(route => pathname === route || pathname.startsWith(route + '/'));

  // Get session token from cookie
  const sessionToken = request.cookies.get('session_token')?.value;

  // If accessing a protected route without a session, redirect to login
  if (isProtectedRoute && !sessionToken) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Don't redirect from login/signup to dashboard on the server side
  // Let the client-side AuthGuard and useAuth hook handle post-login redirects
  // This prevents redirect loops with stale cookies

  // Allow the request to proceed
  return NextResponse.next();
}

// Configure which routes the middleware runs on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
