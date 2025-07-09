<!-- src/pages/TestWidgetDataPage.vue -->
<!-- Comprehensive Testing Component for Data Formatter + Widget Data Composable -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">🧪 Widget Data System Test Lab</div>

    <!-- Test Controls -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">🎮 Test Controls</div>

        <div class="row q-gutter-md">
          <!-- Widget ID Input -->
          <q-input
            v-model="testWidgetId"
            label="Widget ID"
            style="min-width: 200px"
            dense
            outlined
          >
            <template #append>
              <q-btn
                flat
                dense
                icon="shuffle"
                @click="generateRandomWidgetId"
                tooltip="Generate Random ID"
              />
            </template>
          </q-input>

          <!-- Test Mode Selection -->
          <q-select
            v-model="testMode"
            :options="testModeOptions"
            label="Test Mode"
            style="min-width: 200px"
            dense
            outlined
          />

          <!-- Action Buttons -->
          <q-btn
            color="primary"
            icon="play_arrow"
            label="Run Test"
            @click="runTest"
            :loading="isRunningTest"
          />

          <q-btn
            color="secondary"
            icon="refresh"
            label="Refresh Data"
            @click="refreshData"
            :loading="isRefreshing"
          />

          <q-btn
            color="orange"
            icon="clear_all"
            label="Clear Cache"
            @click="clearCache"
          />

          <q-btn
            color="info"
            icon="science"
            label="Mock Data Test"
            @click="testMockData"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Status Overview -->
    <div class="row q-gutter-md q-mb-md">
      <!-- Data Status Card -->
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-h6">📊 Data Status</div>
          <div class="q-mt-sm">
            <q-chip
              :color="dataStatus.hasData ? 'green' : 'grey'"
              text-color="white"
              :icon="dataStatus.hasData ? 'check_circle' : 'cancel'"
            >
              {{ dataStatus.hasData ? 'Has Data' : 'No Data' }}
            </q-chip>

            <q-chip
              v-if="dataStatus.isEmpty"
              color="orange"
              text-color="white"
              icon="warning"
            >
              Empty Dataset
            </q-chip>

            <q-chip
              v-if="dataStatus.isLoading"
              color="blue"
              text-color="white"
              icon="hourglass_empty"
            >
              Loading...
            </q-chip>
          </div>

          <div v-if="dataStatus.lastFetch" class="text-caption q-mt-sm">
            Last Fetch: {{ formatTime(dataStatus.lastFetch) }}<br>
            Age: {{ formatAge(dataStatus.age) }}
          </div>
        </q-card-section>
      </q-card>

      <!-- Cache Statistics -->
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-h6">💾 Cache Stats</div>
          <div class="q-mt-sm">
            <div class="text-body2">
              Hit Rate: <strong>{{ (cacheStats.hitRate * 100).toFixed(1) }}%</strong>
            </div>
            <div class="text-body2">
              Cache Size: <strong>{{ cacheStats.size }}</strong>
            </div>
            <div class="text-body2">
              Total Requests: <strong>{{ cacheStats.totalRequests }}</strong>
            </div>
            <div class="text-caption">
              Hits: {{ cacheStats.hitCount }} | Misses: {{ cacheStats.missCount }}
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Performance Metrics -->
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-h6">⚡ Performance</div>
          <div class="q-mt-sm">
            <div class="text-body2">
              Refresh Count: <strong>{{ dataStatus.refreshCount }}</strong>
            </div>
            <div class="text-body2">
              Error Rate: <strong>{{ errorRate }}%</strong>
            </div>
            <div class="text-body2">
              Cache Hit: <strong>{{ dataStatus.cacheHit ? 'Yes' : 'No' }}</strong>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Error Status -->
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-h6">🚨 Error Status</div>
          <div v-if="error" class="q-mt-sm">
            <q-chip color="red" text-color="white" icon="error">
              {{ error.code }}
            </q-chip>
            <div class="text-caption">{{ error.message }}</div>
          </div>
          <div v-else class="text-positive q-mt-sm">
            <q-icon name="check_circle" /> No Errors
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Global Time Range Display -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">🕒 Current Time Range</div>

        <div class="row q-gutter-md">
          <div class="col">
            <div class="text-body2">
              <strong>Start:</strong> {{ formatDateTime(currentTimeRange.start) }}
            </div>
            <div class="text-body2">
              <strong>End:</strong> {{ formatDateTime(currentTimeRange.end) }}
            </div>
          </div>
          <div class="col">
            <div class="text-body2">
              <strong>Range Type:</strong> {{ currentTimeRange.range_type }}
            </div>
            <div class="text-body2">
              <strong>Window Period:</strong> {{ currentTimeRange.window_period }}
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Raw Data Display -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">🔍 Raw Backend Data</div>

        <q-expansion-item
          icon="data_object"
          label="Raw API Response"
          :model-value="showRawData"
          @update:model-value="showRawData = $event"
        >
          <q-card>
            <q-card-section>
              <div v-if="rawData" class="q-pa-sm">
                <div class="text-body2 q-mb-sm">
                  <strong>Data Structure:</strong>
                </div>
                <ul class="text-caption">
                  <li>isEmpty: {{ rawData.isEmpty }}</li>
                  <li>datasets: {{ rawData.datasets?.length || 0 }}</li>
                  <li>labels: {{ rawData.labels?.length || 0 }}</li>
                  <li>totalPoints: {{ rawData.totalPoints || 0 }}</li>
                </ul>

                <q-separator class="q-my-md" />

                <pre class="bg-grey-2 q-pa-sm text-caption overflow-auto" style="max-height: 300px;">{{ JSON.stringify(rawData, null, 2) }}</pre>
              </div>
              <div v-else class="text-grey-7">
                No raw data available
              </div>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </q-card-section>
    </q-card>

    <!-- Transformed Chart Data -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">📊 Transformed Chart Data</div>

        <div v-if="chartData" class="q-mb-md">
          <!-- Data Summary -->
          <div class="row q-gutter-md q-mb-md">
            <q-chip
              :color="chartData.isEmpty ? 'orange' : 'green'"
              text-color="white"
              :icon="chartData.isEmpty ? 'warning' : 'check'"
            >
              {{ chartData.isEmpty ? 'Empty' : 'Has Data' }}
            </q-chip>

            <q-chip
              color="blue"
              text-color="white"
              icon="timeline"
            >
              {{ chartData.labels?.length || 0 }} time points
            </q-chip>

            <q-chip
              color="purple"
              text-color="white"
              icon="show_chart"
            >
              {{ chartData.datasets?.length || 0 }} signals
            </q-chip>
          </div>

          <!-- Dataset Information -->
          <div v-if="chartData.datasets?.length" class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">📈 Datasets:</div>
            <div class="row q-gutter-sm">
              <q-chip
                v-for="(dataset, index) in chartData.datasets"
                :key="index"
                :style="{ backgroundColor: dataset.borderColor, color: 'white' }"
                :icon="dataset.hidden ? 'visibility_off' : 'visibility'"
              >
                {{ dataset.label }} ({{ dataset.data?.length || 0 }} pts)
              </q-chip>
            </div>
          </div>

          <!-- Validation Results -->
          <div v-if="validationResult" class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">✅ Validation Results:</div>
            <q-chip
              :color="validationResult.valid ? 'green' : 'red'"
              text-color="white"
              :icon="validationResult.valid ? 'check_circle' : 'error'"
            >
              {{ validationResult.valid ? 'Valid' : 'Invalid' }}
            </q-chip>

            <div v-if="validationResult.issues?.length" class="q-mt-sm">
              <div class="text-caption text-red">Issues:</div>
              <ul class="text-caption">
                <li v-for="issue in validationResult.issues" :key="issue">{{ issue }}</li>
              </ul>
            </div>
          </div>

          <!-- Metadata -->
          <q-expansion-item
            icon="info"
            label="Chart Metadata"
            :model-value="showMetadata"
            @update:model-value="showMetadata = $event"
          >
            <q-card>
              <q-card-section>
                <pre class="bg-grey-2 q-pa-sm text-caption overflow-auto" style="max-height: 200px;">{{ JSON.stringify(metadata, null, 2) }}</pre>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </div>

        <div v-else class="text-grey-7">
          No chart data available
        </div>
      </q-card-section>
    </q-card>

    <!-- Data Formatter Testing -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">🧪 Data Formatter Testing</div>

        <div class="row q-gutter-md q-mb-md">
          <q-btn
            color="primary"
            icon="science"
            label="Test Mock Data"
            @click="testDataFormatter"
          />

          <q-btn
            color="secondary"
            icon="palette"
            label="Test Color Generation"
            @click="testColorGeneration"
          />

          <q-btn
            color="orange"
            icon="format_list_numbered"
            label="Test Formatting"
            @click="testFormatting"
          />
        </div>

        <!-- Formatter Test Results -->
        <div v-if="formatterTestResults" class="q-mt-md">
          <div class="text-subtitle1 q-mb-sm">🔬 Test Results:</div>

          <q-expansion-item
            v-for="(result, testName) in formatterTestResults"
            :key="testName"
            :icon="result.success ? 'check_circle' : 'error'"
            :label="`${testName} - ${result.success ? 'PASS' : 'FAIL'}`"
            :header-class="result.success ? 'text-positive' : 'text-negative'"
          >
            <q-card>
              <q-card-section>
                <div class="text-body2 q-mb-sm">
                  <strong>Duration:</strong> {{ result.duration }}ms
                </div>

                <div v-if="result.data" class="q-mb-sm">
                  <strong>Output Sample:</strong>
                  <pre class="bg-grey-2 q-pa-sm text-caption">{{ JSON.stringify(result.data, null, 2).slice(0, 500) }}...</pre>
                </div>

                <div v-if="result.error" class="text-negative">
                  <strong>Error:</strong> {{ result.error }}
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </div>
      </q-card-section>
    </q-card>

    <!-- Console Output -->
    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">📝 Console Output</div>

        <div class="row q-gutter-sm q-mb-md">
          <q-btn
            dense
            flat
            label="Clear Log"
            icon="clear"
            @click="clearConsoleLog"
          />

          <q-btn
            dense
            flat
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
  formatNumericValue,
  formatWindowPeriod,
  CHART_COLORS,
  LINE_STYLES
} from 'src/utils/dataFormatter.js'

const $q = useQuasar()

// ==================== REACTIVE STATE ====================

// Test Configuration
const testWidgetId = ref('test-widget-001')
const testMode = ref('real-api')
const testModeOptions = [
  { label: 'Real API Test', value: 'real-api' },
  { label: 'Mock Data Test', value: 'mock-data' },
  { label: 'Error Simulation', value: 'error-sim' },
  { label: 'Cache Test', value: 'cache-test' }
]

// Test State
const isRunningTest = ref(false)
const isRefreshing = ref(false)
const showRawData = ref(false)
const showMetadata = ref(false)
const formatterTestResults = ref(null)

// Console Log
const consoleLog = ref([])
const autoScroll = ref(true)
const consoleScrollArea = ref(null)

// Global Time
const globalTime = useGlobalTime()

// Widget Data Composable - Will be created dynamically
let widgetDataComposable = null

// ==================== COMPUTED PROPERTIES ====================

const currentTimeRange = computed(() => globalTime.currentTimeRange)

const cacheStats = computed(() => getGlobalCacheStats())

const errorRate = computed(() => {
  if (!widgetDataComposable) return 0
  const total = widgetDataComposable.dataStatus.refreshCount
  const errors = widgetDataComposable.errorCount
  return total > 0 ? ((errors / total) * 100).toFixed(1) : 0
})

// Reactive data from composable
const rawData = computed(() => widgetDataComposable?.rawData || null)
const chartData = computed(() => widgetDataComposable?.chartData || null)
const metadata = computed(() => widgetDataComposable?.metadata || null)
const dataStatus = computed(() => widgetDataComposable?.dataStatus || {})
const error = computed(() => widgetDataComposable?.error || null)

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

    // Create initial widget data composable
    createWidgetComposable()

    addLog('✅ Test lab initialization complete')

  } catch (error) {
    addLog(`❌ Initialization failed: ${error.message}`, 'error')
  }
}

/**
 * Create widget data composable for current test widget
 */
function createWidgetComposable() {
  if (widgetDataComposable) {
    // Clean up existing composable
    widgetDataComposable.stopAutoRefresh()
  }

  // Create new composable
  widgetDataComposable = useWidgetData(
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
      enableAutoRefresh: true
    }
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

  if (!widgetDataComposable) {
    createWidgetComposable()
  }

  try {
    // Initialize and fetch data
    await widgetDataComposable.initialize()

    if (widgetDataComposable.hasData) {
      addLog(`✅ API test successful - ${widgetDataComposable.chartData?.datasets?.length || 0} datasets received`)
    } else if (widgetDataComposable.isEmpty) {
      addLog('⚠️ API returned empty dataset', 'warning')
    } else {
      addLog('❌ API test failed - no data received', 'error')
    }

  } catch (error) {
    addLog(`❌ API test error: ${error.message}`, 'error')
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

    // Transform using our formatter
    const transformedData = transformWidgetDataToChart(mockBackendData)

    // Validate result
    const validation = validateChartData(transformedData)

    if (validation.valid) {
      addLog(`✅ Mock data test successful - ${transformedData.datasets.length} datasets transformed`)
    } else {
      addLog(`❌ Mock data validation failed: ${validation.issues.join(', ')}`, 'error')
    }

    // Update display (simulate the composable)
    // This is just for testing - normally the composable would handle this

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
    const errorComposable = useWidgetData(
      'invalid-widget-999',
      {},
      { enableAutoRefresh: false }
    )

    try {
      await errorComposable.initialize()
    } catch (error) {
      addLog(`✅ Error handling test passed - caught: ${error.message}`)
    }

    // Test data formatter with invalid data
    try {
      transformWidgetDataToChart(null)
      addLog('✅ Data formatter handled null input gracefully')
    } catch (error) {
      addLog(`❌ Data formatter error: ${error.message}`, 'error')
    }

    // Test validation with invalid chart data
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

    // Create multiple composables to test cache
    const composables = []
    for (let i = 0; i < 3; i++) {
      const comp = useWidgetData(`cache-test-${i}`, {}, { enableCaching: true })
      composables.push(comp)
    }

    // Test cache statistics
    const stats = getGlobalCacheStats()
    addLog(`📊 Cache stats: ${stats.size} entries, ${(stats.hitRate * 100).toFixed(1)}% hit rate`)

    addLog('✅ Cache system test completed')

  } catch (error) {
    addLog(`❌ Cache test error: ${error.message}`, 'error')
  }
}

/**
 * Test data formatter functions
 */
function testDataFormatter() {
  addLog('🔬 Testing data formatter functions...')

  const results = {}

  try {
    // Test 1: Mock data generation
    const startTime = performance.now()
    const mockData = generateMockChartData({
      signalCount: 3,
      pointCount: 100
    })
    const duration1 = performance.now() - startTime

    results.mockDataGeneration = {
      success: true,
      duration: Math.round(duration1),
      data: {
        datasets: mockData.datasets.length,
        labels: mockData.labels.length,
        isEmpty: mockData.isEmpty
      }
    }

    // Test 2: Color generation
    const startTime2 = performance.now()
    const colors = Array.from({ length: 20 }, (_, i) => getSignalColor(i))
    const duration2 = performance.now() - startTime2

    results.colorGeneration = {
      success: colors.length === 20,
      duration: Math.round(duration2),
      data: colors.slice(0, 5)
    }

    // Test 3: Number formatting
    const startTime3 = performance.now()
    const testNumbers = [0.0001, 0.5, 1.5, 1000, 1000000]
    const formatted = testNumbers.map(formatNumericValue)
    const duration3 = performance.now() - startTime3

    results.numberFormatting = {
      success: formatted.every(f => f && f !== 'N/A'),
      duration: Math.round(duration3),
      data: formatted
    }

    formatterTestResults.value = results
    addLog('✅ Data formatter tests completed')

  } catch (error) {
    addLog(`❌ Data formatter test error: ${error.message}`, 'error')

    results.error = {
      success: false,
      error: error.message,
      duration: 0
    }

    formatterTestResults.value = results
  }
}

/**
 * Test color generation
 */
function testColorGeneration() {
  addLog('🎨 Testing color generation...')

  try {
    const colors = CHART_COLORS
    const lineStyles = LINE_STYLES

    addLog(`✅ Color palette: ${colors.length} colors available`)
    addLog(`✅ Line styles: ${lineStyles.length} styles available`)

    // Test color cycling
    const testColors = Array.from({ length: 20 }, (_, i) => getSignalColor(i))
    addLog(`✅ Color cycling test: ${testColors.length} colors generated`)

  } catch (error) {
    addLog(`❌ Color generation test error: ${error.message}`, 'error')
  }
}

/**
 * Test formatting functions
 */
function testFormatting() {
  addLog('📐 Testing formatting functions...')

  try {
    // Test number formatting
    const numbers = [0.0001, 0.5, 1.5, 1000, 1000000, null, undefined, 'invalid']
    numbers.forEach(num => {
      const formatted = formatNumericValue(num)
      addLog(`📊 ${num} → ${formatted}`)
    })

    // Test window period formatting
    const windowInfo = {
      window_period: '5m',
      window_seconds: 300,
      estimated_points: 100,
      auto_calculated: true
    }

    const formatted = formatWindowPeriod(windowInfo)
    addLog(`⏱️ Window period: ${formatted}`)

    addLog('✅ Formatting tests completed')

  } catch (error) {
    addLog(`❌ Formatting test error: ${error.message}`, 'error')
  }
}

/**
 * Refresh widget data
 */
async function refreshData() {
  if (!widgetDataComposable) {
    addLog('⚠️ No widget composable available', 'warning')
    return
  }

  isRefreshing.value = true
  addLog('🔄 Refreshing widget data...')

  try {
    await widgetDataComposable.refresh()
    addLog('✅ Data refreshed successfully')
  } catch (error) {
    addLog(`❌ Refresh failed: ${error.message}`, 'error')
  } finally {
    isRefreshing.value = false
  }
}

/**
 * Clear all cache
 */
function clearCache() {
  clearAllWidgetCache()
  addLog('🧹 All widget cache cleared')

  if (widgetDataComposable) {
    widgetDataComposable.clearCache()
  }
}

/**
 * Generate random widget ID
 */
function generateRandomWidgetId() {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substr(2, 5)
  testWidgetId.value = `test-${timestamp}-${random}`
  addLog(`🎲 Generated random widget ID: ${testWidgetId.value}`)
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
  if (widgetDataComposable) {
    widgetDataComposable.stopAutoRefresh()
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
