import { defineStore } from 'pinia'

export const useStore = defineStore('main', {
  state: () => ({
    language: 'en', // Default language
    dateFormat: 'MM/dd/yyyy',
    timeFormat: 'hh:mm a'
  }),
  actions: {
    setLanguage(lang) {
      this.language = lang
      // Update date and time format based on language
      if (lang === 'tl') { // Tagalog
        this.dateFormat = 'dd/MM/yyyy'
        this.timeFormat = 'HH:mm'
      } else if (lang === 'en') { // English
        this.dateFormat = 'MM/dd/yyyy'
        this.timeFormat = 'hh:mm a'
      } else if (lang === 'ja') { // Japanese
        this.dateFormat = 'yyyy/MM/dd'
        this.timeFormat = 'HH:mm'
      }
    }
  }
})
