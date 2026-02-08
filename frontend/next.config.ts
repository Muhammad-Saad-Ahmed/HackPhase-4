import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  // Temporarily disabled standalone mode due to middleware NFT tracing issue
  // output: 'standalone',
};

export default nextConfig;
