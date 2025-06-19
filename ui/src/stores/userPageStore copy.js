import { defineStore } from 'pinia'
import { api } from 'boot/axios'  // assuming axios is booted correctly

export const usePageStore = defineStore('page', {
  state: () => ({
    pages: []
  }),

  actions: {
    async fetchPages() {
      try {
        const res = await api.get('/pages')
        this.pages = res.data
      } catch (err) {
        console.error('Failed to fetch pages:', err)
      }
    },

    async addPage({ page_name, user_name, page_route }) {
      const now = new Date().toISOString()
      try {
        const res = await api.post('/pages', {
          page_name,
          user_name,
          page_route,
          created_at: now,
          updated_at: now
        })
        this.pages.push(res.data)
        return res.data
      } catch (err) {
        console.error('Failed to add page:', err)
        throw err
      }
    },

    async removePage(id) {
      try {
        await api.delete(`/pages/${id}`)
        this.pages = this.pages.filter(p => p.page_id !== id)
      } catch (err) {
        console.error('Failed to delete page:', err)
      }
    },

    async renamePage(id, newName) {
      const page = this.pages.find(p => p.page_id === id)
      if (!page) return

      const updated_at = new Date().toISOString()
      try {
        const res = await api.put(`/pages/${id}`, {
          ...page,
          page_name: newName,
          updated_at
        })
        page.page_name = res.data.page_name
        page.updated_at = res.data.updated_at
      } catch (err) {
        console.error('Failed to rename page:', err)
      }
    },

    async getPageById(id) {
      try {
        const res = await api.get(`/pages/${id}`)
        return res.data
      } catch (err) {
        console.error(`Failed to get page with ID ${id}:`, err)
        return null
      }
    }
  }
})
