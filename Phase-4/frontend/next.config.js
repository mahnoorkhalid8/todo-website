/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://mahnoorkhalid8-todo-bot.hf.space',
  },
  transpilePackages: [
    // Add any packages that need transpilation
  ],
  experimental: {
    // Enable webpack 5 for better tree shaking
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "upgrade-insecure-requests",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig