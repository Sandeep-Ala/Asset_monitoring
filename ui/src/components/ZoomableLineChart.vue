<!-- src/components/ZoomableLineChart.vue -->
<!-- Advanced Chart.js Component with Zoom/Pan and Real Data Integration -->
<!-- Phase 6.3.4 - Complete Widget Visualization System -->

<template>
  <div class="zoomable-chart-container" :style="containerStyle">
    <!-- Chart Header -->
    <div class="chart-header" v-if="showHeader">
      <div class="chart-title">
        <h6 class="q-ma-none">{{ chartTitle }}</h6>
        <div class="chart-subtitle text-caption text-grey-7">
          {{ chartSubtitle }}
        </div>
      </div>

      <!-- Chart Controls -->
      <div class="chart-controls">
        <q-btn
          flat
          dense
          round
          icon="zoom_out_map"
          @click="resetZoom"
          :disable="isLoading"
          size="sm"
          color="grey-7"
        >
          <q-tooltip>Reset Zoom</q-tooltip>
        </q-btn>

        <q-btn
          flat
          dense
          round
          :icon="isAutoRefresh ? 'pause' : 'play_arrow'"
          @click="toggleAutoRefresh"
          :disable="isLoading"
          size="sm"
          :color="isAutoRefresh ? 'green' : 'grey-7'"
        >
          <q-tooltip>{{ isAutoRefresh ? 'Pause' : 'Start' }} Auto Refresh</q-tooltip>
        </q-btn>

        <q-btn
          flat
          dense
          round
          icon="refresh"
          @click="refreshData"
          :loading="isLoading"
          size="sm"
          color="primary"
        >
          <q-tooltip>Refresh Data</q-tooltip>
        </q-btn>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper" :class="{ 'with-header': showHeader }">
      <!-- Loading State -->
      <div v-if="isLoading && !hasData" class="chart-loading">
        <q-spinner-dots size="40px" color="primary" />
        <div class="text-body2 q-mt-sm">Loading chart data...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError && !hasData" class="chart-error">
        <q-icon name="error_outline" size="48px" color="negative" />
        <div class="text-h6 q-mt-sm">Unable to load data</div>
        <div class="text-body2 text-grey-7 q-mt-xs">{{ errorMessage }}</div>
        <q-btn
          flat
          label="Retry"
          @click="refreshData"
          color="primary"
          class="q-mt-md"
        />
      </div>

      <!-- Empty State -->
      <div v-else-if="!hasData && !isLoading" class="chart-empty">
        <q-icon name="timeline" size="48px" color="grey-4" />
        <div class="text-h6 q-mt-sm text-grey-6">No data available</div>
        <div class="text-body2 text-grey-7 q-mt-xs">
          {{ emptyMessage || 'No data found for the selected time range' }}
        </div>
      </div>

      <!-- Chart Canvas -->
      <div v-else class="chart-canvas-container">
        <canvas
          ref="chartCanvas"
          class="chart-canvas"
          :style="canvasStyle"
        ></canvas>

        <!-- Data Info Overlay -->
        <div v-if="showDataInfo" class="data-info-overlay">
          <q-chip
            size="sm"
            :color="dataPointCount > maxRecommendedPoints ? 'orange' : 'blue'"
            text-color="white"
            icon="scatter_plot"
          >
            {{ dataPointCount }} points
          </q-chip>

          <q-chip
            v-if="windowInfo"
            size="sm"
            color="grey"
            text-color="white"
            icon="tune"
            class="q-ml-xs"
          >
            {{ formatWindowPeriod(windowInfo) }}
          </q-chip>
        </div>
      </div>
    </div>

    <!-- Chart Footer/Legend -->
    <div v-if="showLegend && hasData" class="chart-legend">
      <div class="legend-items">
        <div
          v-for="(dataset, index) in legendItems"
          :key="index"
          class="legend-item"
          :class="{ 'legend-hidden': dataset.hidden }"
          @click="toggleDataset(index)"
        >
          <div
            class="legend-color"
            :style="{ backgroundColor: dataset.borderColor }"
          ></div>
          <span class="legend-label">{{ dataset.label }}</span>
          <span v-if="dataset.unit" class="legend-unit">({{ dataset.unit }})</span>
        </div>
      </div>
    </div>

    <!-- Loading Overlay for Refresh -->
    <div v-if="isLoading && hasData" class="refresh-overlay">
      <q-spinner size="24px" color="primary" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns'
import zoomPlugin from 'chartjs-plugin-zoom'

// Services and Utils
import { api } from 'boot/axios'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import {
  transformWidgetDataToChart,
  createLineChartConfig,
  defaultChartOptions,
  formatWindowPeriod,
  optimizeChartForLargeData
} from 'src/utils/chartUtils.js'

// Register Chart.js components
Chart.register(...registerables, zoomPlugin)

// ==================== PROPS ====================

const props = defineProps({
  // Widget Configuration
  widgetId: {
    type: String,
    required: true
  },
  widgetConfig: {
    type: Object,
    default: () => ({})
  },

  // Chart Appearance
  height: {
    type: [Number, String],
    default: 300
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showDataInfo: {
    type: Boolean,
    default: true
  },

  // Data Configuration
  autoRefresh: {
    type: Boolean,
    default: true
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30 seconds
  },
  maxRecommendedPoints: {
    type: Number,
    default: 500
  }
})

// ==================== EMITS ====================

const emit = defineEmits([
  'data-loaded',
  'data-error',
  'zoom-changed',
  'chart-ready'
])

// ==================== SETUP ====================

const $q = useQuasar()
const globalTime = useGlobalTime()

// ==================== REFS ====================

const chartCanvas = ref(null)
const chartInstance = ref(null)

// ==================== STATE ====================

// Loading and Error States
const isLoading = ref(false)
const hasError = ref(false)
const errorMessage = ref('')
const hasData = ref(false)

// Chart Data
const chartData = reactive({
  datasets: [],
  metadata: null
})

// Auto Refresh
const isAutoRefresh = ref(props.autoRefresh)
const refreshTimer = ref(null)

// Data Info
const dataPointCount = ref(0)
const windowInfo = ref(null)
const emptyMessage = ref('')

// ==================== COMPUTED ====================

const chartTitle = computed(() => {
  return props.widgetConfig?.widget_label || 'Chart Widget'
})

const chartSubtitle = computed(() => {
  const equipmentCount = props.widgetConfig?.equipment_ids?.length || 0
  const signalCount = props.widgetConfig?.signal_ids?.length || 0
  return `${equipmentCount} Equipment • ${signalCount} Signals`
})

const containerStyle = computed(() => ({
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  minHeight: '200px'
}))

const canvasStyle = computed(() => ({
  maxHeight: '100%',
  maxWidth: '100%'
}))

const legendItems = computed(() => {
  return chartData.datasets || []
})

// ==================== WATCHERS ====================

// Watch for global time changes
watch(
  () => globalTime.timeState.lastUpdated,
  () => {
    if (hasData.value) {
      console.log('🕒 Global time changed, refreshing chart data')
      refreshData()
    }
  }
)

// Watch for widget config changes
watch(
  () => props.widgetConfig,
  (newConfig, oldConfig) => {
    if (JSON.stringify(newConfig) !== JSON.stringify(oldConfig)) {
      console.log('⚙️ Widget config changed, refreshing chart')
      refreshData()
    }
  },
  { deep: true }
)

// Watch for auto refresh changes
watch(isAutoRefresh, (enabled) => {
  if (enabled) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// ==================== LIFECYCLE ====================

onMounted(async () => {
  console.log('📊 ZoomableLineChart mounted for widget:', props.widgetId)

  await nextTick()
  await initializeChart()
  await loadData()

  if (isAutoRefresh.value) {
    startAutoRefresh()
  }

  // Listen for global events
  window.addEventListener('globalTimeChanged', handleGlobalTimeChange)
})

onBeforeUnmount(() => {
  console.log('🧹 ZoomableLineChart unmounting')

  // Cleanup chart
  destroyChart()

  // Cleanup timers
  stopAutoRefresh()

  // Remove event listeners
  window.removeEventListener('globalTimeChanged', handleGlobalTimeChange)
})

// ==================== CHART INITIALIZATION ====================

async function initializeChart() {
  if (!chartCanvas.value) {
    console.error('❌ Chart canvas not found')
    return
  }

  try {
    // Destroy existing chart
    destroyChart()

    // Create chart configuration
    const config = createLineChartConfig(props.widgetConfig, { datasets: [] })

    // Enhanced configuration for zoom/pan
    config.options = {
      ...config.options,
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        ...config.options.plugins,
        zoom: {
          zoom: {
            wheel: {
              enabled: true,
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            onZoomComplete: handleZoomComplete
          },
          pan: {
            enabled: true,
            mode: 'x',
            onPanComplete: handlePanComplete
          }
        },
        legend: {
          display: false // We use custom legend
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#666',
          borderWidth: 1,
          cornerRadius: 6,
          displayColors: true,
          callbacks: {
            title: function(context) {
              return new Date(context[0].parsed.x).toLocaleString()
            },
            label: function(context) {
              const label = context.dataset.label || ''
              const value = typeof context.parsed.y === 'number' ?
                context.parsed.y.toFixed(4) : context.parsed.y
              const unit = context.dataset.unit || ''
              return `${label}: ${value} ${unit}`.trim()
            }
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          display: true,
          title: {
            display: true,
            text: 'Time'
          },
          time: {
            tooltipFormat: 'MMM dd, yyyy HH:mm:ss',
            displayFormats: {
              millisecond: 'HH:mm:ss.SSS',
              second: 'HH:mm:ss',
              minute: 'HH:mm',
              hour: 'MMM dd, HH:mm',
              day: 'MMM dd',
              week: 'MMM dd',
              month: 'MMM yyyy',
              quarter: 'MMM yyyy',
              year: 'yyyy'
            }
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Value'
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      }
    }

    // Create chart instance
    chartInstance.value = new Chart(chartCanvas.value, config)

    console.log('✅ Chart initialized successfully')
    emit('chart-ready', chartInstance.value)

  } catch (error) {
    console.error('❌ Failed to initialize chart:', error)
    hasError.value = true
    errorMessage.value = 'Failed to initialize chart'
  }
}

// ==================== DATA LOADING ====================

async function loadData() {
  if (!props.widgetId) {
    console.warn('⚠️ No widget ID provided')
    return
  }

  try {
    isLoading.value = true
    hasError.value = false
    errorMessage.value = ''

    console.log('📥 Loading data for widget:', props.widgetId)

    // Get current time range from global time state
    const timeRange = {
      start: globalTime.timeState.timeStart,
      end: globalTime.timeState.timeEnd,
      range_type: globalTime.timeState.rangeType || 'custom'
    }

    if (!timeRange.start || !timeRange.end) {
      throw new Error('No time range available')
    }

    // Make API call to get widget data
    const response = await api.post(`/widgets/${props.widgetId}/data`, {
      time_start: timeRange.start,
      time_end: timeRange.end,
      time_range_type: timeRange.range_type
    })

    const rawData = response.data
    console.log('📊 Raw data received:', rawData)

    // Check if data is empty
    if (rawData.isEmpty) {
      hasData.value = false
      emptyMessage.value = rawData.message || 'No data available for the selected time range'
      updateChart({ datasets: [] })
      return
    }

    // Transform data for Chart.js
    const transformedData = transformWidgetDataToChart(rawData, props.widgetConfig)

    if (transformedData.isEmpty) {
      hasData.value = false
      emptyMessage.value = transformedData.message || 'Unable to process chart data'
      return
    }

    // Update chart data
    updateChart(transformedData)

    // Update metadata
    windowInfo.value = rawData.window_info
    dataPointCount.value = rawData.totalPoints || 0

    hasData.value = true
    emit('data-loaded', transformedData)

    console.log('✅ Data loaded successfully:', {
      datasets: transformedData.datasets.length,
      points: dataPointCount.value
    })

  } catch (error) {
    console.error('❌ Failed to load chart data:', error)

    hasError.value = true
    hasData.value = false

    if (error.response?.status === 404) {
      errorMessage.value = 'Widget not found'
    } else if (error.response?.status === 500) {
      errorMessage.value = 'Server error loading data'
    } else if (error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Failed to load chart data'
    }

    emit('data-error', error)
  } finally {
    isLoading.value = false
  }
}

function updateChart(newData) {
  if (!chartInstance.value) return

  try {
    // Update chart data
    chartInstance.value.data = newData

    // Store reference for legend
    chartData.datasets = newData.datasets || []
    chartData.metadata = newData.metadata

    // Optimize for large datasets
    if (dataPointCount.value > props.maxRecommendedPoints) {
      optimizeChartForLargeData(chartInstance.value.config, dataPointCount.value)
    }

    // Update chart
    chartInstance.value.update('none') // Use 'none' for better performance

    console.log('📊 Chart updated with new data')

  } catch (error) {
    console.error('❌ Failed to update chart:', error)
  }
}

// ==================== CHART INTERACTIONS ====================

function resetZoom() {
  if (chartInstance.value) {
    chartInstance.value.resetZoom()
    emit('zoom-changed', 'reset')
    console.log('🔍 Chart zoom reset')
  }
}

function toggleDataset(datasetIndex) {
  if (!chartInstance.value) return

  try {
    const dataset = chartInstance.value.data.datasets[datasetIndex]
    if (dataset) {
      // Toggle visibility
      const meta = chartInstance.value.getDatasetMeta(datasetIndex)
      meta.hidden = meta.hidden === null ? !dataset.hidden : null

      // Update legend data
      if (chartData.datasets[datasetIndex]) {
        chartData.datasets[datasetIndex].hidden = meta.hidden
      }

      chartInstance.value.update()

      console.log('👁️ Dataset visibility toggled:', dataset.label, meta.hidden ? 'hidden' : 'visible')
    }
  } catch (error) {
    console.error('❌ Failed to toggle dataset:', error)
  }
}

function handleZoomComplete(event) {
  const chart = event.chart
  const xScale = chart.scales.x

  emit('zoom-changed', {
    type: 'zoom',
    min: xScale.min,
    max: xScale.max
  })

  console.log('🔍 Zoom completed:', { min: xScale.min, max: xScale.max })
}

function handlePanComplete(event) {
  const chart = event.chart
  const xScale = chart.scales.x

  emit('zoom-changed', {
    type: 'pan',
    min: xScale.min,
    max: xScale.max
  })

  console.log('👆 Pan completed:', { min: xScale.min, max: xScale.max })
}

// ==================== AUTO REFRESH ====================

function startAutoRefresh() {
  stopAutoRefresh()

  if (props.refreshInterval > 0) {
    refreshTimer.value = setInterval(() => {
      if (hasData.value && !isLoading.value) {
        console.log('🔄 Auto refresh triggered')
        refreshData()
      }
    }, props.refreshInterval)

    console.log('⏰ Auto refresh started:', props.refreshInterval / 1000, 'seconds')
  }
}

function stopAutoRefresh() {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
    console.log('⏹️ Auto refresh stopped')
  }
}

function toggleAutoRefresh() {
  isAutoRefresh.value = !isAutoRefresh.value

  $q.notify({
    type: 'info',
    message: `Auto refresh ${isAutoRefresh.value ? 'enabled' : 'disabled'}`,
    timeout: 2000
  })
}

// ==================== EVENT HANDLERS ====================

function refreshData() {
  console.log('🔄 Manual refresh triggered')
  loadData()
}

function handleGlobalTimeChange(event) {
  console.log('🕒 Global time change detected:', event.detail)
  if (hasData.value) {
    refreshData()
  }
}

// ==================== CLEANUP ====================

function destroyChart() {
  if (chartInstance.value) {
    try {
      chartInstance.value.destroy()
      chartInstance.value = null
      console.log('🗑️ Chart instance destroyed')
    } catch (error) {
      console.error('❌ Error destroying chart:', error)
    }
  }
}

// ==================== PUBLIC METHODS ====================

defineExpose({
  refreshData,
  resetZoom,
  toggleAutoRefresh,
  chartInstance: computed(() => chartInstance.value)
})
</script>

<style scoped>
.zoomable-chart-container {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
}

.chart-title h6 {
  color: #333;
  font-weight: 500;
  margin: 0;
}

.chart-subtitle {
  color: #757575;
  font-size: 12px;
  margin-top: 2px;
}

.chart-controls {
  display: flex;
  gap: 4px;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.chart-wrapper.with-header {
  min-height: calc(100% - 60px);
}

.chart-canvas-container {
  position: relative;
  height: 100%;
  padding: 8px;
}

.chart-canvas {
  display: block;
  height: 100% !important;
  width: 100% !important;
}

/* Loading, Error, Empty States */
.chart-loading,
.chart-error,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  text-align: center;
  padding: 20px;
}

.chart-error {
  color: #f44336;
}

.chart-empty {
  color: #757575;
}

/* Data Info Overlay */
.data-info-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  display: flex;
  gap: 4px;
}

/* Refresh Overlay */
.refresh-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Legend */
.chart-legend {
  border-top: 1px solid #e0e0e0;
  padding: 8px 16px;
  background: #fafafa;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  font-size: 12px;
}

.legend-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.legend-item.legend-hidden {
  opacity: 0.5;
}

.legend-item.legend-hidden .legend-label {
  text-decoration: line-through;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.legend-label {
  font-weight: 500;
  color: #333;
}

.legend-unit {
  color: #757575;
  font-size: 11px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .chart-header {
    padding: 8px 12px;
  }

  .chart-title h6 {
    font-size: 14px;
  }

  .chart-controls {
    gap: 2px;
  }

  .legend-items {
    gap: 8px;
  }

  .legend-item {
    padding: 2px 6px;
    font-size: 11px;
  }

  .data-info-overlay {
    top: 8px;
    right: 8px;
  }
}

/* Chart Cursor */
.chart-canvas {
  cursor: crosshair;
}

.chart-canvas:active {
  cursor: grabbing;
}

/* Animation */
.zoomable-chart-container {
  animation: fadeIn 0.3s ease-out;
}

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

/* Loading Animation */
.chart-loading .q-spinner-dots {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
