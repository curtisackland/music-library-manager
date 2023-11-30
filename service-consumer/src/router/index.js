import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/spotify',
      name: 'spotify',
      component: () => import('../views/Spotify.vue')
    },
    {
      path: '/apple',
      name: 'apple',
      component: () => import('../views/Apple.vue')
    }
  ]
})

export default router
