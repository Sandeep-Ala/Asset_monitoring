<!--
  File: src/pages/QuickAPITestPage.vue
  Purpose: Quick test page to verify the API format fix
  Features: Simple test interface to validate HTTP 422 fix
-->

<template>
  <q-page class="q-pa-md">
    <div class="page-header q-mb-lg">
      <h4 class="q-ma-none text-primary">Quick API Format Test</h4>
      <p class="text-grey-7 q-mt-sm">
        Test the API format fix for HTTP 422 errors
      </p>
    </div>

    <!-- Test Controls -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-auto">
            <q-input
              v-model="testWidgetId"
              label="Widget ID"
              outlined
              dense
              style="min-width: 300px;"
            />
          </div>

          <div class="col-auto">
            <q-select
              v-model="timePreset"
              :options="timePresets"
              label="Time Range"
              outlined
              dense
              emit-value
              map-options
              style="min-width: 150px;"
            />
          </div>

          <div class="col-auto">
            <q-btn
              icon="play_arrow"
              label="Test API"
              color="primary"
              @click="testAPI"
              :loading="testing"
              :disable="!testWidgetId"
            />
          </div>

          <div class="col-auto">
            <q-btn
              icon="clear"
              label="Clear"
              outline
              @click="clearResults"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Test Results -->
    <div class="row q-gutter-md">
      <!-- Status Card -->
      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="text-h6">Test Status</div>

            <div class="q-mt-md">
              <q-chip
                :color="statusColor"
                :icon="statusIcon"
                text-color="white"
                size="md"
              >
                {{ statusText }}
              </q-chip>
            </div>

            <div v-if="lastResult" class="q-mt-md">
              <div class="text-caption text-grey-7">Response Time</div>
              <div class="text-h6">{{ lastResult.responseTime }}ms</div>

              <div class="text-caption text-grey-7 q-mt-sm">Data Points</div>
              <div class="text-h6">{{ lastResult.totalPoints || 0 }}</div>

              <div class="text-caption text-grey-7 q-mt-sm">Datasets</div>
              <div class="text-h6">{{ lastResult.datasets || 0 }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Request Details -->
      <div class="col-12 col-md-8">
        <q-card>
          <q-card-section>
            <div class="text-h6">Request Details</div>

            <div class="q-mt-md">
              <div class="text-caption text-grey-7">API Endpoint</div>
              <code class="request-url">POST /widgets/{{ testWidgetId }}/data</code>
            </div>

            <div class="q-mt-md">
              <div class="text-caption text-grey-7">Request Payload</div>
              <pre class="request-payload">{{ requestPayload }}</pre>
            </div>

            <div v-if="lastResult?.error" class="q-mt-md">
              <div class="text-caption text-grey-7">Error Details</div>
              <q-banner class="bg-red-1 text-red">
                <template v-slot:avatar>
                  <q-icon name="error" color="red" />
                </template>
                {{ lastResult.error }}
              </q-banner>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Raw Response -->
    <q-card v-if="lastResult" class="q-mt-md">
      <q-card-section>
        <div class="text-h6">Response Data</div>

        <q-tabs v-model="activeTab" dense class="q-mt-md">
          <q-tab name="summary" label="Summary" />
          <q-tab name="raw" label="Raw Response" />
          <q-tab name="validation" label="Validation" />
        </q-tabs>

        <q-tab-panels v-model="activeTab" animated>
          <q-tab-panel name="summary">
            <div v-if="lastResult.success" class="summary-grid">
              <div class="summary-item">
                <div class="summary-label">Success</div>
                <div class="summary-value text-positive">{{ lastResult.success ? '✅ Yes' : '❌ No' }}</div>
              </div>

              <div class="summary-item">
                <div class="summary-label">Data Received</div>
                <div class="summary-value">{{ lastResult.dataReceived ? '✅ Yes' : '❌ No' }}</div>
              </div>

              <div class="summary-item">
                <div class="summary-label">Empty Dataset</div>
                <div class="summary-value">{{ lastResult.isEmpty ? '⚠️ Yes' : '✅ No' }}</div>
              </div>

              <div class="summary-item">
                <div class="summary-label">Total Points</div>
                <div class="summary-value">{{ lastResult.totalPoints || 0 }}</div>
              </div>

              <div class="summary-item">
                <div class="summary-label">Datasets</div>
                <div class="summary-value">{{ lastResult.datasets || 0 }}</div>
              </div>

              <div class="summary-item">
                <div class="summary-label">Labels</div>
                <div class="summary-value">{{ lastResult.labels || 0 }}</div>
              </div>
            </div>

            <div v-else class="text-center q-pa-md">
              <q-icon name="error_outline" size="48px" color="negative" />
              <div class="text-h6 text-negative q-mt-sm">API Test Failed</div>
              <div class="text-body2 text-grey-7">{{ lastResult.error }}</div>
            </div>
          </q-tab-panel>

          <q-tab-panel name="raw">
            <q-scroll-area style="height: 300px;">
              <pre class="raw-response">{{ JSON.stringify(lastResult, null, 2) }}</pre>
            </q-scroll-area>
          </q-tab-panel>

          <q-tab-panel name="validation">
            <div v-if="validationResult">
              <div class="validation-section">
                <q-chip
                  :color="validationResult.isValid ? 'positive' : 'negative'"
                  :icon="validationResult.isValid ? 'check_circle' : 'error'"
                  text-color="white"
                >
                  {{ validationResult.isValid ? 'Valid Request Format' : 'Invalid Request Format' }}
                </q-chip>
              </div>

              <div v-if="validationResult.errors.length > 0" class="q-mt-md">
                <div class="text-subtitle2 text-negative">Errors:</div>
                <q-list dense>
                  <q-item v-for="error in validationResult.errors" :key="error">
                    <q-item-section avatar>
                      <q-icon name="error" color="negative" />
                    </q-item-section>
                    <q-item-section>{{ error }}</q-item-section>
                  </q-item>
                </q-list>
              </div>

              <div v-if="validationResult.warnings.length > 0" class="q-mt-md">
                <div class="text-subtitle2 text-warning">Warnings:</div>
                <q-list dense>
                  <q-item v-for="warning in validationResult.warnings" :key="warning">
                    <q-item-section avatar>
                      <q-icon name="warning" color="warning" />
                    </q-item-section>
                    <q-item-section>{{ warning }}</q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>

    <!-- Test Log -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row items-center justify-between">
          <div class="text-h6">Test Log</div>
          <q-btn
            icon="clear_all"
            label="Clear Log"
            size="sm"
            outline
            @click="clearLog"
          />
        </div>

        <q-scroll-area style="height: 200px;" class="q-mt-md">
          <div class="test-log">
            <div
              v-for="(entry, index) in testLog"
              :key="index"
              class="log-entry"
              :class="entry.type"
            >
              <span class="log-time">{{ entry.time }}</span>
              <span class="log-message">{{ entry.message }}</span>
            </div>
          </div>
        </q-scroll-area>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { format } from 'date-fns'
import WidgetAPIService from 'src/services/apiFixService.js'

const $q = useQuasar()

// ==================== REACTIVE STATE ====================

const testWidgetId = ref('92587d13-d13f-4051-bee7-28e5f00c8f62')
const timePreset = ref('last_1h')
const testing = ref(false)
const lastResult = ref(null)
const validationResult = ref(null)
const activeTab = ref('summary')
const testLog = ref([])

const timePresets = [
  { label: 'Last 15 minutes', value: 'last_15m' },
  { label: 'Last 1 hour', value: 'last_1h' },
  { label: 'Last 6 hours', value: 'last_6h' },
  { label: 'Last 24 hours', value: 'last_24h' },
  { label: 'Last 7 days', value: 'last_7d' }
]

// ==================== COMPUTED ====================

const statusColor = computed(() => {
  if (!lastResult.value) return 'grey'
  return lastResult.value.success ? 'positive' : 'negative'
})

const statusIcon = computed(() => {
  if (!lastResult.value) return 'help'
  return lastResult.value.success ? 'check_circle' : 'error'
})

const statusText = computed(() => {
  if (!lastResult.value) return 'Not Tested'
  return lastResult.value.success ? 'API Working' : 'API Failed'
})

const requestPayload = computed(() => {
  const timeRange = WidgetAPIService.createPresetTimeRange(timePreset.value)
  const payload = {
    time_start: timeRange.start,
    time_end: timeRange.end,
    time_range_type: timeRange.range_type
  }
  return JSON.stringify(payload, null, 2)
})

// ==================== METHODS ====================

function addLogEntry(type, message) {
  testLog.value.push({
    type,
    message,
    time: format(new Date(), 'HH:mm:ss.SSS')
  })
}

async function testAPI() {
  if (!testWidgetId.value) {
    $q.notify({
      type: 'negative',
      message: 'Please enter a widget ID',
      timeout: 2000
    })
    return
  }

  testing.value = true
  addLogEntry('info', `Starting API test for widget: ${testWidgetId.value}`)

  try {
    // Create time range
    const timeRange = WidgetAPIService.createPresetTimeRange(timePreset.value)
    addLogEntry('info', `Using time range: ${timeRange.range_type}`)

    // Validate request format
    const requestData = {
      time_start: timeRange.start,
      time_end: timeRange.end,
      time_range_type: timeRange.range_type
    }

    validationResult.value = WidgetAPIService.validateRequestFormat(requestData)

    if (!validationResult.value.isValid) {
      addLogEntry('warning', 'Request format has validation errors')
      validationResult.value.errors.forEach(error => {
        addLogEntry('error', error)
      })
    }

    // Make API call
    addLogEntry('info', 'Making API call...')
    const result = await WidgetAPIService.testWidgetEndpoint(testWidgetId.value, timeRange)

    lastResult.value = result

    if (result.success) {
      addLogEntry('success', `API test successful! Response time: ${result.responseTime}ms`)
      addLogEntry('success', `Data points: ${result.totalPoints}, Datasets: ${result.datasets}`)

      if (result.isEmpty) {
        addLogEntry('warning', 'Dataset is empty - no data points returned')
      }

      $q.notify({
        type: 'positive',
        message: 'API test successful!',
        caption: `${result.totalPoints} data points received`,
        timeout: 3000
      })
    } else {
      addLogEntry('error', `API test failed: ${result.error}`)

      if (result.errorDetails?.status === 422) {
        addLogEntry('error', 'HTTP 422: Request format validation failed on backend')
      }

      $q.notify({
        type: 'negative',
        message: 'API test failed',
        caption: result.error,
        timeout: 5000
      })
    }

  } catch (error) {
    console.error('❌ Test failed:', error)
    addLogEntry('error', `Test failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Test error',
      caption: error.message,
      timeout: 5000
    })
  } finally {
    testing.value = false
  }
}

function clearResults() {
  lastResult.value = null
  validationResult.value = null
  activeTab.value = 'summary'
  addLogEntry('info', 'Results cleared')
}

function clearLog() {
  testLog.value = []
}
</script>

<style scoped>
.request-url {
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 4px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.9rem;
  color: #1976d2;
  border: 1px solid #e0e0e0;
}

.request-payload,
.raw-response {
  background: #f8f8f8;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid #e0e0e0;
  margin: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.summary-label {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.validation-section {
  margin-bottom: 16px;
}

.test-log {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
}

.log-entry {
  display: flex;
  margin-bottom: 4px;
  padding: 4px;
  border-radius: 2px;
}

.log-entry.success {
  background: #f3f9f3;
  color: #2e7d32;
}

.log-entry.error {
  background: #fef5f5;
  color: #d32f2f;
}

.log-entry.warning {
  background: #fff8e1;
  color: #f57c00;
}

.log-entry.info {
  color: #1976d2;
}

.log-time {
  width: 80px;
  color: #666;
  font-weight: 500;
}

.log-message {
  flex: 1;
  margin-left: 8px;
}
</style>
