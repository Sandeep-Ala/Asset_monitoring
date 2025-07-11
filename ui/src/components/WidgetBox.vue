<!--
  File: src/components/WidgetBox.vue - FIXED VERSION
  Purpose: Enhanced widget container with proper chart integration
  FIXES: Chart rendering issues, API compatibility, data flow
-->

<template>
  <div class="widget-box" :class="widgetClasses">
    <!-- Widget Header -->
    <div class="widget-header">
      <div class="widget-title-section">
        <div class="widget-title">{{ widgetData.widget_label || 'Unnamed Widget' }}</div>
        <div class="widget-subtitle" v-if="widgetSubtitle">{{ widgetSubtitle }}</div>
      </div>

      <div class="widget-controls">
        <!-- Widget Type Indicator -->
        <q-chip
          :icon="widgetTypeIcon"
          size="sm"
          outline
          :color="widgetTypeColor"
          class="widget-type-chip"
        >
          {{ widgetTypeLabel }}
        </q-chip>

        <!-- Refresh Status -->
        <q-spinner
          v-if="isRefreshing"
          color="primary"
          size="16px"
          class="q-mr-sm"
        />

        <!-- Widget Actions -->
        <q-btn-dropdown
          flat
          dense
          round
          icon="more_vert"
          size="sm"
          class="widget-menu-btn"
        >
          <q-list dense>
            <q-item clickable @click="refreshWidget">
              <q-item-section avatar>
                <q-icon name="refresh" />
              </q-item-section>
              <q-item-section>Refresh Data</q-item-section>
            </q-item>

            <q-item clickable @click="editWidget">
              <q-item-section avatar>
                <q-icon name="edit" />
              </q-item-section>
              <q-item-section>Edit Widget</q-item-section>
            </q-item>

            <q-item clickable @click="duplicateWidget">
              <q-item-section avatar>
                <q-icon name="content_copy" />
              </q-item-section>
              <q-item-section>Duplicate</q-item-section>
            </q-item>

            <q-separator />

            <q-item clickable @click="exportWidget">
              <q-item-section avatar>
                <q-icon name="download" />
              </q-item-section>
              <q-item-section>Export Data</q-item-section>
            </q-item>

            <q-separator />

            <q-item clickable @click="deleteWidget">
              <q-item-section avatar>
                <q-icon name="delete" color="negative" />
              </q-item-section>
              <q-item-section>Delete Widget</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </div>

    <!-- Widget Content Area -->
    <div class="widget-content" :style="{ height: contentHeight }">

      <!-- ✨ FIXED: ZoomableLineChart with proper props -->
      <ZoomableLineChart
        v-if="widgetData.widget_type === 'line_chart'"
        :widget-id="widgetData.widget_id"
        :widget-config="widgetData"
        :chart-height="contentHeight"
        :enable-zoom="true"
        :enable-pan="true"
        :enable-legend="true"
        :enable-auto-refresh="autoRefreshEnabled"
        :show-debug-info="showDebugInfo"
        @chart-ready="onChartReady"
        @chart-error="onChartError"
        @data-updated="onDataUpdated"
        @zoom-changed="onZoomChanged"
        @pan-changed="onPanChanged"
      />

      <!-- Bar Chart Widget (Future) -->
      <div
        v-else-if="widgetData.widget_type === 'bar_chart'"
        class="placeholder-widget"
      >
        <q-icon name="bar_chart" size="48px" color="primary" />
        <div class="placeholder-text">Bar Chart</div>
        <div class="placeholder-subtext">Coming soon...</div>
        <q-btn
          icon="timeline"
          label="Switch to Line Chart"
          color="primary"
          outline
          size="sm"
          @click="suggestLineChart"
        />
      </div>

      <!-- Pie Chart Widget (Future) -->
      <div
        v-else-if="widgetData.widget_type === 'pie_chart'"
        class="placeholder-widget"
      >
        <q-icon name="pie_chart" size="48px" color="secondary" />
        <div class="placeholder-text">Pie Chart</div>
        <div class="placeholder-subtext">Coming soon...</div>
        <q-btn
          icon="timeline"
          label="Switch to Line Chart"
          color="secondary"
          outline
          size="sm"
          @click="suggestLineChart"
        />
      </div>

      <!-- Table Widget (Future) -->
      <div
        v-else-if="widgetData.widget_type === 'table'"
        class="placeholder-widget"
      >
        <q-icon name="table_chart" size="48px" color="info" />
        <div class="placeholder-text">Data Table</div>
        <div class="placeholder-subtext">Coming soon...</div>
        <q-btn
          icon="timeline"
          label="Switch to Line Chart"
          color="info"
          outline
          size="sm"
          @click="suggestLineChart"
        />
      </div>

      <!-- KPI/Metric Widget -->
      <div
        v-else-if="widgetData.widget_type === 'kpi' || widgetData.widget_type === 'metric'"
        class="kpi-widget"
      >
        <div class="kpi-value">{{ kpiValue }}</div>
        <div class="kpi-label">{{ kpiLabel }}</div>
        <div class="kpi-trend" :class="kpiTrendClass">
          <q-icon :name="kpiTrendIcon" />
          <span>{{ kpiTrendText }}</span>
        </div>
      </div>

      <!-- Simple/Test Widget -->
      <div
        v-else-if="widgetData.widget_type === 'simple'"
        class="simple-widget"
      >
        <q-icon name="widgets" size="48px" color="grey-6" />
        <div class="simple-widget-text">Simple Widget</div>
        <div class="simple-widget-id">ID: {{ widgetData.widget_id }}</div>
        <q-btn
          icon="timeline"
          label="Convert to Line Chart"
          color="primary"
          outline
          size="sm"
          @click="convertToLineChart"
          class="q-mt-md"
        />
      </div>

      <!-- Unknown Widget Type -->
      <div v-else class="unknown-widget">
        <q-icon name="help_outline" size="48px" color="warning" />
        <div class="unknown-text">Unknown Widget Type</div>
        <div class="unknown-subtext">{{ widgetData.widget_type }}</div>
        <q-btn
          icon="timeline"
          label="Convert to Line Chart"
          color="warning"
          outline
          size="sm"
          @click="convertToLineChart"
          class="q-mt-md"
        />
      </div>

    </div>

    <!-- Widget Footer (Status/Info) -->
    <div v-if="showFooter" class="widget-footer">
      <div class="footer-left">
        <span class="status-indicator" :class="statusClass"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>

      <div class="footer-right">
        <span v-if="lastUpdated" class="last-updated">
          Updated {{ formatRelativeTime(lastUpdated) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useQuasar } from 'quasar'
import ZoomableLineChart from 'src/components/ZoomableLineChart.vue'

const $q = useQuasar()

// ==================== COMPONENT PROPS ====================

const props = defineProps({
  // Widget Configuration
  widgetData: {
    type: Object,
    required: true
  },

  // Display Options
  height: {
    type: String,
    default: '300px'
  },

  // Features
  autoRefreshEnabled: {
    type: Boolean,
    default: true
  },

  showDebugInfo: {
    type: Boolean,
    default: false
  },

  showFooter: {
    type: Boolean,
    default: true
  },

  // Theme
  theme: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'dark', 'minimal'].includes(value)
  }
})

// ==================== COMPONENT EMITS ====================

const emit = defineEmits([
  'widget-ready',
  'widget-error',
  'widget-updated',
  'widget-refresh',
  'widget-edit',
  'widget-duplicate',
  'widget-delete',
  'widget-export',
  'chart-zoom',
  'chart-pan'
])

// ==================== REACTIVE STATE ====================

// Widget status
const isReady = ref(false)
const isRefreshing = ref(false)
const hasError = ref(false)
const errorMessage = ref('')
const lastUpdated = ref(null)
const dataCount = ref(0)

// Chart reference
const chartRef = ref(null)

// ==================== COMPUTED PROPERTIES ====================

const contentHeight = computed(() => {
  // Calculate content height minus header and footer
  const headerHeight = 60
  const footerHeight = props.showFooter ? 32 : 0
  const totalHeight = parseInt(props.height) || 300

  return `${Math.max(100, totalHeight - headerHeight - footerHeight)}px`
})

const widgetClasses = computed(() => ({
  'widget-box--ready': isReady.value,
  'widget-box--error': hasError.value,
  'widget-box--refreshing': isRefreshing.value,
  'widget-box--dark': props.theme === 'dark',
  'widget-box--minimal': props.theme === 'minimal',
  [`widget-box--${props.widgetData.widget_type}`]: true
}))

const widgetTypeIcon = computed(() => {
  const iconMap = {
    line_chart: 'show_chart',
    bar_chart: 'bar_chart',
    pie_chart: 'pie_chart',
    table: 'table_chart',
    kpi: 'speed',
    metric: 'analytics',
    simple: 'widgets'
  }
  return iconMap[props.widgetData.widget_type] || 'help_outline'
})

const widgetTypeColor = computed(() => {
  const colorMap = {
    line_chart: 'primary',
    bar_chart: 'secondary',
    pie_chart: 'accent',
    table: 'info',
    kpi: 'positive',
    metric: 'warning',
    simple: 'grey'
  }
  return colorMap[props.widgetData.widget_type] || 'warning'
})

const widgetTypeLabel = computed(() => {
  const labelMap = {
    line_chart: 'Line Chart',
    bar_chart: 'Bar Chart',
    pie_chart: 'Pie Chart',
    table: 'Data Table',
    kpi: 'KPI',
    metric: 'Metric',
    simple: 'Simple'
  }
  return labelMap[props.widgetData.widget_type] || 'Unknown'
})

const widgetSubtitle = computed(() => {
  if (props.widgetData.equipment_ids?.length && props.widgetData.signal_ids?.length) {
    return `${props.widgetData.equipment_ids.length} Equipment • ${props.widgetData.signal_ids.length} Signal${props.widgetData.signal_ids.length !== 1 ? 's' : ''}`
  }
  return null
})

const statusClass = computed(() => {
  if (hasError.value) return 'status-error'
  if (isRefreshing.value) return 'status-loading'
  if (isReady.value) return 'status-ready'
  return 'status-loading'
})

const statusText = computed(() => {
  if (hasError.value) return 'Error'
  if (isRefreshing.value) return 'Loading...'
  if (isReady.value) return dataCount.value > 0 ? `${dataCount.value} points` : 'No data'
  return 'Initializing...'
})

// KPI Widget computed properties
const kpiValue = computed(() => {
  // Mock KPI value - replace with real data
  return '73.2%'
})

const kpiLabel = computed(() => {
  return props.widgetData.widget_label || 'KPI Value'
})

const kpiTrendClass = computed(() => {
  // Mock trend - replace with real calculation
  return 'trend-up' // or 'trend-down', 'trend-neutral'
})

const kpiTrendIcon = computed(() => {
  const trendMap = {
    'trend-up': 'trending_up',
    'trend-down': 'trending_down',
    'trend-neutral': 'trending_flat'
  }
  return trendMap[kpiTrendClass.value] || 'trending_flat'
})

const kpiTrendText = computed(() => {
  // Mock trend text - replace with real calculation
  return '+2.1%'
})

// ==================== LIFECYCLE HOOKS ====================

onMounted(() => {
  console.log('📦 WidgetBox mounted:', props.widgetData.widget_id)

  // Emit ready event
  setTimeout(() => {
    if (!hasError.value) {
      isReady.value = true
      emit('widget-ready', props.widgetData)
    }
  }, 100)
})

onBeforeUnmount(() => {
  console.log('📦 WidgetBox unmounting:', props.widgetData.widget_id)
})

// ==================== CHART EVENT HANDLERS ====================

function onChartReady(chartInstance) {
  console.log('📊 Chart ready in WidgetBox:', props.widgetData.widget_id)
  isReady.value = true
  hasError.value = false
  isRefreshing.value = false
  lastUpdated.value = new Date()

  emit('widget-ready', {
    widget: props.widgetData,
    chart: chartInstance
  })
}

function onChartError(error) {
  console.error('📊 Chart error in WidgetBox:', error)
  hasError.value = true
  isRefreshing.value = false
  errorMessage.value = error.message || 'Chart error'

  emit('widget-error', {
    widget: props.widgetData,
    error: error
  })
}

function onDataUpdated(data) {
  console.log('📊 Chart data updated in WidgetBox')
  lastUpdated.value = new Date()
  isRefreshing.value = false

  // Count total data points
  if (data && data.datasets) {
    dataCount.value = data.datasets.reduce((total, dataset) => {
      return total + (dataset.data?.length || 0)
    }, 0)
  }

  emit('widget-updated', {
    widget: props.widgetData,
    data: data
  })
}

function onZoomChanged(zoomData) {
  emit('chart-zoom', {
    widget: props.widgetData,
    zoom: zoomData
  })
}

function onPanChanged(panData) {
  emit('chart-pan', {
    widget: props.widgetData,
    pan: panData
  })
}

// ==================== WIDGET ACTIONS ====================

function refreshWidget() {
  console.log('🔄 Refreshing widget:', props.widgetData.widget_id)

  // Set refreshing state
  isRefreshing.value = true
  lastUpdated.value = new Date()

  emit('widget-refresh', props.widgetData)

  // Auto-clear refreshing state after timeout (fallback)
  setTimeout(() => {
    isRefreshing.value = false
  }, 10000)

  $q.notify({
    type: 'info',
    message: 'Widget refreshed',
    timeout: 1000
  })
}

function editWidget() {
  console.log('✏️ Editing widget:', props.widgetData.widget_id)
  emit('widget-edit', props.widgetData)
}

function duplicateWidget() {
  console.log('📋 Duplicating widget:', props.widgetData.widget_id)
  emit('widget-duplicate', props.widgetData)
}

function exportWidget() {
  console.log('💾 Exporting widget:', props.widgetData.widget_id)
  emit('widget-export', props.widgetData)

  $q.notify({
    type: 'positive',
    message: 'Widget data exported',
    timeout: 2000
  })
}

function deleteWidget() {
  $q.dialog({
    title: 'Delete Widget',
    message: `Are you sure you want to delete "${props.widgetData.widget_label}"?`,
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(() => {
    console.log('🗑️ Deleting widget:', props.widgetData.widget_id)
    emit('widget-delete', props.widgetData)
  })
}

function suggestLineChart() {
  $q.dialog({
    title: 'Convert to Line Chart',
    message: 'This widget type is not yet implemented. Would you like to convert it to a Line Chart?',
    cancel: true,
    persistent: true
  }).onOk(() => {
    convertToLineChart()
  })
}

function convertToLineChart() {
  console.log('🔄 Converting widget to line chart:', props.widgetData.widget_id)

  // Create updated widget data
  const updatedWidget = {
    ...props.widgetData,
    widget_type: 'line_chart'
  }

  emit('widget-updated', {
    widget: updatedWidget,
    action: 'type_change'
  })

  $q.notify({
    type: 'info',
    message: 'Widget converted to Line Chart',
    timeout: 2000
  })
}

// ==================== UTILITY FUNCTIONS ====================

function formatRelativeTime(date) {
  if (!date) return 'Never'

  const now = new Date()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin}m ago`

  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour}h ago`

  return date.toLocaleDateString()
}

// ==================== WATCHERS ====================

// Watch for widget data changes
watch(() => props.widgetData, (newData) => {
  console.log('🔄 Widget data changed in WidgetBox:', newData?.widget_id)
}, { deep: true })

// ==================== EXPOSE PUBLIC METHODS ====================

defineExpose({
  refresh: refreshWidget,
  isReady,
  isRefreshing,
  hasError,
  errorMessage,
  lastUpdated,
  dataCount
})
</script>

<style scoped>
.widget-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.2s ease;
}

.widget-box:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.widget-box--error {
  border-color: #f44336;
  background: #fff5f5;
}

.widget-box--refreshing {
  opacity: 0.8;
}

.widget-box--dark {
  background: #2d2d2d;
  border-color: #404040;
  color: white;
}

.widget-box--minimal {
  border: none;
  box-shadow: none;
}

/* Widget Header */
.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  min-height: 60px;
  flex-shrink: 0;
}

.widget-title-section {
  flex: 1;
  min-width: 0;
}

.widget-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.widget-subtitle {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.widget-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.widget-type-chip {
  font-size: 10px;
  height: 20px;
}

.widget-menu-btn {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.widget-menu-btn:hover {
  opacity: 1;
}

/* Widget Content */
.widget-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* Placeholder Widgets */
.placeholder-widget,
.simple-widget,
.unknown-widget {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #666;
  padding: 20px;
}

.placeholder-text,
.simple-widget-text,
.unknown-text {
  font-size: 16px;
  font-weight: 500;
  margin-top: 12px;
}

.placeholder-subtext,
.simple-widget-id,
.unknown-subtext {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  margin-bottom: 16px;
}

/* KPI Widget */
.kpi-widget {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
}

.kpi-value {
  font-size: 32px;
  font-weight: bold;
  color: #2196f3;
  margin-bottom: 8px;
}

.kpi-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.trend-up {
  color: #4caf50;
}

.trend-down {
  color: #f44336;
}

.trend-neutral {
  color: #ff9800;
}

/* Widget Footer */
.widget-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  font-size: 11px;
  color: #666;
  min-height: 32px;
  flex-shrink: 0;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-loading {
  background: #ff9800;
  animation: pulse 1.5s infinite;
}

.status-ready {
  background: #4caf50;
}

.status-error {
  background: #f44336;
}

.last-updated {
  font-size: 10px;
  color: #999;
}

/* Dark Theme Overrides */
.widget-box--dark .widget-header,
.widget-box--dark .widget-footer {
  background: #383838;
  border-color: #505050;
}

.widget-box--dark .widget-title {
  color: #fff;
}

.widget-box--dark .widget-subtitle,
.widget-box--dark .status-text,
.widget-box--dark .last-updated {
  color: #ccc;
}

/* Animations */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Responsive */
@media (max-width: 600px) {
  .widget-header {
    padding: 8px 12px;
    min-height: 50px;
  }

  .widget-title {
    font-size: 13px;
  }

  .widget-subtitle {
    font-size: 11px;
  }

  .widget-type-chip {
    display: none;
  }
}
</style>
