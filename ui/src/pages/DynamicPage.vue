<!--
  File: src/pages/DynamicPage.vue - ENHANCED VERSION
  Purpose: Vue Component Integration while preserving ALL existing API functionality
  Changes: Only replace HTML string generation with Vue components, preserve all APIs
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

    <!-- ✨ ENHANCED: Vue Component Grid Container -->
    <div class="dashboard-container">
      <!-- GridStack Container for Layout Management -->
      <div
        ref="gridContainer"
        class="grid-stack"
        style="min-height: 400px;"
      >
        <!-- ✨ NEW: Vue Components for each widget -->
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
            <!-- ✨ ENHANCED: Use WidgetBox component instead of HTML strings -->
            <WidgetBox
              :widget-data="widgetDataMap[widget.id] || widget"
              :height="`${widget.h * (gridState.cellHeight + gridState.margin)}px`"
              theme="default"
              :enable-auto-refresh="true"
              :show-debug-info="isDevelopment"
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
                <pre class="debug-json">{{ gridState }}</pre>
              </div>
              <div class="col">
                <div class="text-subtitle2">Widgets Data</div>
                <pre class="debug-json">{{ widgets }}</pre>
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

// Import services
import api from 'src/services/Api.js'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'

// ==================== SETUP ====================

const route = useRoute()
const $q = useQuasar()

// Grid reference - UNCHANGED
const gridContainer = ref(null)
const grid = ref(null)
const widgetWizardRef = ref(null)

// Page management - UNCHANGED
const pageTitle = computed(() => {
  const routePath = route.params.pageRoute
  return routePath ? routePath.toString().replace(/\//g, ' / ') : 'Dashboard'
})

const pageId = ref(null)
const currentPageId = computed(() => pageId.value || 'demo-page-id')

// Widget Management - UNCHANGED
const widgets = ref([])
const widgetDataMap = ref({})

// Loading States - UNCHANGED
const savingLayout = ref(false)
const loadingLayout = ref(false)

// Layout tracking - UNCHANGED
const lastSaved = ref(null)
const hasUnsavedChanges = ref(false)

// Grid State - UNCHANGED
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

// Backend Status - UNCHANGED
const backendStatus = reactive({
  connected: false,
  lastCheck: null
})

const isDevelopment = computed(() => {
  return process.env.NODE_ENV === 'development' || process.env.DEV
})

// ==================== GLOBAL TIME INTEGRATION - UNCHANGED ====================

const { timeRangeDisplay } = useGlobalTime()

function handleTimeChange() {
  console.log('⏰ Global time changed, refreshing widgets...')
  // Note: WidgetBox components will automatically refresh via useGlobalTime composable
}

// ==================== LIFECYCLE - UNCHANGED ====================

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

// ==================== WATCHERS - UNCHANGED ====================

watch(
  () => widgets.value.length,
  () => {
    hasUnsavedChanges.value = true
  }
)

// ==================== GRID MANAGEMENT - MOSTLY UNCHANGED ====================

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

// ==================== WIDGET MANAGEMENT - ENHANCED ====================

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

// ==================== WIDGET EVENT HANDLERS - NEW ====================

function handleWidgetReady(widgetId) {
  console.log('✅ Widget ready:', widgetId)
}

function handleWidgetError(widgetId, error) {
  console.error('❌ Widget error:', widgetId, error)
  $q.notify({
    type: 'negative',
    message: `Widget error: ${error}`,
    timeout: 3000
  })
}

function handleWidgetUpdated(widgetId, data) {
  console.log('🔄 Widget updated:', widgetId, data)
}

function handleWidgetRefresh(widgetId) {
  console.log('🔄 Widget refresh requested:', widgetId)
}

function handleWidgetEdit(widgetId) {
  console.log('✏️ Edit widget:', widgetId)
  // TODO: Open widget editor
  $q.notify({
    type: 'info',
    message: 'Widget editing coming soon...',
    timeout: 2000
  })
}

function handleWidgetDuplicate(widgetId) {
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

function handleWidgetDelete(widgetId) {
  removeWidget(widgetId)
}

function handleWidgetExport(widgetId) {
  console.log('📤 Export widget data:', widgetId)
  // TODO: Implement data export
  $q.notify({
    type: 'info',
    message: 'Data export coming soon...',
    timeout: 2000
  })
}

function handleChartZoom(widgetId, zoomData) {
  console.log('🔍 Chart zoom:', widgetId, zoomData)
}

function handleChartPan(widgetId, panData) {
  console.log('👆 Chart pan:', widgetId, panData)
}

// ==================== LAYOUT PERSISTENCE - COMPLETELY UNCHANGED ====================

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

// ==================== UTILITY FUNCTIONS - UNCHANGED ====================

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
</style>
