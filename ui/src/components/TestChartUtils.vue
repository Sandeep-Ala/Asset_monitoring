<!-- src/components/TestChartUtils.vue -->
<!-- TEMPORARY TEST COMPONENT - Delete after testing Phase 6.3.1 -->

<template>
  <div class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">🧪 Chart Utils Test</div>
        <div class="text-caption">Testing Phase 6.3.1 - chartUtils.js</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <!-- Mock Data Input -->
        <div class="q-mb-md">
          <div class="text-subtitle1 q-mb-sm">📊 Mock Widget Data</div>
          <q-input
            v-model="mockDataJson"
            type="textarea"
            outlined
            rows="8"
            label="Mock Backend Data (JSON)"
            hint="Edit this JSON to test data transformation"
          />
        </div>

        <!-- Widget Config Input -->
        <div class="q-mb-md">
          <div class="text-subtitle1 q-mb-sm">⚙️ Widget Configuration</div>
          <q-input
            v-model="widgetConfigJson"
            type="textarea"
            outlined
            rows="4"
            label="Widget Config (JSON)"
            hint="Edit styling and widget configuration"
          />
        </div>

        <!-- Test Actions -->
        <div class="q-mb-md">
          <div class="text-subtitle1 q-mb-sm">🔧 Test Actions</div>
          <div class="row q-gutter-sm">
            <q-btn
              color="primary"
              label="Transform Data"
              @click="testDataTransformation"
              icon="transform"
            />

            <q-btn
              color="secondary"
              label="Test Time Formatting"
              @click="testTimeFormatting"
              icon="schedule"
            />

            <q-btn
              color="accent"
              label="Test Color Palette"
              @click="testColorPalette"
              icon="palette"
            />

            <q-btn
              color="orange"
              label="Test Chart Config"
              @click="testChartConfig"
              icon="bar_chart"
            />

            <q-btn
              color="purple"
              label="Test Window Format"
              @click="testWindowFormat"
              icon="tune"
            />
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Results Display -->
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">📋 Test Results</div>

        <!-- Transformed Data -->
        <q-expansion-item
          v-if="transformedData"
          icon="data_object"
          label="Transformed Chart Data"
          class="q-mb-md"
        >
          <q-card>
            <q-card-section>
              <div class="text-body2 q-mb-sm">
                <strong>Empty:</strong> {{ transformedData.isEmpty }}<br>
                <strong>Dataset Count:</strong> {{ transformedData.datasets?.length || 0 }}<br>
                <strong>Has Metadata:</strong> {{ !!transformedData.metadata }}
              </div>

              <div class="text-caption">Full Data:</div>
              <pre>{{ JSON.stringify(transformedData, null, 2) }}</pre>
            </q-card-section>
          </q-card>
        </q-expansion-item>

        <!-- Time Formatting Tests -->
        <q-expansion-item
          v-if="timeFormatTests.length"
          icon="schedule"
          label="Time Formatting Tests"
          class="q-mb-md"
        >
          <q-card>
            <q-card-section>
              <q-list>
                <q-item v-for="(test, index) in timeFormatTests" :key="index">
                  <q-item-section>
                    <q-item-label>{{ test.label }}</q-item-label>
                    <q-item-label caption>{{ test.result }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </q-expansion-item>

        <!-- Color Palette Test -->
        <q-expansion-item
          v-if="colorTests.length"
          icon="palette"
          label="Color Palette Tests"
          class="q-mb-md"
        >
          <q-card>
            <q-card-section>
              <div class="row q-gutter-sm">
                <div
                  v-for="(color, index) in colorTests"
                  :key="index"
                  class="color-box"
                  :style="{ backgroundColor: color.color }"
                >
                  <div class="color-label">{{ index }}</div>
                  <div class="color-value">{{ color.color }}</div>
                  <div class="color-alpha" v-if="color.alpha">α{{ color.alpha }}</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </q-expansion-item>

        <!-- Chart Configuration Test -->
        <q-expansion-item
          v-if="chartConfig"
          icon="bar_chart"
          label="Chart Configuration"
          class="q-mb-md"
        >
          <q-card>
            <q-card-section>
              <div class="text-body2 q-mb-sm">
                <strong>Type:</strong> {{ chartConfig.type }}<br>
                <strong>Title:</strong> {{ chartConfig.options?.plugins?.title?.text }}<br>
                <strong>Datasets:</strong> {{ chartConfig.data?.datasets?.length || 0 }}
              </div>

              <div class="text-caption">Full Config:</div>
              <pre>{{ JSON.stringify(chartConfig, null, 2) }}</pre>
            </q-card-section>
          </q-card>
        </q-expansion-item>

        <!-- Window Format Tests -->
        <q-expansion-item
          v-if="windowFormatTests.length"
          icon="tune"
          label="Window Period Formatting"
          class="q-mb-md"
        >
          <q-card>
            <q-card-section>
              <q-list>
                <q-item v-for="(test, index) in windowFormatTests" :key="index">
                  <q-item-section>
                    <q-item-label>{{ test.input }}</q-item-label>
                    <q-item-label caption>{{ test.output }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </q-card-section>

      <!-- Console Logs -->
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">📝 Console Output</div>
        <q-scroll-area style="height: 200px; border: 1px solid #ddd; padding: 8px;">
          <div v-for="(log, index) in consoleLog" :key="index" class="q-mb-xs">
            <span class="text-caption text-grey-7">{{ log.time }}</span>
            <span class="q-ml-sm" :class="log.type">{{ log.message }}</span>
          </div>
        </q-scroll-area>
        <q-btn flat dense label="Clear Log" @click="consoleLog = []" class="q-mt-xs" />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import {
  transformWidgetDataToChart,
  createLineChartConfig,
  formatAxisTime,
  formatTooltipTime,
  formatAxisValue,
  formatWindowPeriod,
  getSignalColor,
  generateDatasetColors,
  signalColorPalette,
  defaultChartOptions
} from 'src/utils/chartUtils.js'

const $q = useQuasar()

// Test data
const mockDataJson = ref(JSON.stringify({
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
    windowPeriod: '5m',
    windowSeconds: 300,
    estimatedPoints: 5,
    maxPointsLimit: 100,
    autoCalculated: false
  },
  widget_info: {
    widget_id: 'test-widget-1',
    widget_label: 'Test Sensor Data',
    widget_type: 'line_chart'
  }
}, null, 2))

const widgetConfigJson = ref(JSON.stringify({
  widget_label: 'Test Chart Widget',
  widget_type: 'line_chart',
  styling_config: {
    colors: ['#2196F3', '#4CAF50'],
    lineStyles: ['solid', 'dashed'],
    showLegend: true,
    showGrid: true
  }
}, null, 2))

// Test results
const transformedData = ref(null)
const timeFormatTests = ref([])
const colorTests = ref([])
const chartConfig = ref(null)
const windowFormatTests = ref([])
const consoleLog = ref([])

// Console logging
function addLog(message, type = 'info') {
  const time = new Date().toLocaleTimeString()
  consoleLog.value.unshift({ time, message, type })

  if (consoleLog.value.length > 100) {
    consoleLog.value = consoleLog.value.slice(0, 100)
  }

  console.log(`🧪 ${time}: ${message}`)
}

// Test functions
function testDataTransformation() {
  addLog('Testing data transformation...')

  try {
    const mockData = JSON.parse(mockDataJson.value)
    const widgetConfig = JSON.parse(widgetConfigJson.value)

    addLog('✅ JSON parsing successful')

    const result = transformWidgetDataToChart(mockData, widgetConfig)
    transformedData.value = result

    addLog(`✅ Data transformation completed`)
    addLog(`   - Empty: ${result.isEmpty}`)
    addLog(`   - Datasets: ${result.datasets?.length || 0}`)
    addLog(`   - Has metadata: ${!!result.metadata}`)

    if (result.datasets && result.datasets.length > 0) {
      result.datasets.forEach((dataset, index) => {
        addLog(`   - Dataset ${index}: ${dataset.label}, ${dataset.data?.length || 0} points`)
      })
    }

    $q.notify({
      type: 'positive',
      message: 'Data transformation successful'
    })

  } catch (error) {
    addLog(`❌ Data transformation failed: ${error.message}`, 'error')

    $q.notify({
      type: 'negative',
      message: 'Data transformation failed: ' + error.message
    })
  }
}

function testTimeFormatting() {
  addLog('Testing time formatting functions...')

  try {
    const testTimestamps = [
      '2025-01-08T10:00:00Z',
      '2025-01-08T14:30:45Z',
      '2025-01-07T22:15:30Z',
      new Date().toISOString()
    ]

    const timeRange = {
      start: '2025-01-08T10:00:00Z',
      end: '2025-01-08T18:00:00Z'
    }

    timeFormatTests.value = testTimestamps.map(timestamp => ({
      label: `Axis Time: ${timestamp}`,
      result: formatAxisTime(timestamp, timeRange)
    }))

    testTimestamps.forEach(timestamp => {
      timeFormatTests.value.push({
        label: `Tooltip Time: ${timestamp}`,
        result: formatTooltipTime(timestamp)
      })
    })

    // Test axis value formatting
    const testValues = [1234567, 5432, 123.456, 0.00123, 0, -456.789]
    testValues.forEach(value => {
      timeFormatTests.value.push({
        label: `Axis Value: ${value}`,
        result: formatAxisValue(value)
      })
    })

    addLog(`✅ Time formatting tests completed (${timeFormatTests.value.length} tests)`)

    $q.notify({
      type: 'positive',
      message: 'Time formatting tests completed'
    })

  } catch (error) {
    addLog(`❌ Time formatting test failed: ${error.message}`, 'error')

    $q.notify({
      type: 'negative',
      message: 'Time formatting failed: ' + error.message
    })
  }
}

function testColorPalette() {
  addLog('Testing color palette functions...')

  try {
    colorTests.value = []

    // Test base colors
    signalColorPalette.forEach((color, index) => {
      colorTests.value.push({
        color: color,
        index: index,
        alpha: 1
      })
    })

    // Test alpha variations
    for (let i = 0; i < 5; i++) {
      const alphaColor = getSignalColor(i, 0.5)
      colorTests.value.push({
        color: alphaColor,
        index: i,
        alpha: 0.5
      })
    }

    // Test dataset colors
    const mockStylingConfig = {
      colors: ['#FF0000', '#00FF00', '#0000FF']
    }

    for (let i = 0; i < 3; i++) {
      const datasetColors = generateDatasetColors(mockStylingConfig, i)
      addLog(`   Dataset ${i} colors: border=${datasetColors.borderColor}, bg=${datasetColors.backgroundColor}`)
    }

    addLog(`✅ Color palette tests completed (${signalColorPalette.length} base colors)`)

    $q.notify({
      type: 'positive',
      message: 'Color palette tests completed'
    })

  } catch (error) {
    addLog(`❌ Color palette test failed: ${error.message}`, 'error')

    $q.notify({
      type: 'negative',
      message: 'Color palette test failed: ' + error.message
    })
  }
}

function testChartConfig() {
  addLog('Testing chart configuration creation...')

  try {
    const widgetConfig = JSON.parse(widgetConfigJson.value)
    const mockChartData = transformedData.value || {
      datasets: [
        {
          label: 'Test Data',
          data: [{ x: new Date(), y: 100 }],
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)'
        }
      ]
    }

    const config = createLineChartConfig(widgetConfig, mockChartData)
    chartConfig.value = config

    addLog(`✅ Chart config created successfully`)
    addLog(`   - Type: ${config.type}`)
    addLog(`   - Title: ${config.options?.plugins?.title?.text || 'No title'}`)
    addLog(`   - Datasets: ${config.data?.datasets?.length || 0}`)
    addLog(`   - Has zoom plugin: ${!!config.options?.plugins?.zoom}`)
    addLog(`   - Has time scale: ${config.options?.scales?.x?.type === 'time'}`)

    $q.notify({
      type: 'positive',
      message: 'Chart configuration created successfully'
    })

  } catch (error) {
    addLog(`❌ Chart config test failed: ${error.message}`, 'error')

    $q.notify({
      type: 'negative',
      message: 'Chart config test failed: ' + error.message
    })
  }
}

function testWindowFormat() {
  addLog('Testing window period formatting...')

  try {
    const testWindowInfos = [
      {
        windowPeriod: 'auto',
        estimatedPoints: 85,
        autoCalculated: true
      },
      {
        windowPeriod: '5m',
        estimatedPoints: 120,
        autoCalculated: false
      },
      {
        windowPeriod: '1h',
        estimatedPoints: 24,
        autoCalculated: false
      },
      {
        windowPeriod: '1sec',
        estimatedPoints: 3600,
        autoCalculated: false
      },
      null, // Test null case
      undefined // Test undefined case
    ]

    windowFormatTests.value = testWindowInfos.map((info, index) => ({
      input: `Window Info ${index}: ${JSON.stringify(info)}`,
      output: formatWindowPeriod(info)
    }))

    addLog(`✅ Window formatting tests completed (${windowFormatTests.value.length} tests)`)

    $q.notify({
      type: 'positive',
      message: 'Window formatting tests completed'
    })

  } catch (error) {
    addLog(`❌ Window format test failed: ${error.message}`, 'error')

    $q.notify({
      type: 'negative',
      message: 'Window format test failed: ' + error.message
    })
  }
}

// Test default chart options
function testDefaultOptions() {
  addLog('Testing default chart options...')

  try {
    const options = defaultChartOptions

    addLog(`✅ Default options structure valid`)
    addLog(`   - Responsive: ${options.responsive}`)
    addLog(`   - Has plugins: ${!!options.plugins}`)
    addLog(`   - Has scales: ${!!options.scales}`)
    addLog(`   - X-axis type: ${options.scales.x.type}`)
    addLog(`   - Has zoom config: ${!!options.plugins.zoom}`)
    addLog(`   - Animation duration: ${options.animation.duration}ms`)

  } catch (error) {
    addLog(`❌ Default options test failed: ${error.message}`, 'error')
  }
}

onMounted(() => {
  addLog('🚀 Chart Utils test component mounted')

  // Run basic tests on mount
  setTimeout(() => {
    testDefaultOptions()
  }, 500)
})
</script>

<style scoped>
pre {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
}

.q-scroll-area {
  font-family: monospace;
  font-size: 12px;
  background: #f9f9f9;
}

.color-box {
  width: 80px;
  height: 60px;
  border-radius: 4px;
  border: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.7);
  position: relative;
}

.color-label {
  font-weight: bold;
  font-size: 14px;
}

.color-value {
  font-size: 10px;
  margin-top: 2px;
}

.color-alpha {
  font-size: 9px;
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(0,0,0,0.5);
  padding: 1px 3px;
  border-radius: 2px;
}

.error {
  color: #f44336;
}

.success {
  color: #4caf50;
}

.info {
  color: #2196f3;
}
</style>
