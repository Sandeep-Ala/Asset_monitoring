// router/routes.js (Complete with your existing routes)

import MainLayout from 'layouts/MainLayout.vue'
import IndexPage from 'pages/IndexPage.vue'
import DynamicPage from 'pages/DynamicPage.vue'
import DataSourcePage from 'pages/DataSourcePage.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        component: IndexPage,
        meta: {
          title: 'Dashboard',
          icon: 'dashboard'
        }
      },
      {
        path: 'datasources',
        name: 'DataSource',
        component: DataSourcePage,
        meta: {
          title: 'Data Sources',
          icon: 'storage',
          description: 'Manage database connections and schema discovery'
        }
      },
      {
        path: ':pageRoute(.*)',
        component: DynamicPage,
        meta: {
          title: 'Dynamic Page',
          icon: 'dynamic_feed'
        }
      } // ← Catch-all dynamic route (moved to end)
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes

// Optional: Navigation items for your menu/sidebar
export const navigationItems = [
  {
    title: 'Dashboard',
    icon: 'dashboard',
    route: '/',
    description: 'Main dashboard overview'
  },
  {
    title: 'Data Sources',
    icon: 'storage',
    route: '/datasources',
    description: 'Manage database connections and schema discovery'
  },
  {
    title: 'Dynamic Pages',
    icon: 'dynamic_feed',
    route: '/dynamic',
    description: 'Dynamic page routing'
  }
  // Add more navigation items as needed
]
