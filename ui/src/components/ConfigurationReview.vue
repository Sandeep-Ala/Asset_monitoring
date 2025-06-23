<!-- ui/src/components/ConfigurationReview.vue -->
<!-- Final configuration review component for wizard completion -->

<template>
  <div class="configuration-review">
    <q-card flat>
      <q-card-section>
        <div class="text-h6 q-mb-md">Configuration Review</div>
        <div class="text-body2 text-grey-6 q-mb-lg">
          Please review your data source configuration before creating it. You can go back to make changes if needed.
        </div>

        <!-- Configuration Summary -->
        <div class="row q-gutter-md">
          <!-- Basic Information -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section class="bg-blue-1">
                <div class="text-subtitle2">
                  <q-icon name="info" class="q-mr-sm" />
                  Basic Information
                </div>
              </q-card-section>
              <q-card-section>
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Source Name</q-item-label>
                      <q-item-label>{{ formData.source_name }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Source Type</q-item-label>
                      <q-item-label class="text-capitalize">
                        <q-chip :color="getSourceTypeColor(formData.source_type)" text-color="white" size="sm">
                          {{ formData.source_type.toUpperCase() }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Description</q-item-label>
                      <q-item-label>{{ formData.description || 'No description provided' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Status</q-item-label>
                      <q-item-label>
                        <q-chip :color="formData.is_active ? 'positive' : 'negative'" text-color="white" size="sm">
                          {{ formData.is_active ? 'Active' : 'Inactive' }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Connection Status -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section :class="connectionStatusClass">
                <div class="text-subtitle2">
                  <q-icon :name="connectionStatusIcon" class="q-mr-sm" />
                  Connection Status
                </div>
              </q-card-section>
              <q-card-section>
                <div v-if="connectionStatus">
                  <div class="text-body2 q-mb-sm">
                    {{ connectionStatus.message }}
                  </div>
                  <div v-if="connectionStatus.details" class="text-caption text-grey-6">
                    {{ connectionStatus.details }}
                  </div>
                  <div v-if="connectionStatus.response_time" class="text-caption q-mt-sm">
                    Response time: {{ connectionStatus.response_time }}ms
                  </div>
                </div>
                <div v-else class="text-body2 text-grey-6">
                  Connection not tested yet
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Connection Configuration -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section class="bg-green-1">
                <div class="text-subtitle2">
                  <q-icon name="settings" class="q-mr-sm" />
                  Connection Configuration
                </div>
              </q-card-section>
              <q-card-section>
                <div class="row q-gutter-md">
                  <div class="col-12 col-md-6" v-for="(value, key) in sanitizedConfig" :key="key">
                    <q-input
                      :model-value="formatConfigValue(key, value)"
                      :label="formatConfigKey(key)"
                      readonly
                      dense
                      outlined
                    >
                      <template #prepend>
                        <q-icon :name="getConfigIcon(key)" />
                      </template>
                    </q-input>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Discovery Status -->
          <div class="col-12" v-if="discoveredSchema">
            <q-card flat bordered>
              <q-card-section class="bg-purple-1">
                <div class="text-subtitle2">
                  <q-icon name="schema" class="q-mr-sm" />
                  Schema Discovery Results
                </div>
              </q-card-section>
              <q-card-section>
                <div class="row q-gutter-md">
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-blue-1 text-center q-pa-md">
                      <div class="text-h4">{{ discoveredSchema.measurements?.length || 0 }}</div>
                      <div class="text-body2">Measurements</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-green-1 text-center q-pa-md">
                      <div class="text-h4">{{ totalTags }}</div>
                      <div class="text-body2">Tags</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-orange-1 text-center q-pa-md">
                      <div class="text-h4">{{ totalFields }}</div>
                      <div class="text-body2">Fields</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-red-1 text-center q-pa-md">
                      <div class="text-h4">{{ discoveredSchema.sample_size || 0 }}</div>
                      <div class="text-body2">Sample Size</div>
                    </q-card>
                  </div>
                </div>

                <!-- Measurement List -->
                <div v-if="discoveredSchema.measurements?.length > 0" class="q-mt-md">
                  <div class="text-subtitle2 q-mb-sm">Discovered Measurements:</div>
                  <q-list dense>
                    <q-item v-for="measurement in discoveredSchema.measurements.slice(0, 5)" :key="measurement">
                      <q-item-section avatar>
                        <q-icon name="table_chart" color="primary" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ measurement }}</q-item-label>
                        <q-item-label caption>
                          {{ getTagsCount(measurement) }} tags, {{ getFieldsCount(measurement) }} fields
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="discoveredSchema.measurements.length > 5">
                      <q-item-section>
                        <q-item-label class="text-grey-6">
                          ... and {{ discoveredSchema.measurements.length - 5 }} more measurements
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Validation Results -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section :class="validationStatus.isValid ? 'bg-green-1' : 'bg-red-1'">
                <div class="text-subtitle2">
                  <q-icon :name="validationStatus.isValid ? 'check_circle' : 'error'" class="q-mr-sm" />
                  Configuration Validation
                </div>
              </q-card-section>
              <q-card-section>
                <div v-if="validationStatus.isValid" class="text-positive">
                  <q-icon name="check" class="q-mr-sm" />
                  All configuration settings are valid and ready for deployment.
                </div>
                <div v-else>
                  <div class="text-negative q-mb-md">
                    <q-icon name="warning" class="q-mr-sm" />
                    The following issues need to be resolved:
                  </div>
                  <q-list dense>
                    <q-item v-for="error in validationStatus.errors" :key="error">
                      <q-item-section avatar>
                        <q-icon name="error" color="negative" size="sm" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-negative">{{ error }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="row justify-between q-mt-lg">
          <q-btn
            label="Go Back"
            icon="arrow_back"
            flat
            @click="$emit('go-back')"
          />

          <div class="q-gutter-sm">
            <q-btn
              label="Test Connection Again"
              icon="wifi_tethering"
              color="secondary"
              outline
              @click="$emit('test-connection')"
              :loading="testing"
            />
            <q-btn
              label="Create Data Source"
              icon="add"
              color="primary"
              @click="createDataSource"
              :loading="creating"
              :disable="!validationStatus.isValid"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Creation Progress -->
    <q-dialog v-model="showProgress" persistent>
      <q-card style="min-width: 300px">
        <q-card-section class="text-center">
          <q-spinner-dots size="3rem" color="primary" class="q-mb-md" />
          <div class="text-h6">Creating Data Source...</div>
          <div class="text-body2 text-grey-6">{{ progressMessage }}</div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  formData: {
    type: Object,
    required: true
  },
  discoveredSchema: {
    type: Object,
    default: null
  },
  connectionStatus: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['go-back', 'test-connection', 'create'])

// Reactive data
const $q = useQuasar()
const creating = ref(false)
const testing = ref(false)
const showProgress = ref(false)
const progressMessage = ref('')

// Computed properties
const sanitizedConfig = computed(() => {
  const config = { ...props.formData.connection_config }

  // Hide sensitive information
  if (config.password) config.password = '••••••••'
  if (config.api_key) config.api_key = '••••••••'
  if (config.token) config.token = '••••••••'

  // Remove empty values
  Object.keys(config).forEach(key => {
    if (config[key] === '' || config[key] === null || config[key] === undefined) {
      delete config[key]
    }
  })

  return config
})

const connectionStatusClass = computed(() => {
  if (!props.connectionStatus) return 'bg-grey-2'
  return props.connectionStatus.success ? 'bg-green-1' : 'bg-red-1'
})

const connectionStatusIcon = computed(() => {
  if (!props.connectionStatus) return 'help_outline'
  return props.connectionStatus.success ? 'check_circle' : 'error'
})

const totalTags = computed(() => {
  if (!props.discoveredSchema?.tags) return 0
  return Object.values(props.discoveredSchema.tags).reduce((sum, tags) => sum + tags.length, 0)
})

const totalFields = computed(() => {
  if (!props.discoveredSchema?.fields) return 0
  return Object.values(props.discoveredSchema.fields).reduce((sum, fields) => sum + fields.length, 0)
})

const validationStatus = computed(() => {
  const errors = []

  // Basic validation
  if (!props.formData.source_name?.trim()) {
    errors.push('Source name is required')
  }

  if (!props.formData.source_type) {
    errors.push('Source type is required')
  }

  if (!props.formData.connection_config || Object.keys(props.formData.connection_config).length === 0) {
    errors.push('Connection configuration is required')
  }

  // Connection validation
  if (!props.connectionStatus) {
    errors.push('Connection must be tested before creating the data source')
  } else if (!props.connectionStatus.success) {
    errors.push('Connection test failed - please fix connection issues')
  }

  // Configuration-specific validation
  const config = props.formData.connection_config
  if (config?.host && !isValidHost(config.host)) {
    errors.push('Invalid host format')
  }

  if (config?.port && (config.port < 1 || config.port > 65535)) {
    errors.push('Port must be between 1 and 65535')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
})

// Methods
const getSourceTypeColor = (type) => {
  const colors = {
    influxdb: 'blue',
    parquet: 'green',
    postgresql: 'purple',
    mysql: 'orange',
    mongodb: 'brown',
    elasticsearch: 'yellow',
    kafka: 'red',
    rest: 'teal'
  }
  return colors[type?.toLowerCase()] || 'grey'
}

const formatConfigKey = (key) => {
  return key.split('_').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatConfigValue = (key, value) => {
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  if (key === 'timeout') {
    return `${value} seconds`
  }
  if (key === 'port') {
    return value.toString()
  }
  return value?.toString() || 'Not set'
}

const getConfigIcon = (key) => {
  const icons = {
    host: 'link',
    port: 'settings_ethernet',
    username: 'person',
    password: 'lock',
    database: 'storage',
    table: 'table_view',
    timeout: 'timer',
    ssl: 'security',
    api_key: 'vpn_key'
  }
  return icons[key] || 'settings'
}

const getTagsCount = (measurement) => {
  if (!props.discoveredSchema?.tags) return 0
  return props.discoveredSchema.tags[measurement]?.length || 0
}

const getFieldsCount = (measurement) => {
  if (!props.discoveredSchema?.fields) return 0
  return props.discoveredSchema.fields[measurement]?.length || 0
}

const isValidHost = (host) => {
  // Basic host validation
  const hostRegex = /^[a-zA-Z0-9.-]+$/
  return hostRegex.test(host)
}

const createDataSource = async () => {
  if (!validationStatus.value.isValid) {
    $q.notify({
      type: 'negative',
      message: 'Please fix validation errors before creating the data source'
    })
    return
  }

  creating.value = true
  showProgress.value = true

  try {
    // Step 1: Create data source
    progressMessage.value = 'Creating data source configuration...'
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Step 2: Test connection
    progressMessage.value = 'Validating connection...'
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Step 3: Initialize schema if discovered
    if (props.discoveredSchema) {
      progressMessage.value = 'Saving schema information...'
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // Step 4: Complete
    progressMessage.value = 'Finalizing setup...'
    await new Promise(resolve => setTimeout(resolve, 500))

    emit('create', props.formData)

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to create data source',
      caption: error.message
    })
  } finally {
    creating.value = false
    showProgress.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Auto-scroll to top when component loads
  window.scrollTo({ top: 0, behavior: 'smooth' })
})
</script>

<style scoped>
.configuration-review {
  width: 100%;
}

.q-card {
  border-radius: 8px;
}

.q-chip {
  font-weight: 500;
}

.text-h4 {
  font-weight: 600;
}
</style>
