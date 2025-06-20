<!-- ui/src/components/ParquetConfig.vue -->
<template>
  <div class="parquet-config">
    <q-form @submit.prevent="testConnection">
      <div class="row q-gutter-md">
        <!-- Base Path -->
        <div class="col-12">
          <q-input
            v-model="config.base_path"
            label="Base Path *"
            hint="Root directory containing parquet files"
            outlined
            :rules="[val => !!val || 'Base path is required']"
          >
            <template #prepend>
              <q-icon name="folder_open" />
            </template>
            <template #append>
              <q-btn
                icon="folder"
                flat
                round
                @click="showPathDialog = true"
                title="Browse for folder"
              />
            </template>
          </q-input>
        </div>

        <!-- Path Pattern -->
        <div class="col-12">
          <q-input
            v-model="config.path_pattern"
            label="File Pattern *"
            hint="Pattern to match parquet files (e.g., **/*.parquet)"
            outlined
            :rules="[val => !!val || 'File pattern is required']"
          >
            <template #prepend>
              <q-icon name="pattern" />
            </template>
          </q-input>
        </div>

        <!-- Common Patterns -->
        <div class="col-12">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-subtitle2 q-mb-md">Common File Patterns</div>
              <div class="row q-gutter-xs">
                <q-chip
                  v-for="pattern in commonPatterns"
                  :key="pattern.value"
                  :label="pattern.label"
                  clickable
                  outline
                  color="primary"
                  @click="config.path_pattern = pattern.value"
                />
              </div>
            </q-card-section>
          </q-card>
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
                <!-- Date Column -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="config.date_column"
                    label="Date Column"
                    hint="Column name containing timestamps"
                    outlined
                  >
                    <template #prepend>
                      <q-icon name="access_time" />
                    </template>
                  </q-input>
                </div>

                <!-- Date Format -->
                <div class="col-12 col-md-6">
                  <q-select
                    v-model="config.date_format"
                    :options="dateFormatOptions"
                    label="Date Format"
                    hint="Expected date format in files"
                    outlined
                    emit-value
                    map-options
                  >
                    <template #prepend>
                      <q-icon name="event" />
                    </template>
                  </q-select>
                </div>

                <!-- Partition Columns -->
                <div class="col-12">
                  <q-select
                    v-model="config.partition_columns"
                    label="Partition Columns"
                    hint="Columns used for partitioning (optional)"
                    outlined
                    multiple
                    use-chips
                    use-input
                    @new-value="addPartitionColumn"
                  >
                    <template #prepend>
                      <q-icon name="view_column" />
                    </template>
                  </q-select>
                </div>

                <!-- Max Files to Scan -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model.number="config.max_files_scan"
                    label="Max Files to Scan"
                    hint="Limit for schema discovery"
                    type="number"
                    outlined
                    :min="1"
                    :max="1000"
                  >
                    <template #prepend>
                      <q-icon name="speed" />
                    </template>
                  </q-input>
                </div>

                <!-- Memory Limit -->
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="config.memory_limit"
                    label="Memory Limit (MB)"
                    hint="Memory limit for processing"
                    type="number"
                    outlined
                    :min="100"
                    :max="8192"
                  >
                    <template #prepend>
                      <q-icon name="memory" />
                    </template>
                  </q-input>
                </div>

                <!-- Use Pandas -->
                <div class="col-12">
                  <q-toggle
                    v-model="config.use_pandas"
                    label="Use Pandas Engine"
                    color="primary"
                  />
                  <div class="text-caption text-grey-6 q-mt-xs">
                    Use pandas for better compatibility (slower for large files)
                  </div>
                </div>

                <!-- Cache Schema -->
                <div class="col-12">
                  <q-toggle
                    v-model="config.cache_schema"
                    label="Cache Schema"
                    color="primary"
                  />
                  <div class="text-caption text-grey-6 q-mt-xs">
                    Cache discovered schema for faster subsequent access
                  </div>
                </div>
              </div>
            </div>
          </q-expansion-item>
        </div>

        <!-- File Structure Preview -->
        <div class="col-12" v-if="config.base_path">
          <q-card flat bordered>
            <q-card-section>
              <div class="row items-center justify-between">
                <div class="text-subtitle2">Expected File Structure</div>
                <q-btn
                  label="Scan Files"
                  icon="search"
                  size="sm"
                  color="secondary"
                  outline
                  @click="scanFiles"
                  :loading="scanningFiles"
                />
              </div>

              <div class="q-mt-md">
                <div class="text-body2 text-grey-7 q-mb-sm">
                  Pattern: <code>{{ config.base_path }}/{{ config.path_pattern }}</code>
                </div>

                <div v-if="scannedFiles.length > 0">
                  <div class="text-caption text-positive q-mb-xs">
                    Found {{ scannedFiles.length }} matching files:
                  </div>
                  <q-list dense bordered>
                    <q-item v-for="(file, index) in previewFiles" :key="index">
                      <q-item-section avatar>
                        <q-icon name="insert_drive_file" color="blue-grey" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-body2">{{ file.name }}</q-item-label>
                        <q-item-label caption>{{ file.size }} • {{ file.modified }}</q-item-label>
                      </q-item-section>
                    </q-item>

                    <q-item v-if="scannedFiles.length > 3">
                      <q-item-section class="text-center text-grey-6">
                        ... and {{ scannedFiles.length - 3 }} more files
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <div v-else-if="scanningFiles">
                  <q-linear-progress indeterminate color="primary" />
                  <div class="text-center text-grey-6 q-mt-sm">Scanning files...</div>
                </div>
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
                    <q-icon name="folder_open" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Base Path</q-item-label>
                    <q-item-label>{{ config.base_path }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="pattern" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Pattern</q-item-label>
                    <q-item-label>{{ config.path_pattern }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="connectionStatus.details?.files_count">
                  <q-item-section avatar>
                    <q-icon name="description" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Files Found</q-item-label>
                    <q-item-label>{{ connectionStatus.details.files_count }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-form>

    <!-- Path Browser Dialog -->
    <q-dialog v-model="showPathDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Select Base Path</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="tempPath"
            label="Enter path manually"
            outlined
            autofocus
          />

          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Common Paths:</div>
            <q-list dense>
              <q-item
                v-for="path in commonPaths"
                :key="path"
                clickable
                @click="tempPath = path"
              >
                <q-item-section avatar>
                  <q-icon name="folder" />
                </q-item-section>
                <q-item-section>{{ path }}</q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancel" flat @click="showPathDialog = false" />
          <q-btn
            label="Select"
            color="primary"
            @click="selectPath"
            :disable="!tempPath"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  modelValue: Object,
  testing: Boolean,
  connectionStatus: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'test-connection'])

// Reactive data
const showPathDialog = ref(false)
const tempPath = ref('')
const scanningFiles = ref(false)
const scannedFiles = ref([])

// Default configuration
const defaultConfig = {
  base_path: '',
  path_pattern: '**/*.parquet',
  date_column: 'timestamp',
  date_format: 'auto',
  partition_columns: [],
  max_files_scan: 100,
  memory_limit: 1024,
  use_pandas: false,
  cache_schema: true
}

// Configuration object
const config = computed({
  get: () => ({ ...defaultConfig, ...props.modelValue }),
  set: (value) => emit('update:modelValue', value)
})

// Options
const commonPatterns = [
  { label: 'All Parquet (*.parquet)', value: '*.parquet' },
  { label: 'Recursive Parquet (**/*.parquet)', value: '**/*.parquet' },
  { label: 'Daily Files (YYYY/MM/DD/*.parquet)', value: 'year=*/month=*/day=*/*.parquet' },
  { label: 'Hourly Files (**/hour=*/*.parquet)', value: '**/hour=*/*.parquet' },
  { label: 'All Extensions (*.*)', value: '*.*' }
]

const dateFormatOptions = [
  { label: 'Auto-detect', value: 'auto' },
  { label: 'ISO 8601 (YYYY-MM-DD HH:MM:SS)', value: '%Y-%m-%d %H:%M:%S' },
  { label: 'Unix Timestamp', value: 'unix' },
  { label: 'Date Only (YYYY-MM-DD)', value: '%Y-%m-%d' },
  { label: 'Custom Format', value: 'custom' }
]

const commonPaths = [
  'D:\\Asset Monitoring System\\Data-Backup',
  'C:\\Data\\Parquet',
  '/data/parquet',
  './data',
  '../data/parquet'
]

// Computed properties
const isFormValid = computed(() => {
  return config.value.base_path && config.value.path_pattern
})

const previewFiles = computed(() => {
  return scannedFiles.value.slice(0, 3)
})

// Methods
const testConnection = () => {
  emit('test-connection')
}

const addPartitionColumn = (val, done) => {
  if (val && val.trim()) {
    const columns = config.value.partition_columns || []
    if (!columns.includes(val.trim())) {
      columns.push(val.trim())
      config.value = { ...config.value, partition_columns: columns }
    }
    done(val.trim(), 'add-unique')
  }
}

const selectPath = () => {
  config.value = { ...config.value, base_path: tempPath.value }
  showPathDialog.value = false
  tempPath.value = ''
}

const scanFiles = async () => {
  scanningFiles.value = true
  scannedFiles.value = []

  try {
    // Simulate file scanning (in real implementation, this would call a backend API)
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Mock file data
    scannedFiles.value = [
      {
        name: 'equipment_data_2024_01.parquet',
        size: '2.3 MB',
        modified: '2024-01-15'
      },
      {
        name: 'equipment_data_2024_02.parquet',
        size: '2.1 MB',
        modified: '2024-02-15'
      },
      {
        name: 'equipment_data_2024_03.parquet',
        size: '2.5 MB',
        modified: '2024-03-15'
      },
      {
        name: 'equipment_data_2024_04.parquet',
        size: '2.2 MB',
        modified: '2024-04-15'
      }
    ]
  } catch (error) {
    console.error('File scanning error:', error)
  } finally {
    scanningFiles.value = false
  }
}

const getConnectionDetails = () => {
  if (!props.connectionStatus?.details) return ''

  if (typeof props.connectionStatus.details === 'string') {
    return props.connectionStatus.details
  }

  const details = props.connectionStatus.details
  const parts = []

  if (details.files_count) {
    parts.push(`${details.files_count} files found`)
  }

  if (details.total_size) {
    parts.push(`Total size: ${details.total_size}`)
  }

  if (details.columns) {
    parts.push(`${details.columns} columns detected`)
  }

  return parts.join(' • ') || 'Connection established successfully'
}

// Update parent when config changes
watch(config, (newConfig) => {
  emit('update:modelValue', newConfig)
}, { deep: true })

// Auto-scan files when path changes
watch(() => config.value.base_path, (newPath) => {
  if (newPath && newPath.trim()) {
    // Auto-scan after a short delay
    setTimeout(() => {
      if (config.value.base_path === newPath) {
        scanFiles()
      }
    }, 500)
  }
})
</script>

<style scoped>
.parquet-config {
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

code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.q-chip {
  margin: 2px;
}
</style>
