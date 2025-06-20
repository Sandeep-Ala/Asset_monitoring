<!-- ui/src/components/SchemaExplorer.vue -->
<template>
  <q-dialog v-model="show" maximized>
    <q-card>
      <!-- Header -->
      <q-card-section class="bg-primary text-white">
        <div class="row items-center">
          <div class="col">
            <div class="text-h6">Schema Explorer</div>
            <div class="text-subtitle2">{{ source?.source_name }} • {{ source?.source_type?.toUpperCase() }}</div>
          </div>
          <div class="col-auto">
            <q-btn icon="close" flat round @click="show = false" />
          </div>
        </div>
      </q-card-section>

      <!-- Progress -->
      <q-linear-progress
        v-if="discovering"
        indeterminate
        color="primary"
        size="4px"
      />

      <!-- Main Content -->
      <q-card-section class="q-pa-none">
        <div class="row no-wrap" style="height: calc(100vh - 120px);">
          <!-- Sidebar - Measurements -->
          <div class="col-auto bg-grey-1" style="min-width: 300px; max-width: 400px;">
            <div class="q-pa-md">
              <div class="row items-center justify-between q-mb-md">
                <div class="text-h6">Measurements</div>
                <q-btn
                  icon="refresh"
                  flat
                  round
                  size="sm"
                  @click="discoverMeasurements"
                  :loading="discovering"
                />
              </div>

              <!-- Search -->
              <q-input
                v-model="searchQuery"
                placeholder="Search measurements..."
                dense
                clearable
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="search" />
                </template>
              </q-input>

              <!-- Measurements List -->
              <q-list separator v-if="filteredMeasurements.length > 0">
                <q-item
                  v-for="measurement in filteredMeasurements"
                  :key="measurement"
                  clickable
                  :class="selectedMeasurement === measurement ? 'bg-blue-1' : ''"
                  @click="selectMeasurement(measurement)"
                >
                  <q-item-section avatar>
                    <q-avatar color="primary" text-color="white" size="sm">
                      <q-icon name="table_chart" />
                    </q-avatar>
                  </q-item-section>

                  <q-item-section>
                    <q-item-label>{{ measurement }}</q-item-label>
                    <q-item-label caption v-if="measurementStats[measurement]">
                      {{ measurementStats[measurement].fields || 0 }} fields •
                      {{ measurementStats[measurement].tags || 0 }} tags
                    </q-item-label>
                  </q-item-section>

                  <q-item-section side>
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click.stop="previewMeasurement(measurement)"
                    />
                  </q-item-section>
                </q-item>
              </q-list>

              <!-- Empty State -->
              <div v-else-if="!discovering" class="text-center q-pa-lg text-grey-6">
                <q-icon name="search" size="3rem" class="q-mb-md" />
                <div class="text-h6">No Measurements</div>
                <div class="text-body2">
                  {{ searchQuery ? 'No matching measurements found' : 'Click refresh to discover measurements' }}
                </div>
              </div>

              <!-- Loading State -->
              <div v-if="discovering" class="text-center q-pa-lg">
                <q-spinner-dots size="2rem" color="primary" />
                <div class="text-body2 q-mt-md">Discovering measurements...</div>
              </div>
            </div>
          </div>

          <!-- Main Content -->
          <div class="col">
            <div v-if="selectedMeasurement" class="q-pa-md">
              <!-- Measurement Header -->
              <div class="row items-center justify-between q-mb-lg">
                <div>
                  <div class="text-h5">{{ selectedMeasurement }}</div>
                  <div class="text-subtitle1 text-grey-6">Measurement Schema and Data Preview</div>
                </div>
                <div class="row q-gutter-sm">
                  <q-btn
                    label="Discover Tags"
                    icon="label"
                    color="blue"
                    outline
                    @click="discoverTags"
                    :loading="discoveringTags"
                  />
                  <q-btn
                    label="Discover Fields"
                    icon="insights"
                    color="green"
                    outline
                    @click="discoverFields"
                    :loading="discoveringFields"
                  />
                  <q-btn
                    label="Get Sample Data"
                    icon="preview"
                    color="orange"
                    outline
                    @click="getSampleData"
                    :loading="loadingSample"
                  />
                </div>
              </div>

              <!-- Tabs -->
              <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
                <q-tab name="overview" label="Overview" icon="dashboard" />
                <q-tab name="tags" label="Tags" icon="label" :disable="!discoveredTags.length" />
                <q-tab name="fields" label="Fields" icon="insights" :disable="!discoveredFields.length" />
                <q-tab name="sample" label="Sample Data" icon="preview" :disable="!sampleData.length" />
                <q-tab name="schema" label="Raw Schema" icon="code" />
              </q-tabs>

              <q-separator />

              <!-- Tab Panels -->
              <q-tab-panels v-model="activeTab" animated class="q-mt-md">
                <!-- Overview Tab -->
                <q-tab-panel name="overview">
                  <MeasurementOverview
                    :measurement="selectedMeasurement"
                    :tags="discoveredTags"
                    :fields="discoveredFields"
                    :sample-data="sampleData"
                    @discover-tags="discoverTags"
                    @discover-fields="discoverFields"
                    @get-sample="getSampleData"
                  />
                </q-tab-panel>

                <!-- Tags Tab -->
                <q-tab-panel name="tags">
                  <TagsExplorer
                    :tags="discoveredTags"
                    :sample-data="sampleData"
                    @refresh="discoverTags"
                    :loading="discoveringTags"
                  />
                </q-tab-panel>

                <!-- Fields Tab -->
                <q-tab-panel name="fields">
                  <FieldsExplorer
                    :fields="discoveredFields"
                    :sample-data="sampleData"
                    @refresh="discoverFields"
                    :loading="discoveringFields"
                  />
                </q-tab-panel>

                <!-- Sample Data Tab -->
                <q-tab-panel name="sample">
                  <SampleDataExplorer
                    :data="sampleData"
                    :measurement="selectedMeasurement"
                    @refresh="getSampleData"
                    :loading="loadingSample"
                  />
                </q-tab-panel>

                <!-- Raw Schema Tab -->
                <q-tab-panel name="schema">
                  <RawSchemaViewer
                    :tags="discoveredTags"
                    :fields="discoveredFields"
                    :sample-data="sampleData"
                    :measurement="selectedMeasurement"
                  />
                </q-tab-panel>
              </q-tab-panels>
            </div>

            <!-- Empty State -->
            <div v-else class="q-pa-xl text-center">
              <q-icon name="table_chart" size="4rem" class="text-grey-4 q-mb-md" />
              <div class="text-h6 text-grey-6 q-mb-sm">Select a Measurement</div>
              <div class="text-body2 text-grey-5">
                Choose a measurement from the sidebar to explore its schema and data
              </div>
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Footer Actions -->
      <q-separator />
      <q-card-actions class="q-pa-md">
        <q-btn
          label="Export Schema"
          icon="file_download"
          color="secondary"
          outline
          @click="exportSchema"
          :disable="!selectedMeasurement"
        />

        <q-space />

        <q-btn label="Close" flat @click="show = false" />
        <q-btn
          label="Use for Mapping"
          color="positive"
          @click="createMapping"
          :disable="!selectedMeasurement || (!discoveredTags.length && !discoveredFields.length)"
        />
      </q-card-actions>
    </q-card>

    <!-- Preview Dialog -->
    <q-dialog v-model="showPreview">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ previewMeasurement }}</div>
        </q-card-section>

        <q-card-section>
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="label" color="blue" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Tags</q-item-label>
                <q-item-label caption>{{ previewData.tags?.length || 0 }} tag columns</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="insights" color="green" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Fields</q-item-label>
                <q-item-label caption>{{ previewData.fields?.length || 0 }} field columns</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="preview" color="orange" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Sample Data</q-item-label>
                <q-item-label caption>{{ previewData.sample?.length || 0 }} sample records</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showPreview = false" />
          <q-btn
            label="Explore"
            color="primary"
            @click="selectMeasurement(previewMeasurement); showPreview = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import sub-components
import MeasurementOverview from 'src/components/MeasurementOverview.vue'
import TagsExplorer from 'src/components/TagsExplorer.vue'
import FieldsExplorer from 'src/components/FieldsExplorer.vue'
import SampleDataExplorer from 'src/components/SampleDataExplorer.vue'
import RawSchemaViewer from 'src/components/RawSchemaViewer.vue'

// Props
const props = defineProps({
  modelValue: Boolean,
  source: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'schema-discovered'])

// Reactive data
const $q = useQuasar()
const searchQuery = ref('')
const selectedMeasurement = ref(null)
const activeTab = ref('overview')

// Discovery states
const discovering = ref(false)
const discoveringTags = ref(false)
const discoveringFields = ref(false)
const loadingSample = ref(false)

// Data
const measurements = ref([])
const discoveredTags = ref([])
const discoveredFields = ref([])
const sampleData = ref([])
const measurementStats = ref({})

// Preview
const showPreview = ref(false)
const previewMeasurement = ref('')
const previewData = ref({})

// Computed properties
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const filteredMeasurements = computed(() => {
  if (!searchQuery.value) return measurements.value

  const query = searchQuery.value.toLowerCase()
  return measurements.value.filter(measurement =>
    measurement.toLowerCase().includes(query)
  )
})

// Methods
const discoverMeasurements = async () => {
  if (!props.source) return

  discovering.value = true
  try {
    const response = await axios.get(`http://localhost:8000/datasources/${props.source.source_id}/discover/measurements`)
    measurements.value = response.data.measurements || []

    // Get quick stats for each measurement
    for (const measurement of measurements.value) {
      try {
        const [tagsResponse, fieldsResponse] = await Promise.all([
          axios.post('http://localhost:8000/datasources/discover/tags', {
            source_type: props.source.source_type,
            connection_config: JSON.parse(props.source.connection_config),
            measurement
          }),
          axios.post('http://localhost:8000/datasources/discover/fields', {
            source_type: props.source.source_type,
            connection_config: JSON.parse(props.source.connection_config),
            measurement
          })
        ])

        measurementStats.value[measurement] = {
          tags: tagsResponse.data.tags?.length || 0,
          fields: fieldsResponse.data.fields?.length || 0
        }
      } catch (error) {
        console.warn(`Failed to get stats for ${measurement}:`, error)
      }
    }

    $q.notify({
      type: 'positive',
      message: `Discovered ${measurements.value.length} measurements`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover measurements',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discovering.value = false
  }
}

const selectMeasurement = (measurement) => {
  selectedMeasurement.value = measurement
  activeTab.value = 'overview'

  // Clear previous data
  discoveredTags.value = []
  discoveredFields.value = []
  sampleData.value = []
}

const discoverTags = async () => {
  if (!props.source || !selectedMeasurement.value) return

  discoveringTags.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
      source_type: props.source.source_type,
      connection_config: JSON.parse(props.source.connection_config),
      measurement: selectedMeasurement.value
    })

    discoveredTags.value = response.data.tags || []

    $q.notify({
      type: 'positive',
      message: `Discovered ${discoveredTags.value.length} tags`
    })

    // Switch to tags tab if we have tags
    if (discoveredTags.value.length > 0 && activeTab.value === 'overview') {
      activeTab.value = 'tags'
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover tags',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discoveringTags.value = false
  }
}

const discoverFields = async () => {
  if (!props.source || !selectedMeasurement.value) return

  discoveringFields.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_type: props.source.source_type,
      connection_config: JSON.parse(props.source.connection_config),
      measurement: selectedMeasurement.value
    })

    discoveredFields.value = response.data.fields || []

    $q.notify({
      type: 'positive',
      message: `Discovered ${discoveredFields.value.length} fields`
    })

    // Switch to fields tab if we have fields
    if (discoveredFields.value.length > 0 && activeTab.value === 'overview') {
      activeTab.value = 'fields'
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover fields',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discoveringFields.value = false
  }
}

const getSampleData = async () => {
  if (!props.source || !selectedMeasurement.value) return

  loadingSample.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/sample', {
      source_type: props.source.source_type,
      connection_config: JSON.parse(props.source.connection_config),
      measurement: selectedMeasurement.value
    })

    sampleData.value = response.data.sample_data || []

    $q.notify({
      type: 'positive',
      message: `Retrieved ${sampleData.value.length} sample records`
    })

    // Switch to sample tab if we have data
    if (sampleData.value.length > 0 && activeTab.value === 'overview') {
      activeTab.value = 'sample'
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to get sample data',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    loadingSample.value = false
  }
}

const previewMeasurement = async (measurement) => {
  previewMeasurement.value = measurement
  previewData.value = {
    tags: measurementStats.value[measurement]?.tags || 0,
    fields: measurementStats.value[measurement]?.fields || 0,
    sample: 0
  }
  showPreview.value = true
}

const exportSchema = () => {
  if (!selectedMeasurement.value) return

  const schemaData = {
    measurement: selectedMeasurement.value,
    source: {
      name: props.source.source_name,
      type: props.source.source_type
    },
    tags: discoveredTags.value,
    fields: discoveredFields.value,
    sampleData: sampleData.value.slice(0, 5), // Only include first 5 records
    discoveredAt: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(schemaData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${selectedMeasurement.value}_schema.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Schema exported successfully'
  })
}

const createMapping = () => {
  // Emit schema data for mapping creation
  emit('schema-discovered', {
    measurement: selectedMeasurement.value,
    tags: discoveredTags.value,
    fields: discoveredFields.value,
    sampleData: sampleData.value
  })

  show.value = false

  $q.notify({
    type: 'info',
    message: 'Opening mapping wizard with discovered schema'
  })
}

// Auto-discover measurements when dialog opens
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.source) {
    discoverMeasurements()
  }
})

// Reset data when source changes
watch(() => props.source, () => {
  measurements.value = []
  selectedMeasurement.value = null
  discoveredTags.value = []
  discoveredFields.value = []
  sampleData.value = []
  measurementStats.value = {}
})
</script>

<style scoped>
.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.q-tab-panel {
  padding: 0;
}

.q-card {
  border-radius: 12px;
}

/* Custom scrollbar */
.q-list {
  max-height: calc(100vh - 300px);
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
</style>
