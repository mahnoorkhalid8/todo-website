/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://mahnoorkhalid8-todo-bot.hf.space',
  },
}

module.exports = nextConfig