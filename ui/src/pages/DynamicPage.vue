<!-- src/pages/DynamicPage.vue -->
<!-- Complete Updated Dynamic Page with Fixed Layout Saving -->
<!-- Integrates Widget Wizard, Global Time Picker, and Fixed Backend API -->

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

    <!-- Empty State -->
    <div v-if="widgets.length === 0 && !loadingLayout" class="empty-state text-center q-pa-xl">
      <q-icon name="dashboard" size="64px" color="grey-4" />
      <div class="text-h6 text-grey-6 q-mt-md">No widgets yet</div>
      <div class="text-body2 text-grey-7 q-mb-md">
        Create your first widget to get started with your dashboard
      </div>
      <q-btn
        icon="auto_awesome"
        label="Create Widget"
        @click="openWidgetWizard"
        color="primary"
        unelevated
      />
    </div>

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
      <q-card flat bordered class="col-12 col-sm-6 col-md-3 status-card">
        <q-card-section class="text-center">
          <q-icon name="widgets" size="32px" color="primary" />
          <div class="text-h6 q-mt-sm">{{ widgets.length }}</div>
          <div class="text-caption text-grey-7">Total Widgets</div>
        </q-card-section>
      </q-card>

      <!-- Layout Info -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3 status-card">
        <q-card-section class="text-center">
          <q-icon name="dashboard" size="32px" color="orange" />
          <div class="text-h6 q-mt-sm">{{ gridDimensions.cols }}x{{ gridDimensions.rows }}</div>
          <div class="text-caption text-grey-7">Grid Size</div>
        </q-card-section>
      </q-card>

      <!-- Backend Status -->
      <q-card flat bordered class="col-12 col-sm-6 col-md-3 status-card">
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
      <q-card flat bordered class="col-12 col-sm-6 col-md-3 status-card">
        <q-card-section class="text-center">
          <q-icon name="access_time" size="32px" color="blue" />
          <div class="text-h6 q-mt-sm">{{ timeRangeDisplay }}</div>
          <div class="text-caption text-grey-7">Time Range</div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Layout Save Status -->
    <div v-if="lastSaved" class="row q-mt-md">
      <q-card flat bordered class="col-12">
        <q-card-section class="row items-center">
          <q-icon name="save" color="green" class="q-mr-sm" />
          <div class="col">
            <div class="text-body2">
              Layout last saved: {{ formatLastSaved() }}
            </div>
          </div>
          <div class="col-auto">
            <q-chip
              :color="hasUnsavedChanges ? 'orange' : 'green'"
              :icon="hasUnsavedChanges ? 'edit' : 'check'"
              text-color="white"
              size="sm"
            >
              {{ hasUnsavedChanges ? 'Unsaved Changes' : 'All Saved' }}
            </q-chip>
          </div>
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
          <div class="col-12 col-md-4">
            <div class="text-subtitle2 q-mb-sm">Widget Data:</div>
            <pre class="debug-json">{{ JSON.stringify(widgets, null, 2) }}</pre>
          </div>
          <div class="col-12 col-md-4">
            <div class="text-subtitle2 q-mb-sm">Grid State:</div>
            <pre class="debug-json">{{ JSON.stringify(gridState, null, 2) }}</pre>
          </div>
          <div class="col-12 col-md-4">
            <div class="text-subtitle2 q-mb-sm">Widget Data Map:</div>
            <pre class="debug-json">{{ JSON.stringify(widgetDataMap, null, 2) }}</pre>
          </div>
        </div>

        <!-- Debug Actions -->
        <div class="row q-gutter-sm q-mt-md">
          <q-btn
            label="Log Grid State"
            @click="logGridState"
            size="sm"
            color="grey"
            outline
          />
          <q-btn
            label="Log Widgets"
            @click="logWidgets"
            size="sm"
            color="grey"
            outline
          />
          <q-btn
            label="Test Backend"
            @click="checkBackendStatus"
            size="sm"
            color="grey"
            outline
          />
        </div>
      </div>
    </q-expansion-item>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
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
const currentPageId = computed(() => pageId.value || 'demo-page-id')

// Widget Management
const widgets = ref([])
const widgetDataMap = ref({})

// Loading States
const savingLayout = ref(false)
const loadingLayout = ref(false)

// Layout tracking
const lastSaved = ref(null)
const hasUnsavedChanges = ref(false)

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
      // Keep using demo page ID
    }

  } catch (error) {
    console.error('❌ Failed to fetch pages:', error)
    // Keep using demo page ID
  }
}

onMounted(async () => {
  console.log('🚀 DynamicPage mounted, route:', route.params.pageRoute)

  // Resolve page ID
  await resolvePageId()

  // Initialize grid
  await initializeGrid()

  // Check backend status
  await checkBackendStatus()

  // Try to load existing layout
  await loadLayout()

  // Listen for global time changes
  window.addEventListener('globalTimeChanged', handleTimeChange)

  console.log('✅ DynamicPage initialization complete')
})

onUnmounted(() => {
  console.log('🧹 DynamicPage unmounting')

  // Cleanup grid
  if (grid.value) {
    grid.value.destroy()
  }

  // Remove event listeners
  window.removeEventListener('globalTimeChanged', handleTimeChange)
})

// ==================== WATCHERS ====================

// Watch for widget changes to track unsaved changes
watch(
  () => widgets.value.length,
  () => {
    hasUnsavedChanges.value = true
  }
)

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
  console.log('📊 Grid layout changed:', items?.length || 0, 'items')

  // Update widget positions
  if (items && items.length > 0) {
    items.forEach(item => {
      const widgetData = widgets.value.find(w => w.id === item.el.getAttribute('data-id'))
      if (widgetData) {
        widgetData.x = item.x
        widgetData.y = item.y
        widgetData.w = item.w
        widgetData.h = item.h
      }
    })

    hasUnsavedChanges.value = true
  }
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

    hasUnsavedChanges.value = true
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

  // Auto-save after widget creation
  setTimeout(() => {
    saveLayout()
  }, 1000)
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
    equipment_ids: [],
    signal_ids: [],
    filter_selections: {},
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
  const newWidget = {
    id: id,
    ...widgetData,
    x: position.x || 0,
    y: position.y || 0,
    w: position.w || 4,
    h: position.h || 3,
    locked: false
  }

  widgets.value.push(newWidget)

  // Store widget data
  widgetDataMap.value[id] = widgetData

  // Add event listeners after DOM update
  nextTick(() => {
    const deleteBtn = wrapper.querySelector('[data-action="delete"]')
    if (deleteBtn) {
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation()
        removeWidget(id)
      })
    }
  })

  console.log('✅ Widget added to grid:', id)
}

/**
 * Create widget content HTML
 */
function createWidgetContent(widgetData) {
  const type = widgetData.widget_type
  const label = widgetData.widget_label || 'Untitled Widget'

  return `
    <div class="widget-content q-pa-sm" style="height: 100%; border: 1px solid #ddd; border-radius: 4px; background: white;">
      <div class="widget-header row items-center justify-between q-mb-sm">
        <div class="widget-title text-subtitle2 text-weight-medium">${label}</div>
        <div class="widget-actions">
          <button class="q-btn q-btn--dense q-btn--flat q-btn--round"
                  data-action="delete"
                  title="Delete Widget"
                  style="width: 24px; height: 24px; min-height: 24px;">
            <i class="material-icons text-red" style="font-size: 16px;">delete</i>
          </button>
        </div>
      </div>
      <div class="widget-body" style="height: calc(100% - 40px);">
        ${getWidgetBodyContent(type, widgetData)}
      </div>
    </div>
  `
}

/**
 * Get widget body content based on type
 */
function getWidgetBodyContent(type, widgetData) {
  const equipmentCount = widgetData.equipment_ids?.length || 0
  const signalCount = widgetData.signal_ids?.length || 0

  switch (type) {
    case 'line_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #2196f3;">timeline</i>
          <div class="text-subtitle2 q-mt-sm">Line Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${equipmentCount} | Signals: ${signalCount}
          </div>
          <div class="text-caption text-blue-7 q-mt-xs">
            Ready for data visualization
          </div>
        </div>
      `
    case 'bar_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #4caf50;">bar_chart</i>
          <div class="text-subtitle2 q-mt-sm">Bar Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${equipmentCount} | Signals: ${signalCount}
          </div>
          <div class="text-caption text-green-7 q-mt-xs">
            Ready for data visualization
          </div>
        </div>
      `
    case 'pie_chart':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #ff9800;">pie_chart</i>
          <div class="text-subtitle2 q-mt-sm">Pie Chart</div>
          <div class="text-caption text-grey-7">
            Equipment: ${equipmentCount} | Signals: ${signalCount}
          </div>
          <div class="text-caption text-orange-7 q-mt-xs">
            Ready for data visualization
          </div>
        </div>
      `
    case 'table':
      return `
        <div class="chart-placeholder text-center q-pa-md">
          <i class="material-icons" style="font-size: 48px; color: #9c27b0;">table_rows</i>
          <div class="text-subtitle2 q-mt-sm">Data Table</div>
          <div class="text-caption text-grey-7">
            Equipment: ${equipmentCount} | Signals: ${signalCount}
          </div>
          <div class="text-caption text-purple-7 q-mt-xs">
            Ready for data display
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
          <div class="text-caption text-blue-grey-7 q-mt-xs">
            ID: ${widgetData.widget_id}
          </div>
        </div>
      `
  }
}

/**
 * Remove widget from grid
 */
function removeWidget(widgetId) {
  $q.dialog({
    title: 'Delete Widget',
    message: 'Are you sure you want to delete this widget?',
    cancel: true,
    persistent: false
  }).onOk(() => {
    if (!grid.value) return

    const element = gridContainer.value.querySelector(`[data-id="${widgetId}"]`)
    if (element) {
      grid.value.removeWidget(element)
      console.log('🗑️ Widget removed:', widgetId)

      $q.notify({
        type: 'info',
        message: 'Widget deleted',
        timeout: 2000
      })
    }
  })
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
      hasUnsavedChanges.value = true

      $q.notify({
        type: 'info',
        message: 'All widgets cleared',
        timeout: 2000
      })

      console.log('🧹 All widgets cleared')
    }
  })
}

// ==================== LAYOUT PERSISTENCE - FIXED ====================

/**
 * Save current layout to backend - FIXED VERSION
 */
async function saveLayout() {
  savingLayout.value = true

  try {
    console.log('💾 Saving layout...')
    console.log('📊 Current widgets:', widgets.value.length)

    // Format data according to PageLayoutData model - FIXED
    const layoutData = {
      // ✅ Correct key: widgets_data (not widgets)
      widgets_data: widgets.value.map(widget => ({
        // Widget metadata
        widget_type: widget.widget_type || 'line_chart',
        widget_label: widget.widget_label || 'Untitled Widget',
        equipment_ids: widget.equipment_ids || [],
        signal_ids: widget.signal_ids || [],
        filter_selections: widget.filter_selections || {},
        styling_config: widget.styling_config || {},

        // Position data from GridStack
        position_data: {
          x: widget.x || 0,
          y: widget.y || 0,
          w: widget.w || 4,
          h: widget.h || 3
        }
      })),

      // ✅ Layout configuration
      layout_data: {
        grid_config: {
          columns: gridState.columns,
          cellHeight: gridState.cellHeight,
          margin: gridState.margin
        },
        timestamp: new Date().toISOString(),
        version: "1.0"
      },

      // ✅ Time settings (optional)
      time_settings_data: null
    }

    console.log('📤 Sending layout data:', layoutData)

    // Save to backend with correct endpoint and data structure
    const response = await api.put(`/widgets/pages/${currentPageId.value}/layout`, layoutData)

    console.log('✅ Layout saved successfully:', response.data)

    lastSaved.value = new Date()
    hasUnsavedChanges.value = false

    $q.notify({
      type: 'positive',
      message: 'Layout saved successfully!',
      timeout: 3000
    })

  } catch (error) {
    console.error('❌ Failed to save layout:', error)

    // Enhanced error reporting
    let errorMessage = 'Failed to save layout'
    if (error.response?.status === 422) {
      errorMessage += ': Invalid data format'
      console.error('💡 Validation Error Details:', error.response.data)
    } else if (error.response?.data?.detail) {
      errorMessage += ': ' + error.response.data.detail
    }

    $q.notify({
      type: 'negative',
      message: errorMessage,
      timeout: 5000
    })
  } finally {
    savingLayout.value = false
  }
}

/**
 * Load layout from backend - FIXED VERSION
 */
async function loadLayout() {
  loadingLayout.value = true

  try {
    console.log('📥 Loading layout for page:', currentPageId.value)

    const response = await api.get(`/widgets/pages/${currentPageId.value}/layout`)
    const layoutData = response.data

    console.log('📊 Layout data received:', layoutData)

    // Clear existing widgets
    if (grid.value) {
      grid.value.removeAll()
      widgets.value = []
      widgetDataMap.value = {}
    }

    // FIXED: Handle the correct response structure
    const widgetsArray = layoutData.widgets || []

    if (widgetsArray.length > 0) {
      console.log('📊 Loading widgets:', widgetsArray.length)

      for (const widgetData of widgetsArray) {
        try {
          // Ensure position_data is properly structured
          const position = widgetData.position_data || {
            x: widgetData.x || 0,
            y: widgetData.y || 0,
            w: widgetData.w || 4,
            h: widgetData.h || 3
          }

          const completeWidgetData = {
            ...widgetData,
            position_data: position
          }

          addWidgetToGrid(completeWidgetData)
          console.log('✅ Widget loaded:', widgetData.widget_id)

        } catch (error) {
          console.error('❌ Error loading widget:', widgetData.widget_id, error)
          // Continue loading other widgets even if one fails
        }
      }

      lastSaved.value = new Date()
      hasUnsavedChanges.value = false

      $q.notify({
        type: 'positive',
        message: `Loaded ${widgetsArray.length} widget(s)`,
        timeout: 3000
      })
    } else {
      console.log('📝 No saved widgets found')
      $q.notify({
        type: 'info',
        message: 'No saved widgets found',
        timeout: 2000
      })
    }

  } catch (error) {
    console.error('❌ Failed to load layout:', error)

    // Enhanced error handling
    let errorMessage = 'Failed to load layout'

    if (error.response?.status === 404) {
      errorMessage = 'No saved layout found for this page'
      console.log('📝 No layout found (404) - this is normal for new pages')
    } else if (error.response?.status === 500) {
      errorMessage = 'Server error loading layout'
      console.error('💥 Server error details:', error.response?.data)
    } else if (error.response?.data?.detail) {
      errorMessage += ': ' + error.response.data.detail
    } else {
      errorMessage += ': ' + error.message
    }

    // Only show error notification for non-404 errors
    if (error.response?.status !== 404) {
      $q.notify({
        type: 'negative',
        message: errorMessage,
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

// ==================== EVENT HANDLERS ====================

/**
 * Handle global time changes
 */
function handleTimeChange(event) {
  console.log('🕒 Global time changed:', event.detail)
  // This would trigger widget data refresh in real implementation
  // For now, just log the change
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Format last saved time for display
 */
function formatLastSaved() {
  if (!lastSaved.value) return 'Never'

  const now = new Date()
  const saved = lastSaved.value
  const diffMs = now - saved
  const diffMin = Math.floor(diffMs / (1000 * 60))

  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`

  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`

  return saved.toLocaleDateString() + ' ' + saved.toLocaleTimeString()
}

// ==================== DEBUG FUNCTIONS ====================

/**
 * Log current grid state for debugging
 */
function logGridState() {
  console.log('🐛 Grid State:', {
    initialized: gridState.initialized,
    widgetCount: widgets.value.length,
    gridNodes: grid.value?.engine?.nodes || [],
    gridState: gridState
  })
}

/**
 * Log current widgets for debugging
 */
function logWidgets() {
  console.log('🐛 Widget Data:', {
    widgets: widgets.value,
    widgetDataMap: widgetDataMap.value,
    hasUnsavedChanges: hasUnsavedChanges.value
  })
}
</script>

<style scoped>
/* Grid Stack Styling */
.grid-stack {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  min-height: 400px;
  border: 2px dashed #e0e0e0;
  transition: border-color 0.2s ease;
}

.grid-stack:hover {
  border-color: #c0c0c0;
}

.grid-stack-item {
  background: transparent;
}

.grid-stack-item-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  border: 1px solid #e0e0e0;
}

.grid-stack-item-content:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.grid-stack-item.ui-draggable-dragging .grid-stack-item-content {
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  transform: rotate(2deg);
}

/* Widget Content Styling */
.widget-content {
  position: relative;
  overflow: hidden;
  height: 100%;
}

.widget-header {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
  margin-bottom: 8px;
  background: #fafafa;
  margin: -8px -8px 8px -8px;
  padding: 8px 12px;
  border-radius: 8px 8px 0 0;
}

.widget-title {
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.widget-actions button {
  width: 24px;
  height: 24px;
  min-height: 24px;
  padding: 0;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.widget-actions button:hover {
  background-color: rgba(244, 67, 54, 0.1);
  transform: scale(1.1);
}

.widget-body {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

.chart-placeholder {
  color: #757575;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 16px;
}

.chart-placeholder i {
  margin-bottom: 8px;
  opacity: 0.7;
}

/* Empty State Styling */
.empty-state {
  background: white;
  border-radius: 12px;
  border: 2px dashed #d0d0d0;
  margin: 20px 0;
}

/* Status Cards Styling */
.status-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Debug Information Styling */
.debug-json {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  font-size: 11px;
  max-height: 300px;
  overflow: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.4;
}

/* Action Bar Styling */
.q-btn {
  transition: all 0.2s ease;
}

.q-btn:hover {
  transform: translateY(-1px);
}

/* Loading States */
.q-btn--loading {
  pointer-events: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .grid-stack {
    padding: 8px;
    border-radius: 8px;
  }

  .widget-header {
    font-size: 13px;
    padding: 6px 8px;
  }

  .chart-placeholder i {
    font-size: 36px !important;
  }

  .chart-placeholder {
    padding: 12px;
  }

  .status-card {
    margin-bottom: 8px;
  }

  .debug-json {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .text-h4 {
    font-size: 1.5rem;
  }

  .row.q-gutter-md {
    flex-direction: column;
  }

  .row.q-gutter-md > * {
    margin: 4px 0;
  }
}

/* Animation Classes */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.widget-content {
  animation: fadeIn 0.3s ease-out;
}

/* Scrollbar Styling */
.debug-json::-webkit-scrollbar {
  width: 6px;
}

.debug-json::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.debug-json::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.debug-json::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Enhanced Visual Feedback */
.q-chip {
  font-weight: 500;
}

.q-card {
  border: 1px solid #e0e0e0;
}

.q-card:hover {
  border-color: #c0c0c0;
}

/* Grid Stack Item States */
.grid-stack-item.ui-resizable-resizing .grid-stack-item-content {
  opacity: 0.8;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

/* Success/Error States */
.layout-saved {
  border-color: #4caf50 !important;
}

.layout-error {
  border-color: #f44336 !important;
}

/* Improved Button Styles */
.q-btn--unelevated {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.q-btn--unelevated:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Page Header Enhancement */
.text-h4 {
  color: #333;
  margin-bottom: 4px;
}

.text-subtitle2 {
  color: #666;
}

/* Global Time Picker Integration */
:deep(.global-time-picker) {
  margin-bottom: 16px;
}

/* Enhanced Tooltips */
:deep(.q-tooltip) {
  background: rgba(0, 0, 0, 0.87);
  color: white;
  font-size: 12px;
  border-radius: 4px;
  padding: 8px 12px;
}
</style>
