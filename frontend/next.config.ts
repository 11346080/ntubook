import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Note: Removed rewrites() due to infinite redirect issues in dev mode.
     Use NEXT_PUBLIC_API_URL environment variable directly in frontend code instead. */
};

export default nextConfig;
