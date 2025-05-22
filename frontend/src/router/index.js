import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Forum from '../views/Forum.vue'
import About from '../views/About.vue'
import Contact from '../views/Contact.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import ForgotPassword from '../views/auth/ForgotPassword.vue'
import ResetPassword from '../views/auth/ResetPassword.vue'
import Profile from '../views/Profile.vue'
import FAQ from '../views/FAQ.vue';
import { useAuth } from '../services/security'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/forum',
    name: 'Forum',
    component: Forum
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/contact',
    name: 'Contact',
    component: Contact
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: Login,
    meta: { requiresUnauth: true }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: Register,
    meta: { requiresUnauth: true }
  },
  {
    path: '/auth/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { requiresUnauth: true }
  },
  {
    path: '/auth/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { requiresUnauth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/faq',
    name: 'FAQ',
    component: FAQ
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  
  if (to.meta.requiresAuth && !auth.isAuthenticated.value) {
    next('/auth/login')
  } else if (to.meta.requiresUnauth && auth.isAuthenticated.value) {
    next('/')
  } else {
    next()
  }
})

export default router
