.data-controls {
  display: flex;
  gap: 8px;
}<!--
  File: src/components/ZoomableLineChart.vue
  Purpose: Professional time-series chart with zoom/pan capabilities
  Status: Part 1 + Part 2 - Basic Structure + Real Data Integration
  Dependencies: Chart.js, chartjs-plugin-zoom, useWidgetData, useGlobalTime
-->

<template>
  <div class="zoomable-line-chart">
    <!-- Chart Container -->
    <div
      ref="chartContainer"
      class="chart-container"
      :style="{ height: chartHeight }"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="chart-loading">
        <q-spinner-dots
          color="primary"
          size="50px"
        />
        <div class="loading-text">
          {{ isInitialLoad ? 'Loading chart data...' : 'Refreshing...' }}
        </div>
        <div v-if="!isInitialLoad" class="loading-subtext">
          {{ `Fetching ${totalDataPoints} data points` }}
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="chart-error">
        <q-icon name="warning" color="negative" size="48px" />
        <div class="error-text">{{ error }}</div>
        <div class="error-details">
          <small>Widget ID: {{ widgetId }}</small>
          <small v-if="errorCount > 0">Retry attempts: {{ errorCount }}</small>
        </div>
        <q-btn
          outline
          color="primary"
          icon="refresh"
          label="Retry"
          @click="retryLoad"
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
      </div>

      <!-- Chart Canvas -->
      <canvas
        v-else
        ref="chartCanvas"
        :id="`chart-${widgetId}`"
        class="chart-canvas"
      ></canvas>

      <!-- Background Refresh Indicator -->
      <div v-if="isBackgroundRefresh" class="refresh-indicator">
        <q-spinner size="20px" color="primary" />
        <span class="q-ml-sm">Updating...</span>
      </div>
    </div>

    <!-- Chart Controls -->
    <div v-if="!isLoading && !error && !isEmpty" class="chart-controls">
      <!-- Left Controls: Zoom -->
      <div class="zoom-controls">
        <q-btn-group outline>
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

      <!-- Data Controls -->
      <div class="data-controls">
        <q-btn-group outline class="q-ml-sm">
          <q-btn
            icon="refresh"
            size="sm"
            @click="refreshData"
            :loading="isRefreshing"
            :disable="isLoading"
          >
            <q-tooltip>Manual Refresh</q-tooltip>
          </q-btn>

          <!-- Auto Refresh Interval Selector -->
          <q-btn-dropdown
            :icon="isAutoRefreshActive ? 'pause' : 'play_arrow'"
            size="sm"
            :color="isAutoRefreshActive ? 'negative' : 'positive'"
            :label="autoRefreshLabel"
            dropdown-icon="expand_more"
          >
            <q-list>
              <q-item-label header>Auto Refresh Interval</q-item-label>

              <q-item
                clickable
                @click="setAutoRefresh(0)"
                :active="!isAutoRefreshActive"
              >
                <q-item-section>
                  <q-item-label>Manual Only</q-item-label>
                  <q-item-label caption>Disable auto refresh</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator />

              <q-item
                clickable
                @click="setAutoRefresh(2)"
                :active="isAutoRefreshActive && refreshInterval === 2"
              >
                <q-item-section>
                  <q-item-label>2 seconds</q-item-label>
                  <q-item-label caption>Very fast refresh</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                @click="setAutoRefresh(5)"
                :active="isAutoRefreshActive && refreshInterval === 5"
              >
                <q-item-section>
                  <q-item-label>5 seconds</q-item-label>
                  <q-item-label caption>Fast refresh</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                @click="setAutoRefresh(30)"
                :active="isAutoRefreshActive && refreshInterval === 30"
              >
                <q-item-section>
                  <q-item-label>30 seconds</q-item-label>
                  <q-item-label caption>Normal refresh</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                @click="setAutoRefresh(300)"
                :active="isAutoRefreshActive && refreshInterval === 300"
              >
                <q-item-section>
                  <q-item-label>5 minutes</q-item-label>
                  <q-item-label caption>Slow refresh</q-item-label>
                </q-item-section>
              </q-item>

              <q-item
                clickable
                @click="setAutoRefresh(600)"
                :active="isAutoRefreshActive && refreshInterval === 600"
              >
                <q-item-section>
                  <q-item-label>10 minutes</q-item-label>
                  <q-item-label caption>Very slow refresh</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </q-btn-group>
      </div>
      </div>

      <!-- Right Controls: Legend -->
      <div class="legend-controls">
        <div
          v-for="(dataset, index) in chartData?.datasets || []"
          :key="index"
          class="legend-item"
          @click="toggleDataset(index)"
        >
          <div
            class="legend-color"
            :style="{ backgroundColor: dataset.borderColor }"
          ></div>
          <span
            class="legend-label"
            :class="{ 'legend-hidden': dataset.hidden }"
          >
            {{ dataset.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- Chart Status Info -->
    <div v-if="showDebugInfo && hasData" class="chart-debug">
      <div class="debug-info">
        <small>
          Widget: {{ widgetId }} |
          Data Points: {{ totalDataPoints }} |
          Last Update: {{ lastUpdateTime }} |
          Cache: {{ performanceMetrics.cacheHit ? 'HIT' : 'MISS' }} |
          Time Range: {{ formatTimeRange }}
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
import 'chartjs-adapter-date-fns'

// Real Data Integration Imports
import { useWidgetData } from 'src/composables/useWidgetData.js'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import { transformWidgetDataToChart } from 'src/utils/dataFormatter.js'
import { createLineChartConfig, optimizeChartForLargeData } from 'src/utils/chartUtils.js'

// ==================== COMPONENT PROPS ====================

const props = defineProps({
  // Widget Configuration
  widgetId: {
    type: [String, Number],
    required: true
  },
  widgetConfig: {
    type: Object,
    default: () => ({})
  },

  // Custom Time Range (optional override)
  customTimeRange: {
    type: Object,
    default: null
  },

  // Chart Appearance
  chartHeight: {
    type: String,
    default: '300px'
  },

  // Features
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
    default: true
  },

  // Debug
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

// ==================== REFS ====================

// Chart instances
const chartContainer = ref(null)
const chartCanvas = ref(null)
const chartInstance = ref(null)

// ==================== REAL DATA INTEGRATION ====================

// Initialize widget data composable with real API integration
const {
  rawData,
  chartData,
  metadata,

  // Loading states
  isLoading,
  isInitialLoad,
  isBackgroundRefresh,
  isRetrying,

  // Error handling
  error,
  errorCount,
  lastErrorTime,

  // Data status
  hasData,
  isEmpty,
  lastFetchTime,
  dataAge,
  dataStatus,

  // Computed properties
  currentTimeRange,
  isDataStale,
  needsBackgroundRefresh,
  performanceMetrics,

  // Actions
  initialize: initializeWidgetData,
  refresh: refreshData,
  retryFetch,
  clearCache,
  startAutoRefresh,
  stopAutoRefresh,
  cleanup: cleanupWidgetData
} = useWidgetData(
  props.widgetId,  // Fixed: Pass the actual widget ID, not a function
  props.widgetConfig,  // Fixed: Pass the actual config, not a function
  {
    enableCaching: true,
    enableAutoRefresh: props.enableAutoRefresh
  },
  props.customTimeRange  // Fixed: Pass the actual time range, not a function
)

// Global time management
const globalTime = useGlobalTime()

// ==================== REACTIVE STATE ====================

// Auto-refresh management
const refreshInterval = ref(30) // Default 30 seconds
const refreshTimer = ref(null)

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

const isAutoRefreshActive = computed(() => {
  return refreshTimer.value !== null
})

const isRefreshing = computed(() => {
  return isBackgroundRefresh.value || isRetrying.value
})

const autoRefreshLabel = computed(() => {
  if (!isAutoRefreshActive.value) return 'Manual'
  if (refreshInterval.value < 60) return `${refreshInterval.value}s`
  return `${Math.floor(refreshInterval.value / 60)}m`
})

// ==================== CHART.JS SETUP ====================

// Register Chart.js components
Chart.register(...registerables, zoomPlugin)

// ==================== LIFECYCLE HOOKS ====================

onMounted(async () => {
  console.log('🚀 ZoomableLineChart mounting for widget:', props.widgetId)

  try {
    await nextTick()

    // Initialize widget data management
    await initializeWidgetData()

    // Initialize chart
    await initializeChart()

    // Start auto-refresh if enabled
    if (props.enableAutoRefresh) {
      startAutoRefresh()
    }

    emit('chart-ready', chartInstance.value)

  } catch (err) {
    console.error('❌ Error mounting chart:', err)
    emit('chart-error', err)
  }
})

onBeforeUnmount(() => {
  console.log('🧹 ZoomableLineChart unmounting')

  // Cleanup chart
  destroyChart()

  // Cleanup widget data
  cleanupWidgetData()

  // Stop auto-refresh
  stopAutoRefresh()
  stopCustomAutoRefresh()

  // Remove global event listeners
  removeEventListeners()
})

// ==================== WATCHERS ====================

// Watch for chart data changes and update chart
watch(chartData, async (newData) => {
  if (newData && chartInstance.value) {
    console.log('📊 Chart data changed, updating chart...', {
      datasets: newData.datasets?.length || 0,
      totalPoints: newData.datasets?.reduce((total, dataset) => total + (dataset.data?.length || 0), 0) || 0
    })

    // CRITICAL FIX: Sort data before updating chart (frontend backup)
    const sortedData = sortChartDataByTime(newData)

    await updateChartData(sortedData)
    emit('data-updated', sortedData)
  }
}, { deep: true })

// Watch for global time changes
watch(currentTimeRange, async (newRange, oldRange) => {
  if (newRange && hasData.value) {
    // Only refresh if time range actually changed
    if (JSON.stringify(newRange) !== JSON.stringify(oldRange)) {
      console.log('⏰ Time range changed, refreshing chart data...', newRange)
      await refreshData()
    }
  }
}, { deep: true })

// ==================== DATA SORTING FIX ====================

function sortChartDataByTime(chartData) {
  if (!chartData || !chartData.labels || !chartData.datasets) {
    return chartData
  }

  try {
    console.log('🔄 Sorting chart data by time (frontend backup)')

    // Create array of {index, time, label} for sorting
    const labelTimeMap = chartData.labels.map((label, index) => ({
      index,
      label,
      time: parseTimeLabel(label)
    }))

    // Sort by time
    labelTimeMap.sort((a, b) => a.time - b.time)

    // Create new sorted labels
    const sortedLabels = labelTimeMap.map(item => item.label)

    // Sort datasets according to the new order
    const sortedDatasets = chartData.datasets.map(dataset => ({
      ...dataset,
      data: labelTimeMap.map(item => dataset.data[item.index])
    }))

    console.log('✅ Chart data sorted successfully')

    return {
      ...chartData,
      labels: sortedLabels,
      datasets: sortedDatasets
    }

  } catch (error) {
    console.warn('⚠️ Error sorting chart data, using original:', error)
    return chartData
  }
}

function parseTimeLabel(label) {
  try {
    // Handle time-only format like "09:00:00"
    if (typeof label === 'string' && label.includes(':')) {
      const [hours, minutes, seconds] = label.split(':').map(Number)
      // Use today's date with the time
      const today = new Date()
      today.setHours(hours, minutes, seconds || 0, 0)
      return today.getTime()
    }

    // Handle Date objects
    if (label instanceof Date) {
      return label.getTime()
    }

    // Handle ISO strings
    if (typeof label === 'string') {
      return new Date(label).getTime()
    }

    return 0
  } catch (error) {
    console.warn('⚠️ Could not parse time label:', label)
    return 0
  }
}

// ==================== CHART METHODS ====================

async function initializeChart() {
  if (!chartCanvas.value) {
    throw new Error('Chart canvas not found')
  }

  try {
    // Destroy existing chart
    destroyChart()

    // Create initial chart configuration
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
              enabled: props.enableZoom,
            },
            pinch: {
              enabled: props.enableZoom
            },
            mode: 'x',
            onZoomComplete: handleZoomComplete
          },
          pan: {
            enabled: props.enablePan,
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
                context.parsed.y.toFixed(2) : context.parsed.y
              return `${label}: ${value}`
            }
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

    // Create chart instance
    chartInstance.value = new Chart(chartCanvas.value, config)

    // Add event listeners
    addEventListeners()

    console.log('📊 Chart initialized successfully')

  } catch (err) {
    console.error('❌ Chart initialization error:', err)
    throw err
  }
}

async function updateChartData(newData) {
  if (!chartInstance.value || !newData) return

  try {
    console.log('🔄 Updating chart with new data:', {
      datasets: newData.datasets?.length || 0,
      totalPoints: newData.datasets?.reduce((total, dataset) => total + (dataset.data?.length || 0), 0) || 0,
      isEmpty: newData.isEmpty
    })

    // Handle empty data
    if (newData.isEmpty) {
      chartInstance.value.data = { labels: [], datasets: [] }
      chartInstance.value.update('none')
      return
    }

    // Optimize chart for large datasets
    const dataPointCount = newData.datasets?.reduce((total, dataset) =>
      total + (dataset.data?.length || 0), 0) || 0

    if (dataPointCount > 1000) {
      optimizeChartForLargeData(chartInstance.value.config, dataPointCount)
    }

    // Update chart data - newData is already in Chart.js format from dataFormatter
    chartInstance.value.data = {
      labels: newData.labels || [],
      datasets: newData.datasets || []
    }

    // Update chart configuration if needed
    updateChartConfiguration(newData)

    // Fast update without animation for better performance
    chartInstance.value.update('none')

    console.log(`📊 Chart updated successfully with ${dataPointCount} data points`)

  } catch (err) {
    console.error('❌ Error updating chart data:', err)
  }
}

function updateChartConfiguration(newData) {
  if (!chartInstance.value || !newData.metadata) return

  try {
    // Update Y-axis label if available
    if (newData.metadata.widgetInfo?.y_axis_label) {
      chartInstance.value.options.scales.y.title.text = newData.metadata.widgetInfo.y_axis_label
    }

    // Update chart title if available
    if (newData.metadata.widgetInfo?.widget_label) {
      chartInstance.value.options.plugins.title.text = newData.metadata.widgetInfo.widget_label
    }

  } catch (err) {
    console.warn('⚠️ Error updating chart configuration:', err)
  }
}

function destroyChart() {
  if (chartInstance.value) {
    try {
      chartInstance.value.destroy()
      chartInstance.value = null
      console.log('📊 Chart instance destroyed')
    } catch (err) {
      console.error('❌ Error destroying chart:', err)
    }
  }
}

// ==================== EVENT HANDLERS ====================

function handleZoomComplete(context) {
  const { chart } = context
  const { min, max } = chart.scales.x

  console.log('🔍 Zoom completed:', { min, max })
  emit('zoom-changed', { min, max, type: 'zoom' })

  // Emit global zoom event for chart synchronization
  window.dispatchEvent(new CustomEvent('chartZoomed', {
    detail: { chartId: chart.canvas.id, scale: { min, max } }
  }))
}

function handlePanComplete(context) {
  const { chart } = context
  const { min, max } = chart.scales.x

  console.log('👆 Pan completed:', { min, max })
  emit('pan-changed', { min, max, type: 'pan' })

  // Emit global pan event for chart synchronization
  window.dispatchEvent(new CustomEvent('chartPanned', {
    detail: { chartId: chart.canvas.id, scale: { min, max } }
  }))
}

function handleGlobalTimeChange(event) {
  console.log('⏰ Global time change detected:', event.detail)
  // Data will be automatically refreshed by the watcher
}

// ==================== CONTROL METHODS ====================

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

function toggleDataset(index) {
  if (chartInstance.value && chartData.value?.datasets?.[index]) {
    const dataset = chartData.value.datasets[index]
    dataset.hidden = !dataset.hidden
    chartInstance.value.update()

    console.log(`👁️ Dataset "${dataset.label}" ${dataset.hidden ? 'hidden' : 'shown'}`)
  }
}

function toggleAutoRefresh() {
  if (isAutoRefreshActive.value) {
    stopCustomAutoRefresh()
    console.log('⏸️ Auto-refresh paused')
  } else {
    startCustomAutoRefresh()
    console.log('▶️ Auto-refresh started')
  }
}

function setAutoRefresh(intervalSeconds) {
  stopCustomAutoRefresh()

  if (intervalSeconds > 0) {
    refreshInterval.value = intervalSeconds
    startCustomAutoRefresh()
    console.log(`⏰ Auto-refresh set to ${intervalSeconds} seconds`)
  } else {
    console.log('⏸️ Auto-refresh disabled')
  }
}

function startCustomAutoRefresh() {
  if (refreshTimer.value) return // Already running

  refreshTimer.value = setInterval(async () => {
    if (!isLoading.value) {
      console.log(`🔄 Auto-refresh triggered (${refreshInterval.value}s interval)`)
      await refreshData()
    }
  }, refreshInterval.value * 1000)
}

function stopCustomAutoRefresh() {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

function retryLoad() {
  console.log('🔄 Retrying data load...')
  retryFetch()
}

// ==================== EVENT LISTENERS ====================

function addEventListeners() {
  // Listen for global time changes
  window.addEventListener('globalTimeChanged', handleGlobalTimeChange)

  // Listen for chart synchronization events
  window.addEventListener('chartZoomed', handleChartSyncZoom)
  window.addEventListener('chartPanned', handleChartSyncPan)
}

function removeEventListeners() {
  window.removeEventListener('globalTimeChanged', handleGlobalTimeChange)
  window.removeEventListener('chartZoomed', handleChartSyncZoom)
  window.removeEventListener('chartPanned', handleChartSyncPan)
}

function handleChartSyncZoom(event) {
  const { chartId, scale } = event.detail
  if (chartInstance.value && chartInstance.value.canvas.id !== chartId) {
    chartInstance.value.zoomScale('x', scale, 'none')
  }
}

function handleChartSyncPan(event) {
  const { chartId, scale } = event.detail
  if (chartInstance.value && chartInstance.value.canvas.id !== chartId) {
    chartInstance.value.zoomScale('x', scale, 'none')
  }
}

// ==================== EXPOSE PUBLIC METHODS ====================

defineExpose({
  chartInstance,
  resetZoom,
  zoomIn,
  zoomOut,
  retryLoad,
  toggleDataset,
  refreshData,
  toggleAutoRefresh,
  // Data access
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

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
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
  font-size: 14px;
}

.empty-subtext {
  font-size: 12px;
  color: #999;
  max-width: 300px;
}

/* Background Refresh Indicator */
.refresh-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  backdrop-filter: blur(4px);
}

/* Controls */
.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
  min-height: 48px;
}

.zoom-controls {
  display: flex;
  gap: 8px;
}

.legend-controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  max-width: 60%;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.legend-item:hover {
  background-color: #f0f0f0;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid #ddd;
}

.legend-label {
  font-size: 12px;
  color: #333;
  transition: opacity 0.2s;
}

.legend-hidden {
  opacity: 0.5;
  text-decoration: line-through;
}

/* Debug Info */
.chart-debug {
  padding: 4px 8px;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
  font-family: monospace;
}

.debug-info {
  color: #666;
  font-size: 11px;
}

/* Responsive */
@media (max-width: 600px) {
  .chart-controls {
    flex-direction: column;
    gap: 8px;
  }

  .legend-controls {
    max-width: 100%;
    justify-content: center;
  }

  .zoom-controls {
    flex-direction: row;
    justify-content: center;
  }
}
</style>
