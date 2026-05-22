import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: { unoptimized: true },
  async rewrites() {
    const backend = process.env.BACKEND_URL || "http://localhost:8092";
    return [
      { source: "/api/:path*",    destination: `${backend}/api/:path*` },
      { source: "/health/:path*", destination: `${backend}/health/:path*` },
      { source: "/health",        destination: `${backend}/health` },
    ];
  },
};

export default nextConfig;
