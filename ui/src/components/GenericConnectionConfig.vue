<!-- ui/src/components/GenericConnectionConfig.vue -->
<!-- Generic connection configuration component for non-standard data sources -->

<template>
  <div class="generic-connection-config">
    <q-card flat bordered>
      <q-card-section>
        <div class="text-h6 q-mb-md">
          {{ sourceType.toUpperCase() }} Connection Configuration
        </div>

        <!-- Dynamic Configuration Form -->
        <div class="row q-gutter-md">
          <!-- Connection URL/Host -->
          <div class="col-12 col-md-6">
            <q-input
              v-model="localConfig.host"
              label="Host/URL"
              outlined
              dense
              :rules="[val => !!val || 'Host is required']"
              @update:model-value="updateConfig"
            >
              <template #prepend>
                <q-icon name="link" />
              </template>
            </q-input>
          </div>

          <!-- Port -->
          <div class="col-12 col-md-6">
            <q-input
              v-model.number="localConfig.port"
              label="Port"
              type="number"
              outlined
              dense
              :rules="[val => (val > 0 && val <= 65535) || 'Valid port required']"
              @update:model-value="updateConfig"
            >
              <template #prepend>
                <q-icon name="settings_ethernet" />
              </template>
            </q-input>
          </div>

          <!-- Authentication -->
          <div class="col-12">
            <q-expansion-item
              v-model="showAuth"
              icon="security"
              label="Authentication"
              default-opened
            >
              <div class="row q-gutter-md q-pa-md bg-grey-1">
                <!-- Username -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="localConfig.username"
                    label="Username"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="person" />
                    </template>
                  </q-input>
                </div>

                <!-- Password -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="localConfig.password"
                    label="Password"
                    type="password"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="lock" />
                    </template>
                  </q-input>
                </div>

                <!-- API Key -->
                <div class="col-12">
                  <q-input
                    v-model="localConfig.api_key"
                    label="API Key (Optional)"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="vpn_key" />
                    </template>
                  </q-input>
                </div>
              </div>
            </q-expansion-item>
          </div>

          <!-- Source-Specific Configuration -->
          <div class="col-12">
            <q-expansion-item
              v-model="showAdvanced"
              icon="tune"
              label="Advanced Configuration"
            >
              <div class="row q-gutter-md q-pa-md bg-grey-1">
                <!-- Database/Schema -->
                <div class="col-12 col-md-6" v-if="requiresDatabase">
                  <q-input
                    v-model="localConfig.database"
                    label="Database/Schema"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="storage" />
                    </template>
                  </q-input>
                </div>

                <!-- Table/Collection -->
                <div class="col-12 col-md-6" v-if="requiresTable">
                  <q-input
                    v-model="localConfig.table"
                    label="Table/Collection"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="table_view" />
                    </template>
                  </q-input>
                </div>

                <!-- Connection Timeout -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model.number="localConfig.timeout"
                    label="Connection Timeout (seconds)"
                    type="number"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="timer" />
                    </template>
                  </q-input>
                </div>

                <!-- SSL/TLS -->
                <div class="col-12 col-md-6">
                  <q-toggle
                    v-model="localConfig.ssl"
                    label="Use SSL/TLS"
                    color="primary"
                    @update:model-value="updateConfig"
                  />
                </div>

                <!-- Connection Pool Size -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model.number="localConfig.pool_size"
                    label="Connection Pool Size"
                    type="number"
                    outlined
                    dense
                    @update:model-value="updateConfig"
                  >
                    <template #prepend>
                      <q-icon name="hub" />
                    </template>
                  </q-input>
                </div>

                <!-- Custom Headers (for REST APIs) -->
                <div class="col-12" v-if="requiresHeaders">
                  <div class="text-subtitle2 q-mb-sm">Custom Headers</div>
                  <div v-for="(header, index) in localConfig.headers" :key="index" class="row q-gutter-sm q-mb-sm">
                    <div class="col">
                      <q-input
                        v-model="header.key"
                        placeholder="Header Name"
                        outlined
                        dense
                        @update:model-value="updateConfig"
                      />
                    </div>
                    <div class="col">
                      <q-input
                        v-model="header.value"
                        placeholder="Header Value"
                        outlined
                        dense
                        @update:model-value="updateConfig"
                      />
                    </div>
                    <div class="col-auto">
                      <q-btn
                        icon="remove"
                        flat
                        round
                        color="negative"
                        size="sm"
                        @click="removeHeader(index)"
                      />
                    </div>
                  </div>
                  <q-btn
                    label="Add Header"
                    icon="add"
                    size="sm"
                    flat
                    color="primary"
                    @click="addHeader"
                  />
                </div>
              </div>
            </q-expansion-item>
          </div>
        </div>

        <!-- Test Connection -->
        <div class="row q-gutter-sm q-mt-lg" v-if="editMode">
          <q-btn
            label="Test Connection"
            icon="wifi_tethering"
            color="primary"
            @click="testConnection"
            :loading="testing"
            :disable="!isConfigValid"
          />
          <q-btn
            label="Auto-Detect Settings"
            icon="auto_fix_high"
            color="secondary"
            outline
            @click="autoDetectSettings"
            :loading="autoDetecting"
          />
        </div>

        <!-- Connection Test Results -->
        <div v-if="testResult" class="q-mt-md">
          <q-banner
            :class="testResult.success ? 'bg-green-1' : 'bg-red-1'"
            :icon="testResult.success ? 'check_circle' : 'error'"
          >
            <div class="text-subtitle2">
              {{ testResult.success ? 'Connection Successful' : 'Connection Failed' }}
            </div>
            <div class="text-body2">{{ testResult.message }}</div>
            <div v-if="testResult.details" class="text-caption q-mt-sm">
              {{ testResult.details }}
            </div>
          </q-banner>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  config: {
    type: Object,
    default: () => ({})
  },
  editMode: {
    type: Boolean,
    default: false
  },
  sourceType: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['update', 'test'])

// Reactive data
const $q = useQuasar()
const localConfig = ref({
  host: '',
  port: null,
  username: '',
  password: '',
  api_key: '',
  database: '',
  table: '',
  timeout: 30,
  ssl: false,
  pool_size: 5,
  headers: []
})

const showAuth = ref(true)
const showAdvanced = ref(false)
const testing = ref(false)
const autoDetecting = ref(false)
const testResult = ref(null)

// Computed properties
const requiresDatabase = computed(() => {
  return ['postgresql', 'mysql', 'mongodb', 'mssql'].includes(props.sourceType.toLowerCase())
})

const requiresTable = computed(() => {
  return ['postgresql', 'mysql', 'mssql', 'clickhouse'].includes(props.sourceType.toLowerCase())
})

const requiresHeaders = computed(() => {
  return ['rest', 'http', 'api'].includes(props.sourceType.toLowerCase())
})

const isConfigValid = computed(() => {
  return localConfig.value.host &&
         localConfig.value.port &&
         localConfig.value.port > 0 &&
         localConfig.value.port <= 65535
})

// Methods
const updateConfig = () => {
  emit('update', { ...localConfig.value })
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null

  try {
    emit('test', { ...localConfig.value })

    // Simulate test result (in real app, this would come from parent)
    setTimeout(() => {
      testResult.value = {
        success: Math.random() > 0.3, // 70% success rate for demo
        message: Math.random() > 0.3 ? 'Connection established successfully' : 'Unable to connect to the specified host',
        details: Math.random() > 0.3 ? `Connected to ${localConfig.value.host}:${localConfig.value.port}` : 'Check your network settings and credentials'
      }
      testing.value = false
    }, 2000)
  } catch (error) {
    testResult.value = {
      success: false,
      message: 'Connection test failed',
      details: error.message
    }
    testing.value = false
  }
}

const autoDetectSettings = async () => {
  autoDetecting.value = true

  try {
    // Simulate auto-detection
    setTimeout(() => {
      // Set common defaults based on source type
      const defaults = getSourceDefaults(props.sourceType)
      Object.assign(localConfig.value, defaults)
      updateConfig()

      $q.notify({
        type: 'positive',
        message: 'Settings auto-detected successfully'
      })
      autoDetecting.value = false
    }, 1500)
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Auto-detection failed',
      caption: error.message
    })
    autoDetecting.value = false
  }
}

const getSourceDefaults = (sourceType) => {
  const defaults = {
    postgresql: { port: 5432, database: 'postgres' },
    mysql: { port: 3306, database: 'mysql' },
    mongodb: { port: 27017, database: 'admin' },
    redis: { port: 6379 },
    elasticsearch: { port: 9200 },
    kafka: { port: 9092 },
    rabbitmq: { port: 5672 },
    rest: { port: 80, ssl: false },
    https: { port: 443, ssl: true }
  }

  return defaults[sourceType.toLowerCase()] || { port: 80 }
}

const addHeader = () => {
  if (!localConfig.value.headers) {
    localConfig.value.headers = []
  }
  localConfig.value.headers.push({ key: '', value: '' })
  updateConfig()
}

const removeHeader = (index) => {
  localConfig.value.headers.splice(index, 1)
  updateConfig()
}

// Watchers
watch(() => props.config, (newConfig) => {
  if (newConfig) {
    localConfig.value = { ...localConfig.value, ...newConfig }
  }
}, { immediate: true, deep: true })

// Lifecycle
onMounted(() => {
  // Initialize headers array if source type requires it
  if (requiresHeaders.value && !localConfig.value.headers) {
    localConfig.value.headers = []
  }

  // Set default port if not specified
  if (!localConfig.value.port) {
    const defaults = getSourceDefaults(props.sourceType)
    if (defaults.port) {
      localConfig.value.port = defaults.port
      updateConfig()
    }
  }
})
</script>

<style scoped>
.generic-connection-config {
  width: 100%;
}

.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.q-banner {
  border-radius: 4px;
}
</style>
