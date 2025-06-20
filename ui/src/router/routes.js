// ui/src/router/routes.js
import MainLayout from 'layouts/MainLayout.vue'
import IndexPage from 'pages/IndexPage.vue'
import DynamicPage from 'pages/DynamicPage.vue'
import DataSourcePage from 'pages/DataSourcePage.vue'  // New import

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: IndexPage },
      { path: 'datasources', component: DataSourcePage }, // New route
      { path: ':pageRoute(.*)', component: DynamicPage } // Keep as catch-all
    ]
  }
]

export default routes
