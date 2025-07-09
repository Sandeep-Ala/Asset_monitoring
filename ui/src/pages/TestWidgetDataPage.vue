src/pages/TestWidgetDataPage.vue
<!-- FIXED VERSION - Widget Data Testing Component -->
<!-- Proper lifecycle management and API integration testing -->

<template>
  <q-page padding>
    <!-- Header -->
    <div class="row q-mb-lg">
      <div class="col">
        <h4 class="q-ma-none">Widget Data Test Lab 🧪</h4>
        <p class="text-caption text-grey-7">
          Test widget data composable, API integration, and data transformation
        </p>
      </div>
    </div>
    <!-- Test Configuration -->
    <q-card class="q-mb-lg">
      <q-card-section>
        <h6 class="q-ma-none q-mb-md">Test Configuration</h6>

        <div class="row q-gutter-md">
          <!-- Widget ID Input -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-input
              v-model="testWidgetId"
              label="Widget ID"
              outlined
              dense
              :readonly="isRunningTest"
            >
              <template v-slot:append>
                <q-btn
                  flat
                  dense
                  round
                  icon="shuffle"
                  @click="generateRandomWidgetId"
                  :disable="isRunningTest"
                  size="sm"
                >
                  <q-tooltip>Generate Random ID</q-tooltip>
                </q-btn>
              </template>
            </q-input>
          </div>

          <!-- Test Mode Selection -->
          <div class="col-md-3 col-sm-6 col-xs-12">
            <q-select
              v-model="testMode"
              :options="testModeOptions"
              label="Test Mode"
              outlined
              dense
              emit-value
              map-options
              :readonly="isRunningTest"
            />
          </div>

          <!-- Test Controls -->
          <div class="col-md-4 col-sm-12 col-xs-12">
            <div class="row q-gutter-sm">
              <q-btn
                color="primary"
                icon="play_arrow"
                label="Run Test"
                @click="runTest"
                :loading="isRunningTest"
                :disable="!testWidgetId || !isTimeRangeValid"
              />

              <q-btn
                color="secondary"
                icon="refresh"
                label="Refresh"
                @click="refreshData"
                :loading="isRefreshing"
                :disable="!currentComposable"
              />

              <q-btn
                color="negative"
                icon="clear"
                label="Clear Cache"
                @click="clearCache"
                outline
              />
            </div>
          </div>
        </div>

        <!-- Time Range Configuration -->
        <div class="row q-gutter-md q-mt-md">
          <div class="col-12">
            <h6 class="q-ma-none q-mb-md">📅 Time Range Configuration</h6>
          </div>

          <!-- Start Time -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-input
              v-model="customStartTime"
              label="Start Time"
              type="datetime-local"
              outlined
              dense
              :readonly="isRunningTest"
              @update:model-value="onTimeRangeChange"
            >
              <template v-slot:prepend>
                <q-icon name="schedule" />
              </template>
            </q-input>
          </div>

          <!-- End Time -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-input
              v-model="customEndTime"
              label="End Time"
              type="datetime-local"
              outlined
              dense
              :readonly="isRunningTest"
              @update:model-value="onTimeRangeChange"
            >
              <template v-slot:prepend>
                <q-icon name="schedule" />
              </template>
            </q-input>
          </div>

          <!-- Quick Presets -->
          <div class="col-md-4 col-sm-12 col-xs-12">
            <q-select
              v-model="quickPreset"
              :options="presetOptions"
              label="Quick Presets"
              outlined
              dense
              emit-value
              map-options
              @update:model-value="applyPreset"
              :readonly="isRunningTest"
            >
              <template v-slot:prepend>
                <q-icon name="access_time" />
              </template>
            </q-select>
          </div>
        </div>

        <!-- Time Range Status -->
        <div class="row q-gutter-md q-mt-sm">
          <div class="col-12">
            <q-banner
              v-if="timeRangeError"
              class="bg-red-1 text-red-8"
            >
              <template v-slot:avatar>
                <q-icon name="error" color="red" />
              </template>
              {{ timeRangeError }}
            </q-banner>

            <q-banner
              v-else-if="isTimeRangeValid"
              class="bg-green-1 text-green-8"
            >
              <template v-slot:avatar>
                <q-icon name="check_circle" color="green" />
              </template>
              Time range is valid: {{ formatTimeRange() }}
            </q-banner>

            <q-banner
              v-else
              class="bg-orange-1 text-orange-8"
            >
              <template v-slot:avatar>
                <q-icon name="warning" color="orange" />
              </template>
              Please set both start and end times to run tests
            </q-banner>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Status Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <!-- Global Time Status -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">⏰ Global Time</div>
            <div class="text-caption text-grey-7">
              {{ formatDateTime(currentTimeRange?.start) }} -<br>
              {{ formatDateTime(currentTimeRange?.end) }}
            </div>
            <div class="text-caption q-mt-sm">
              <q-chip
                size="sm"
                :color="currentTimeRange ? 'green' : 'grey'"
                text-color="white"
              >
                {{ currentTimeRange ? 'Active' : 'Not Set' }}
              </q-chip>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Widget Status -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">📊 Widget Status</div>
            <div class="text-caption text-grey-7">
              ID: {{ testWidgetId }}<br>
              State: {{ getWidgetState() }}
            </div>
            <div class="text-caption q-mt-sm">
              <q-chip
                size="sm"
                :color="currentComposable ? 'green' : 'grey'"
                text-color="white"
              >
                {{ currentComposable ? 'Active' : 'Inactive' }}
              </q-chip>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Cache Statistics -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">💾 Cache Stats</div>
            <div class="text-caption text-grey-7">
              Size: {{ cacheStats.size }}<br>
              Hit Rate: {{ (cacheStats.hitRate * 100).toFixed(1) }}%
            </div>
            <div class="text-caption q-mt-sm">
              <q-chip
                size="sm"
                :color="cacheStats.hitRate > 0.5 ? 'green' : 'orange'"
                text-color="white"
              >
                {{ cacheStats.totalRequests }} requests
              </q-chip>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Error Rate -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">⚠️ Error Rate</div>
            <div class="text-caption text-grey-7">
              Errors: {{ errorCount }}<br>
              Rate: {{ errorRate }}%
            </div>
            <div class="text-caption q-mt-sm">
              <q-chip
                size="sm"
                :color="errorRate < 10 ? 'green' : 'red'"
                text-color="white"
              >
                {{ errorRate < 10 ? 'Good' : 'High' }}
              </q-chip>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Display -->
    <div class="row q-gutter-md q-mb-lg">
      <!-- Widget Data Status -->
      <div class="col-md-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="q-ma-none">📈 Widget Data Status</h6>
              <q-space />
              <q-chip
                v-if="dataStatus.hasData"
                size="sm"
                color="green"
                text-color="white"
                icon="check_circle"
              >
                Has Data
              </q-chip>
              <q-chip
                v-else-if="dataStatus.isEmpty"
                size="sm"
                color="orange"
                text-color="white"
                icon="warning"
              >
                Empty
              </q-chip>
              <q-chip
                v-else
                size="sm"
                color="grey"
                text-color="white"
                icon="help"
              >
                No Data
              </q-chip>
            </div>

            <div class="text-caption">
              <div class="row q-gutter-sm q-mb-sm">
                <div class="col">
                  <strong>Loading:</strong> {{ dataStatus.isLoading ? 'Yes' : 'No' }}
                </div>
                <div class="col">
                  <strong>Initial Load:</strong> {{ dataStatus.isInitialLoad ? 'Yes' : 'No' }}
                </div>
              </div>

              <div class="row q-gutter-sm q-mb-sm">
                <div class="col">
                  <strong>Background Refresh:</strong> {{ dataStatus.isBackgroundRefresh ? 'Yes' : 'No' }}
                </div>
                <div class="col">
                  <strong>Retrying:</strong> {{ dataStatus.isRetrying ? 'Yes' : 'No' }}
                </div>
              </div>

              <div class="row q-gutter-sm q-mb-sm">
                <div class="col">
                  <strong>Refresh Count:</strong> {{ dataStatus.refreshCount }}
                </div>
                <div class="col">
                  <strong>Data Age:</strong> {{ formatAge(dataStatus.dataAge) }}
                </div>
              </div>

              <div class="row q-gutter-sm">
                <div class="col">
                  <strong>Last Fetch:</strong> {{ formatTime(dataStatus.lastFetchTime) }}
                </div>
                <div class="col">
                  <strong>Error Count:</strong> {{ dataStatus.errorCount }}
                </div>
              </div>
            </div>

            <!-- Error Display -->
            <div v-if="error" class="q-mt-md">
              <q-banner class="bg-red-1 text-red-8">
                <template v-slot:avatar>
                  <q-icon name="error" color="red" />
                </template>
                <strong>Error:</strong> {{ error.message || error }}
              </q-banner>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Validation Results -->
      <div class="col-md-6 col-xs-12">
        <q-card>
          <q-card-section>
            <h6 class="q-ma-none q-mb-md">✓ Validation Results</h6>

            <div v-if="validationResult" class="text-caption">
              <div class="row items-center q-mb-sm">
                <q-icon
                  :name="validationResult.valid ? 'check_circle' : 'error'"
                  :color="validationResult.valid ? 'green' : 'red'"
                  class="q-mr-sm"
                />
                <strong>Chart Data:</strong>
                {{ validationResult.valid ? 'Valid' : 'Invalid' }}
              </div>

              <div v-if="!validationResult.valid && validationResult.issues" class="q-ml-lg">
                <div v-for="issue in validationResult.issues" :key="issue" class="text-red">
                  • {{ issue }}
                </div>
              </div>

              <div v-if="chartData" class="q-mt-sm">
                <div><strong>Datasets:</strong> {{ chartData.datasets?.length || 0 }}</div>
                <div><strong>Labels:</strong> {{ chartData.labels?.length || 0 }}</div>
                <div><strong>Total Points:</strong> {{ getTotalDataPoints() }}</div>
              </div>
            </div>

            <div v-else class="text-caption text-grey-7">
              No chart data to validate
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Raw Data & Chart Data Toggle -->
    <div class="row q-gutter-md q-mb-lg">
      <!-- Raw Data Display -->
      <div class="col-md-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="q-ma-none">📄 Raw Data</h6>
              <q-space />
              <q-btn
                flat
                dense
                :icon="showRawData ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
                @click="showRawData = !showRawData"
              />
            </div>

            <div v-if="showRawData">
              <q-scroll-area style="height: 300px; border: 1px solid #ddd;" class="bg-grey-1">
                <pre class="q-pa-sm text-caption">{{ JSON.stringify(rawData, null, 2) }}</pre>
              </q-scroll-area>
            </div>

            <div v-else class="text-caption text-grey-7">
              Click arrow to expand raw data
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Chart Data Display -->
      <div class="col-md-6 col-xs-12">
        <q-card>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="q-ma-none">📊 Chart Data</h6>
              <q-space />
              <q-btn
                flat
                dense
                :icon="showChartData ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
                @click="showChartData = !showChartData"
              />
            </div>

            <div v-if="showChartData">
              <q-scroll-area style="height: 300px; border: 1px solid #ddd;" class="bg-grey-1">
                <pre class="q-pa-sm text-caption">{{ JSON.stringify(chartData, null, 2) }}</pre>
              </q-scroll-area>
            </div>

            <div v-else class="text-caption text-grey-7">
              Click arrow to expand chart data
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Metadata Display -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <h6 class="q-ma-none">🏷️ Metadata</h6>
              <q-space />
              <q-btn
                flat
                dense
                :icon="showMetadata ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
                @click="showMetadata = !showMetadata"
              />
            </div>

            <div v-if="showMetadata">
              <q-scroll-area style="height: 200px; border: 1px solid #ddd;" class="bg-grey-1">
                <pre class="q-pa-sm text-caption">{{ JSON.stringify(metadata, null, 2) }}</pre>
              </q-scroll-area>
            </div>

            <div v-else class="text-caption text-grey-7">
              Click arrow to expand metadata
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Console Log -->
    <q-card>
      <q-card-section>
        <div class="row items-center q-mb-md">
          <h6 class="q-ma-none">🖥️ Console Log</h6>
          <q-space />
          <q-btn
            flat
            dense
            round
            icon="clear"
            @click="clearConsoleLog"
            size="sm"
          >
            <q-tooltip>Clear Log</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            :label="autoScroll ? 'Auto-scroll: ON' : 'Auto-scroll: OFF'"
            :icon="autoScroll ? 'keyboard_arrow_down' : 'keyboard_arrow_right'"
            @click="autoScroll = !autoScroll"
          />
        </div>

        <q-scroll-area
          style="height: 300px; border: 1px solid #ddd;"
          class="bg-grey-1"
          ref="consoleScrollArea"
        >
          <div class="q-pa-sm">
            <div
              v-for="(log, index) in consoleLog"
              :key="index"
              class="console-line q-mb-xs"
              :class="log.type"
            >
              <span class="text-caption text-grey-7">{{ log.time }}</span>
              <span class="q-ml-sm">{{ log.message }}</span>
            </div>
          </div>
        </q-scroll-area>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useQuasar } from 'quasar'
import { format } from 'date-fns'

// Composables
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import useWidgetData, { getGlobalCacheStats, clearAllWidgetCache } from 'src/composables/useWidgetData.js'

// Data Formatter
import {
  transformWidgetDataToChart,
  validateChartData,
  generateMockChartData,
  getSignalColor,
  // formatNumericValue,
  formatWindowPeriod,
  CHART_COLORS,
  LINE_STYLES
} from 'src/utils/dataFormatter.js'
import zon from 'src/components/ZoomableLineChart.vue'
const $q = useQuasar()

// ==================== REACTIVE STATE ====================

// Test Configuration
const testWidgetId = ref('3dcaf1a0-3989-4ff0-9e32-6e6235887d3a')
const testMode = ref('real-api')
const testModeOptions = [
  { label: 'Real API Test', value: 'real-api' },
  { label: 'Mock Data Test', value: 'mock-data' },
  { label: 'Error Simulation', value: 'error-sim' },
  { label: 'Cache Test', value: 'cache-test' }
]

// Time Range Configuration
const customStartTime = ref('')
const customEndTime = ref('')
const quickPreset = ref('')
const timeRangeError = ref('')

const presetOptions = [
  { label: 'Last 15 minutes', value: 'last_15m' },
  { label: 'Last 1 hour', value: 'last_1h' },
  { label: 'Last 6 hours', value: 'last_6h' },
  { label: 'Last 24 hours', value: 'last_24h' },
  { label: 'Custom', value: 'custom' }
]

// Test State
const isRunningTest = ref(false)
const isRefreshing = ref(false)
const showRawData = ref(false)
const showChartData = ref(false)
const showMetadata = ref(false)
const formatterTestResults = ref(null)

// Console Log
const consoleLog = ref([])
const autoScroll = ref(true)
const consoleScrollArea = ref(null)

// Global Time
const globalTime = useGlobalTime()

// Widget Data Composable - Created in setup() context
const currentComposable = ref(null)

// ==================== COMPUTED PROPERTIES ====================

const currentTimeRange = computed(() => {
  // Return user-defined time range if both times are set
  if (customStartTime.value && customEndTime.value) {
    // Convert datetime-local to ISO string WITHOUT timezone conversion
    // datetime-local is already in local timezone, treat it as UTC for API
    const startDate = new Date(customStartTime.value)
    const endDate = new Date(customEndTime.value)

    // Create ISO strings treating the local datetime as if it were UTC
    const startISO = customStartTime.value + ':00.000Z'
    const endISO = customEndTime.value + ':00.000Z'

    return {
      start: startISO,
      end: endISO,
      range_type: 'custom'
    }
  }

  // Fallback to global time if available
  return globalTime.currentTimeRange
})

const isTimeRangeValid = computed(() => {
  if (!customStartTime.value || !customEndTime.value) return false

  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)
  const now = new Date()

  return start < end && start <= now && end <= now
})

const cacheStats = computed(() => getGlobalCacheStats())

const errorCount = computed(() => {
  return currentComposable.value?.errorCount || 0
})

const errorRate = computed(() => {
  if (!currentComposable.value) return 0
  const total = currentComposable.value.dataStatus.refreshCount
  const errors = currentComposable.value.errorCount
  return total > 0 ? ((errors / total) * 100).toFixed(1) : 0
})

// Reactive data from composable
const rawData = computed(() => currentComposable.value?.rawData || null)
const chartData = computed(() => currentComposable.value?.chartData || null)
const metadata = computed(() => currentComposable.value?.metadata || null)
const dataStatus = computed(() => currentComposable.value?.dataStatus || {})
const error = computed(() => currentComposable.value?.error || null)

const validationResult = computed(() => {
  if (!chartData.value) return null
  return validateChartData(chartData.value)
})

// ==================== METHODS ====================

/**
 * Initialize the test environment
 */
async function initialize() {
  addLog('🚀 Initializing Widget Data Test Lab...')

  try {
    // Initialize global time management
    await globalTime.initialize()
    addLog('✅ Global time management initialized')

    // Set default time range inputs
    setDefaultTimeInputs()

    // Create initial widget data composable
    createWidgetComposable()

    addLog('✅ Test lab initialization complete')
    addLog('📝 Please set start and end times before running tests')

  } catch (error) {
    addLog(`❌ Initialization failed: ${error.message}`, 'error')
  }
}

/**
 * Set default time inputs (last 1 hour)
 */
function setDefaultTimeInputs() {
  const now = new Date()
  const oneHourAgo = new Date(now - 60 * 60 * 1000)

  customStartTime.value = formatToDatetimeLocal(oneHourAgo)
  customEndTime.value = formatToDatetimeLocal(now)

  addLog('📅 Default time range set to last 1 hour')
}

/**
 * Format date to datetime-local input format
 */
function formatToDatetimeLocal(date) {
  // Format: YYYY-MM-DDTHH:MM
  return date.toISOString().slice(0, 16)
}

/**
 * Handle time range changes
 */
function onTimeRangeChange() {
  validateTimeRange()
  quickPreset.value = 'custom'
}

/**
 * Validate current time range
 */
function validateTimeRange() {
  timeRangeError.value = ''

  if (!customStartTime.value || !customEndTime.value) {
    timeRangeError.value = 'Both start and end times are required'
    return false
  }

  // For validation, we can use Date objects since we're just comparing
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

  // Note: Removed future time validation since user might want to test with any dates

  return true
}

/**
 * Apply quick preset
 */
function applyPreset(preset) {
  if (!preset || preset === 'custom') return

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
      return
  }

  customStartTime.value = formatToDatetimeLocal(startTime)
  customEndTime.value = formatToDatetimeLocal(now)

  validateTimeRange()

  addLog(`📅 Applied preset: ${preset}`)
}

/**
 * Format time range for display
 */
function formatTimeRange() {
  if (!isTimeRangeValid.value) return 'Invalid range'

  // Parse the datetime-local values directly for display
  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)
  const duration = end - start

  const hours = Math.floor(duration / (1000 * 60 * 60))
  const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))

  let durationStr = ''
  if (hours > 0) durationStr += `${hours}h `
  if (minutes > 0) durationStr += `${minutes}m`

  // Show the exact values as entered by user
  return `${durationStr.trim()} (${customStartTime.value.replace('T', ' ')} → ${customEndTime.value.replace('T', ' ')})`
}

/**
 * Create widget data composable for current test widget
 */
function createWidgetComposable() {
  // Clean up existing composable
  if (currentComposable.value) {
    currentComposable.value.cleanup()
    currentComposable.value = null
  }

  // Create new composable in setup() context with custom time range
  currentComposable.value = useWidgetData(
    testWidgetId.value,
    {
      widget_type: 'line_chart',
      widget_label: `Test Widget ${testWidgetId.value}`,
      equipment_ids: [1, 2],
      signal_ids: [1, 2, 3],
      styling_config: {
        show_points: true,
        line_width: 2,
        curve_smooth: 0.1
      }
    },
    {
      enableCaching: true,
      enableAutoRefresh: false // Disable auto-refresh for testing
    },
    currentTimeRange.value // Pass custom time range
  )

  addLog(`🔧 Created widget composable for: ${testWidgetId.value}`)
}

/**
 * Run the selected test
 */
async function runTest() {
  isRunningTest.value = true
  addLog(`🧪 Running ${testMode.value} test...`)

  try {
    switch (testMode.value) {
      case 'real-api':
        await testRealAPI()
        break
      case 'mock-data':
        await testMockData()
        break
      case 'error-sim':
        await testErrorSimulation()
        break
      case 'cache-test':
        await testCacheSystem()
        break
      default:
        addLog('❌ Unknown test mode', 'error')
    }
  } catch (error) {
    addLog(`❌ Test failed: ${error.message}`, 'error')
  } finally {
    isRunningTest.value = false
  }
}

/**
 * Test real API integration
 */
async function testRealAPI() {
  addLog('📡 Testing real API integration...')

  // Validate time range first
  if (!validateTimeRange()) {
    addLog('❌ Invalid time range - cannot proceed with API test', 'error')
    return
  }

  if (!currentComposable.value) {
    createWidgetComposable()
  }

  try {
    const timeRange = currentTimeRange.value
    addLog(`📤 Making API call for widget: ${testWidgetId.value}`)
    addLog(`🕒 Input times: ${customStartTime.value} → ${customEndTime.value}`)
    addLog(`📡 API time range: ${timeRange.start} to ${timeRange.end}`)
    addLog(`⏱️ Display duration: ${formatTimeRange()}`)

    // Override the composable's time range for this test
    await currentComposable.value.initialize()

    // Wait a moment for data to be processed
    await nextTick()

    if (currentComposable.value.hasData) {
      addLog(`✅ API test successful - ${currentComposable.value.chartData?.datasets?.length || 0} datasets received`)
      addLog(`📊 Total data points: ${getTotalDataPoints()}`)
    } else if (currentComposable.value.isEmpty) {
      addLog('⚠️ API returned empty dataset', 'warning')
    } else {
      addLog('❌ API test failed - no data received', 'error')
    }

  } catch (error) {
    addLog(`❌ API test error: ${error.message}`, 'error')
    console.error('API Test Error:', error)
  }
}

/**
 * Test mock data processing
 */
async function testMockData() {
  addLog('🎭 Testing mock data processing...')

  try {
    // Generate mock backend data
    const mockBackendData = {
      labels: [
        '2025-01-08T10:00:00Z',
        '2025-01-08T10:05:00Z',
        '2025-01-08T10:10:00Z',
        '2025-01-08T10:15:00Z',
        '2025-01-08T10:20:00Z'
      ],
      datasets: [
        {
          label: 'Temperature',
          data: [25.5, 26.1, 25.8, 26.3, 26.0],
          unit: '°C'
        },
        {
          label: 'Humidity',
          data: [65.2, 66.0, 64.8, 67.1, 65.5],
          unit: '%'
        }
      ],
      isEmpty: false,
      totalPoints: 5,
      timeRange: {
        start: '2025-01-08T10:00:00Z',
        end: '2025-01-08T10:20:00Z'
      },
      window_info: {
        window_period: '5m',
        window_seconds: 300,
        estimated_points: 5,
        auto_calculated: true
      }
    }

    addLog('📥 Generated mock backend data')

    // Transform using our formatter
    const transformedData = transformWidgetDataToChart(mockBackendData)

    // Validate result
    const validation = validateChartData(transformedData)

    if (validation.valid) {
      addLog(`✅ Mock data test successful - ${transformedData.datasets.length} datasets transformed`)
      addLog(`📊 Chart has ${transformedData.labels.length} labels and ${transformedData.datasets.length} datasets`)
    } else {
      addLog(`❌ Mock data validation failed: ${validation.issues.join(', ')}`, 'error')
    }

    // Store results for display
    formatterTestResults.value = {
      input: mockBackendData,
      output: transformedData,
      validation: validation
    }

  } catch (error) {
    addLog(`❌ Mock data test error: ${error.message}`, 'error')
  }
}

/**
 * Test error simulation
 */
async function testErrorSimulation() {
  addLog('💥 Testing error handling...')

  try {
    // Test invalid widget ID
    addLog('🔄 Testing invalid widget ID...')

    const errorComposable = useWidgetData(
      'invalid-widget-999',
      {},
      { enableAutoRefresh: false }
    )

    try {
      await errorComposable.initialize()
      addLog('❌ Expected error but got success', 'warning')
    } catch (error) {
      addLog(`✅ Error handling test passed - caught: ${error.message}`)
    }

    // Test data formatter with invalid data
    addLog('🔄 Testing data formatter with invalid data...')
    try {
      transformWidgetDataToChart(null)
      addLog('✅ Data formatter handled null input gracefully')
    } catch (error) {
      addLog(`✅ Data formatter correctly rejected null: ${error.message}`)
    }

    // Test validation with invalid chart data
    addLog('🔄 Testing chart data validation...')
    const invalidData = { labels: [], datasets: null }
    const validation = validateChartData(invalidData)

    if (!validation.valid) {
      addLog(`✅ Validation caught invalid data: ${validation.issues.join(', ')}`)
    }

  } catch (error) {
    addLog(`❌ Error simulation failed: ${error.message}`, 'error')
  }
}

/**
 * Test cache system
 */
async function testCacheSystem() {
  addLog('💾 Testing cache system...')

  try {
    // Clear cache first
    clearAllWidgetCache()
    addLog('🧹 Cache cleared')

    // Test cache statistics
    const stats = getGlobalCacheStats()
    addLog(`📊 Cache stats: ${JSON.stringify(stats)}`)

    // Test with current composable
    if (currentComposable.value) {
      addLog('🔄 Testing cache with current composable...')

      // First call - should be cache miss
      await currentComposable.value.refresh()
      addLog('📤 First call completed (cache miss expected)')

      // Second call - should be cache hit
      await currentComposable.value.refresh()
      addLog('📥 Second call completed (cache hit expected)')

      const finalStats = getGlobalCacheStats()
      addLog(`📊 Final cache stats: Hit rate ${(finalStats.hitRate * 100).toFixed(1)}%`)
    }

  } catch (error) {
    addLog(`❌ Cache test error: ${error.message}`, 'error')
  }
}

/**
 * Refresh data manually
 */
async function refreshData() {
  if (!currentComposable.value) {
    addLog('❌ No active composable to refresh', 'error')
    return
  }

  isRefreshing.value = true
  addLog('🔄 Manual refresh triggered...')

  try {
    await currentComposable.value.refresh()
    addLog('✅ Manual refresh completed')
  } catch (error) {
    addLog(`❌ Manual refresh failed: ${error.message}`, 'error')
  } finally {
    isRefreshing.value = false
  }
}

/**
 * Clear cache
 */
function clearCache() {
  clearAllWidgetCache()

  if (currentComposable.value) {
    currentComposable.value.clearCache()
  }

  addLog('🧹 All cache cleared')

  $q.notify({
    type: 'positive',
    message: 'Cache cleared successfully',
    position: 'top'
  })
}

/**
 * Generate random widget ID for testing
 */
function generateRandomWidgetId() {
  testWidgetId.value = `test-widget-${Math.random().toString(36).substr(2, 9)}`
  addLog(`🎲 Generated random widget ID: ${testWidgetId.value}`)
}

/**
 * Get widget state description
 */
function getWidgetState() {
  if (!currentComposable.value) return 'No Composable'

  const status = currentComposable.value.dataStatus
  if (status.isLoading) return 'Loading'
  if (status.hasData) return 'Has Data'
  if (status.isEmpty) return 'Empty'
  if (currentComposable.value.error) return 'Error'
  return 'Ready'
}

/**
 * Get total data points across all datasets
 */
function getTotalDataPoints() {
  if (!chartData.value?.datasets) return 0
  return chartData.value.datasets.reduce((total, dataset) => {
    return total + (dataset.data?.length || 0)
  }, 0)
}

/**
 * Add log entry to console
 */
function addLog(message, type = 'info') {
  const logEntry = {
    time: format(new Date(), 'HH:mm:ss.SSS'),
    message,
    type
  }

  consoleLog.value.push(logEntry)

  // Limit log size
  if (consoleLog.value.length > 100) {
    consoleLog.value.shift()
  }

  // Auto-scroll to bottom
  if (autoScroll.value) {
    nextTick(() => {
      if (consoleScrollArea.value) {
        consoleScrollArea.value.setScrollPosition('vertical', 9999)
      }
    })
  }
}

/**
 * Clear console log
 */
function clearConsoleLog() {
  consoleLog.value = []
  addLog('📝 Console log cleared')
}

/**
 * Format time for display
 */
function formatTime(date) {
  if (!date) return 'Never'
  return format(new Date(date), 'HH:mm:ss')
}

/**
 * Format age in human readable format
 */
function formatAge(ageMs) {
  if (!ageMs || ageMs < 0) return '0s'

  const seconds = Math.floor(ageMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) return `${hours}h ${minutes % 60}m`
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

/**
 * Format date time for display
 */
function formatDateTime(dateStr) {
  if (!dateStr) return 'Not set'
  try {
    return format(new Date(dateStr), 'yyyy-MM-dd HH:mm:ss')
  } catch {
    return 'Invalid date'
  }
}

// ==================== WATCHERS ====================

// Watch widget ID changes
watch(testWidgetId, (newId) => {
  addLog(`🔧 Widget ID changed to: ${newId}`)
  createWidgetComposable()
})

// ==================== LIFECYCLE ====================

onMounted(async () => {
  await initialize()
})

onBeforeUnmount(() => {
  if (currentComposable.value) {
    currentComposable.value.cleanup()
  }
})
</script>

<style scoped>
.console-line.error {
  color: #c62828;
}

.console-line.warning {
  color: #f57c00;
}

.console-line.info {
  color: #333;
}

.console-line {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}
</style>
