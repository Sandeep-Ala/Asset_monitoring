<!-- pages/DynamicPage.vue -->
<!-- Enhanced Dynamic Page with WidgetWizard Integration -->
<!-- Phase 6.3.3 Testing Implementation -->

<template>
  <q-page padding>
    <!-- Page Header -->
    <div class="row items-center justify-between q-mb-md">
      <div class="col">
        <div class="text-h4 text-weight-light">
          📊 {{ pageTitle }}
        </div>
        <div class="text-subtitle2 text-grey-7">
          Route: {{ route.params.pageRoute }}
        </div>
      </div>
      <div class="col-auto">
        <q-chip
          :color="pageId ? 'green' : 'orange'"
          :icon="pageId ? 'check_circle' : 'warning'"
          text-color="white"
        >
          {{ pageId ? `Page ID: ${pageId}` : 'Using Demo Page ID' }}
        </q-chip>
      </div>
    </div>

    <!-- Global Time Picker Integration -->
    <div class="row items-center q-mb-lg">
      <div class="col">
        <GlobalTimePicker />
      </div>
    </div>

    <!-- Action Bar -->
    <div class="row q-gutter-md items-center q-mb-lg">
      <!-- Widget Wizard Button -->
      <q-btn
        icon="auto_awesome"
        label="Create Widget"
        @click="openWidgetWizard"
        color="primary"
        size="md"
        unelevated
        class="q-px-lg"
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Open Widget Creation Wizard
        </q-tooltip>
      </q-btn>

      <!-- Quick Add Simple Widget -->
      <q-btn
        icon="add"
        label="Add Simple Widget"
        @click="addSimpleWidget"
        color="secondary"
        outline
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Add a simple placeholder widget for testing
        </q-tooltip>
      </q-btn>

      <!-- Save Layout -->
      <q-btn
        icon="save"
        label="Save Layout"
        @click="saveLayout"
        color="positive"
        outline
        :loading="savingLayout"
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Save current widget layout and positions
        </q-tooltip>
      </q-btn>

      <!-- Load Layout -->
      <q-btn
        icon="refresh"
        label="Load Layout"
        @click="loadLayout"
        color="info"
        outline
        :loading="loadingLayout"
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Load saved widget layout from backend
        </q-tooltip>
      </q-btn>

      <!-- Clear All -->
      <q-btn
        icon="clear_all"
        label="Clear All"
        @click="clearAllWidgets"
        color="negative"
        outline
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Remove all widgets from the grid
        </q-tooltip>
      </q-btn>
    </div>

    <!-- Grid Container -->
    <div ref="gridContainer" class="grid-stack q-mt-md"></div>

    <!-- Widget Wizard Component -->
    <WidgetWizard
      ref="widgetWizardRef"
      :page-id="currentPageId"
      @widget-created="handleWidgetCreated"
      @close="handleWizardClose"
    />

    <!-- Status Information -->
    <div class="row q-gutter-md q-mt-lg">
      <!-- Widget Count -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3">
        <q-card-section class="text-center">
          <q-icon name="widgets" size="32px" color="primary" />
          <div class="text-h6 q-mt-sm">{{ widgets.length }}</div>
          <div class="text-caption text-grey-7">Total Widgets</div>
        </q-card-section>
      </q-card>

      <!-- Layout Info -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3">
        <q-card-section class="text-center">
          <q-icon name="dashboard" size="32px" color="orange" />
          <div class="text-h6 q-mt-sm">{{ gridDimensions.cols }}x{{ gridDimensions.rows }}</div>
          <div class="text-caption text-grey-7">Grid Size</div>
        </q-card-section>
      </q-card>

      <!-- Backend Status -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3">
        <q-card-section class="text-center">
          <q-icon
            :name="backendStatus.connected ? 'cloud_done' : 'cloud_off'"
            size="32px"
            :color="backendStatus.connected ? 'green' : 'red'"
          />
          <div class="text-h6 q-mt-sm">{{ backendStatus.connected ? 'Online' : 'Offline' }}</div>
          <div class="text-caption text-grey-7">Backend Status</div>
        </q-card-section>
      </q-card>

      <!-- Time Settings -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3">
        <q-card-section class="text-center">
          <q-icon name="access_time" size="32px" color="blue" />
          <div class="text-h6 q-mt-sm">{{ timeRangeDisplay }}</div>
          <div class="text-caption text-grey-7">Time Range</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Debug Information (Development Only) -->
    <q-expansion-item
      v-if="isDevelopment"
      icon="bug_report"
      label="Debug Information"
      class="q-mt-lg bg-grey-1"
    >
      <div class="q-pa-md">
        <div class="row q-gutter-md">
          <div class="col-12 col-md-6">
            <div class="text-subtitle2 q-mb-sm">Widget Data:</div>
            <pre class="debug-json">{{ JSON.stringify(widgets, null, 2) }}</pre>
          </div>
          <div class="col-12 col-md-6">
            <div class="text-subtitle2 q-mb-sm">Grid State:</div>
            <pre class="debug-json">{{ JSON.stringify(gridState, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </q-expansion-item>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { GridStack } from 'gridstack'
import 'gridstack/dist/gridstack.min.css'

// Components
import WidgetWizard from 'src/components/WidgetWizard.vue'
import GlobalTimePicker from 'src/components/GlobalTimePicker.vue'

// Composables and Services
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import { api } from 'boot/axios'

// ==================== ROUTE & SETUP ====================

const route = useRoute()
const $q = useQuasar()

// ==================== REFS ====================

const gridContainer = ref(null)
const widgetWizardRef = ref(null)
const grid = ref(null)

// ==================== STATE ====================

// Page Information
const pageTitle = computed(() => {
  const routePath = route.params.pageRoute
  return routePath ? routePath.toString().replace(/\//g, ' / ') : 'Dashboard'
})

// Use demo page ID if no real page found
const pageId = ref(null)
const currentPageId = computed(() => pageId.value)

// Widget Management
const widgets = ref([])
const widgetDataMap = ref({})

// Loading States
const savingLayout = ref(false)
const loadingLayout = ref(false)

// Grid State
const gridState = reactive({
  initialized: false,
  cellHeight: 100,
  margin: 10,
  columns: 12
})

const gridDimensions = computed(() => ({
  cols: gridState.columns,
  rows: Math.max(1, Math.ceil(widgets.value.length / gridState.columns))
}))

// Backend Status
const backendStatus = reactive({
  connected: false,
  lastCheck: null
})

// Development mode detection
const isDevelopment = computed(() => {
  return process.env.NODE_ENV === 'development' || process.env.DEV
})

// ==================== GLOBAL TIME INTEGRATION ====================

const { timeRangeDisplay } = useGlobalTime()

// ==================== LIFECYCLE ====================
async function resolvePageId() {
  try {
    const response = await api.get('/pages/')
    const pages = response.data

    const matchedPage = pages.find(p => p.page_route === route.params.pageRoute)

    if (matchedPage) {
      pageId.value = matchedPage.page_id
      console.log('🔗 Resolved page ID:', pageId.value)
    } else {
      console.warn('⚠️ No page found for route:', route.params.pageRoute)
    }

  } catch (error) {
    console.error('❌ Failed to fetch pages:', error)
  }
}

onMounted(async () => {
  console.log('🚀 DynamicPage mounted, route:', route.params.pageRoute)
  await resolvePageId() // ⬅️ Fetch the real page_id
  // Initialize grid
  await initializeGrid()

  // Check backend status
  await checkBackendStatus()

  // Try to load existing layout
  await loadLayout()

  console.log('✅ DynamicPage initialization complete')
})

onUnmounted(() => {
  // Cleanup grid
  if (grid.value) {
    grid.value.destroy()
  }
})

// ==================== GRID MANAGEMENT ====================

/**
 * Initialize GridStack with proper configuration
 */
async function initializeGrid() {
  await nextTick()

  if (!gridContainer.value) {
    console.error('❌ Grid container not found')
    return
  }

  try {
    grid.value = GridStack.init({
      cellHeight: gridState.cellHeight,
      margin: gridState.margin,
      float: true,
      resizable: { handles: 'all' },
      removable: true,
      acceptWidgets: true,
      column: gridState.columns,
      animate: true
    }, gridContainer.value)

    // Listen for grid changes
    grid.value.on('change', handleGridChange)
    grid.value.on('removed', handleWidgetRemoved)

    gridState.initialized = true
    console.log('✅ GridStack initialized successfully')

  } catch (error) {
    console.error('❌ Failed to initialize GridStack:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to initialize grid layout',
      timeout: 3000
    })
  }
}

/**
 * Handle grid layout changes
 */
function handleGridChange(event, items) {
  console.log('📊 Grid layout changed:', items)

  // Update widget positions
  items.forEach(item => {
    const widgetData = widgets.value.find(w => w.id === item.el.getAttribute('data-id'))
    if (widgetData) {
      widgetData.x = item.x
      widgetData.y = item.y
      widgetData.w = item.w
      widgetData.h = item.h
    }
  })
}

/**
 * Handle widget removal from grid
 */
function handleWidgetRemoved(event, items) {
  items.forEach(item => {
    const widgetId = item.el.getAttribute('data-id')
    console.log('🗑️ Widget removed from grid:', widgetId)

    // Remove from widgets array
    widgets.value = widgets.value.filter(w => w.id !== widgetId)

    // Remove from data map
    delete widgetDataMap.value[widgetId]
  })
}

// ==================== WIDGET MANAGEMENT ====================

/**
 * Open the widget creation wizard
 */
function openWidgetWizard() {
  console.log('🧙‍♂️ Opening Widget Wizard for page:', currentPageId.value)

  if (widgetWizardRef.value) {
    widgetWizardRef.value.open()
  } else {
    console.error('❌ Widget Wizard reference not found')
    $q.notify({
      type: 'negative',
      message: 'Widget Wizard not available',
      timeout: 3000
    })
  }
}

/**
 * Handle widget created from wizard
 */
function handleWidgetCreated(widgetData) {
  console.log('✨ Widget created from wizard:', widgetData)

  // Add the widget to the grid
  addWidgetToGrid(widgetData)

  $q.notify({
    type: 'positive',
    message: `Widget "${widgetData.widget_label}" created successfully!`,
    timeout: 3000
  })
}

/**
 * Handle wizard close
 */
function handleWizardClose() {
  console.log('🧙‍♂️ Widget Wizard closed')
}

/**
 * Add a simple placeholder widget for testing
 */
function addSimpleWidget() {
  const id = `widget-${Date.now()}`

  const simpleWidget = {
    widget_id: id,
    widget_type: 'simple',
    widget_label: `Test Widget ${widgets.value.length + 1}`,
    position_data: {
      x: 0,
      y: 0,
      w: 4,
      h: 3
    },
    styling_config: {
      backgroundColor: '#f5f5f5',
      borderColor: '#ddd'
    }
  }

  addWidgetToGrid(simpleWidget)

  console.log('🧪 Simple widget added for testing:', simpleWidget)
}

/**
 * Add widget to the GridStack grid
 */
function addWidgetToGrid(widgetData) {
  if (!grid.value || !gridState.initialized) {
    console.error('❌ Grid not initialized')
    return
  }

  const id = widgetData.widget_id
  const position = widgetData.position_data || {}

  // Create widget wrapper element
  const wrapper = document.createElement('div')
  wrapper.className = 'grid-stack-item'
  wrapper.setAttribute('data-id', id)
  wrapper.setAttribute('gs-x', position.x || 0)
  wrapper.setAttribute('gs-y', position.y || 0)
  wrapper.setAttribute('gs-w', position.w || 4)
  wrapper.setAttribute('gs-h', position.h || 3)

  // Create content container
  const content = document.createElement('div')
  content.className = 'grid-stack-item-content'
  content.innerHTML = createWidgetContent(widgetData)

  wrapper.appendChild(content)

  // Add to grid
  grid.value.addWidget(wrapper)

  // Track widget
  widgets.value.push({
    id: id,
    ...widgetData,
    x: position.x || 0,
    y: position.y || 0,
    w: position.w || 4,
    h: position.h || 3,
    locked: false
  })

  // Store widget data
  widgetDataMap.value[id] = widgetData

  console.log('✅ Widget added to grid:', id)
}

/**
 * Create widget content HTML
 */
function createWidgetContent(widgetData) {
  const type = widgetData.widget_type
  const label = widgetData.widget_label || 'Untitled Widget'

  const baseContent = `
    <div class="widget-content q-pa-sm" style="height: 100%; border: 1px solid #ddd; border-radius: 4px; background: white;">
      <div class="widget-header row items-center justify-between q-mb-sm">
        <div class="widget-title text-subtitle2 text-weight-medium">${label}</div>
        <div class="widget-actions">
          <button class="q-btn q-btn--dense q-btn--flat q-btn--round"
                  data-action="delete"
                  title="Delete Widget">
            <i class="material-icons text-red">delete</i>
          </button>
        </div>
      </div>
      <div class="widget-body" style="height: calc(100% - 40px);">
        ${getWidgetBodyContent(type, widgetData)}
      </div>
    </div>
  `

  // Add event listeners after next tick
  setTimeout(() => {
    const deleteBtn = wrapper.querySelector('[data-action="delete"]')
    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => removeWidget(widgetData.widget_id))
    }
  }, 100)

  return baseContent
}

/**
 * Get widget body content based on type
 */
function getWidgetBodyContent(type, widgetData) {
  switch (type) {
    case 'line_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #2196f3;">timeline</i>
          <div class="text-subtitle2 q-mt-sm">Line Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${widgetData.equipment_ids?.length || 0} |
            Signals: ${widgetData.signal_ids?.length || 0}
          </div>
        </div>
      `
    case 'bar_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #4caf50;">bar_chart</i>
          <div class="text-subtitle2 q-mt-sm">Bar Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${widgetData.equipment_ids?.length || 0} |
            Signals: ${widgetData.signal_ids?.length || 0}
          </div>
        </div>
      `
    case 'pie_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #ff9800;">pie_chart</i>
          <div class="text-subtitle2 q-mt-sm">Pie Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${widgetData.equipment_ids?.length || 0} |
            Signals: ${widgetData.signal_ids?.length || 0}
          </div>
        </div>
      `
    case 'table':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #9c27b0;">table_rows</i>
          <div class="text-subtitle2 q-mt-sm">Data Table</div>
          <div class="text-caption text-grey-7">
            Equipment: ${widgetData.equipment_ids?.length || 0} |
            Signals: ${widgetData.signal_ids?.length || 0}
          </div>
        </div>
      `
    case 'simple':
    default:
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #607d8b;">widgets</i>
          <div class="text-subtitle2 q-mt-sm">Simple Widget</div>
          <div class="text-caption text-grey-7">Test widget for development</div>
        </div>
      `
  }
}

/**
 * Remove widget from grid
 */
function removeWidget(widgetId) {
  if (!grid.value) return

  const element = gridContainer.value.querySelector(`[data-id="${widgetId}"]`)
  if (element) {
    grid.value.removeWidget(element)
    console.log('🗑️ Widget removed:', widgetId)
  }
}

/**
 * Clear all widgets from grid
 */
function clearAllWidgets() {
  $q.dialog({
    title: 'Clear All Widgets',
    message: 'Are you sure you want to remove all widgets from the grid? This action cannot be undone.',
    cancel: true,
    persistent: true
  }).onOk(() => {
    if (grid.value) {
      grid.value.removeAll()
      widgets.value = []
      widgetDataMap.value = {}

      $q.notify({
        type: 'info',
        message: 'All widgets cleared',
        timeout: 2000
      })

      console.log('🧹 All widgets cleared')
    }
  })
}

// ==================== LAYOUT PERSISTENCE ====================

/**
 * Save current layout to backend
 */
async function saveLayout() {
  savingLayout.value = true

  try {
    console.log('💾 Saving layout...')

    // Prepare layout data
    const layoutData = {
      page_id: currentPageId.value,
      widgets: widgets.value,
      grid_config: {
        columns: gridState.columns,
        cellHeight: gridState.cellHeight,
        margin: gridState.margin
      },
      timestamp: new Date().toISOString()
    }

    // Save to backend
    const response = await api.put(`/widgets/pages/${currentPageId.value}/layout`, layoutData)

    console.log('✅ Layout saved successfully:', response.data)

    $q.notify({
      type: 'positive',
      message: 'Layout saved successfully!',
      timeout: 3000
    })

  } catch (error) {
    console.error('❌ Failed to save layout:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to save layout: ' + (error.response?.data?.detail || error.message),
      timeout: 5000
    })
  } finally {
    savingLayout.value = false
  }
}

/**
 * Load layout from backend
 */
async function loadLayout() {
  loadingLayout.value = true

  try {
    console.log('📥 Loading layout...')

    const response = await api.get(`/widgets/pages/${currentPageId.value}/layout`)
    const layoutData = response.data

    console.log('📊 Layout data received:', layoutData)

    // Clear existing widgets
    if (grid.value) {
      grid.value.removeAll()
      widgets.value = []
      widgetDataMap.value = {}
    }

    // Load widgets from layout
    if (layoutData.widgets && layoutData.widgets.length > 0) {
      for (const widgetData of layoutData.widgets) {
        addWidgetToGrid(widgetData)
      }

      $q.notify({
        type: 'positive',
        message: `Loaded ${layoutData.widgets.length} widget(s)`,
        timeout: 3000
      })
    } else {
      $q.notify({
        type: 'info',
        message: 'No saved widgets found',
        timeout: 2000
      })
    }

  } catch (error) {
    console.error('❌ Failed to load layout:', error)

    // Don't show error for 404 (no layout saved yet)
    if (error.response?.status !== 404) {
      $q.notify({
        type: 'negative',
        message: 'Failed to load layout: ' + (error.response?.data?.detail || error.message),
        timeout: 5000
      })
    }
  } finally {
    loadingLayout.value = false
  }
}

// ==================== BACKEND STATUS ====================

/**
 * Check backend connectivity
 */
async function checkBackendStatus() {
  try {
    const response = await api.get('/widgets/time-ranges/presets')
    backendStatus.connected = true
    backendStatus.lastCheck = new Date()
    console.log('✅ Backend is connected')
  } catch (error) {
    backendStatus.connected = false
    backendStatus.lastCheck = new Date()
    console.warn('⚠️ Backend connection failed:', error.message)
  }
}

// ==================== COMPUTED PROPERTIES ====================

const wrapper = computed(() => {
  // This is used in the createWidgetContent function
  return null
})
</script>

<style scoped>
/* Grid Stack Styling */
.grid-stack {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 10px;
  min-height: 400px;
}

.grid-stack-item {
  background: transparent;
}

.grid-stack-item-content {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s ease;
}

.grid-stack-item-content:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Widget Content Styling */
.widget-content {
  position: relative;
  overflow: hidden;
}

.widget-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
  margin-bottom: 8px;
}

.widget-title {
  color: #333;
  font-weight: 500;
}

.widget-actions button {
  width: 24px;
  height: 24px;
  min-height: 24px;
  padding: 0;
}

.widget-body {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  color: #757575;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* Debug Information Styling */
.debug-json {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
  font-family: 'Courier New', monospace;
}

/* Responsive Design */
@media (max-width: 768px) {
  .grid-stack {
    padding: 5px;
  }

  .widget-header {
    font-size: 14px;
  }

  .chart-placeholder i {
    font-size: 32px !important;
  }
}

/* Animation for widget actions */
.widget-actions button {
  transition: all 0.2s ease;
}

.widget-actions button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

/* Status cards styling */
.q-card {
  transition: transform 0.2s ease;
}

.q-card:hover {
  transform: translateY(-2px);
}
</style>
