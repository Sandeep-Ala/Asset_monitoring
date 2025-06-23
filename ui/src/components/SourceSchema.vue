<!-- ui/src/components/SourceSchema.vue -->
<template>
  <div class="source-schema q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Schema Management</div>
        <div class="text-subtitle2 text-grey-6">
          Discover, analyze, and manage data structure from your source
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Refresh Schema"
          icon="refresh"
          color="primary"
          @click="refreshSchema"
          :loading="refreshing"
        />
        <q-btn
          label="Export Schema"
          icon="file_download"
          color="secondary"
          outline
          @click="exportSchema"
          :disable="!hasSchema"
        />
        <q-btn
          label="Schema Explorer"
          icon="explore"
          color="positive"
          outline
          @click="showSchemaExplorer = true"
        />
      </div>
    </div>

    <!-- Schema Discovery Status -->
    <div class="q-mb-lg">
      <q-card flat bordered :class="schemaStatusClass">
        <q-card-section>
          <div class="row items-center">
            <q-icon
              :name="schemaStatusIcon"
              :color="schemaStatusColor"
              size="2rem"
              class="q-mr-md"
            />
            <div class="col">
              <div class="text-h6">{{ schemaStatusTitle }}</div>
              <div class="text-body2 text-grey-7">{{ schemaStatusMessage }}</div>
            </div>
            <div class="col-auto">
              <q-btn
                v-if="!hasSchema"
                label="Discover Now"
                icon="search"
                color="primary"
                @click="discoverSchema"
                :loading="discovering"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Schema Summary -->
        <q-card-section v-if="hasSchema" class="q-pt-none">
          <q-separator class="q-mb-md" />
          <div class="row q-gutter-md text-caption">
            <div>
              <strong>Measurements:</strong> {{ discoveredSchema?.measurements?.length || 0 }}
            </div>
            <div>
              <strong>Total Columns:</strong> {{ totalColumns }}
            </div>
            <div>
              <strong>Last Discovery:</strong> {{ formatDateTime(lastDiscovery) }}
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Schema Content -->
    <div v-if="!hasSchema && !discovering" class="text-center q-pa-xl">
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

    <div v-else-if="discovering" class="text-center q-pa-xl">
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

    <!-- Schema Tabs -->
    <div v-else>
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
            @preview-measurement="previewMeasurement"
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
      </q-tabs>
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
          <div class="text-h6">Data Quality Report</div>
        </q-card-section>

        <q-card-section>
          <div class="text-center q-mb-md">
            <q-circular-progress
              :value="overallQualityScore"
              size="100px"
              :thickness="0.2"
              :color="getQualityColor(overallQualityScore)"
              track-color="grey-3"
            >
              <div class="text-h5">{{ Math.round(overallQualityScore) }}%</div>
            </q-circular-progress>
            <div class="text-subtitle2 q-mt-sm">Overall Quality Score</div>
          </div>

          <q-list v-if="qualityIssues.length > 0" separator>
            <q-item
              v-for="issue in qualityIssues"
              :key="issue.id"
              :class="getIssueClass(issue.severity)"
            >
              <q-item-section avatar>
                <q-icon
                  :name="getIssueIcon(issue.severity)"
                  :color="getIssueColor(issue.severity)"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ issue.message }}</q-item-label>
                <q-item-label caption>{{ issue.details }}</q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-btn
                  v-if="issue.fixable"
                  label="Fix"
                  color="positive"
                  size="sm"
                  @click="fixQualityIssue(issue)"
                />
              </q-item-section>
            </q-item>
          </q-list>

          <div v-else class="text-center q-pa-lg text-grey-6">
            <q-icon name="verified" size="3rem" class="text-positive q-mb-md" />
            <div class="text-h6">No Quality Issues Found</div>
            <div class="text-body2">Your schema appears to be in good condition</div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Re-run Check"
            icon="refresh"
            color="primary"
            outline
            @click="runQualityCheck"
          />
          <q-btn label="Close" flat @click="showQualityDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import sub-components
import SchemaExplorer from 'src/components/SchemaExplorer.vue'
import MeasurementOverview from 'src/components/MeasurementOverview.vue'
import SchemaOverview from 'src/components/SchemaOverview.vue'
import MeasurementsAnalysis from 'src/components/MeasurementsAnalysis.vue'
import FieldsAnalysis from 'src/components/FieldsAnalysis.vue'
import SchemaRelationships from 'src/components/SchemaRelationships.vue'
import SchemaQuality from 'src/components/SchemaQuality.vue'

// Props
const props = defineProps({
  source: Object,
  discoveredSchema: Object
})

// Emits
const emit = defineEmits(['discover', 'refresh-schema'])

// Reactive data
const $q = useQuasar()
const activeTab = ref('overview')
const discovering = ref(false)
const refreshing = ref(false)
const discoveryProgress = ref('')
const discoveryProgressValue = ref(0)
const lastDiscovery = ref(null)

// Dialog states
const showSchemaExplorer = ref(false)
const showMeasurementDialog = ref(false)
const showQualityDialog = ref(false)

// Selection states
const selectedMeasurement = ref(null)
const measurementDetails = ref({
  tags: [],
  fields: [],
  sampleData: []
})

// Quality metrics
const qualityMetrics = ref({
  completeness: 0,
  consistency: 0,
  validity: 0,
  uniqueness: 0
})
const qualityIssues = ref([])

// Computed properties
const hasSchema = computed(() => {
  return props.discoveredSchema &&
         props.discoveredSchema.measurements &&
         props.discoveredSchema.measurements.length > 0
})

const totalColumns = computed(() => {
  if (!props.discoveredSchema) return 0

  let total = 0
  if (props.discoveredSchema.tags) {
    total += Object.values(props.discoveredSchema.tags).reduce((sum, tags) => sum + tags.length, 0)
  }
  if (props.discoveredSchema.fields) {
    total += Object.values(props.discoveredSchema.fields).reduce((sum, fields) => sum + fields.length, 0)
  }

  return total
})

const allFields = computed(() => {
  if (!props.discoveredSchema?.fields) return []

  const fields = []
  Object.entries(props.discoveredSchema.fields).forEach(([measurement, measurementFields]) => {
    measurementFields.forEach(field => {
      fields.push({
        ...field,
        measurement
      })
    })
  })

  return fields
})

const schemaStatusClass = computed(() => {
  if (!hasSchema.value) return 'bg-grey-2'
  return 'bg-green-1'
})

const schemaStatusIcon = computed(() => {
  if (!hasSchema.value) return 'help_outline'
  return 'check_circle'
})

const schemaStatusColor = computed(() => {
  if (!hasSchema.value) return 'grey'
  return 'positive'
})

const schemaStatusTitle = computed(() => {
  if (!hasSchema.value) return 'Schema Not Discovered'
  return 'Schema Available'
})

const schemaStatusMessage = computed(() => {
  if (!hasSchema.value) return 'No schema information available for this data source'
  return `${props.discoveredSchema.measurements.length} measurements discovered with ${totalColumns.value} total columns`
})

const overallQualityScore = computed(() => {
  const metrics = qualityMetrics.value
  return (metrics.completeness + metrics.consistency + metrics.validity + metrics.uniqueness) / 4
})

const canCreateMapping = computed(() => {
  return measurementDetails.value.fields && measurementDetails.value.fields.length > 0
})

// Methods
onMounted(() => {
  if (props.discoveredSchema) {
    lastDiscovery.value = new Date()
    calculateQualityMetrics()
  }
})

const discoverSchema = async () => {
  discovering.value = true
  discoveryProgress.value = 'Initializing discovery...'
  discoveryProgressValue.value = 10

  try {
    // Step 1: Discover measurements
    discoveryProgress.value = 'Discovering measurements...'
    discoveryProgressValue.value = 30

    const measurementsResponse = await axios.get(`http://localhost:8000/datasources/${props.source.source_id}/discover/measurements`)
    const measurements = measurementsResponse.data.measurements || []

    // Step 2: Discover tags and fields for each measurement
    discoveryProgress.value = 'Analyzing structure...'
    discoveryProgressValue.value = 60

    const schema = {
      measurements,
      tags: {},
      fields: {},
      sampleData: {}
    }

    const connectionConfig = JSON.parse(props.source.connection_config)

    // Process each measurement
    for (let i = 0; i < measurements.length; i++) {
      const measurement = measurements[i]
      discoveryProgress.value = `Processing ${measurement}... (${i + 1}/${measurements.length})`
      discoveryProgressValue.value = 60 + (i / measurements.length) * 30

      try {
        const [tagsResponse, fieldsResponse] = await Promise.allSettled([
          axios.post('http://localhost:8000/datasources/discover/tags', {
            source_type: props.source.source_type,
            connection_config: connectionConfig,
            measurement
          }),
          axios.post('http://localhost:8000/datasources/discover/fields', {
            source_type: props.source.source_type,
            connection_config: connectionConfig,
            measurement
          })
        ])

        if (tagsResponse.status === 'fulfilled') {
          schema.tags[measurement] = tagsResponse.value.data.tags || []
        }

        if (fieldsResponse.status === 'fulfilled') {
          schema.fields[measurement] = fieldsResponse.value.data.fields || []
        }
      } catch (error) {
        console.warn(`Failed to process measurement ${measurement}:`, error)
      }
    }

    // Step 3: Finalize
    discoveryProgress.value = 'Finalizing discovery...'
    discoveryProgressValue.value = 95

    lastDiscovery.value = new Date()
    emit('discover', schema)

    await calculateQualityMetrics()

    discoveryProgressValue.value = 100

    $q.notify({
      type: 'positive',
      message: 'Schema discovery completed',
      caption: `Discovered ${measurements.length} measurements`
    })

  } catch (error) {
    console.error('Schema discovery error:', error)
    $q.notify({
      type: 'negative',
      message: 'Schema discovery failed',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    discovering.value = false
    discoveryProgress.value = ''
    discoveryProgressValue.value = 0
  }
}

const refreshSchema = async () => {
  refreshing.value = true
  try {
    emit('refresh-schema')
    await discoverSchema()
  } finally {
    refreshing.value = false
  }
}

const exportSchema = () => {
  if (!hasSchema.value) return

  const exportData = {
    source: {
      id: props.source.source_id,
      name: props.source.source_name,
      type: props.source.source_type
    },
    schema: props.discoveredSchema,
    quality: qualityMetrics.value,
    discoveredAt: lastDiscovery.value,
    exportedAt: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `${props.source.source_name}_schema.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Schema exported successfully',
    icon: 'file_download'
  })
}

const discoverMeasurementDetails = async (measurement) => {
  selectedMeasurement.value = measurement
  measurementDetails.value = {
    tags: props.discoveredSchema?.tags?.[measurement] || [],
    fields: props.discoveredSchema?.fields?.[measurement] || [],
    sampleData: props.discoveredSchema?.sampleData?.[measurement] || []
  }
  showMeasurementDialog.value = true
}

const analyzeMeasurement = async (measurement) => {
  await discoverMeasurementDetails(measurement)
}

const previewMeasurement = async (measurement) => {
  await discoverMeasurementDetails(measurement)
}

const discoverMeasurementTags = async () => {
  if (!selectedMeasurement.value) return

  try {
    const connectionConfig = JSON.parse(props.source.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
      source_type: props.source.source_type,
      connection_config: connectionConfig,
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
    const connectionConfig = JSON.parse(props.source.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_type: props.source.source_type,
      connection_config: connectionConfig,
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
    const connectionConfig = JSON.parse(props.source.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/discover/sample', {
      source_type: props.source.source_type,
      connection_config: connectionConfig,
      measurement: selectedMeasurement.value
    })

    measurementDetails.value.sampleData = response.data.sample_data || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to get sample data'
    })
  }
}

const createMapping = () => {
  $q.notify({
    type: 'info',
    message: 'Opening mapping wizard...'
  })
  // This would typically emit an event to parent
}

const createMappingFromMeasurement = () => {
  showMeasurementDialog.value = false
  createMapping()
}

const calculateQualityMetrics = async () => {
  if (!hasSchema.value) return

  // Mock quality calculation - in real implementation, this would analyze the schema
  qualityMetrics.value = {
    completeness: Math.random() * 20 + 80, // 80-100%
    consistency: Math.random() * 15 + 85,  // 85-100%
    validity: Math.random() * 10 + 90,     // 90-100%
    uniqueness: Math.random() * 25 + 75    // 75-100%
  }

  // Generate quality issues
  qualityIssues.value = []

  if (qualityMetrics.value.completeness < 90) {
    qualityIssues.value.push({
      id: 'completeness',
      severity: 'warning',
      message: 'Some measurements have missing metadata',
      details: 'Consider adding descriptions for better documentation',
      fixable: false
    })
  }

  if (qualityMetrics.value.consistency < 85) {
    qualityIssues.value.push({
      id: 'consistency',
      severity: 'error',
      message: 'Inconsistent naming patterns detected',
      details: 'Some field names use different conventions',
      fixable: true
    })
  }
}

const runQualityCheck = async () => {
  await calculateQualityMetrics()
  showQualityDialog.value = true
}

const fixQualityIssue = async (issue) => {
  $q.notify({
    type: 'info',
    message: `Fixing quality issue: ${issue.message}`,
    caption: 'Quality fix functionality coming soon'
  })
}

const analyzeField = (field) => {
  $q.notify({
    type: 'info',
    message: `Analyzing field: ${field.name || field}`,
    caption: 'Field analysis functionality coming soon'
  })
}

const compareFields = (fields) => {
  $q.notify({
    type: 'info',
    message: `Comparing ${fields.length} fields`,
    caption: 'Field comparison functionality coming soon'
  })
}

const visualizeRelationship = (relationship) => {
  $q.notify({
    type: 'info',
    message: 'Visualizing schema relationships',
    caption: 'Relationship visualization coming soon'
  })
}

const onSchemaDiscovered = (schema) => {
  emit('discover', schema)
  lastDiscovery.value = new Date()
  calculateQualityMetrics()
}

// Utility methods
const formatDateTime = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const getQualityColor = (score) => {
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
}

const getIssueIcon = (severity) => {
  const icons = {
    'error': 'error',
    'warning': 'warning',
    'info': 'info'
  }
  return icons[severity] || 'info'
}

const getIssueColor = (severity) => {
  const colors = {
    'error': 'negative',
    'warning': 'warning',
    'info': 'info'
  }
  return colors[severity] || 'info'
}

const getIssueClass = (severity) => {
  const classes = {
    'error': 'bg-red-1',
    'warning': 'bg-orange-1',
    'info': 'bg-blue-1'
  }
  return classes[severity] || ''
}
</script>

<style scoped>
.source-schema {
  background-color: #fafafa;
  min-height: 100%;
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-grey-2 {
  background-color: rgba(158, 158, 158, 0.1);
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.bg-orange-1 {
  background-color: rgba(255, 152, 0, 0.1);
}

.bg-red-1 {
  background-color: rgba(244, 67, 54, 0.1);
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-tab-panel {
  padding: 0;
}

.q-chip {
  font-weight: 500;
}

.q-item {
  border-radius: 8px;
  margin-bottom: 4px;
}

.q-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
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
