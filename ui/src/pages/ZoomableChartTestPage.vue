<!--
  File: src/pages/ZoomableChartTestPage.vue
  Purpose: Comprehensive testing for ZoomableLineChart component
  Tests: Part 1 (Basic Structure) + Part 2 (Real Data Integration)
-->

<template>
  <q-page padding class="zoomable-chart-test-page">
    <!-- Page Header -->
    <div class="page-header q-mb-lg">
      <h4 class="text-h4 q-ma-none">ZoomableLineChart Test Lab</h4>
      <p class="text-subtitle1 text-grey-7 q-mt-sm">
        Comprehensive testing for Parts 1 & 2: Basic Structure + Real Data Integration
      </p>
    </div>

    <!-- Test Configuration Card -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">🧪 Test Configuration</div>

        <div class="row q-gutter-md">
          <!-- Widget Selection -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="selectedWidgetId"
              :options="widgetOptions"
              label="Test Widget"
              outlined
              dense
              emit-value
              map-options
            />
          </div>

          <!-- Test Mode -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="testMode"
              :options="testModeOptions"
              label="Test Mode"
              outlined
              dense
              emit-value
              map-options
            />
          </div>

          <!-- Chart Height -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="chartHeight"
              :options="heightOptions"
              label="Chart Height"
              outlined
              dense
              emit-value
              map-options
            />
          </div>
        </div>

        <!-- Time Range Configuration -->
        <div class="q-mt-md">
          <div class="text-subtitle2 q-mb-sm">⏰ Time Range Configuration</div>
          <div class="row q-gutter-md">
            <div class="col-12 col-md-3">
              <q-select
                v-model="quickPreset"
                :options="presetOptions"
                label="Quick Preset"
                outlined
                dense
                emit-value
                map-options
                @update:model-value="applyPreset"
              />
            </div>
            <div class="col-12 col-md-4">
              <q-input
                v-model="customStartTime"
                type="datetime-local"
                label="Custom Start Time"
                outlined
                dense
                @update:model-value="onTimeRangeChange"
              />
            </div>
            <div class="col-12 col-md-4">
              <q-input
                v-model="customEndTime"
                type="datetime-local"
                label="Custom End Time"
                outlined
                dense
                @update:model-value="onTimeRangeChange"
              />
            </div>
          </div>

          <!-- Time Range Error -->
          <div v-if="timeRangeError" class="text-negative q-mt-sm">
            {{ timeRangeError }}
          </div>
        </div>

        <!-- Feature Toggles -->
        <div class="q-mt-md">
          <div class="text-subtitle2 q-mb-sm">🎛️ Feature Configuration</div>
          <div class="row q-gutter-md">
            <q-toggle v-model="enableZoom" label="Enable Zoom" />
            <q-toggle v-model="enablePan" label="Enable Pan" />
            <q-toggle v-model="enableLegend" label="Enable Legend" />
            <q-toggle v-model="enableAutoRefresh" label="Enable Auto-refresh" />
            <q-toggle v-model="showDebugInfo" label="Show Debug Info" />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="q-mt-md">
          <q-btn-group>
            <q-btn
              color="primary"
              icon="play_arrow"
              label="Start Test"
              @click="startTest"
              :loading="isTestRunning"
            />
            <q-btn
              outline
              color="secondary"
              icon="refresh"
              label="Reset"
              @click="resetTest"
            />
            <q-btn
              outline
              color="info"
              icon="info"
              label="Show Test Data"
              @click="showTestData = !showTestData"
            />
          </q-btn-group>
        </div>
      </q-card-section>
    </q-card>

    <!-- Test Results Card -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">📊 Test Results</div>

        <!-- Test Status -->
        <div class="test-status q-mb-md">
          <div class="row q-gutter-md">
            <div class="col">
              <q-chip
                :color="testStatus.color"
                text-color="white"
                :icon="testStatus.icon"
              >
                {{ testStatus.label }}
              </q-chip>
            </div>
            <div class="col-auto">
              <q-btn
                v-if="chartRef"
                outline
                size="sm"
                icon="zoom_out_map"
                label="Reset Zoom"
                @click="chartRef.resetZoom()"
              />
            </div>
          </div>
        </div>

        <!-- Chart Container -->
        <div class="chart-test-container">
          <ZoomableLineChart
            v-if="isTestActive"
            ref="chartRef"
            :widget-id="selectedWidgetId"
            :widget-config="currentWidgetConfig"
            :custom-time-range="customTimeRange"
            :chart-height="chartHeight"
            :enable-zoom="enableZoom"
            :enable-pan="enablePan"
            :enable-legend="enableLegend"
            :enable-auto-refresh="enableAutoRefresh"
            :show-debug-info="showDebugInfo"
            @chart-ready="onChartReady"
            @chart-error="onChartError"
            @data-updated="onDataUpdated"
            @zoom-changed="onZoomChanged"
            @pan-changed="onPanChanged"
          />

          <!-- Placeholder when test not active -->
          <div v-else class="chart-placeholder">
            <q-icon name="bar_chart" size="64px" color="grey-5" />
            <div class="text-h6 q-mt-md text-grey-7">Click "Start Test" to begin</div>
          </div>
        </div>

        <!-- Chart Events Log -->
        <div v-if="chartEvents.length > 0" class="q-mt-md">
          <q-expansion-item
            label="Chart Events Log"
            icon="event_note"
            header-class="text-subtitle2"
          >
            <div class="events-log">
              <div
                v-for="(event, index) in chartEvents.slice(-10)"
                :key="index"
                class="event-item"
              >
                <span class="event-time">{{ event.time }}</span>
                <span class="event-type" :class="event.type">{{ event.type }}</span>
                <span class="event-message">{{ event.message }}</span>
              </div>
            </div>
          </q-expansion-item>
        </div>
      </q-card-section>
    </q-card>

    <!-- Test Data Inspection -->
    <q-card v-if="showTestData" class="q-mb-lg">
      <q-card-section>
        <div class="text-h6 q-mb-md">🔍 Test Data Inspection</div>

        <q-tabs v-model="dataTab" dense>
          <q-tab name="raw" label="Raw Data" />
          <q-tab name="chart" label="Chart Data" />
          <q-tab name="metadata" label="Metadata" />
          <q-tab name="performance" label="Performance" />
        </q-tabs>

        <q-tab-panels v-model="dataTab" animated>
          <!-- Raw Data -->
          <q-tab-panel name="raw">
            <div class="data-inspector">
              <div v-if="chartRef?.rawData" class="data-content">
                <pre>{{ JSON.stringify(chartRef.rawData, null, 2) }}</pre>
              </div>
              <div v-else class="no-data">No raw data available</div>
            </div>
          </q-tab-panel>

          <!-- Chart Data -->
          <q-tab-panel name="chart">
            <div class="data-inspector">
              <div v-if="chartRef?.chartData" class="data-content">
                <div class="data-summary q-mb-md">
                  <q-chip outline>
                    Datasets: {{ chartRef.chartData.datasets?.length || 0 }}
                  </q-chip>
                  <q-chip outline>
                    Total Points: {{ totalDataPoints }}
                  </q-chip>
                </div>
                <pre>{{ JSON.stringify(chartRef.chartData, null, 2) }}</pre>
              </div>
              <div v-else class="no-data">No chart data available</div>
            </div>
          </q-tab-panel>

          <!-- Metadata -->
          <q-tab-panel name="metadata">
            <div class="data-inspector">
              <div v-if="chartRef?.metadata" class="data-content">
                <pre>{{ JSON.stringify(chartRef.metadata, null, 2) }}</pre>
              </div>
              <div v-else class="no-data">No metadata available</div>
            </div>
          </q-tab-panel>

          <!-- Performance -->
          <q-tab-panel name="performance">
            <div class="performance-metrics">
              <div class="metrics-grid">
                <div class="metric-card">
                  <div class="metric-value">{{ performanceData.loadTime }}ms</div>
                  <div class="metric-label">Load Time</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">{{ performanceData.renderTime }}ms</div>
                  <div class="metric-label">Render Time</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">{{ performanceData.dataPoints }}</div>
                  <div class="metric-label">Data Points</div>
                </div>
                <div class="metric-card">
                  <div class="metric-value">{{ performanceData.cacheHit ? 'HIT' : 'MISS' }}</div>
                  <div class="metric-label">Cache Status</div>
                </div>
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Test Instructions -->
    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">📋 Testing Instructions</div>

        <q-list dense>
          <q-item-label header>Part 1 Testing (Basic Structure)</q-item-label>
          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Verify chart canvas renders correctly</q-item-label>
              <q-item-label caption>Check that the chart container and canvas element appear</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test zoom controls (wheel, buttons, reset)</q-item-label>
              <q-item-label caption>Use mouse wheel to zoom, test zoom in/out buttons</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test pan functionality (click and drag)</q-item-label>
              <q-item-label caption>Click and drag on chart to pan through time</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test legend controls (hide/show datasets)</q-item-label>
              <q-item-label caption>Click on legend items to toggle dataset visibility</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator class="q-my-md" />

          <q-item-label header>Part 2 Testing (Real Data Integration)</q-item-label>
          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Verify real API data loading</q-item-label>
              <q-item-label caption>Ensure data comes from widget API endpoint</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test time range changes</q-item-label>
              <q-item-label caption>Change time range and verify chart updates</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test auto-refresh functionality</q-item-label>
              <q-item-label caption>Enable auto-refresh and verify periodic updates</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section avatar>
              <q-icon name="check_circle" color="positive" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Test error handling</q-item-label>
              <q-item-label caption>Verify proper error display and retry functionality</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import ZoomableLineChart from 'src/components/ZoomableLineChart.vue'

const $q = useQuasar()

// ==================== REACTIVE STATE ====================

// Component refs
const chartRef = ref(null)

// Test configuration
const selectedWidgetId = ref('2d6ba3a5-1d2c-4c6d-bc39-5d2a1411b532')
const testMode = ref('real-api')
const chartHeight = ref('400px')
const isTestRunning = ref(false)
const isTestActive = ref(false)

// Widget options
const widgetOptions = [
  { label: 'soc bms-1', value: '2d6ba3a5-1d2c-4c6d-bc39-5d2a1411b532' },
  { label: 'SOC BMS', value: '6dd220a2-5752-452a-b4fe-a7990f80fab9' },
  { label: 'DC Voltage', value: '11de1d52-bba6-4d3c-9d07-3106d86c3056' }
]

const testModeOptions = [
  { label: 'Real API Test', value: 'real-api' },
  { label: 'Mock Data Test', value: 'mock-data' },
  { label: 'Error Simulation', value: 'error-sim' },
  { label: 'Performance Test', value: 'performance' }
]

const heightOptions = [
  { label: '300px', value: '300px' },
  { label: '400px', value: '400px' },
  { label: '500px', value: '500px' },
  { label: '600px', value: '600px' }
]

// Time range configuration
const customStartTime = ref('')
const customEndTime = ref('')
const quickPreset = ref('last_1h')
const timeRangeError = ref('')

const presetOptions = [
  { label: 'Last 15 minutes', value: 'last_15m' },
  { label: 'Last 1 hour', value: 'last_1h' },
  { label: 'Last 6 hours', value: 'last_6h' },
  { label: 'Last 24 hours', value: 'last_24h' },
  { label: 'Custom', value: 'custom' }
]

// Feature toggles
const enableZoom = ref(true)
const enablePan = ref(true)
const enableLegend = ref(true)
const enableAutoRefresh = ref(true)
const showDebugInfo = ref(true)

// Test data inspection
const showTestData = ref(false)
const dataTab = ref('raw')

// Chart events tracking
const chartEvents = ref([])
const performanceData = ref({
  loadTime: 0,
  renderTime: 0,
  dataPoints: 0,
  cacheHit: false
})

// ==================== COMPUTED PROPERTIES ====================

const testStatus = computed(() => {
  if (isTestRunning.value) {
    return { color: 'warning', icon: 'hourglass_empty', label: 'Running...' }
  }
  if (isTestActive.value) {
    return { color: 'positive', icon: 'check_circle', label: 'Active' }
  }
  return { color: 'grey', icon: 'radio_button_unchecked', label: 'Inactive' }
})

const currentWidgetConfig = computed(() => ({
  widget_label: `Test Chart (${testMode.value})`,
  y_axis_label: 'Test Values',
  chart_type: 'line',
  styling_config: {
    colors: ['#1976d2', '#388e3c', '#f57c00'],
    line_width: 2
  }
}))

const customTimeRange = computed(() => {
  if (!customStartTime.value || !customEndTime.value) return null

  return {
    start: customStartTime.value,
    end: customEndTime.value
  }
})

const totalDataPoints = computed(() => {
  if (!chartRef.value?.chartData?.datasets) return 0
  return chartRef.value.chartData.datasets.reduce((total, dataset) => {
    return total + (dataset.data?.length || 0)
  }, 0)
})

// ==================== LIFECYCLE HOOKS ====================

onMounted(() => {
  console.log('🧪 ZoomableChart Test Lab initialized')
  setDefaultTimeInputs()
})

// ==================== METHODS ====================

/**
 * Set default time inputs (last 1 hour)
 */
function setDefaultTimeInputs() {
  const now = new Date()
  const oneHourAgo = new Date(now - 60 * 60 * 1000)

  customStartTime.value = formatToDatetimeLocal(oneHourAgo)
  customEndTime.value = formatToDatetimeLocal(now)

  addEvent('info', 'Default time range set to last 1 hour')
}

/**
 * Format date to datetime-local input format
 */
function formatToDatetimeLocal(date) {
  return date.toISOString().slice(0, 16)
}

/**
 * Apply quick preset time ranges
 */
function applyPreset(preset) {
  const now = new Date()
  let startTime

  switch (preset) {
    case 'last_15m':
      startTime = new Date(now - 15 * 60 * 1000)
      break
    case 'last_1h':
      startTime = new Date(now - 60 * 60 * 1000)
      break
    case 'last_6h':
      startTime = new Date(now - 6 * 60 * 60 * 1000)
      break
    case 'last_24h':
      startTime = new Date(now - 24 * 60 * 60 * 1000)
      break
    default:
      return // Custom - don't change times
  }

  if (startTime) {
    customStartTime.value = formatToDatetimeLocal(startTime)
    customEndTime.value = formatToDatetimeLocal(now)
    addEvent('info', `Applied preset: ${preset}`)
  }
}

/**
 * Handle time range changes
 */
function onTimeRangeChange() {
  validateTimeRange()
  if (quickPreset.value !== 'custom') {
    quickPreset.value = 'custom'
  }
}

/**
 * Validate time range
 */
function validateTimeRange() {
  timeRangeError.value = ''

  if (!customStartTime.value || !customEndTime.value) {
    timeRangeError.value = 'Both start and end times are required'
    return false
  }

  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)

  if (start >= end) {
    timeRangeError.value = 'Start time must be before end time'
    return false
  }

  const diffDays = (end - start) / (1000 * 60 * 60 * 24)
  if (diffDays > 30) {
    timeRangeError.value = 'Time range cannot exceed 30 days'
    return false
  }

  return true
}

/**
 * Start the test
 */
async function startTest() {
  if (!validateTimeRange()) {
    $q.notify({
      type: 'negative',
      message: 'Please fix time range errors before starting test'
    })
    return
  }

  isTestRunning.value = true

  try {
    const startTime = performance.now()

    addEvent('info', `Starting test with widget ${selectedWidgetId.value}`)
    addEvent('info', `Test mode: ${testMode.value}`)
    addEvent('info', `Time range: ${customStartTime.value} to ${customEndTime.value}`)

    // Activate the chart
    isTestActive.value = true

    // Wait for chart to be ready
    await new Promise(resolve => setTimeout(resolve, 100))

    const endTime = performance.now()
    performanceData.value.loadTime = Math.round(endTime - startTime)

    addEvent('success', `Test started successfully in ${performanceData.value.loadTime}ms`)

    $q.notify({
      type: 'positive',
      message: 'Test started successfully',
      timeout: 2000
    })

  } catch (error) {
    addEvent('error', `Test start failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Test start failed: ' + error.message
    })
  } finally {
    isTestRunning.value = false
  }
}

/**
 * Reset the test
 */
function resetTest() {
  isTestActive.value = false
  chartEvents.value = []
  performanceData.value = {
    loadTime: 0,
    renderTime: 0,
    dataPoints: 0,
    cacheHit: false
  }

  addEvent('info', 'Test reset')

  $q.notify({
    type: 'info',
    message: 'Test reset',
    timeout: 1000
  })
}

/**
 * Add event to log
 */
function addEvent(type, message) {
  chartEvents.value.push({
    time: new Date().toLocaleTimeString(),
    type,
    message
  })
}

// ==================== CHART EVENT HANDLERS ====================

function onChartReady(chartInstance) {
  addEvent('success', 'Chart ready and initialized')
  console.log('📊 Chart ready:', chartInstance)
}

function onChartError(error) {
  addEvent('error', `Chart error: ${error.message || error}`)
  console.error('❌ Chart error:', error)
}

function onDataUpdated(data) {
  const dataPoints = data.datasets?.reduce((total, dataset) =>
    total + (dataset.data?.length || 0), 0) || 0

  performanceData.value.dataPoints = dataPoints
  addEvent('info', `Data updated: ${dataPoints} points`)
}

function onZoomChanged(event) {
  addEvent('info', `Zoom ${event.type}: ${JSON.stringify(event)}`)
}

function onPanChanged(event) {
  addEvent('info', `Pan ${event.type}: ${JSON.stringify(event)}`)
}
</script>

<style scoped>
.zoomable-chart-test-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  padding: 20px 0;
}

.chart-test-container {
  min-height: 400px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  position: relative;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.events-log {
  max-height: 200px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.event-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  padding: 2px 0;
}

.event-time {
  color: #666;
  width: 80px;
  flex-shrink: 0;
}

.event-type {
  width: 80px;
  flex-shrink: 0;
  font-weight: bold;
}

.event-type.success { color: #4caf50; }
.event-type.error { color: #f44336; }
.event-type.warning { color: #ff9800; }
.event-type.info { color: #2196f3; }

.event-message {
  flex: 1;
}

.data-inspector {
  max-height: 400px;
  overflow-y: auto;
}

.data-content pre {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
}

.data-summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 40px;
}

.performance-metrics {
  padding: 16px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.metric-card {
  text-align: center;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #1976d2;
}

.metric-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
</style>
