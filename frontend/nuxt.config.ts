export default defineNuxtConfig({
  app: {
    head: {
      title: 'ITRS Transport System',
      meta: [
        {
          name: 'description',
          content: 'Intelligent public transport routing and simulation system.',
        },
      ],
    },
  },
  css: ['@/assets/main.css'],
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000',
    },
  },
});
