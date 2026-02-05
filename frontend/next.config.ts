import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  // Enable standalone output for Docker
  output: 'standalone',
};

export default nextConfig;
