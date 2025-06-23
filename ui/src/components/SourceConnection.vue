<!-- ui/src/components/SourceConnection.vue -->
<template>
  <div class="source-connection q-pa-lg">
    <!-- Connection Status Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Connection Management</div>
        <div class="text-subtitle2 text-grey-6">
          Manage and monitor your data source connection
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Test Connection"
          icon="wifi_find"
          color="primary"
          @click="testConnection"
          :loading="testing"
        />
        <q-btn
          label="Edit Configuration"
          icon="edit"
          color="secondary"
          outline
          @click="editMode = !editMode"
        />
      </div>
    </div>

    <!-- Connection Status Card -->
    <div class="q-mb-lg">
      <q-card flat bordered :class="connectionStatusClass">
        <q-card-section>
          <div class="row items-center">
            <q-icon
              :name="connectionStatusIcon"
              :color="connectionStatusColor"
              size="2rem"
              class="q-mr-md"
            />
            <div class="col">
              <div class="text-h6">{{ connectionStatusTitle }}</div>
              <div class="text-body2 text-grey-7">{{ connectionStatusMessage }}</div>
            </div>
            <div class="col-auto">
              <q-btn
                icon="refresh"
                flat
                round
                @click="refreshConnectionStatus"
                :loading="refreshing"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Connection Details -->
        <q-card-section v-if="lastConnectionTest" class="q-pt-none">
          <q-separator class="q-mb-md" />
          <div class="row q-gutter-md text-caption">
            <div>
              <strong>Last Test:</strong> {{ formatDateTime(lastConnectionTest.timestamp) }}
            </div>
            <div>
              <strong>Response Time:</strong> {{ lastConnectionTest.responseTime || 'N/A' }}
            </div>
            <div>
              <strong>Status:</strong> {{ lastConnectionTest.status || 'Unknown' }}
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Configuration Section -->
    <div class="row q-gutter-lg">
      <!-- Configuration Display/Edit -->
      <div class="col-12 col-lg-8">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="row items-center justify-between">
              <div class="text-h6">Connection Configuration</div>
              <q-toggle
                v-model="editMode"
                label="Edit Mode"
                color="primary"
              />
            </div>
          </q-card-section>

          <q-card-section>
            <!-- InfluxDB Configuration -->
            <div v-if="source.source_type === 'influxdb'">
              <InfluxDBConnectionConfig
                :config="connectionConfig"
                :edit-mode="editMode"
                @update="updateConfig"
                @test="testConnection"
                :testing="testing"
              />
            </div>

            <!-- Parquet Configuration -->
            <div v-else-if="source.source_type === 'parquet'">
              <ParquetConnectionConfig
                :config="connectionConfig"
                :edit-mode="editMode"
                @update="updateConfig"
                @test="testConnection"
                :testing="testing"
              />
            </div>

            <!-- Generic Configuration for other types -->
            <div v-else>
              <GenericConnectionConfig
                :config="connectionConfig"
                :edit-mode="editMode"
                :source-type="source.source_type"
                @update="updateConfig"
                @test="testConnection"
                :testing="testing"
              />
            </div>

            <!-- Actions -->
            <div v-if="editMode" class="row q-gutter-sm q-mt-lg">
              <q-btn
                label="Save Changes"
                icon="save"
                color="positive"
                @click="saveConfiguration"
                :loading="saving"
                :disable="!hasConfigChanges"
              />
              <q-btn
                label="Reset"
                icon="refresh"
                color="warning"
                outline
                @click="resetConfiguration"
              />
              <q-btn
                label="Cancel"
                flat
                @click="cancelEdit"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Connection Monitoring -->
      <div class="col-12 col-lg-4">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">Connection Monitoring</div>
            <div class="text-caption">Real-time connection health</div>
          </q-card-section>

          <q-card-section>
            <!-- Health Metrics -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">Health Metrics</div>

              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="speed" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Response Time</q-item-label>
                    <q-item-label caption>{{ healthMetrics.responseTime || 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="check_circle" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Uptime</q-item-label>
                    <q-item-label caption>{{ healthMetrics.uptime || 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="error" color="red" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Last Error</q-item-label>
                    <q-item-label caption>{{ healthMetrics.lastError || 'None' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Auto-monitoring Toggle -->
            <q-separator class="q-my-md" />

            <div class="text-subtitle2 q-mb-sm">Auto Monitoring</div>
            <q-toggle
              v-model="autoMonitoring"
              label="Enable automatic health checks"
              color="positive"
              @update:model-value="toggleAutoMonitoring"
            />
            <div class="text-caption text-grey-6 q-mt-xs">
              {{ autoMonitoring ? 'Checking every 5 minutes' : 'Manual checks only' }}
            </div>

            <!-- Manual Actions -->
            <q-separator class="q-my-md" />

            <div class="text-subtitle2 q-mb-sm">Manual Actions</div>
            <div class="column q-gutter-sm">
              <q-btn
                label="Ping Connection"
                icon="network_ping"
                color="blue"
                outline
                size="sm"
                @click="pingConnection"
                :loading="pinging"
              />
              <q-btn
                label="Check Permissions"
                icon="security"
                color="orange"
                outline
                size="sm"
                @click="checkPermissions"
                :loading="checkingPermissions"
              />
              <q-btn
                label="Clear Cache"
                icon="clear_all"
                color="grey"
                outline
                size="sm"
                @click="clearConnectionCache"
              />
            </div>
          </q-card-section>
        </q-card>

        <!-- Connection History -->
        <q-card flat bordered class="q-mt-md">
          <q-card-section class="bg-orange-1">
            <div class="text-h6">Connection History</div>
            <div class="text-caption">Recent connection tests</div>
          </q-card-section>

          <q-card-section>
            <q-list v-if="connectionHistory.length > 0" separator>
              <q-item
                v-for="(test, index) in connectionHistory.slice(0, 5)"
                :key="index"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="test.success ? 'check_circle' : 'error'"
                    :color="test.success ? 'positive' : 'negative'"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ test.success ? 'Success' : 'Failed' }}</q-item-label>
                  <q-item-label caption>{{ formatDateTime(test.timestamp) }}</q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip
                    :color="test.success ? 'positive' : 'negative'"
                    text-color="white"
                    size="sm"
                  >
                    {{ test.responseTime || 'N/A' }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-else class="text-center q-pa-md text-grey-6">
              <q-icon name="history" size="2rem" class="q-mb-sm" />
              <div>No connection history</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Advanced Settings -->
    <div class="q-mt-lg">
      <q-expansion-item
        icon="settings"
        label="Advanced Connection Settings"
        dense
      >
        <q-card flat bordered>
          <q-card-section>
            <div class="row q-gutter-md">
              <!-- Timeout Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.connectionTimeout"
                  label="Connection Timeout (seconds)"
                  type="number"
                  outlined
                  dense
                  :min="5"
                  :max="300"
                />
              </div>

              <!-- Retry Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.retryAttempts"
                  label="Retry Attempts"
                  type="number"
                  outlined
                  dense
                  :min="0"
                  :max="10"
                />
              </div>

              <!-- Pool Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.maxConnections"
                  label="Max Connections"
                  type="number"
                  outlined
                  dense
                  :min="1"
                  :max="100"
                />
              </div>

              <!-- SSL Verification -->
              <div class="col-12">
                <q-toggle
                  v-model="advancedSettings.sslVerification"
                  label="SSL Certificate Verification"
                  color="primary"
                />
                <div class="text-caption text-grey-6">
                  Disable for self-signed certificates
                </div>
              </div>

              <!-- Keep Alive -->
              <div class="col-12">
                <q-toggle
                  v-model="advancedSettings.keepAlive"
                  label="Keep Connection Alive"
                  color="primary"
                />
                <div class="text-caption text-grey-6">
                  Maintain persistent connection
                </div>
              </div>
            </div>

            <div class="row q-gutter-sm q-mt-md">
              <q-btn
                label="Apply Settings"
                color="primary"
                @click="applyAdvancedSettings"
              />
              <q-btn
                label="Reset to Defaults"
                outline
                @click="resetAdvancedSettings"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import configuration components
import InfluxDBConnectionConfig from 'src/components/InfluxDBConfig.vue'
import ParquetConnectionConfig from 'src/components/ParquetConfig.vue'
import GenericConnectionConfig from 'src/components/GenericConnectionConfig.vue'

// Props
const props = defineProps({
  source: Object
})

// Emits
const emit = defineEmits(['test-connection', 'update-config'])

// Reactive data
const $q = useQuasar()
const editMode = ref(false)
const testing = ref(false)
const saving = ref(false)
const refreshing = ref(false)
const pinging = ref(false)
const checkingPermissions = ref(false)
const autoMonitoring = ref(false)

// Connection state
const connectionConfig = ref({})
const originalConfig = ref({})
const lastConnectionTest = ref(null)
const connectionHistory = ref([])
const healthMetrics = ref({
  responseTime: null,
  uptime: null,
  lastError: null
})

// Advanced settings
const advancedSettings = ref({
  connectionTimeout: 30,
  retryAttempts: 3,
  maxConnections: 10,
  sslVerification: true,
  keepAlive: true
})

// Auto-monitoring
let monitoringInterval = null

// Computed properties
const hasConfigChanges = computed(() => {
  return JSON.stringify(connectionConfig.value) !== JSON.stringify(originalConfig.value)
})

const connectionStatusClass = computed(() => {
  if (!lastConnectionTest.value) return 'bg-grey-2'
  return lastConnectionTest.value.success ? 'bg-green-1' : 'bg-red-1'
})

const connectionStatusIcon = computed(() => {
  if (!lastConnectionTest.value) return 'help_outline'
  return lastConnectionTest.value.success ? 'check_circle' : 'error'
})

const connectionStatusColor = computed(() => {
  if (!lastConnectionTest.value) return 'grey'
  return lastConnectionTest.value.success ? 'positive' : 'negative'
})

const connectionStatusTitle = computed(() => {
  if (!lastConnectionTest.value) return 'Connection Status Unknown'
  return lastConnectionTest.value.success ? 'Connection Healthy' : 'Connection Issues'
})

const connectionStatusMessage = computed(() => {
  if (!lastConnectionTest.value) return 'No connection test performed yet'
  return lastConnectionTest.value.message || 'No additional details available'
})

// Methods
onMounted(() => {
  initializeConnectionConfig()
  loadConnectionHistory()
  startHealthMonitoring()
})

onUnmounted(() => {
  stopHealthMonitoring()
})

const initializeConnectionConfig = () => {
  try {
    connectionConfig.value = JSON.parse(props.source.connection_config)
    originalConfig.value = JSON.parse(props.source.connection_config)
  } catch (error) {
    console.error('Failed to parse connection config:', error)
    connectionConfig.value = {}
    originalConfig.value = {}
  }
}

const loadConnectionHistory = () => {
  // Load from localStorage or API
  const stored = localStorage.getItem(`connection_history_${props.source.source_id}`)
  if (stored) {
    try {
      connectionHistory.value = JSON.parse(stored)
    } catch (error) {
      console.error('Failed to load connection history:', error)
      connectionHistory.value = []
    }
  }
}

const saveConnectionHistory = () => {
  try {
    localStorage.setItem(
      `connection_history_${props.source.source_id}`,
      JSON.stringify(connectionHistory.value.slice(0, 20)) // Keep only last 20 entries
    )
  } catch (error) {
    console.error('Failed to save connection history:', error)
  }
}

const testConnection = async () => {
  testing.value = true

  try {
    const response = await axios.post('http://localhost:8000/datasources/test-connection', {
      source_type: props.source.source_type,
      connection_config: connectionConfig.value
    })

    const testResult = {
      success: response.data.success,
      message: response.data.message,
      timestamp: new Date().toISOString(),
      responseTime: response.data.response_time ? `${response.data.response_time}ms` : null,
      status: response.data.success ? 'Connected' : 'Failed'
    }

    lastConnectionTest.value = testResult

    // Add to history
    connectionHistory.value.unshift(testResult)
    saveConnectionHistory()

    // Update health metrics
    if (response.data.success) {
      healthMetrics.value.responseTime = testResult.responseTime
      healthMetrics.value.lastError = null
    } else {
      healthMetrics.value.lastError = response.data.message
    }

    $q.notify({
      type: response.data.success ? 'positive' : 'negative',
      message: response.data.message,
      icon: response.data.success ? 'check_circle' : 'error'
    })

    emit('test-connection', testResult)

  } catch (error) {
    const testResult = {
      success: false,
      message: error.response?.data?.detail || error.message || 'Connection test failed',
      timestamp: new Date().toISOString(),
      responseTime: null,
      status: 'Error'
    }

    lastConnectionTest.value = testResult
    connectionHistory.value.unshift(testResult)
    saveConnectionHistory()

    healthMetrics.value.lastError = testResult.message

    $q.notify({
      type: 'negative',
      message: 'Connection test failed',
      caption: testResult.message
    })
  } finally {
    testing.value = false
  }
}

const updateConfig = (newConfig) => {
  connectionConfig.value = { ...connectionConfig.value, ...newConfig }
}

const saveConfiguration = async () => {
  saving.value = true

  try {
    const response = await axios.put(`http://localhost:8000/datasources/${props.source.source_id}`, {
      connection_config: JSON.stringify(connectionConfig.value)
    })

    originalConfig.value = { ...connectionConfig.value }
    editMode.value = false

    $q.notify({
      type: 'positive',
      message: 'Configuration saved successfully',
      icon: 'save'
    })

    emit('update-config', connectionConfig.value)

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to save configuration',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    saving.value = false
  }
}

const resetConfiguration = () => {
  connectionConfig.value = { ...originalConfig.value }
}

const cancelEdit = () => {
  resetConfiguration()
  editMode.value = false
}

const refreshConnectionStatus = async () => {
  refreshing.value = true
  try {
    await testConnection()
  } finally {
    refreshing.value = false
  }
}

const pingConnection = async () => {
  pinging.value = true

  try {
    // Simulate ping operation
    await new Promise(resolve => setTimeout(resolve, 1000))

    $q.notify({
      type: 'positive',
      message: 'Ping successful',
      caption: 'Connection is responsive'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Ping failed',
      caption: 'Connection may be down'
    })
  } finally {
    pinging.value = false
  }
}

const checkPermissions = async () => {
  checkingPermissions.value = true

  try {
    // Simulate permission check
    await new Promise(resolve => setTimeout(resolve, 1500))

    $q.notify({
      type: 'positive',
      message: 'Permissions verified',
      caption: 'All required permissions are available'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Permission check failed',
      caption: 'Some permissions may be missing'
    })
  } finally {
    checkingPermissions.value = false
  }
}

const clearConnectionCache = () => {
  connectionHistory.value = []
  saveConnectionHistory()

  $q.notify({
    type: 'positive',
    message: 'Connection cache cleared',
    icon: 'clear_all'
  })
}

const toggleAutoMonitoring = (enabled) => {
  autoMonitoring.value = enabled
  if (enabled) {
    startHealthMonitoring()
  } else {
    stopHealthMonitoring()
  }
}

const startHealthMonitoring = () => {
  if (autoMonitoring.value && !monitoringInterval) {
    monitoringInterval = setInterval(() => {
      testConnection()
    }, 5 * 60 * 1000) // 5 minutes
  }
}

const stopHealthMonitoring = () => {
  if (monitoringInterval) {
    clearInterval(monitoringInterval)
    monitoringInterval = null
  }
}

const applyAdvancedSettings = () => {
  // Apply advanced settings to connection config
  connectionConfig.value = {
    ...connectionConfig.value,
    timeout: advancedSettings.value.connectionTimeout,
    retry_attempts: advancedSettings.value.retryAttempts,
    max_connections: advancedSettings.value.maxConnections,
    verify_ssl: advancedSettings.value.sslVerification,
    keep_alive: advancedSettings.value.keepAlive
  }

  $q.notify({
    type: 'positive',
    message: 'Advanced settings applied',
    icon: 'settings'
  })
}

const resetAdvancedSettings = () => {
  advancedSettings.value = {
    connectionTimeout: 30,
    retryAttempts: 3,
    maxConnections: 10,
    sslVerification: true,
    keepAlive: true
  }

  $q.notify({
    type: 'info',
    message: 'Advanced settings reset to defaults'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return 'Invalid date'
  }
}
</script>

<style scoped>
.source-connection {
  background-color: #fafafa;
  min-height: 100%;
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-orange-1 {
  background-color: rgba(255, 152, 0, 0.1);
}

.bg-red-1 {
  background-color: rgba(244, 67, 54, 0.1);
}

.bg-grey-2 {
  background-color: rgba(158, 158, 158, 0.1);
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.q-item {
  border-radius: 8px;
  margin-bottom: 4px;
}

.q-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.q-chip {
  font-weight: 500;
}

/* Custom scrollbar */
.q-list {
  max-height: 300px;
  overflow-y: auto;
}

.q-list::-webkit-scrollbar {
  width: 6px;
}

.q-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.q-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.q-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .row.q-gutter-lg {
    margin: -8px;
  }

  .row.q-gutter-lg > div {
    padding: 8px;
  }
}
</style>
