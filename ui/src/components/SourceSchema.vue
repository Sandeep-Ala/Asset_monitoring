<!-- src/components/SourceSchema.vue - Fixed invalid HTML structure -->
<template>
  <div class="source-schema">
    <!-- Schema Discovery Progress -->
    <div v-if="discovering" class="text-center q-pa-xl">
      <q-spinner-dots size="3rem" color="primary" class="q-mb-md" />
      <div class="text-h6 q-mb-sm">Discovering Schema...</div>
      <div class="text-body2 text-grey-6">{{ discoveryProgress }}</div>
      <q-linear-progress
        :value="discoveryProgressValue"
        color="primary"
        size="8px"
        class="q-mt-md"
        style="max-width: 400px; margin: 0 auto;"
      />
    </div>

    <!-- No Schema State -->
    <div v-else-if="!hasSchema" class="text-center q-pa-xl">
      <q-icon name="schema" size="4rem" class="text-grey-4 q-mb-md" />
      <div class="text-h6 text-grey-6 q-mb-sm">No Schema Discovered</div>
      <div class="text-body2 text-grey-5 q-mb-lg">
        Discover the data structure from your source to understand available measurements and fields
      </div>
      <q-btn
        label="Start Schema Discovery"
        icon="search"
        color="primary"
        size="lg"
        @click="discoverSchema"
        :loading="discovering"
      />
    </div>

    <!-- Schema Content -->
    <div v-else>
      <!-- FIXED: Properly structured q-tabs and q-tab-panels -->
      <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
        <q-tab name="overview" label="Overview" icon="dashboard" />
        <q-tab name="measurements" label="Measurements" icon="table_chart" />
        <q-tab name="fields" label="Fields Analysis" icon="insights" />
        <q-tab name="relationships" label="Relationships" icon="account_tree" />
        <q-tab name="quality" label="Data Quality" icon="verified" />
      </q-tabs>

      <q-separator />

      <!-- Tab Panels -->
      <q-tab-panels v-model="activeTab" animated class="q-mt-md">
        <!-- Overview Tab -->
        <q-tab-panel name="overview">
          <SchemaOverview
            :schema="discoveredSchema"
            :source="source"
            @discover-measurement="discoverMeasurementDetails"
            @create-mapping="createMapping"
          />
        </q-tab-panel>

        <!-- Measurements Tab -->
        <q-tab-panel name="measurements">
          <MeasurementsAnalysis
            :measurements="discoveredSchema?.measurements || []"
            :schema="discoveredSchema"
            :source="source"
            @analyze-measurement="analyzeMeasurement"
            @preview-measurement="showMeasurementPreview"
          />
        </q-tab-panel>

        <!-- Fields Analysis Tab -->
        <q-tab-panel name="fields">
          <FieldsAnalysis
            :fields="allFields"
            :schema="discoveredSchema"
            @analyze-field="analyzeField"
            @compare-fields="compareFields"
          />
        </q-tab-panel>

        <!-- Relationships Tab -->
        <q-tab-panel name="relationships">
          <SchemaRelationships
            :schema="discoveredSchema"
            :measurements="discoveredSchema?.measurements || []"
            @visualize-relationship="visualizeRelationship"
          />
        </q-tab-panel>

        <!-- Data Quality Tab -->
        <q-tab-panel name="quality">
          <SchemaQuality
            :schema="discoveredSchema"
            :quality-metrics="qualityMetrics"
            @run-quality-check="runQualityCheck"
            @fix-quality-issue="fixQualityIssue"
          />
        </q-tab-panel>
      </q-tab-panels>
      <!-- FIXED: Properly closed tab panels -->
    </div>

    <!-- Schema Explorer Dialog -->
    <q-dialog v-model="showSchemaExplorer" maximized>
      <SchemaExplorer
        :source="source"
        @schema-discovered="onSchemaDiscovered"
      />
    </q-dialog>

    <!-- Measurement Analysis Dialog -->
    <q-dialog v-model="showMeasurementDialog">
      <q-card style="min-width: 800px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6">Measurement Analysis: {{ selectedMeasurement }}</div>
        </q-card-section>

        <q-card-section>
          <MeasurementOverview
            v-if="selectedMeasurement"
            :measurement="selectedMeasurement"
            :tags="measurementDetails.tags || []"
            :fields="measurementDetails.fields || []"
            :sample-data="measurementDetails.sampleData || []"
            @discover-tags="discoverMeasurementTags"
            @discover-fields="discoverMeasurementFields"
            @get-sample="getMeasurementSample"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Create Mapping"
            icon="link"
            color="positive"
            @click="createMappingFromMeasurement"
            :disable="!canCreateMapping"
          />
          <q-btn label="Close" flat @click="showMeasurementDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Quality Check Results Dialog -->
    <q-dialog v-model="showQualityDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Data Quality Analysis</div>
        </q-card-section>

        <q-card-section>
          <div v-if="qualityResults.length">
            <q-list>
              <q-item
                v-for="result in qualityResults"
                :key="result.id"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="getQualityIcon(result.severity)"
                    :color="getQualityColor(result.severity)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ result.title }}</q-item-label>
                  <q-item-label caption>{{ result.description }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
          <div v-else class="text-center q-pa-lg">
            <q-icon name="check_circle" size="3rem" color="positive" class="q-mb-md" />
            <div class="text-h6 text-positive">No Quality Issues Found</div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showQualityDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import sub-components
import SchemaOverview from 'src/components/SchemaOverview.vue'
import MeasurementsAnalysis from 'src/components/MeasurementsAnalysis.vue'
import FieldsAnalysis from 'src/components/FieldsAnalysis.vue'
import SchemaRelationships from 'src/components/SchemaRelationships.vue'
import SchemaQuality from 'src/components/SchemaQuality.vue'
import SchemaExplorer from 'src/components/SchemaExplorer.vue'
import MeasurementOverview from 'src/components/MeasurementOverview.vue'

// Props
const props = defineProps({
  source: Object,
  discoveredSchema: Object
})

// Emits
const emit = defineEmits(['discover', 'refresh-schema', 'create-mapping'])

// Reactive data
const $q = useQuasar()
const activeTab = ref('overview')

// Discovery states
const discovering = ref(false)
const discoveryProgress = ref('')
const discoveryProgressValue = ref(0)

// Data
const localDiscoveredSchema = ref(props.discoveredSchema || {})
const qualityMetrics = ref({})
const qualityResults = ref([])

// Dialog states
const showSchemaExplorer = ref(false)
const showMeasurementDialog = ref(false)
const showQualityDialog = ref(false)

// Selected items
const selectedMeasurement = ref(null)
const measurementDetails = ref({
  tags: [],
  fields: [],
  sampleData: []
})

// Computed properties
const hasSchema = computed(() => {
  return localDiscoveredSchema.value &&
         localDiscoveredSchema.value.measurements &&
         localDiscoveredSchema.value.measurements.length > 0
})

const allFields = computed(() => {
  if (!localDiscoveredSchema.value?.fields) return []

  return Object.values(localDiscoveredSchema.value.fields).flat()
})

const canCreateMapping = computed(() => {
  return selectedMeasurement.value &&
         (measurementDetails.value.tags.length > 0 || measurementDetails.value.fields.length > 0)
})

// Methods
const discoverSchema = async () => {
  if (!props.source) return

  discovering.value = true
  discoveryProgress.value = 'Initializing discovery...'
  discoveryProgressValue.value = 0

  try {
    // Step 1: Discover measurements
    discoveryProgress.value = 'Discovering measurements...'
    discoveryProgressValue.value = 0.2

    const measurementsResponse = await axios.get(
      `http://localhost:8000/datasources/${props.source.source_id}/discover/measurements`
    )

    const measurements = measurementsResponse.data.measurements || []

    // Step 2: Discover schema for each measurement
    discoveryProgress.value = 'Analyzing schema structure...'
    discoveryProgressValue.value = 0.4

    const schemaPromises = measurements.slice(0, 5).map(async (measurement) => {
      try {
        const [tagsResponse, fieldsResponse] = await Promise.all([
          axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: props.source.source_type,
        connection_config :props.source,
            measurement
          }),
          axios.post('http://localhost:8000/datasources/discover/fields', {
        source_type: props.source.source_type,
        connection_config :props.source,
            measurement
          })
        ])

        return {
          measurement,
          tags: tagsResponse.data.tags || [],
          fields: fieldsResponse.data.fields || []
        }
      } catch (error) {
        return {
          measurement,
          tags: [],
          fields: []
        }
      }
    })

    discoveryProgress.value = 'Processing schema data...'
    discoveryProgressValue.value = 0.7

    const schemaResults = await Promise.all(schemaPromises)

    // Build discovered schema
    const schema = {
      measurements,
      tags: {},
      fields: {}
    }

    schemaResults.forEach(result => {
      schema.tags[result.measurement] = result.tags
      schema.fields[result.measurement] = result.fields
    })

    discoveryProgress.value = 'Finalizing discovery...'
    discoveryProgressValue.value = 0.9

    localDiscoveredSchema.value = schema

    discoveryProgressValue.value = 1.0

    emit('discover', schema)

    $q.notify({
      type: 'positive',
      message: `Schema discovered successfully`,
      caption: `Found ${measurements.length} measurements`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover schema',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discovering.value = false
    discoveryProgress.value = ''
    discoveryProgressValue.value = 0
  }
}

const discoverMeasurementDetails = async (measurement) => {
  selectedMeasurement.value = measurement
  measurementDetails.value = {
    tags: localDiscoveredSchema.value?.tags?.[measurement] || [],
    fields: localDiscoveredSchema.value?.fields?.[measurement] || [],
    sampleData: localDiscoveredSchema.value?.sampleData?.[measurement] || []
  }
  showMeasurementDialog.value = true
}

const analyzeMeasurement = async (measurement) => {
  await discoverMeasurementDetails(measurement)
}

const showMeasurementPreview = async (measurement) => {
  await discoverMeasurementDetails(measurement)
}

const discoverMeasurementTags = async () => {
  if (!selectedMeasurement.value) return

  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: props.source.source_type,
        connection_config :props.source,
      measurement: selectedMeasurement.value
    })

    measurementDetails.value.tags = response.data.tags || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover tags'
    })
  }
}

const discoverMeasurementFields = async () => {
  if (!selectedMeasurement.value) return

  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_id: props.source.source_id,
      measurement: selectedMeasurement.value
    })

    measurementDetails.value.fields = response.data.fields || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover fields'
    })
  }
}

const getMeasurementSample = async () => {
  if (!selectedMeasurement.value) return

  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/sample', {
      source_id: props.source.source_id,
      measurement: selectedMeasurement.value
    })

    measurementDetails.value.sampleData = response.data.sample_data || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to load sample data'
    })
  }
}

const analyzeField = (field) => {
  // Field analysis logic
  console.log('Analyzing field:', field)
}

const compareFields = (fields) => {
  // Field comparison logic
  console.log('Comparing fields:', fields)
}

const visualizeRelationship = (relationship) => {
  // Relationship visualization logic
  console.log('Visualizing relationship:', relationship)
}

const runQualityCheck = async () => {
  // Run quality check logic
  qualityResults.value = [
    {
      id: 1,
      title: 'Missing Values Detected',
      description: 'Some fields have null values',
      severity: 'warning'
    }
  ]
  showQualityDialog.value = true
}

const fixQualityIssue = (issue) => {
  // Fix quality issue logic
  console.log('Fixing quality issue:', issue)
}

const createMapping = () => {
  emit('create-mapping', localDiscoveredSchema.value)
}

const createMappingFromMeasurement = () => {
  const mappingData = {
    measurement: selectedMeasurement.value,
    tags: measurementDetails.value.tags,
    fields: measurementDetails.value.fields,
    sampleData: measurementDetails.value.sampleData
  }
  emit('create-mapping', mappingData)
  showMeasurementDialog.value = false
}

const getQualityIcon = (severity) => {
  const icons = {
    error: 'error',
    warning: 'warning',
    info: 'info'
  }
  return icons[severity] || 'info'
}

const getQualityColor = (severity) => {
  const colors = {
    error: 'negative',
    warning: 'warning',
    info: 'info'
  }
  return colors[severity] || 'info'
}

// Watch for schema changes
watch(() => props.discoveredSchema, (newSchema) => {
  if (newSchema) {
    localDiscoveredSchema.value = newSchema
  }
}, { immediate: true })

// Initialize component
onMounted(() => {
  if (props.discoveredSchema) {
    localDiscoveredSchema.value = props.discoveredSchema
  }
})
</script>
