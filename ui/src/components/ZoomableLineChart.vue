<!--
  File: src/components/ZoomableLineChart.vue - FINAL WORKING VERSION
  Purpose: Professional interactive line chart with Chart.js integration

  CRITICAL FIXES APPLIED:
  1. Added missing LineController registration
  2. Fixed readonly data issue by cloning reactive data
  3. Enhanced canvas detection and lifecycle management
  4. Working manual refresh and time synchronization
-->

<template>
  <div class="zoomable-line-chart">
    <!-- Chart Container -->
    <div class="chart-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="chart-loading">
        <q-spinner color="primary" size="40px" />
        <div class="loading-text">
          {{ isInitialLoad ? 'Loading chart data...' : 'Refreshing...' }}
        </div>
        <div v-if="!isInitialLoad" class="loading-subtext">
          Time: {{ formatTimeRange }}
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="chart-error">
        <q-icon name="warning" color="negative" size="48px" />
        <div class="error-text">{{ error }}</div>
        <div class="error-details">
          <small>Widget ID: {{ widgetId }}</small>
          <small v-if="errorCount > 0">Errors: {{ errorCount }}</small>
        </div>
        <q-btn
          outline
          color="primary"
          icon="refresh"
          label="Retry"
          @click="handleRetryLoad"
          class="q-mt-md"
        />
      </div>

      <!-- No Data State -->
      <div v-else-if="isEmpty" class="chart-empty">
        <q-icon name="bar_chart" color="grey-5" size="48px" />
        <div class="empty-text">No data available</div>
        <div class="empty-subtext">
          Try adjusting the time range or check your data source
        </div>
        <div class="empty-time-info">
          Time range: {{ formatTimeRange }}
        </div>
        <q-btn
          outline
          color="primary"
          icon="refresh"
          label="Refresh Data"
          @click="handleManualRefresh"
          :loading="isRefreshing"
          class="q-mt-md"
        />
      </div>

      <!-- Chart Canvas -->
      <div v-else-if="hasData" class="canvas-wrapper">
        <canvas
          ref="chartCanvas"
          :id="`chart-${widgetId}`"
          class="chart-canvas"
        ></canvas>

        <!-- Loading overlay while chart initializes -->
        <div v-if="!isChartReady" class="chart-initializing">
          <q-spinner color="primary" size="30px" />
          <div class="init-text">Initializing chart...</div>
        </div>
      </div>

      <!-- Background Refresh Indicator -->
      <div v-if="isBackgroundRefresh" class="refresh-indicator">
        <q-spinner size="20px" color="primary" />
        <span class="q-ml-sm">Updating...</span>
      </div>
    </div>

    <!-- Chart Controls -->
    <div v-if="isChartReady && chartInstance" class="chart-controls">
      <!-- Manual Refresh Button -->
      <q-btn
        icon="refresh"
        size="sm"
        @click="handleManualRefresh"
        :loading="isRefreshing"
        :disable="isLoading"
        outline
        color="primary"
      >
        <q-tooltip>Manual Refresh</q-tooltip>
      </q-btn>

      <!-- Zoom Controls -->
      <q-btn-group outline class="q-ml-sm">
        <q-btn
          icon="zoom_out_map"
          size="sm"
          @click="resetZoom"
          :disable="!chartInstance"
        >
          <q-tooltip>Reset Zoom</q-tooltip>
        </q-btn>
        <q-btn
          icon="zoom_in"
          size="sm"
          @click="zoomIn"
          :disable="!chartInstance"
        >
          <q-tooltip>Zoom In</q-tooltip>
        </q-btn>
        <q-btn
          icon="zoom_out"
          size="sm"
          @click="zoomOut"
          :disable="!chartInstance"
        >
          <q-tooltip>Zoom Out</q-tooltip>
        </q-btn>
      </q-btn-group>

      <!-- Data Info -->
      <div class="q-ml-auto">
        <q-chip dense outline color="info">
          {{ totalDataPoints }} points
        </q-chip>
        <q-chip dense outline color="grey" class="q-ml-xs">
          {{ lastUpdateTime }}
        </q-chip>
      </div>
    </div>

    <!-- Debug Info -->
    <div v-if="showDebugInfo" class="debug-info q-mt-sm">
      <details>
        <summary>🔍 Debug Information</summary>
        <div class="debug-content">
          <div><strong>Widget ID:</strong> {{ widgetId }}</div>
          <div><strong>Chart Ready:</strong> {{ isChartReady ? '✅ Yes' : '❌ No' }}</div>
          <div><strong>Chart Instance:</strong> {{ chartInstance ? '✅ Yes' : '❌ No' }}</div>
          <div><strong>Canvas:</strong> {{ chartCanvas ? '✅ Found' : '❌ Missing' }}</div>
          <div><strong>Has Data:</strong> {{ hasData ? '✅ Yes' : '❌ No' }}</div>
          <div><strong>Is Empty:</strong> {{ isEmpty ? '⚠️ Yes' : '✅ No' }}</div>
          <div><strong>Current Time:</strong> {{ formatTimeRange }}</div>
          <div><strong>Global Time:</strong> {{ globalTimeDisplay }}</div>
          <div><strong>Canvas Size:</strong> {{ canvasSize }}</div>
          <div><strong>Container:</strong> {{ containerInfo }}</div>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

// CRITICAL FIX: Import ALL required Chart.js components including controllers
import {
  Chart,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  LineController,  // CRITICAL: This was missing and caused the error!
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
import 'chartjs-adapter-date-fns'

// Import composables
import { useWidgetData } from 'src/composables/useWidgetData.js'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'

// ==================== COMPONENT PROPS ====================

const props = defineProps({
  widgetId: {
    type: String,
    required: true
  },
  widgetConfig: {
    type: Object,
    required: true
  },
  chartHeight: {
    type: String,
    default: '300px'
  },
  enableZoom: {
    type: Boolean,
    default: true
  },
  enablePan: {
    type: Boolean,
    default: true
  },
  enableLegend: {
    type: Boolean,
    default: true
  },
  enableAutoRefresh: {
    type: Boolean,
    default: false
  },
  showDebugInfo: {
    type: Boolean,
    default: false
  }
})

// ==================== COMPONENT EMITS ====================

const emit = defineEmits([
  'chart-ready',
  'chart-error',
  'data-updated',
  'zoom-changed',
  'pan-changed'
])

// ==================== REACTIVE STATE ====================

const chartCanvas = ref(null)
const chartInstance = ref(null)
const isChartReady = ref(false)

// ==================== DATA INTEGRATION ====================

const globalTime = useGlobalTime()

const {
  rawData,
  chartData,
  metadata,
  isLoading,
  isInitialLoad,
  isBackgroundRefresh,
  isRetrying,
  error,
  errorCount,
  lastErrorTime,
  hasData,
  isEmpty,
  lastFetchTime,
  dataAge,
  dataStatus,
  currentTimeRange,
  isDataStale,
  needsBackgroundRefresh,
  performanceMetrics,
  initialize: initializeWidgetData,
  refresh,
  retryFetch,
  clearCache,
  startAutoRefresh,
  stopAutoRefresh,
  cleanup: cleanupWidgetData
} = useWidgetData(
  props.widgetId,
  props.widgetConfig,
  {
    enableCaching: true,
    enableAutoRefresh: false
  },
  null // Always use global time
)

// ==================== COMPUTED PROPERTIES ====================

const totalDataPoints = computed(() => {
  if (!chartData.value?.datasets) return 0
  return chartData.value.datasets.reduce((total, dataset) => {
    return total + (dataset.data?.length || 0)
  }, 0)
})

const lastUpdateTime = computed(() => {
  if (!lastFetchTime.value) return 'Never'
  return new Date(lastFetchTime.value).toLocaleTimeString()
})

const formatTimeRange = computed(() => {
  if (!currentTimeRange.value) return 'None'
  const start = new Date(currentTimeRange.value.start).toLocaleTimeString()
  const end = new Date(currentTimeRange.value.end).toLocaleTimeString()
  return `${start} - ${end}`
})

const globalTimeDisplay = computed(() => {
  if (!globalTime.currentTimeRange.value) return 'None'
  const start = new Date(globalTime.currentTimeRange.value.start).toLocaleTimeString()
  const end = new Date(globalTime.currentTimeRange.value.end).toLocaleTimeString()
  return `${start} - ${end}`
})

const isRefreshing = computed(() => {
  return isBackgroundRefresh.value || isRetrying.value
})

// Debug computed properties
const canvasSize = computed(() => {
  if (!chartCanvas.value) return 'N/A'
  const rect = chartCanvas.value.getBoundingClientRect()
  return `${rect.width}x${rect.height}`
})

const containerInfo = computed(() => {
  const container = document.querySelector(`[data-id="${props.widgetId}"]`)
  if (!container) return 'Not found'
  const rect = container.getBoundingClientRect()
  return `${rect.width}x${rect.height}`
})

// ==================== CHART.JS SETUP - FIXED ====================

// CRITICAL FIX: Register ALL required components including LineController
Chart.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  LineController,  // CRITICAL: This registration was missing!
  Title,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin
)

// ==================== LIFECYCLE HOOKS ====================

onMounted(async () => {
  console.log('🚀 ZoomableLineChart mounting for widget:', props.widgetId)

  try {
    // Initialize widget data management first
    await initializeWidgetData()

    // Enhanced canvas waiting with fallback
    try {
      await waitForChartRequirements()
    } catch (err) {
      console.warn('⚠️ Primary canvas waiting failed, trying alternative approach...')
      await waitForChartRequirementsAlternative()
    }

    emit('chart-ready', chartInstance.value)

  } catch (err) {
    console.error('❌ Error mounting chart:', err)

    const debugInfo = {
      widgetId: props.widgetId,
      canvasRef: !!chartCanvas.value,
      hasData: hasData.value,
      isEmpty: isEmpty.value,
      isLoading: isLoading.value,
      containerExists: !!document.querySelector(`[data-id="${props.widgetId}"]`)
    }

    console.error('📊 Chart mount debug info:', debugInfo)
    emit('chart-error', err)
  }
})

onBeforeUnmount(() => {
  console.log('🧹 ZoomableLineChart unmounting')
  destroyChart()
  cleanupWidgetData()
  removeEventListeners()
})

// ==================== ENHANCED DOM WAITING LOGIC ====================

async function waitForChartRequirements() {
  console.log('⏳ Waiting for chart requirements...')

  let domReady = false
  let attempts = 0
  const maxAttempts = 10
  const baseDelay = 150

  while (!domReady && attempts < maxAttempts) {
    await nextTick()

    // Exponential backoff delay
    const delay = baseDelay * Math.pow(1.5, attempts)
    await new Promise(resolve => setTimeout(resolve, delay))

    // Check if canvas element exists AND is visible
    if (chartCanvas.value) {
      const canvasRect = chartCanvas.value.getBoundingClientRect()
      const isVisible = canvasRect.width > 0 && canvasRect.height > 0

      if (isVisible) {
        console.log('✅ Canvas element found and visible')
        domReady = true
      } else {
        console.log(`⏳ Canvas found but not visible (${canvasRect.width}x${canvasRect.height}), attempt ${attempts + 1}/${maxAttempts}`)
      }
    } else {
      console.log(`⏳ Canvas not found, attempt ${attempts + 1}/${maxAttempts}`)
    }

    attempts++
  }

  if (!domReady) {
    const canvasInfo = chartCanvas.value ? {
      exists: true,
      rect: chartCanvas.value.getBoundingClientRect(),
      parentExists: !!chartCanvas.value.parentElement,
      parentRect: chartCanvas.value.parentElement?.getBoundingClientRect()
    } : { exists: false }

    console.error('❌ Canvas element debug info:', canvasInfo)
    throw new Error(`Canvas element not ready after ${maxAttempts} attempts. Canvas info: ${JSON.stringify(canvasInfo)}`)
  }

  setupChartInitialization()
}

async function waitForChartRequirementsAlternative() {
  console.log('⏳ Waiting for chart requirements (MutationObserver approach)...')

  return new Promise((resolve, reject) => {
    let timeoutId
    let observer

    timeoutId = setTimeout(() => {
      if (observer) observer.disconnect()
      reject(new Error('Canvas element not found within timeout period'))
    }, 8000) // 8 second timeout

    const checkCanvas = () => {
      if (chartCanvas.value) {
        const rect = chartCanvas.value.getBoundingClientRect()
        if (rect.width > 0 && rect.height > 0) {
          console.log('✅ Canvas element ready (alternative method)')
          clearTimeout(timeoutId)
          if (observer) observer.disconnect()
          setupChartInitialization()
          resolve()
          return true
        }
      }
      return false
    }

    // Check immediately
    if (checkCanvas()) return

    // Setup mutation observer to watch for DOM changes
    observer = new MutationObserver((mutations) => {
      checkCanvas()
    })

    // Observe the parent container for changes
    const container = document.querySelector(`[data-id="${props.widgetId}"]`)
    if (container) {
      observer.observe(container, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
      })
    }

    // Also check periodically
    const intervalId = setInterval(() => {
      if (checkCanvas()) {
        clearInterval(intervalId)
      }
    }, 200)

    // Cleanup interval on timeout
    setTimeout(() => clearInterval(intervalId), 8000)
  })
}

function setupChartInitialization() {
  console.log('📋 Setting up chart initialization watcher...')

  // Watch for data availability and initialize chart
  const stopWatcher = watch(
    [hasData, chartData, () => chartCanvas.value],
    async ([hasDataNow, chartDataNow, canvasNow]) => {
      console.log('📊 Chart initialization check:', {
        hasData: hasDataNow,
        hasChartData: !!chartDataNow,
        isEmpty: chartDataNow?.isEmpty,
        hasCanvas: !!canvasNow,
        hasChartInstance: !!chartInstance.value
      })

      if (hasDataNow && chartDataNow && !chartDataNow.isEmpty && canvasNow && !chartInstance.value) {
        console.log('📊 All requirements met, initializing chart...')
        try {
          await initializeChart()
          isChartReady.value = true
          stopWatcher() // Stop watching once chart is initialized
          console.log('✅ Chart initialization complete')
        } catch (err) {
          console.error('❌ Chart initialization failed:', err)
          emit('chart-error', err)
        }
      }
    },
    { immediate: true }
  )
}

// ==================== CHART INITIALIZATION - FIXED ====================

async function initializeChart() {
  if (!chartCanvas.value) {
    throw new Error('Canvas element not available')
  }

  if (chartInstance.value) {
    destroyChart()
  }

  try {
    console.log('📊 Initializing Chart.js instance...')

    // CRITICAL FIX: Clone the reactive data to avoid readonly issues
    const chartDataClone = JSON.parse(JSON.stringify(chartData.value))

    console.log('📊 Chart data clone:', {
      labels: chartDataClone.labels?.length || 0,
      datasets: chartDataClone.datasets?.length || 0
    })

    const config = {
      type: 'line',
      data: chartDataClone, // Use cloned data instead of reactive data
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: props.enableLegend,
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          },
          zoom: {
            pan: {
              enabled: props.enablePan,
              mode: 'x',
              onPanComplete: handlePanComplete
            },
            zoom: {
              wheel: {
                enabled: props.enableZoom,
              },
              pinch: {
                enabled: props.enableZoom
              },
              mode: 'x',
              onZoomComplete: handleZoomComplete
            }
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              displayFormats: {
                millisecond: 'HH:mm:ss.SSS',
                second: 'HH:mm:ss',
                minute: 'HH:mm',
                hour: 'HH:mm',
                day: 'MMM dd',
                week: 'MMM dd',
                month: 'MMM yyyy',
                quarter: 'MMM yyyy',
                year: 'yyyy'
              }
            },
            title: {
              display: true,
              text: 'Time'
            }
          },
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: props.widgetConfig?.y_axis_label || 'Value'
            }
          }
        }
      }
    }

    chartInstance.value = new Chart(chartCanvas.value, config)
    addEventListeners()

    console.log('📊 Chart initialized successfully')

  } catch (err) {
    console.error('❌ Chart initialization error:', err)
    throw err
  }
}

function destroyChart() {
  if (chartInstance.value) {
    console.log('🗑️ Destroying chart instance')
    chartInstance.value.destroy()
    chartInstance.value = null
    isChartReady.value = false
  }
}

// FIXED: Update chart data with cloning to avoid readonly issues
async function updateChartData(newData) {
  if (!chartInstance.value || !newData) return

  try {
    console.log('🔄 Updating chart with new data:', {
      datasets: newData.datasets?.length || 0,
      totalPoints: newData.datasets?.reduce((total, dataset) => total + (dataset.data?.length || 0), 0) || 0
    })

    // Clone the data to avoid readonly issues
    const chartDataClone = JSON.parse(JSON.stringify(newData))

    chartInstance.value.data = chartDataClone
    chartInstance.value.update('active')

  } catch (err) {
    console.error('❌ Error updating chart data:', err)
  }
}

// ==================== WATCHERS ====================

// Watch for chart data changes and update chart
watch(chartData, async (newData) => {
  if (newData && chartInstance.value) {
    await updateChartData(newData)
    emit('data-updated', newData)
  }
}, { deep: true })

// ==================== CONTROL METHODS ====================

// CRITICAL FIX: Use the correct refresh function from useWidgetData
async function handleManualRefresh() {
  console.log('🔄 Manual refresh button clicked for widget:', props.widgetId)
  console.log('🔍 Current time range:', currentTimeRange.value)

  try {
    // Call the correct refresh function from useWidgetData
    await refresh()
    console.log('✅ Manual refresh completed successfully')
  } catch (err) {
    console.error('❌ Manual refresh failed:', err)
    emit('chart-error', err)
  }
}

async function handleRetryLoad() {
  console.log('🔄 Retry button clicked for widget:', props.widgetId)

  try {
    await retryFetch()
    console.log('✅ Retry completed successfully')
  } catch (err) {
    console.error('❌ Retry failed:', err)
  }
}

function resetZoom() {
  if (chartInstance.value) {
    chartInstance.value.resetZoom()
    emit('zoom-changed', { type: 'reset' })
    console.log('🔍 Zoom reset')
  }
}

function zoomIn() {
  if (chartInstance.value) {
    chartInstance.value.zoom(1.1)
    emit('zoom-changed', { type: 'zoom-in' })
    console.log('🔍 Zoomed in')
  }
}

function zoomOut() {
  if (chartInstance.value) {
    chartInstance.value.zoom(0.9)
    emit('zoom-changed', { type: 'zoom-out' })
    console.log('🔍 Zoomed out')
  }
}

// ==================== EVENT HANDLERS ====================

function handleZoomComplete(context) {
  const { chart } = context
  const { min, max } = chart.scales.x
  console.log('🔍 Zoom completed:', { min, max })
  emit('zoom-changed', { min, max, type: 'zoom' })
}

function handlePanComplete(context) {
  const { chart } = context
  const { min, max } = chart.scales.x
  console.log('👆 Pan completed:', { min, max })
  emit('pan-changed', { min, max, type: 'pan' })
}

function handleGlobalTimeChange(event) {
  console.log('⏰ Global time change event detected:', event.detail)
  // The useWidgetData composable handles this automatically via watchers
}

// ==================== EVENT LISTENERS ====================

function addEventListeners() {
  window.addEventListener('globalTimeChanged', handleGlobalTimeChange)
}

function removeEventListeners() {
  window.removeEventListener('globalTimeChanged', handleGlobalTimeChange)
}

// ==================== EXPOSE PUBLIC METHODS ====================

defineExpose({
  chartInstance,
  resetZoom,
  zoomIn,
  zoomOut,
  refresh: handleManualRefresh, // Expose the correct refresh function
  rawData,
  chartData,
  metadata,
  hasData,
  isEmpty,
  isLoading,
  error
})
</script>

<style scoped>
.zoomable-line-chart {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.chart-container {
  position: relative;
  flex: 1;
  min-height: 200px;
  background: white;
  border-radius: 4px;
  overflow: hidden;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Chart Initializing Overlay */
.chart-initializing {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.init-text {
  margin-top: 12px;
  font-size: 14px;
  color: #666;
}

/* Loading States */
.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.loading-text {
  margin-top: 16px;
  font-size: 14px;
}

.loading-subtext {
  margin-top: 4px;
  font-size: 12px;
  color: #999;
}

/* Error State */
.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  text-align: center;
}

.error-text {
  margin: 16px 0 8px;
  font-size: 14px;
  max-width: 300px;
}

.error-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.error-details small {
  color: #999;
  font-size: 11px;
}

/* Empty State */
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  text-align: center;
}

.empty-text {
  margin: 16px 0 8px;
  font-size: 16px;
}

.empty-subtext {
  margin-bottom: 4px;
  font-size: 12px;
  color: #999;
}

.empty-time-info {
  margin-bottom: 16px;
  font-size: 11px;
  color: #999;
  font-family: monospace;
}

/* Controls */
.chart-controls {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  gap: 8px;
}

/* Background Refresh Indicator */
.refresh-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  z-index: 5;
}

/* Debug Info */
.debug-info {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 8px;
}

.debug-content {
  margin-top: 8px;
  font-size: 12px;
  font-family: monospace;
}

.debug-content div {
  margin-bottom: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    gap: 8px;
    padding: 12px;
  }
}

/* Animation */
.chart-initializing {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
