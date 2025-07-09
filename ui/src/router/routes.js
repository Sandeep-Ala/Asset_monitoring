// router/routes.js (Complete with your existing routes)


import MainLayout from 'layouts/MainLayout.vue'
import IndexPage from 'pages/IndexPage.vue'
import DynamicPage from 'pages/DynamicPage.vue'
import DataSourcePage from 'pages/DataSourcePage.vue'
import MetadataMappingPage from 'pages/MetadataMappingPage.vue'
import TestPage from 'pages/TestPage.vue'
import TestWidget from 'pages/TestWidgetDataPage.vue'
import zoomtest from 'pages/ZoomableChartTestPage.vue'
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
        path: 'metadata-mapping',
        name: 'MetadataMapping',
        component: MetadataMappingPage,
        meta: {
          title: 'Metadata Mapping',
          icon: 'drag_indicator',
          description: 'Drag and drop tables/columns to create metadata'
        }
      },
      {
        path: '/test',
        component: TestPage,
        meta: {
          title: 'Testing Phase 6.3',
          icon: 'bug_report'
        }
      },
      {
        path: '/test-widget-data',
        component: TestWidget,
        meta: {
          title: 'Testing Phase 6.3.4',
          icon: 'bug_report'
        }
      },
        {
        path: '/test-zoomable-chart',
        component: zoomtest,
        meta: {
          title: 'Testing Phase 6.3.4-D',
          icon: 'bug_report'
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
    title: 'Metadata Mapping',
    icon: 'drag_indicator',
    route: '/metadata-mapping',
    description: 'Drag and drop tables/columns to create metadata'
  },
  {
    title: 'Dynamic Pages',
    icon: 'dynamic_feed',
    route: '/dynamic',
    description: 'Dynamic page routing'
  }
  // Add more navigation items as needed
]
