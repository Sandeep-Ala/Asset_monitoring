import MainLayout from 'layouts/MainLayout.vue'
import IndexPage from 'pages/IndexPage.vue'
import DynamicPage from 'pages/DynamicPage.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: IndexPage },
      { path: ':pageRoute(.*)', component: DynamicPage } // ← Catch-all dynamic route
    ]
  }
]

export default routes
