<!-- ui/src/components/DataSourceWizard.vue -->
<template>
  <q-dialog v-model="show" persistent maximized>
    <q-card>
      <!-- Header -->
      <q-card-section class="bg-primary text-white">
        <div class="row items-center">
          <div class="col">
            <div class="text-h6">Create New Data Source</div>
            <div class="text-subtitle2">Step {{ currentStep }} of {{ totalSteps }}</div>
          </div>
          <div class="col-auto">
            <q-btn icon="close" flat round @click="cancelWizard" />
          </div>
        </div>
      </q-card-section>

      <!-- Progress -->
      <q-linear-progress
        :value="progress"
        color="primary"
        size="4px"
        class="q-mb-none"
      />

      <!-- Wizard Content -->
      <q-card-section class="q-pa-none">
        <div class="row no-wrap" style="height: calc(100vh - 200px);">
          <!-- Steps Sidebar -->
          <div class="col-auto bg-grey-1 q-pa-md" style="min-width: 250px;">
            <q-list>
              <q-item
                v-for="(step, index) in steps"
                :key="index"
                :class="getStepClass(index + 1)"
                clickable
                @click="goToStep(index + 1)"
                :disable="!canNavigateToStep(index + 1)"
              >
                <q-item-section avatar>
                  <q-avatar
                    :color="getStepAvatarColor(index + 1)"
                    text-color="white"
                    size="sm"
                  >
                    <q-icon
                      :name="getStepIcon(index + 1)"
                      size="sm"
                    />
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ step.title }}</q-item-label>
                  <q-item-label caption>{{ step.description }}</q-item-label>
                </q-item-section>

                <q-item-section side v-if="isStepCompleted(index + 1)">
                  <q-icon name="check_circle" color="positive" />
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Main Content -->
          <div class="col q-pa-lg">
            <!-- Step 1: Source Type Selection -->
            <div v-if="currentStep === 1">
              <div class="text-h5 q-mb-md">Choose Data Source Type</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Select the type of data source you want to connect to your asset monitoring system.
              </div>

              <div class="row q-gutter-lg">
                <q-card
                  v-for="sourceType in sourceTypes"
                  :key="sourceType.value"
                  class="col-12 col-md-5 cursor-pointer source-type-card"
                  :class="formData.source_type === sourceType.value ? 'selected' : ''"
                  @click="selectSourceType(sourceType.value)"
                >
                  <q-card-section class="text-center q-pa-xl">
                    <q-avatar :color="sourceType.color" text-color="white" size="4rem" class="q-mb-md">
                      <q-icon :name="sourceType.icon" size="2rem" />
                    </q-avatar>

                    <div class="text-h6 q-mb-sm">{{ sourceType.label }}</div>
                    <div class="text-body2 text-grey-6 q-mb-md">{{ sourceType.description }}</div>

                    <q-chip
                      :color="sourceType.color"
                      text-color="white"
                      size="sm"
                    >
                      {{ sourceType.category }}
                    </q-chip>
                  </q-card-section>

                  <q-card-section v-if="sourceType.features" class="q-pt-none">
                    <div class="text-subtitle2 q-mb-sm">Key Features:</div>
                    <q-list dense>
                      <q-item v-for="feature in sourceType.features" :key="feature" class="q-pa-none">
                        <q-item-section avatar class="q-pr-sm">
                          <q-icon name="check" color="positive" size="xs" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label caption>{{ feature }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- Step 2: Basic Information -->
            <div v-if="currentStep === 2">
              <div class="text-h5 q-mb-md">Basic Information</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Provide basic details about your {{ getSelectedSourceTypeLabel() }} data source.
              </div>

              <div class="row q-gutter-md">
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="formData.source_name"
                    label="Data Source Name *"
                    hint="A descriptive name for your data source"
                    outlined
                    :rules="[val => !!val || 'Name is required']"
                  />
                </div>

                <div class="col-12 col-md-6">
                  <q-input
                    v-model="formData.description"
                    label="Description"
                    hint="Optional description of this data source"
                    outlined
                  />
                </div>

                <div class="col-12">
                  <q-select
                    v-model="formData.environment"
                    :options="environmentOptions"
                    label="Environment"
                    hint="Select the environment type"
                    outlined
                    emit-value
                    map-options
                  />
                </div>

                <div class="col-12">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-subtitle2 q-mb-sm">Selected Source Type</div>
                      <div class="row items-center q-gutter-md">
                        <q-avatar
                          :color="getSelectedSourceType()?.color"
                          text-color="white"
                          size="md"
                        >
                          <q-icon :name="getSelectedSourceType()?.icon" />
                        </q-avatar>
                        <div>
                          <div class="text-body1">{{ getSelectedSourceType()?.label }}</div>
                          <div class="text-caption text-grey-6">{{ getSelectedSourceType()?.description }}</div>
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Step 3: Connection Configuration -->
            <div v-if="currentStep === 3">
              <div class="text-h5 q-mb-md">Connection Configuration</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Configure the connection parameters for your {{ getSelectedSourceTypeLabel() }} data source.
              </div>

              <!-- InfluxDB Configuration -->
              <div v-if="formData.source_type === 'influxdb'">
                <InfluxDBConfig
                  v-model="formData.connection_config"
                  @test-connection="testConnection"
                  :testing="testingConnection"
                  :connection-status="connectionStatus"
                />
              </div>

              <!-- Parquet Configuration -->
              <div v-if="formData.source_type === 'parquet'">
                <ParquetConfig
                  v-model="formData.connection_config"
                  @test-connection="testConnection"
                  :testing="testingConnection"
                  :connection-status="connectionStatus"
                />
              </div>

              <!-- Connection Status -->
              <q-card v-if="connectionStatus" class="q-mt-md" flat bordered>
                <q-card-section>
                  <div class="row items-center">
                    <q-icon
                      :name="connectionStatus.success ? 'check_circle' : 'error'"
                      :color="connectionStatus.success ? 'positive' : 'negative'"
                      size="sm"
                      class="q-mr-sm"
                    />
                    <div class="col">
                      <div class="text-body1">{{ connectionStatus.message }}</div>
                      <div v-if="connectionStatus.details" class="text-caption text-grey-6">
                        {{ connectionStatus.details }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Step 4: Schema Discovery -->
            <div v-if="currentStep === 4">
              <div class="text-h5 q-mb-md">Discover Schema</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Discover available measurements and data structure from your data source.
              </div>

              <div v-if="!discoveredSchema.measurements.length">
                <q-card flat bordered class="text-center q-pa-xl">
                  <q-icon name="search" size="3rem" class="text-grey-4 q-mb-md" />
                  <div class="text-h6 text-grey-6 q-mb-sm">Discover Your Data</div>
                  <div class="text-body2 text-grey-5 q-mb-lg">
                    Click the button below to discover measurements and schema from your data source.
                  </div>
                  <q-btn
                    label="Discover Schema"
                    icon="search"
                    color="primary"
                    size="lg"
                    @click="discoverSchema"
                    :loading="discoveringSchema"
                  />
                </q-card>
              </div>

              <div v-else>
                <SchemaPreview
                  :schema="discoveredSchema"
                  @refresh="discoverSchema"
                  :loading="discoveringSchema"
                />
              </div>
            </div>

            <!-- Step 5: Review and Create -->
            <div v-if="currentStep === 5">
              <div class="text-h5 q-mb-md">Review and Create</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Review your configuration and create the data source.
              </div>

              <ConfigurationReview
                :form-data="formData"
                :discovered-schema="discoveredSchema"
                :connection-status="connectionStatus"
              />
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Actions -->
      <q-separator />
      <q-card-actions class="q-pa-md">
        <q-btn
          label="Cancel"
          flat
          @click="cancelWizard"
        />

        <q-space />

        <q-btn
          v-if="currentStep > 1"
          label="Previous"
          flat
          @click="previousStep"
        />

        <q-btn
          v-if="currentStep < totalSteps"
          label="Next"
          color="primary"
          @click="nextStep"
          :disable="!canProceedToNext"
        />

        <q-btn
          v-if="currentStep === totalSteps"
          label="Create Data Source"
          color="positive"
          @click="createDataSource"
          :loading="creatingDataSource"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import sub-components
import InfluxDBConfig from 'src/components/InfluxDBConfig.vue'
import ParquetConfig from 'src/components/ParquetConfig.vue'
import SchemaPreview from 'src/components/SchemaPreview.vue'
import ConfigurationReview from 'src/components/ConfigurationReview.vue'

// Props
const props = defineProps({
  modelValue: Boolean,
  equipments: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'source-created'])

// Reactive data
const $q = useQuasar()
const currentStep = ref(1)
const totalSteps = 5

// Form data
const formData = ref({
  source_name: '',
  source_type: '',
  description: '',
  environment: 'production',
  connection_config: {}
})

// States
const testingConnection = ref(false)
const discoveringSchema = ref(false)
const creatingDataSource = ref(false)
const connectionStatus = ref(null)
const discoveredSchema = ref({
  measurements: [],
  tags: {},
  fields: {}
})

// Configuration
const sourceTypes = [
  {
    value: 'influxdb',
    label: 'InfluxDB',
    description: 'Time-series database optimized for IoT and monitoring data',
    icon: 'timeline',
    color: 'deep-purple',
    category: 'Time Series',
    features: [
      'High-performance time-series data',
      'Built-in data retention policies',
      'Flexible querying with InfluxQL',
      'Real-time data ingestion'
    ]
  },
  {
    value: 'parquet',
    label: 'Parquet Files',
    description: 'Columnar storage format for efficient data analytics',
    icon: 'folder_special',
    color: 'blue-grey',
    category: 'File-based',
    features: [
      'Efficient columnar storage',
      'Schema evolution support',
      'Compression and encoding',
      'Cross-platform compatibility'
    ]
  }
]

const environmentOptions = [
  { label: 'Production', value: 'production' },
  { label: 'Staging', value: 'staging' },
  { label: 'Development', value: 'development' },
  { label: 'Testing', value: 'testing' }
]

const steps = [
  {
    title: 'Source Type',
    description: 'Choose data source type'
  },
  {
    title: 'Basic Info',
    description: 'Name and description'
  },
  {
    title: 'Connection',
    description: 'Configure connection'
  },
  {
    title: 'Schema',
    description: 'Discover data structure'
  },
  {
    title: 'Review',
    description: 'Confirm and create'
  }
]

// Computed properties
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const progress = computed(() => currentStep.value / totalSteps)

const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!formData.value.source_type
    case 2:
      return !!formData.value.source_name
    case 3:
      return connectionStatus.value?.success === true
    case 4:
      return discoveredSchema.value.measurements.length > 0
    default:
      return true
  }
})

// Methods
const selectSourceType = (type) => {
  formData.value.source_type = type
  formData.value.connection_config = {}
  connectionStatus.value = null
}

const getSelectedSourceType = () => {
  return sourceTypes.find(type => type.value === formData.value.source_type)
}

const getSelectedSourceTypeLabel = () => {
  return getSelectedSourceType()?.label || 'Unknown'
}

const testConnection = async () => {
  testingConnection.value = true
  connectionStatus.value = null

  try {
    const response = await axios.post('http://localhost:8000/datasources/test-connection', {
      source_type: formData.value.source_type,
      connection_config: formData.value.connection_config
    })

    connectionStatus.value = response.data

    $q.notify({
      type: response.data.success ? 'positive' : 'negative',
      message: response.data.message,
      icon: response.data.success ? 'check_circle' : 'error'
    })
  } catch (error) {
    connectionStatus.value = {
      success: false,
      message: 'Connection test failed',
      details: error.response?.data?.detail || error.message
    }

    $q.notify({
      type: 'negative',
      message: 'Connection test failed',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    testingConnection.value = false
  }
}

const discoverSchema = async () => {
  discoveringSchema.value = true

  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/measurements', {
      source_type: formData.value.source_type,
      connection_config: formData.value.connection_config
    })

    discoveredSchema.value = {
      measurements: response.data.measurements || [],
      tags: {},
      fields: {}
    }

    $q.notify({
      type: 'positive',
      message: `Discovered ${response.data.measurements?.length || 0} measurements`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Schema discovery failed',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discoveringSchema.value = false
  }
}

const createDataSource = async () => {
  creatingDataSource.value = true

  try {
    const payload = {
      source_name: formData.value.source_name,
      source_type: formData.value.source_type,
      connection_config: formData.value.connection_config
    }

    const response = await axios.post('http://localhost:8000/datasources/', payload)

    $q.notify({
      type: 'positive',
      message: 'Data source created successfully',
      icon: 'check_circle'
    })

    emit('source-created', response.data)
    resetWizard()
    show.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to create data source',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    creatingDataSource.value = false
  }
}

// Navigation
const nextStep = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const goToStep = (step) => {
  if (canNavigateToStep(step)) {
    currentStep.value = step
  }
}

const canNavigateToStep = (step) => {
  // Allow navigation to completed steps or current step
  return step <= currentStep.value || isStepCompleted(step - 1)
}

const isStepCompleted = (step) => {
  switch (step) {
    case 1:
      return !!formData.value.source_type
    case 2:
      return !!formData.value.source_name
    case 3:
      return connectionStatus.value?.success === true
    case 4:
      return discoveredSchema.value.measurements.length > 0
    default:
      return false
  }
}

// Step styling
const getStepClass = (step) => {
  if (step === currentStep.value) return 'text-primary bg-blue-1'
  if (isStepCompleted(step)) return 'text-positive'
  return 'text-grey-6'
}

const getStepAvatarColor = (step) => {
  if (step === currentStep.value) return 'primary'
  if (isStepCompleted(step)) return 'positive'
  return 'grey-5'
}

const getStepIcon = (step) => {
  if (isStepCompleted(step)) return 'check'
  return steps[step - 1]?.icon || 'circle'
}

// Wizard lifecycle
const resetWizard = () => {
  currentStep.value = 1
  formData.value = {
    source_name: '',
    source_type: '',
    description: '',
    environment: 'production',
    connection_config: {}
  }
  connectionStatus.value = null
  discoveredSchema.value = {
    measurements: [],
    tags: {},
    fields: {}
  }
}

const cancelWizard = () => {
  $q.dialog({
    title: 'Cancel Wizard',
    message: 'Are you sure you want to cancel? All progress will be lost.',
    cancel: true,
    persistent: true
  }).onOk(() => {
    resetWizard()
    show.value = false
  })
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetWizard()
  }
})
</script>

<style scoped>
.source-type-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.source-type-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.source-type-card.selected {
  border-color: var(--q-primary);
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.3);
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.q-card {
  border-radius: 12px;
}

.q-stepper {
  box-shadow: none;
}
</style>
