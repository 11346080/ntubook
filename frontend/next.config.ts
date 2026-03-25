/**
 *                  oo0oo
 *                 o8888888o
 *                 88" . "88
 *                 (| -_- |)
 *                 0\  =  /0
 *               ___/`---'\___
 *             .' \\|     |// '.
 *            / \\|||  :  |||// \
 *           / _||||| -:- |||||- \
 *          |   | \\\  -  /// |   |
 *          | \_|  ''\---/''  |_/ |
 *          \  .-\__  '-'  ___/-. /
 *        ___'. .'  /--.--\  `. .'___
 *     ."" '<  `.___\_<|>_/___.' >' "".
 *    | | :  `- \`.;`\ _ /`;.`/ - ` : | |
 *    \  \ `_.   \_ __\ /__ _/   .-` /  /
 *===== `-.____`.___ \_____/___.-`___.-' =====
 *                  `=---='
 *
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *
 *          佛祖保佑         永無 BUG
 *
 *  @author 北商傳書開發團隊
 *  @date 2026/03/24
 */

import type { NextConfig } from "next";

/**
 * 將 env 中可能出現的：
 * - http://localhost:8000
 * - http://localhost:8000/
 * - http://localhost:8000/api
 * - http://localhost:8000/api/
 *
 * 全部正規化成：
 * - http://localhost:8000
 */
function normalizeApiOrigin(rawValue?: string): string {
  const fallback = "http://localhost:8000";
  const value = (rawValue || fallback).trim();

  return value
    .replace(/\/api\/?$/i, "")
    .replace(/\/+$/g, "");
}

const apiOrigin = normalizeApiOrigin(process.env.NEXT_PUBLIC_API_URL);

const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,

  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/backend-api/:path*",
          destination: `${apiOrigin}/api/:path*/`,
        },
      ],
    };
  },

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "test.ntubook.com",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;