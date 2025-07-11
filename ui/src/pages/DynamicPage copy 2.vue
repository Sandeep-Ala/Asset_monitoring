<!--
  File: src/pages/DynamicPageOLD.vue - COMPLETE FIXED VERSION
  Purpose: Vue Component Integration with proper API compatibility
  FIXES: WidgetBox integration, layout preservation, API compatibility
-->

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
          Save current widget layout
        </q-tooltip>
      </q-btn>

      <!-- Load Layout -->
      <q-btn
        icon="cloud_download"
        label="Load Layout"
        @click="loadLayout"
        color="info"
        outline
        :loading="loadingLayout"
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Load saved widget layout
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
          Remove all widgets
        </q-tooltip>
      </q-btn>
      <!-- Manual Refresh All -->
      <q-btn
        icon="refresh"
        label="Refresh All"
        @click="refreshAllWidgets"
        color="accent"
        outline
        :loading="refreshingWidgets"
      >
        <q-tooltip anchor="bottom middle" self="top middle">
          Manually refresh all widget data
        </q-tooltip>
      </q-btn>

      <!-- Layout Status -->
      <div class="col-auto">
        <div class="row items-center q-gutter-sm">
          <q-icon
            :name="hasUnsavedChanges ? 'schedule' : 'check_circle'"
            :color="hasUnsavedChanges ? 'orange' : 'green'"
          />
          <div class="text-caption">
            {{ hasUnsavedChanges ? 'Unsaved changes' : 'All saved' }}
            <div v-if="lastSaved" class="text-grey-7">
              Last saved: {{ formatTime(lastSaved) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid Status Bar -->
    <div class="row items-center q-mb-md">
      <div class="col">
        <q-chip dense outline color="primary">
          <q-icon name="grid_3x3" size="16px" class="q-mr-xs" />
          {{ widgets.length }} Widgets
        </q-chip>
        <q-chip dense outline color="secondary" class="q-ml-sm">
          <q-icon name="view_module" size="16px" class="q-mr-xs" />
          {{ gridDimensions.cols }}x{{ gridDimensions.rows }} Grid
        </q-chip>
        <q-chip dense outline :color="backendStatus.connected ? 'positive' : 'negative'" class="q-ml-sm">
          <q-icon :name="backendStatus.connected ? 'cloud_done' : 'cloud_off'" size="16px" class="q-mr-xs" />
          {{ backendStatus.connected ? 'Connected' : 'Disconnected' }}
        </q-chip>
      </div>
      <div class="col-auto">
        <div class="text-caption text-grey-7">
          Time Range: {{ timeRangeDisplay }}
        </div>
      </div>
    </div>

    <!-- ✨ FIXED: Vue Component Grid Container -->
    <div class="dashboard-container">
      <!-- GridStack Container for Layout Management -->
      <div
        ref="gridContainer"
        class="grid-stack"
        style="min-height: 400px;"
      >
        <!-- ✨ FIXED: Vue Components for each widget with proper height calculation -->
        <div
          v-for="widget in widgets"
          :key="widget.id"
          class="grid-stack-item"
          :data-id="widget.id"
          :gs-x="widget.x"
          :gs-y="widget.y"
          :gs-w="widget.w"
          :gs-h="widget.h"
        >
          <div class="grid-stack-item-content">
            <!-- ✨ FIXED: Use WidgetBox component with proper props -->
            <WidgetBox
              :widget-data="widgetDataMap[widget.id] || widget"
              :height="calculateWidgetHeight(widget)"
              theme="default"
              :auto-refresh-enabled="true"
              :show-debug-info="isDevelopment"
              :show-footer="true"
              @widget-ready="handleWidgetReady"
              @widget-error="handleWidgetError"
              @widget-updated="handleWidgetUpdated"
              @widget-refresh="handleWidgetRefresh"
              @widget-edit="handleWidgetEdit"
              @widget-duplicate="handleWidgetDuplicate"
              @widget-delete="handleWidgetDelete"
              @widget-export="handleWidgetExport"
              @chart-zoom="handleChartZoom"
              @chart-pan="handleChartPan"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="widgets.length === 0"
        class="empty-state text-center q-pa-xl"
      >
        <q-icon name="dashboard" size="80px" color="grey-4" />
        <div class="text-h6 text-grey-6 q-mt-md">No widgets yet</div>
        <div class="text-body2 text-grey-7 q-mb-lg">
          Create your first widget using the wizard or add a simple test widget
        </div>
        <q-btn
          icon="auto_awesome"
          label="Create First Widget"
          @click="openWidgetWizard"
          color="primary"
          size="lg"
          unelevated
        />
      </div>
    </div>

    <!-- Widget Creation Wizard -->
    <WidgetWizard
      ref="widgetWizardRef"
      :page-id="currentPageId"
      @widget-created="handleWidgetCreated"
      @wizard-close="handleWizardClose"
    />

    <!-- Development Debug Panel -->
    <div v-if="isDevelopment" class="debug-panel q-mt-lg">
      <q-expansion-item
        icon="bug_report"
        label="Development Debug Panel"
        header-class="text-grey-7"
      >
        <q-card>
          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col">
                <div class="text-subtitle2">Grid State</div>
                <pre class="debug-json">{{ JSON.stringify(gridState, null, 2) }}</pre>
              </div>
              <div class="col">
                <div class="text-subtitle2">Widget Data</div>
                <pre class="debug-json">{{ JSON.stringify(widgetDataMap, null, 2) }}</pre>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, reactive, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { GridStack } from 'gridstack'
import 'gridstack/dist/gridstack.css'

// Import components
import GlobalTimePicker from 'src/components/GlobalTimePicker.vue'
import WidgetWizard from 'src/components/WidgetWizard.vue'
import WidgetBox from 'src/components/WidgetBox.vue'

// Import services - FIXED imports
import { api } from 'src/boot/axios.js'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'

// ==================== SETUP ====================

const route = useRoute()
const $q = useQuasar()

// Grid reference
const gridContainer = ref(null)
const grid = ref(null)
const widgetWizardRef = ref(null)

// Page management
const pageTitle = computed(() => {
  const routePath = route.params.pageRoute
  return routePath ? routePath.toString().replace(/\//g, ' / ') : 'Dashboard'
})

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

const isDevelopment = computed(() => {
  return process.env.NODE_ENV === 'development' || process.env.DEV
})

// ==================== GLOBAL TIME INTEGRATION ====================

const { timeRangeDisplay } = useGlobalTime()

function handleTimeChange() {
  console.log('⏰ Global time changed, refreshing widgets...')
  // Note: WidgetBox components will automatically refresh via useGlobalTime composable
}


// ==================== UTILITY FUNCTIONS ====================

/**
 * Calculate widget height based on grid dimensions
 */
function calculateWidgetHeight(widget) {
  const heightInGridUnits = widget.h || 3
  const totalHeight = heightInGridUnits * (gridState.cellHeight + gridState.margin) - gridState.margin
  return `${Math.max(200, totalHeight)}px`
}

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

  await resolvePageId()
  await initializeGrid()
  await checkBackendStatus()
  await loadLayout()

  window.addEventListener('globalTimeChanged', handleTimeChange)

  console.log('✅ DynamicPage initialization complete')
})

onUnmounted(() => {
  console.log('🧹 DynamicPage unmounting')

  if (grid.value) {
    grid.value.destroy()
  }

  window.removeEventListener('globalTimeChanged', handleTimeChange)
})

// ==================== WATCHERS ====================

watch(
  () => widgets.value.length,
  () => {
    hasUnsavedChanges.value = true
  }
)

// ==================== GRID MANAGEMENT ====================

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

function handleGridChange(event, items) {
  console.log('📊 Grid layout changed:', items?.length || 0, 'items')

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

function handleWidgetRemoved(event, items) {
  items.forEach(item => {
    const widgetId = item.el.getAttribute('data-id')
    console.log('🗑️ Widget removed from grid:', widgetId)

    widgets.value = widgets.value.filter(w => w.id !== widgetId)
    delete widgetDataMap.value[widgetId]

    hasUnsavedChanges.value = true
  })
}

// ==================== WIDGET MANAGEMENT ====================

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

function handleWidgetCreated(widgetData) {
  console.log('✨ Widget created from wizard:', widgetData)

  addWidgetToGrid(widgetData)

  $q.notify({
    type: 'positive',
    message: `Widget "${widgetData.widget_label}" created successfully!`,
    timeout: 3000
  })

  setTimeout(() => {
    saveLayout()
  }, 1000)
}

function handleWizardClose() {
  console.log('🧙‍♂️ Widget Wizard closed')
}

function addSimpleWidget() {
  const id = `widget-${Date.now()}`

  const simpleWidget = {
    widget_id: id,
    widget_type: 'line_chart', // FIXED: Changed from 'simple' to 'line_chart' for testing
    widget_label: `Test Line Chart ${widgets.value.length + 1}`,
    equipment_ids: [1], // FIXED: Added test equipment ID
    signal_ids: [1], // FIXED: Added test signal ID
    filter_selections: {'1_n_bank': '1', '1_dcu': '1'}, // FIXED: Added test filters
    position_data: {
      x: 0,
      y: 0,
      w: 6,
      h: 4
    },
    styling_config: {
      colors: ['#2196F3'],
      lineStyles: ['solid'],
      showLegend: true,
      showGrid: true
    }
  }

  addWidgetToGrid(simpleWidget)

  console.log('🧪 Test line chart widget added:', simpleWidget)
}

// ✨ ENHANCED: Simplified addWidgetToGrid - No more HTML generation
function addWidgetToGrid(widgetData) {
  if (!grid.value || !gridState.initialized) {
    console.error('❌ Grid not initialized')
    return
  }

  const id = widgetData.widget_id
  const position = widgetData.position_data || {}

  // Create the widget data structure that Vue will render
  const newWidget = {
    id: id,
    ...widgetData,
    x: position.x || 0,
    y: position.y || 0,
    w: position.w || 4,
    h: position.h || 3,
    locked: false
  }

  // Add to reactive arrays - Vue will handle the DOM
  widgets.value.push(newWidget)
  widgetDataMap.value[id] = widgetData

  // Let Vue render the component, then initialize GridStack item
  nextTick(() => {
    const widgetElement = gridContainer.value.querySelector(`[data-id="${id}"]`)
    if (widgetElement) {
      // GridStack will automatically pick up the element with gs-* attributes
      grid.value.makeWidget(widgetElement)
      console.log('✅ Widget added to grid:', id)
    } else {
      console.error('❌ Widget element not found for ID:', id)
    }
  })
}

function removeWidget(widgetId) {
  console.log('🗑️ Removing widget:', widgetId)

  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this widget?',
    cancel: true,
    persistent: true
  }).onOk(() => {
    const widgetElement = gridContainer.value.querySelector(`[data-id="${widgetId}"]`)
    if (widgetElement && grid.value) {
      grid.value.removeWidget(widgetElement)
    }

    widgets.value = widgets.value.filter(w => w.id !== widgetId)
    delete widgetDataMap.value[widgetId]

    hasUnsavedChanges.value = true

    $q.notify({
      type: 'info',
      message: 'Widget deleted',
      timeout: 2000
    })
  })
}

function clearAllWidgets() {
  $q.dialog({
    title: 'Clear All Widgets',
    message: 'Are you sure you want to remove all widgets? This action cannot be undone.',
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

// ==================== WIDGET EVENT HANDLERS ====================

function handleWidgetReady(widgetData) {
  console.log('✅ Widget ready:', widgetData?.widget?.widget_id || widgetData?.widget_id)
}

function handleWidgetError(widgetData) {
  const widgetId = widgetData?.widget?.widget_id || widgetData?.widget_id
  const error = widgetData?.error

  console.error('❌ Widget error:', widgetId, error)
  $q.notify({
    type: 'negative',
    message: `Widget error: ${error?.message || error}`,
    timeout: 3000
  })
}

function handleWidgetUpdated(widgetData) {
  const widgetId = widgetData?.widget?.widget_id || widgetData?.widget_id
  console.log('🔄 Widget updated:', widgetId)

  // Handle type change updates
  if (widgetData?.action === 'type_change') {
    const updatedWidget = widgetData.widget
    const existingWidget = widgets.value.find(w => w.id === updatedWidget.widget_id)

    if (existingWidget) {
      // Update widget type
      existingWidget.widget_type = updatedWidget.widget_type
      widgetDataMap.value[updatedWidget.widget_id] = updatedWidget

      hasUnsavedChanges.value = true

      console.log('🔄 Widget type updated:', updatedWidget.widget_id, 'to', updatedWidget.widget_type)
    }
  }
}

function handleWidgetRefresh(widgetData) {
  const widgetId = widgetData?.widget_id
  console.log('🔄 Widget refresh requested:', widgetId)

  // The individual widget will handle its own refresh via useWidgetData
}

function handleWidgetEdit(widgetData) {
  const widgetId = widgetData?.widget_id
  console.log('✏️ Edit widget:', widgetId)

  $q.notify({
    type: 'info',
    message: 'Widget editing coming soon...',
    timeout: 2000
  })
}

function handleWidgetDuplicate(widgetData) {
  const widgetId = widgetData?.widget_id
  console.log('📋 Duplicate widget:', widgetId)

  const originalWidget = widgetDataMap.value[widgetId]
  if (originalWidget) {
    const duplicatedWidget = {
      ...originalWidget,
      widget_id: `widget-${Date.now()}`,
      widget_label: `${originalWidget.widget_label} (Copy)`,
      position_data: {
        ...originalWidget.position_data,
        x: (originalWidget.position_data?.x || 0) + 1,
        y: (originalWidget.position_data?.y || 0) + 1
      }
    }

    addWidgetToGrid(duplicatedWidget)

    $q.notify({
      type: 'positive',
      message: 'Widget duplicated successfully',
      timeout: 2000
    })
  }
}

function handleWidgetDelete(widgetData) {
  const widgetId = widgetData?.widget_id
  removeWidget(widgetId)
}

function handleWidgetExport(widgetData) {
  const widgetId = widgetData?.widget_id
  console.log('📤 Export widget data:', widgetId)

  $q.notify({
    type: 'info',
    message: 'Data export coming soon...',
    timeout: 2000
  })
}

function handleChartZoom(chartData) {
  const widgetId = chartData?.widget?.widget_id
  console.log('🔍 Chart zoom:', widgetId, chartData?.zoom)
}

function handleChartPan(chartData) {
  const widgetId = chartData?.widget?.widget_id
  console.log('👆 Chart pan:', widgetId, chartData?.pan)
}

// ==================== LAYOUT PERSISTENCE ====================

async function saveLayout() {
  savingLayout.value = true

  try {
    console.log('💾 Saving layout...')
    console.log('📊 Current widgets:', widgets.value.length)

    const layoutData = {
      widgets_data: widgets.value.map(widget => ({
        widget_type: widget.widget_type || 'line_chart',
        widget_label: widget.widget_label || 'Untitled Widget',
        equipment_ids: widget.equipment_ids || [],
        signal_ids: widget.signal_ids || [],
        filter_selections: widget.filter_selections || {},
        styling_config: widget.styling_config || {},

        position_data: {
          x: widget.x || 0,
          y: widget.y || 0,
          w: widget.w || 4,
          h: widget.h || 3
        }
      })),

      layout_data: {
        grid_config: {
          columns: gridState.columns,
          cellHeight: gridState.cellHeight,
          margin: gridState.margin
        },
        timestamp: new Date().toISOString(),
        version: "1.0"
      },

      time_settings_data: null
    }

    console.log('📤 Sending layout data:', layoutData)

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

async function loadLayout() {
  loadingLayout.value = true

  try {
    console.log('📥 Loading layout for page:', currentPageId.value)

    const response = await api.get(`/widgets/pages/${currentPageId.value}/layout`)
    const layoutData = response.data

    console.log('📊 Layout data received:', layoutData)

    if (grid.value) {
      grid.value.removeAll()
      widgets.value = []
      widgetDataMap.value = {}
    }

    const widgetsArray = layoutData.widgets || []

    if (widgetsArray.length > 0) {
      console.log('📊 Loading widgets:', widgetsArray.length)

      for (const widgetData of widgetsArray) {
        try {
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

    let errorMessage = 'Failed to load layout'

    if (error.response?.status === 404) {
      errorMessage = 'No saved layout found for this page'
      console.log('📝 No layout found (404) - this is normal for new pages')
    } else if (error.response?.status === 500) {
      errorMessage = 'Server error loading layout'
      console.error('💥 Server error details:', error.response?.data)
    } else if (error.response?.data?.detail) {
      errorMessage += ': ' + error.response.data.detail
    } else if (error.message) {
      errorMessage += ': ' + error.message
    }

    $q.notify({
      type: 'negative',
      message: errorMessage,
      timeout: 5000
    })
  } finally {
    loadingLayout.value = false
  }
}

// ==================== UTILITY FUNCTIONS ====================

async function checkBackendStatus() {
  try {
    const response = await api.get('/health', { timeout: 5000 })
    backendStatus.connected = response.status === 200
    backendStatus.lastCheck = new Date()
    console.log('💚 Backend connection: OK')
  } catch (error) {
    backendStatus.connected = false
    backendStatus.lastCheck = new Date()
    console.warn('💛 Backend connection: Failed', error.message)
  }
}

function formatTime(date) {
  if (!date) return 'Never'

  const now = new Date()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)

  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHour < 24) return `${diffHour}h ago`

  return date.toLocaleDateString()
}
</script>

<style scoped>
.dashboard-container {
  min-height: 400px;
  position: relative;
}

.grid-stack {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  min-height: 400px;
}

:deep(.grid-stack-item) {
  background: transparent;
}

:deep(.grid-stack-item-content) {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%;
}

:deep(.grid-stack-item:hover .grid-stack-item-content) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.empty-state {
  background: white;
  border-radius: 8px;
  border: 2px dashed #e0e0e0;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.debug-panel {
  border-top: 1px solid #e0e0e0;
  margin-top: 24px;
  padding-top: 16px;
}

.debug-json {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  max-height: 300px;
  overflow: auto;
}

/* GridStack Responsive */
@media (max-width: 768px) {
  :deep(.grid-stack) {
    padding: 5px;
  }

  :deep(.grid-stack-item-content) {
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }
}

/* Loading States */
.widget-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f9f9f9;
}

/* Animation */
:deep(.grid-stack-item) {
  transition: all 0.3s ease;
}

:deep(.grid-stack-item.grid-stack-animate) {
  transition: all 0.3s ease;
}

/* Status Indicators */
.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-connected {
  background-color: #4caf50;
}

.status-disconnected {
  background-color: #f44336;
}

.status-loading {
  background-color: #ff9800;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Widget Grid Enhancements */
:deep(.grid-stack-item.ui-resizable-resizing) {
  opacity: 0.8;
}

:deep(.grid-stack-item.ui-draggable-dragging) {
  opacity: 0.8;
  transform: rotate(3deg);
}

/* Empty State Enhancements */
.empty-state .q-icon {
  opacity: 0.5;
}

.empty-state:hover {
  border-color: #1976d2;
  background: #f8f9ff;
}

/* Action Bar Responsive */
@media (max-width: 1024px) {
  .row.q-gutter-md {
    flex-direction: column;
    gap: 8px;
  }

  .row.q-gutter-md .q-btn {
    width: 100%;
  }
}

/* Grid Status Bar */
.grid-status-bar {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 8px 12px;
}

/* Widget Hover Effects */
:deep(.grid-stack-item:hover) {
  z-index: 10;
}

:deep(.grid-stack-item:hover .grid-stack-item-content) {
  transform: translateY(-2px);
  transition: all 0.2s ease;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Debug Panel Styling */
.debug-panel .q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.debug-panel .debug-json {
  font-size: 11px;
  line-height: 1.4;
}

/* Custom Scrollbar for Debug */
.debug-json::-webkit-scrollbar {
  width: 6px;
}

.debug-json::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.debug-json::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.debug-json::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Header Enhancements */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.page-header .text-h4 {
  color: white;
}

.page-header .text-subtitle2 {
  color: rgba(255, 255, 255, 0.8);
}

/* Widget Type Specific Styling */
:deep(.widget-box--line_chart) {
  border-left: 4px solid #2196f3;
}

:deep(.widget-box--bar_chart) {
  border-left: 4px solid #9c27b0;
}

:deep(.widget-box--pie_chart) {
  border-left: 4px solid #4caf50;
}

:deep(.widget-box--table) {
  border-left: 4px solid #00bcd4;
}

:deep(.widget-box--kpi) {
  border-left: 4px solid #ff9800;
}

/* Success/Error States */
.success-state {
  color: #4caf50;
}

.error-state {
  color: #f44336;
}

.warning-state {
  color: #ff9800;
}

/* Tooltip Enhancements */
.q-tooltip {
  font-size: 12px;
  padding: 6px 8px;
}

/* Button Group Styling */
.q-btn-group .q-btn {
  border-radius: 0;
}

.q-btn-group .q-btn:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.q-btn-group .q-btn:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

/* Widget Animation on Add */
@keyframes widgetSlideIn {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

:deep(.grid-stack-item.widget-entering) {
  animation: widgetSlideIn 0.3s ease-out;
}

/* Enhanced Focus States */
.q-btn:focus {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

/* Custom Chip Styling */
.q-chip {
  font-weight: 500;
}

.q-chip.dense {
  font-size: 11px;
}

/* Time Display Styling */
.time-display {
  font-family: 'Roboto Mono', monospace;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.05);
  padding: 4px 8px;
  border-radius: 4px;
}

/* Widget Count Badge */
.widget-count-badge {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-radius: 12px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
}

/* Enhanced Grid Styling */
.grid-stack {
  position: relative;
}

.grid-stack::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20px 20px, rgba(0,0,0,0.02) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

/* Final Responsive Adjustments */
@media (max-width: 600px) {
  .dashboard-container {
    padding: 0;
  }

  .grid-stack {
    border-radius: 0;
    padding: 5px;
  }

  .text-h4 {
    font-size: 1.5rem;
  }

  .action-bar {
    flex-direction: column;
    gap: 8px;
  }

  .status-chips {
    flex-wrap: wrap;
    gap: 4px;
  }
}

/* Print Styles */
@media print {
  .q-btn,
  .action-bar,
  .debug-panel {
    display: none !important;
  }

  .grid-stack {
    background: white !important;
    box-shadow: none !important;
  }

  :deep(.grid-stack-item-content) {
    box-shadow: 1px 1px 3px rgba(0,0,0,0.1) !important;
  }
}
</style>
