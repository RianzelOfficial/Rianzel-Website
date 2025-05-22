import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import './assets/main.css'

const app = createApp(App)

// Configure i18n
import { translations } from './locales/translations'

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: translations
})

// Use Pinia for state management
app.use(createPinia())

// Use router
app.use(router)

// Use i18n
app.use(i18n)

// Mount the app
app.mount('#app')
