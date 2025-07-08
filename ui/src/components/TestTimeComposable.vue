<!-- src/components/TestTimeComposable.vue -->
<!-- TEMPORARY TEST COMPONENT - Delete after testing Phase 6.3.1 -->

<template>
  <div class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">🧪 Global Time Composable Test</div>
        <div class="text-caption">Testing Phase 6.3.1 - useGlobalTime.js</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <!-- Loading State -->
        <div v-if="timeState.isLoading" class="text-center q-pa-md">
          <q-spinner-dots size="40px" color="primary" />
          <div class="q-mt-sm">Loading time management...</div>
        </div>

        <!-- Time State Display -->
        <div v-else>
          <div class="row q-gutter-md">
            <div class="col-12 col-md-6">
              <q-list bordered separator>
                <q-item-label header>Current Time State</q-item-label>

                <q-item>
                  <q-item-section>
                    <q-item-label>Time Start</q-item-label>
                    <q-item-label caption>{{ timeState.timeStart || 'Not set' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Time End</q-item-label>
                    <q-item-label caption>{{ timeState.timeEnd || 'Not set' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Range Type</q-item-label>
                    <q-item-label caption>{{ timeState.rangeType || 'Not set' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Window Period</q-item-label>
                    <q-item-label caption>{{ timeState.windowPeriod || 'Not set' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Refresh Rate</q-item-label>
                    <q-item-label caption>{{ timeState.refreshRate || 'Not set' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label>Last Updated</q-item-label>
                    <q-item-label caption>{{ timeState.lastUpdated || 'Never' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-12 col-md-6">
              <q-list bordered separator>
                <q-item-label header>Window Information</q-item-label>

                <q-item v-if="timeState.windowInfo">
                  <q-item-section>
                    <q-item-label>Window Period</q-item-label>
                    <q-item-label caption>{{ timeState.windowInfo.windowPeriod }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="timeState.windowInfo">
                  <q-item-section>
                    <q-item-label>Window Seconds</q-item-label>
                    <q-item-label caption>{{ timeState.windowInfo.windowSeconds }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="timeState.windowInfo">
                  <q-item-section>
                    <q-item-label>Estimated Points</q-item-label>
                    <q-item-label caption>{{ timeState.windowInfo.estimatedPoints }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="timeState.windowInfo">
                  <q-item-section>
                    <q-item-label>Max Points Limit</q-item-label>
                    <q-item-label caption>{{ timeState.windowInfo.maxPointsLimit }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="timeState.windowInfo">
                  <q-item-section>
                    <q-item-label>Auto Calculated</q-item-label>
                    <q-item-label caption>{{ timeState.windowInfo.autoCalculated ? 'Yes' : 'No' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>

          <!-- Computed Properties Display -->
          <div class="q-mt-md">
            <q-expansion-item icon="info" label="Computed Properties">
              <q-card>
                <q-card-section>
                  <div class="row q-gutter-md">
                    <div class="col">
                      <strong>Current Time Range:</strong>
                      <pre>{{ JSON.stringify(currentTimeRange, null, 2) }}</pre>
                    </div>
                    <div class="col">
                      <strong>Time Range Display:</strong> {{ timeRangeDisplay }}<br>
                      <strong>Is Valid Range:</strong> {{ isValidTimeRange }}<br>
                      <strong>Refresh Rate (ms):</strong> {{ refreshRateMs }}
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </div>

          <!-- Backend Data Display -->
          <div class="q-mt-md">
            <q-expansion-item icon="api" label="Backend Presets Data">
              <q-card>
                <q-card-section>
                  <div v-if="timeState.presets">
                    <strong>Presets loaded:</strong>
                    <pre>{{ JSON.stringify(timeState.presets, null, 2) }}</pre>
                  </div>
                  <div v-else>
                    <q-banner class="bg-orange-1 text-orange-8">
                      <template v-slot:avatar>
                        <q-icon name="warning" />
                      </template>
                      No presets loaded from backend
                    </q-banner>
                  </div>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Test Actions -->
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">🔧 Test Actions</div>

        <div class="row q-gutter-sm">
          <q-btn
            color="primary"
            label="Initialize"
            @click="testInitialize"
            :loading="loading.initialize"
          />

          <q-btn
            color="secondary"
            label="Set Last 1h"
            @click="testSetTimeRange('last_1h')"
            :loading="loading.timeRange"
          />

          <q-btn
            color="secondary"
            label="Set Last 6h"
            @click="testSetTimeRange('last_6h')"
            :loading="loading.timeRange"
          />

          <q-btn
            color="accent"
            label="Set Auto Window"
            @click="testSetWindowPeriod('auto')"
            :loading="loading.window"
          />

          <q-btn
            color="accent"
            label="Set 5m Window"
            @click="testSetWindowPeriod('5m')"
            :loading="loading.window"
          />

          <q-btn
            color="orange"
            label="Set 15m Refresh"
            @click="testSetRefreshRate('15m')"
          />

          <q-btn
            color="orange"
            label="Manual Refresh"
            @click="testManualRefresh"
          />

          <q-btn
            color="red"
            label="Test Custom Range"
            @click="testCustomRange"
            :loading="loading.custom"
          />
        </div>
      </q-card-section>

      <!-- Event Log -->
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">📝 Event Log</div>
        <q-scroll-area style="height: 200px; border: 1px solid #ddd; padding: 8px;">
          <div v-for="(log, index) in eventLog" :key="index" class="q-mb-xs">
            <span class="text-caption text-grey-7">{{ log.time }}</span>
            <span class="q-ml-sm">{{ log.message }}</span>
          </div>
        </q-scroll-area>
        <q-btn flat dense label="Clear Log" @click="eventLog = []" class="q-mt-xs" />
      </q-card-section>

      <!-- Auto-refresh Status -->
      <q-card-section v-if="timeState.autoRefreshEnabled">
        <q-banner class="bg-green-1 text-green-8">
          <template v-slot:avatar>
            <q-icon name="schedule" />
          </template>
          Auto-refresh is active ({{ timeState.refreshRate }})
        </q-banner>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useGlobalTimeInstance } from 'src/composables/useGlobalTime.js'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// Get global time instance
const globalTime = useGlobalTimeInstance()

// Local state for testing
const loading = reactive({
  initialize: false,
  timeRange: false,
  window: false,
  custom: false
})

const eventLog = ref([])

// Access to global time state
const timeState = globalTime.timeState

// Access to computed properties
const currentTimeRange = globalTime.currentTimeRange
const isValidTimeRange = globalTime.isValidTimeRange
const timeRangeDisplay = globalTime.timeRangeDisplay
const refreshRateMs = globalTime.refreshRateMs

// Add log entry
function addLog(message) {
  const time = new Date().toLocaleTimeString()
  eventLog.value.unshift({ time, message })

  // Keep only last 50 entries
  if (eventLog.value.length > 50) {
    eventLog.value = eventLog.value.slice(0, 50)
  }

  console.log(`🧪 ${time}: ${message}`)
}

// Test functions
async function testInitialize() {
  loading.initialize = true
  addLog('Testing initialize()...')

  try {
    await globalTime.initialize()
    addLog('✅ Initialize completed successfully')

    $q.notify({
      type: 'positive',
      message: 'Global time initialized successfully'
    })
  } catch (error) {
    addLog(`❌ Initialize failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to initialize: ' + error.message
    })
  } finally {
    loading.initialize = false
  }
}

async function testSetTimeRange(rangeType) {
  loading.timeRange = true
  addLog(`Testing setTimeRange(${rangeType})...`)

  try {
    await globalTime.setTimeRange(rangeType)
    addLog(`✅ Time range set to ${rangeType}`)

    $q.notify({
      type: 'positive',
      message: `Time range set to ${rangeType}`
    })
  } catch (error) {
    addLog(`❌ Set time range failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to set time range: ' + error.message
    })
  } finally {
    loading.timeRange = false
  }
}

async function testSetWindowPeriod(period) {
  loading.window = true
  addLog(`Testing setWindowPeriod(${period})...`)

  try {
    await globalTime.setWindowPeriod(period)
    addLog(`✅ Window period set to ${period}`)

    $q.notify({
      type: 'positive',
      message: `Window period set to ${period}`
    })
  } catch (error) {
    addLog(`❌ Set window period failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to set window period: ' + error.message
    })
  } finally {
    loading.window = false
  }
}

function testSetRefreshRate(rate) {
  addLog(`Testing setRefreshRate(${rate})...`)

  try {
    globalTime.setRefreshRate(rate)
    addLog(`✅ Refresh rate set to ${rate}`)

    $q.notify({
      type: 'positive',
      message: `Refresh rate set to ${rate}`
    })
  } catch (error) {
    addLog(`❌ Set refresh rate failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to set refresh rate: ' + error.message
    })
  }
}

function testManualRefresh() {
  addLog('Testing manual refresh()...')

  try {
    globalTime.refresh()
    addLog('✅ Manual refresh triggered')

    $q.notify({
      type: 'info',
      message: 'Manual refresh triggered'
    })
  } catch (error) {
    addLog(`❌ Manual refresh failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to trigger refresh: ' + error.message
    })
  }
}

async function testCustomRange() {
  loading.custom = true
  addLog('Testing custom time range...')

  try {
    // Create a custom range (last 2 hours)
    const now = new Date()
    const twoHoursAgo = new Date(now - 2 * 60 * 60 * 1000)

    await globalTime.setTimeRange('custom', twoHoursAgo.toISOString(), now.toISOString())
    addLog('✅ Custom time range set (last 2 hours)')

    $q.notify({
      type: 'positive',
      message: 'Custom time range set successfully'
    })
  } catch (error) {
    addLog(`❌ Custom range failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Failed to set custom range: ' + error.message
    })
  } finally {
    loading.custom = false
  }
}

// Listen for global time change events
function handleGlobalTimeChange(event) {
  addLog(`🔄 Global time changed: ${JSON.stringify(event.detail)}`)
}

onMounted(async () => {
  addLog('🚀 Test component mounted')

  // Listen for global time change events
  window.addEventListener('globalTimeChanged', handleGlobalTimeChange)

  // Auto-initialize for testing
  setTimeout(() => {
    testInitialize()
  }, 1000)
})

onBeforeUnmount(() => {
  addLog('🧹 Test component unmounting')
  window.removeEventListener('globalTimeChanged', handleGlobalTimeChange)
  globalTime.cleanup()
})
</script>

<style scoped>
pre {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
}

.q-scroll-area {
  font-family: monospace;
  font-size: 12px;
  background: #f9f9f9;
}
</style>
