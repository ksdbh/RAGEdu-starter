const backendUrl = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [{ source: "/api/backend/:path*", destination: `${backendUrl}/:path*` }];
  },
};
