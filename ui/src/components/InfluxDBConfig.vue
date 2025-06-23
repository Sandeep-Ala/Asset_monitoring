<!-- src/components/InfluxDBConfig.vue - Fixed input reset issue -->
<template>
  <div class="influxdb-config">
    <q-form @submit.prevent="testConnection">
      <div class="row q-gutter-md">
        <!-- Server URL -->
        <div class="col-12">
          <q-input
            v-model="localConfig.url"
            label="InfluxDB Server URL *"
            hint="e.g., http://localhost:8086 or https://your-influxdb.com"
            outlined
            :rules="urlRules"
          >
            <template #prepend>
              <q-icon name="language" />
            </template>
          </q-input>
        </div>

        <!-- Organization -->
        <div class="col-12 col-md-6">
          <q-input
            v-model="localConfig.org"
            label="Organization *"
            hint="Your InfluxDB organization name"
            outlined
            :rules="[val => !!val || 'Organization is required']"
          >
            <template #prepend>
              <q-icon name="business" />
            </template>
          </q-input>
        </div>

        <!-- Bucket -->
        <div class="col-12 col-md-6">
          <q-input
            v-model="localConfig.bucket"
            label="Bucket *"
            hint="The bucket containing your data"
            outlined
            :rules="[val => !!val || 'Bucket is required']"
          >
            <template #prepend>
              <q-icon name="folder" />
            </template>
          </q-input>
        </div>

        <!-- Token -->
        <div class="col-12">
          <q-input
            v-model="localConfig.token"
            :label="tokenLabel"
            hint="Your InfluxDB authentication token"
            outlined
            :type="showToken ? 'text' : 'password'"
            :rules="[val => !!val || 'Token is required']"
          >
            <template #prepend>
              <q-icon name="vpn_key" />
            </template>
            <template #append>
              <q-btn
                :icon="showToken ? 'visibility_off' : 'visibility'"
                flat
                round
                @click="showToken = !showToken"
              />
            </template>
          </q-input>
        </div>

        <!-- Advanced Options -->
        <div class="col-12">
          <q-expansion-item
            icon="settings"
            label="Advanced Options"
            dense
          >
            <div class="q-pa-md bg-grey-1">
              <div class="row q-gutter-md">
                <!-- Timeout -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model.number="localConfig.timeout"
                    label="Timeout (seconds)"
                    hint="Connection timeout in seconds"
                    type="number"
                    outlined
                    :min="5"
                    :max="300"
                  >
                    <template #prepend>
                      <q-icon name="timer" />
                    </template>
                  </q-input>
                </div>

                <!-- SSL Verification -->
                <div class="col-12 col-md-6">
                  <q-toggle
                    v-model="localConfig.verify_ssl"
                    label="Verify SSL Certificate"
                    color="primary"
                  />
                  <div class="text-caption text-grey-6 q-mt-xs">
                    Uncheck for self-signed certificates
                  </div>
                </div>

                <!-- Default Measurement -->
                <div class="col-12">
                  <q-input
                    v-model="localConfig.default_measurement"
                    label="Default Measurement"
                    hint="Optional: Default measurement for queries"
                    outlined
                  >
                    <template #prepend>
                      <q-icon name="analytics" />
                    </template>
                  </q-input>
                </div>
              </div>
            </div>
          </q-expansion-item>
        </div>

        <!-- Quick Setup Templates -->
        <div class="col-12">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-subtitle2 q-mb-md">Quick Setup Templates</div>
              <div class="row q-gutter-sm">
                <q-btn
                  v-for="template in templates"
                  :key="template.name"
                  :label="template.name"
                  outline
                  size="sm"
                  @click="applyTemplate(template)"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Test Connection Button -->
        <div class="col-12">
          <q-btn
            label="Test Connection"
            icon="wifi_find"
            color="primary"
            size="lg"
            @click="testConnection"
            :loading="testing"
            :disable="!isFormValid"
            class="full-width"
          />
        </div>

        <!-- Connection Status -->
        <div v-if="connectionStatus" class="col-12">
          <q-card
            flat
            bordered
            :class="connectionStatus.success ? 'bg-green-1' : 'bg-red-1'"
          >
            <q-card-section>
              <div class="row items-center">
                <q-icon
                  :name="connectionStatus.success ? 'check_circle' : 'error'"
                  :color="connectionStatus.success ? 'positive' : 'negative'"
                  size="md"
                  class="q-mr-md"
                />
                <div class="col">
                  <div class="text-h6">{{ connectionStatus.message }}</div>
                  <div v-if="connectionStatus.details" class="text-body2 text-grey-7">
                    {{ getConnectionDetails() }}
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Connection Info -->
        <div v-if="connectionStatus?.success" class="col-12">
          <q-card flat bordered class="bg-blue-1">
            <q-card-section>
              <div class="text-subtitle2 q-mb-sm">Connection Information</div>
              <q-list dense>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="language" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Server</q-item-label>
                    <q-item-label>{{ localConfig.url }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="business" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Organization</q-item-label>
                    <q-item-label>{{ localConfig.org }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="folder" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Bucket</q-item-label>
                    <q-item-label>{{ localConfig.bucket }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

// Props
const props = defineProps({
  modelValue: Object,
  testing: Boolean,
  connectionStatus: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'test-connection'])

// Reactive data
const showToken = ref(false)

// Default configuration
const defaultConfig = {
  url: 'http://localhost:8086',
  org: '',
  bucket: '',
  token: '',
  timeout: 30,
  verify_ssl: true,
  default_measurement: ''
}

// FIXED: Use a reactive ref instead of computed to prevent input reset
const localConfig = ref({ ...defaultConfig })

// Quick setup templates
const templates = [
  {
    name: 'Local Development',
    config: {
      url: 'http://localhost:8086',
      timeout: 30,
      verify_ssl: false
    }
  },
  {
    name: 'InfluxDB Cloud',
    config: {
      url: 'https://us-west-2-1.aws.cloud2.influxdata.com',
      timeout: 60,
      verify_ssl: true
    }
  },
  {
    name: 'Docker Container',
    config: {
      url: 'http://influxdb:8086',
      timeout: 30,
      verify_ssl: false
    }
  }
]

// Validation rules
const urlRules = [
  val => !!val || 'URL is required',
  val => {
    try {
      new URL(val)
      return true
    } catch {
      return 'Please enter a valid URL'
    }
  }
]

// Computed properties
const tokenLabel = computed(() => {
  return localConfig.value.token ? 'Authentication Token *' : 'Authentication Token * (Required)'
})

const isFormValid = computed(() => {
  return localConfig.value.url &&
         localConfig.value.org &&
         localConfig.value.bucket &&
         localConfig.value.token
})

// Methods
const testConnection = () => {
  emit('test-connection')
}

const applyTemplate = (template) => {
  // FIXED: Update the local config properly
  Object.assign(localConfig.value, template.config)
}

const getConnectionDetails = () => {
  if (!props.connectionStatus?.details) return ''

  if (typeof props.connectionStatus.details === 'string') {
    return props.connectionStatus.details
  }

  if (props.connectionStatus.details.server_version) {
    return `Server Version: ${props.connectionStatus.details.server_version}`
  }

  return 'Connection established successfully'
}

// FIXED: Watch localConfig and emit changes to parent
watch(localConfig, (newConfig) => {
  emit('update:modelValue', { ...newConfig })
}, { deep: true })

// FIXED: Watch for changes from parent and update local config
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    // Only update if there are actual differences to prevent infinite loops
    const hasChanges = Object.keys(newValue).some(key =>
      newValue[key] !== localConfig.value[key]
    )

    if (hasChanges) {
      localConfig.value = { ...defaultConfig, ...newValue }
    }
  }
}, { deep: true })

// FIXED: Initialize local config on mount
onMounted(() => {
  if (props.modelValue) {
    localConfig.value = { ...defaultConfig, ...props.modelValue }
  }
})
</script>

<style scoped>
.influxdb-config {
  max-width: 100%;
}

.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.05);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-red-1 {
  background-color: rgba(244, 67, 54, 0.1);
}

.q-card {
  border-radius: 8px;
}
</style>
