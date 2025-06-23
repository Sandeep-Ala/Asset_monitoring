<!-- src/components/SchemaExplorer.vue - Fixed duplicate variable declarations -->
<template>
  <q-dialog v-model="show" maximized>
    <q-card class="column">
      <!-- Header -->
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Schema Explorer</div>
        <div class="text-subtitle2 text-grey-6 q-ml-md">
          {{ source?.source_name }}
        </div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <!-- Main Content -->
      <q-card-section class="col row no-wrap">
        <!-- Sidebar - Measurements List -->
        <div class="col-3 q-pr-md">
          <q-card flat bordered class="full-height">
            <q-card-section>
              <div class="text-subtitle1 q-mb-md">Measurements</div>

              <!-- Search -->
              <q-input
                v-model="searchQuery"
                placeholder="Search measurements..."
                dense
                outlined
                clearable
              >
                <template #prepend>
                  <q-icon name="search" />
                </template>
              </q-input>

              <!-- Discover Button -->
              <q-btn
                v-if="!measurements.length"
                label="Discover Measurements"
                icon="search"
                color="primary"
                class="full-width q-mt-md"
                @click="discoverMeasurements"
                :loading="discovering"
              />

              <!-- Measurements List -->
              <q-list v-if="measurements.length" class="q-mt-md">
                <q-item
                  v-for="measurement in filteredMeasurements"
                  :key="measurement"
                  clickable
                  :active="selectedMeasurement === measurement"
                  @click="selectMeasurement(measurement)"
                >
                  <q-item-section avatar>
                    <q-icon name="table_chart" />
                  </q-item-section>

                  <q-item-section>
                    <q-item-label>{{ measurement }}</q-item-label>
                  </q-item-section>

                  <q-item-section side>
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click.stop="showMeasurementPreview(measurement)"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>

        <!-- Main Content Area -->
        <div class="col-9">
          <!-- Selected Measurement Details -->
          <div v-if="selectedMeasurement">
            <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
              <q-tab name="overview" label="Overview" icon="dashboard" />
              <q-tab name="tags" label="Tags" icon="label" />
              <q-tab name="fields" label="Fields" icon="insights" />
              <q-tab name="sample" label="Sample Data" icon="preview" />
              <q-tab name="raw" label="Raw Schema" icon="code" />
            </q-tabs>

            <q-separator />

            <q-tab-panels v-model="activeTab" animated class="q-mt-md">
              <q-tab-panel name="overview">
                <MeasurementOverview
                  :measurement="selectedMeasurement"
                  :tags="discoveredTags"
                  :fields="discoveredFields"
                  :sample-data="sampleData"
                  :stats="measurementStats[selectedMeasurement]"
                />
              </q-tab-panel>

              <q-tab-panel name="tags">
                <TagsExplorer
                  :tags="discoveredTags"
                  :sample-data="sampleData"
                  :loading="discoveringTags"
                  @refresh="discoverMeasurementTags"
                />
              </q-tab-panel>

              <q-tab-panel name="fields">
                <FieldsExplorer
                  :fields="discoveredFields"
                  :sample-data="sampleData"
                  :loading="discoveringFields"
                  @refresh="discoverMeasurementFields"
                />
              </q-tab-panel>

              <q-tab-panel name="sample">
                <SampleDataExplorer
                  :measurement="selectedMeasurement"
                  :sample-data="sampleData"
                  :loading="loadingSample"
                  @refresh="getMeasurementSample"
                />
              </q-tab-panel>

              <q-tab-panel name="raw">
                <RawSchemaViewer
                  :measurement="selectedMeasurement"
                  :tags="discoveredTags"
                  :fields="discoveredFields"
                  :sample-data="sampleData"
                />
              </q-tab-panel>
            </q-tab-panels>
          </div>

          <!-- No Selection State -->
          <div v-else class="full-height flex flex-center">
            <div class="text-center q-pa-xl">
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
          <div class="text-h6">{{ currentPreviewMeasurement }}</div>
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
            @click="selectMeasurement(currentPreviewMeasurement); showPreview = false"
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

// Preview - FIXED: Renamed variables to avoid conflicts
const showPreview = ref(false)
const currentPreviewMeasurement = ref('')  // RENAMED from previewMeasurement
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

    $q.notify({
      type: 'positive',
      message: `Discovered ${measurements.value.length} measurements`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover measurements'
    })
  } finally {
    discovering.value = false
  }
}

const selectMeasurement = async (measurement) => {
  selectedMeasurement.value = measurement
  activeTab.value = 'overview'

  // Clear previous data
  discoveredTags.value = []
  discoveredFields.value = []
  sampleData.value = []

  // Auto-discover tags, fields, and sample data
  await Promise.all([
    discoverMeasurementTags(),
    discoverMeasurementFields(),
    getMeasurementSample()
  ])
}

// FIXED: Renamed function to avoid conflict
const showMeasurementPreview = async (measurement) => {
  currentPreviewMeasurement.value = measurement  // FIXED: Use renamed variable
  previewData.value = {
    tags: [],
    fields: [],
    sample: []
  }

  try {
    // Quick preview discovery
    const [tagsResponse, fieldsResponse, sampleResponse] = await Promise.all([
      axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: props.source.source_type,
        connection_config :props.source,
        measurement
      }),
      axios.post('http://localhost:8000/datasources/discover/fields', {
        source_type: props.source.source_type,
        connection_config :props.source,
        measurement
      }),
      axios.post('http://localhost:8000/datasources/discover/sample', {
        source_type: props.source.source_type,
        connection_config :props.source,
        measurement,
        limit: 3
      })
    ])

    previewData.value = {
      tags: tagsResponse.data.tags || [],
      fields: fieldsResponse.data.fields || [],
      sample: sampleResponse.data.sample_data || []
    }
  } catch (error) {
    $q.notify({
      type: 'warning',
      message: 'Failed to load preview data'
    })
  }

  showPreview.value = true
}

const discoverMeasurementTags = async () => {
  if (!selectedMeasurement.value) return

  discoveringTags.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: props.source.source_type,
        connection_config :props.source,
      measurement: selectedMeasurement.value
    })

    discoveredTags.value = response.data.tags || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover tags'
    })
  } finally {
    discoveringTags.value = false
  }
}

const discoverMeasurementFields = async () => {
  if (!selectedMeasurement.value) return

  discoveringFields.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_id: props.source.source_id,
      measurement: selectedMeasurement.value
    })

    discoveredFields.value = response.data.fields || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover fields'
    })
  } finally {
    discoveringFields.value = false
  }
}

const getMeasurementSample = async () => {
  if (!selectedMeasurement.value) return

  loadingSample.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/sample', {
      source_id: props.source.source_id,
      measurement: selectedMeasurement.value
    })

    sampleData.value = response.data.sample_data || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to load sample data'
    })
  } finally {
    loadingSample.value = false
  }
}

const exportSchema = () => {
  const schemaData = {
    measurement: selectedMeasurement.value,
    tags: discoveredTags.value,
    fields: discoveredFields.value,
    sampleData: sampleData.value.slice(0, 5),
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
  const schemaData = {
    measurement: selectedMeasurement.value,
    tags: discoveredTags.value,
    fields: discoveredFields.value,
    sampleData: sampleData.value
  }

  emit('schema-discovered', schemaData)
  show.value = false
}

// Watch for source changes
watch(() => props.source, () => {
  if (props.source && show.value) {
    discoverMeasurements()
  }
})
</script>
