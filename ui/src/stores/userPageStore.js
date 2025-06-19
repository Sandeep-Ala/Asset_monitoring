import { defineStore } from 'pinia'
import { api } from 'boot/axios' // uses boot/axios.js baseURL = 'http://127.0.0.1:8000'
import { useQuasar } from 'quasar'

export const usePageStore = defineStore('page', {
  state: () => ({
    pages: []
  }),

  actions: {
    notify(message, type = 'info') {
      const $q = useQuasar()
      $q.notify({ message, type, position: 'top' })
    },

    async fetchPages() {
      try {
        const response = await api.get('/pages')
        this.pages = response.data
        this.notify('Pages fetched successfully', 'positive')
      } catch (error) {
        console.error('Error fetching pages:', error)
        this.notify('Failed to fetch pages', 'negative')
      }
    },

    async addPage({ page_name, user_name, page_route }) {
      try {
        const response = await api.post('/pages', {
          page_name,
          user_name,
          page_route
        })
        this.pages.push(response.data)
        this.notify(`Page "${page_name}" created successfully`, 'positive')
        return response.data
      } catch (error) {
        console.error('Error creating page:', error)
        this.notify('Failed to create page', 'negative')
      }
    },

    async updatePage(page_id, { page_name, page_route }) {
      try {
        const page = this.pages.find(p => p.page_id === page_id)
        if (!page) throw new Error('Page not found')

        const response = await api.put(`/pages/${page_id}`, {
          page_name,
          page_route
        })

        // Update local store
        page.page_name = page_name
        page.page_route = page_route
        page.updated_at = response.data.updated_at

        this.notify(`Page updated successfully`, 'positive')
      } catch (error) {
        console.error('Error updating page:', error)
        this.notify('Failed to update page', 'negative')
      }
    },

    async removePage(page_id) {
      try {
        await api.delete(`/pages/${page_id}`)
        this.pages = this.pages.filter(p => p.page_id !== page_id)
        this.notify('Page deleted successfully', 'positive')
      } catch (error) {
        console.error('Error deleting page:', error)
        this.notify('Failed to delete page', 'negative')
      }
    },

    getPageById(id) {
      return this.pages.find(p => p.page_id === id)
    }
  }
})
