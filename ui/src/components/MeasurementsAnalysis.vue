<!-- ui/src/components/MeasurementsAnalysis.vue -->
<!-- Detailed measurement analysis component -->

<template>
  <div class="measurements-analysis">
    <!-- Analysis Controls -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">
              <q-icon name="analytics" class="q-mr-sm" />
              Measurement Analysis
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md items-end">
              <!-- Measurement Selection -->
              <div class="col-12 col-md-4">
                <q-select
                  v-model="selectedMeasurements"
                  :options="measurementOptions"
                  label="Select Measurements"
                  multiple
                  use-chips
                  outlined
                  dense
                  @update:model-value="updateAnalysis"
                >
                  <template #option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                        <q-item-label caption>
                          {{ getTagsCount(scope.opt.value) }} tags, {{ getFieldsCount(scope.opt.value) }} fields
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>

              <!-- Analysis Type -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="analysisType"
                  :options="analysisOptions"
                  label="Analysis Type"
                  outlined
                  dense
                  @update:model-value="updateAnalysis"
                />
              </div>

              <!-- Time Range -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="timeRange"
                  :options="timeRangeOptions"
                  label="Time Range"
                  outlined
                  dense
                  @update:model-value="updateAnalysis"
                />
              </div>

              <!-- Actions -->
              <div class="col-12 col-md-2">
                <div class="row q-gutter-sm">
                  <q-btn
                    label="Analyze"
                    icon="play_arrow"
                    color="primary"
                    @click="runAnalysis"
                    :loading="analyzing"
                    :disable="selectedMeasurements.length === 0"
                  />
                  <q-btn
                    icon="refresh"
                    flat
                    round
                    @click="refreshData"
                    :loading="refreshing"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Analysis Results -->
    <div v-if="analysisResults" class="row q-gutter-md q-mb-lg">
      <!-- Summary Cards -->
      <div class="col-12">
        <div class="row q-gutter-md">
          <div class="col-6 col-md-3">
            <q-card flat class="bg-green-1 text-center q-pa-md">
              <q-icon name="table_chart" size="2rem" color="green" class="q-mb-sm" />
              <div class="text-h5">{{ analysisResults.totalMeasurements }}</div>
              <div class="text-body2">Analyzed</div>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat class="bg-blue-1 text-center q-pa-md">
              <q-icon name="storage" size="2rem" color="blue" class="q-mb-sm" />
              <div class="text-h5">{{ formatBytes(analysisResults.totalDataSize) }}</div>
              <div class="text-body2">Data Size</div>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat class="bg-orange-1 text-center q-pa-md">
              <q-icon name="speed" size="2rem" color="orange" class="q-mb-sm" />
              <div class="text-h5">{{ analysisResults.avgResponseTime }}ms</div>
              <div class="text-body2">Avg Response</div>
            </q-card>
          </div>
          <div class="col-6 col-md-3">
            <q-card flat class="bg-purple-1 text-center q-pa-md">
              <q-icon name="timeline" size="2rem" color="purple" class="q-mb-sm" />
              <div class="text-h5">{{ analysisResults.dataPoints }}</div>
              <div class="text-body2">Data Points</div>
            </q-card>
          </div>
        </div>
      </div>
    </div>

    <!-- Measurement Comparison Table -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="compare" class="q-mr-sm" />
              Measurement Comparison
            </div>
          </q-card-section>
          <q-card-section>
            <q-table
              :rows="comparisonData"
              :columns="comparisonColumns"
              row-key="measurement"
              flat
              :pagination="{ rowsPerPage: 10 }"
              :loading="analyzing"
            >
              <template #body-cell-measurement="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-chip color="primary" text-color="white" size="sm">
                      {{ props.value }}
                    </q-chip>
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click="previewMeasurement(props.value)"
                    >
                      <q-tooltip>Preview</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </template>
              <template #body-cell-tags="props">
                <q-td :props="props">
                  <q-chip color="green" outline size="sm">
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>
              <template #body-cell-fields="props">
                <q-td :props="props">
                  <q-chip color="orange" outline size="sm">
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>
              <template #body-cell-size="props">
                <q-td :props="props">
                  {{ formatBytes(props.value) }}
                </q-td>
              </template>
              <template #body-cell-quality="props">
                <q-td :props="props">
                  <q-linear-progress
                    :value="props.value / 100"
                    :color="getQualityColor(props.value)"
                    size="20px"
                    class="q-mt-sm"
                  />
                  <div class="text-center text-caption">{{ props.value }}%</div>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Field Analysis -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="text-h6">
              <q-icon name="insights" class="q-mr-sm" />
              Field Distribution
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="fieldDistribution.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="pie_chart" size="2rem" class="q-mb-sm" />
              <div>No field data available</div>
            </div>
            <div v-else>
              <div v-for="field in fieldDistribution" :key="field.name" class="q-mb-md">
                <div class="row items-center q-gutter-sm q-mb-xs">
                  <q-icon :name="getFieldTypeIcon(field.type)" :color="getFieldTypeColor(field.type)" />
                  <div class="text-body2">{{ field.name }}</div>
                  <q-space />
                  <q-chip :color="getFieldTypeColor(field.type)" text-color="white" size="sm">
                    {{ field.count }}
                  </q-chip>
                </div>
                <q-linear-progress
                  :value="field.percentage / 100"
                  :color="getFieldTypeColor(field.type)"
                  size="8px"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Data Quality Insights -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-purple-1">
            <div class="text-h6">
              <q-icon name="verified" class="q-mr-sm" />
              Data Quality Insights
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="qualityInsights.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="verified" size="2rem" class="q-mb-sm" />
              <div>No quality issues found</div>
            </div>
            <q-list v-else dense>
              <q-item v-for="insight in qualityInsights" :key="insight.id">
                <q-item-section avatar>
                  <q-icon
                    :name="getInsightIcon(insight.type)"
                    :color="getInsightColor(insight.type)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ insight.title }}</q-item-label>
                  <q-item-label caption>{{ insight.description }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip
                    :color="getInsightColor(insight.type)"
                    text-color="white"
                    size="sm"
                  >
                    {{ insight.severity }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Performance Analysis -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-red-1">
            <div class="text-h6">
              <q-icon name="speed" class="q-mr-sm" />
              Performance Analysis
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <!-- Query Performance -->
              <div class="col-12 col-md-6">
                <div class="text-subtitle2 q-mb-sm">Query Performance</div>
                <q-list dense>
                  <q-item v-for="perf in performanceMetrics" :key="perf.measurement">
                    <q-item-section>
                      <q-item-label>{{ perf.measurement }}</q-item-label>
                      <q-item-label caption>
                        Avg: {{ perf.avgTime }}ms | Max: {{ perf.maxTime }}ms
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-circular-progress
                        :value="getPerformanceScore(perf.avgTime)"
                        size="40px"
                        :thickness="0.15"
                        :color="getPerformanceColor(perf.avgTime)"
                        track-color="grey-3"
                        show-value
                        font-size="10px"
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Resource Usage -->
              <div class="col-12 col-md-6">
                <div class="text-subtitle2 q-mb-sm">Resource Usage</div>
                <div class="row q-gutter-sm">
                  <div class="col-12">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="memory" color="blue" />
                      <div class="text-body2">Memory Usage</div>
                      <q-space />
                      <div class="text-body2">{{ resourceUsage.memory }}%</div>
                    </div>
                    <q-linear-progress
                      :value="resourceUsage.memory / 100"
                      color="blue"
                      size="8px"
                      class="q-mt-xs"
                    />
                  </div>
                  <div class="col-12">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="computer" color="green" />
                      <div class="text-body2">CPU Usage</div>
                      <q-space />
                      <div class="text-body2">{{ resourceUsage.cpu }}%</div>
                    </div>
                    <q-linear-progress
                      :value="resourceUsage.cpu / 100"
                      color="green"
                      size="8px"
                      class="q-mt-xs"
                    />
                  </div>
                  <div class="col-12">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="network_check" color="orange" />
                      <div class="text-body2">Network I/O</div>
                      <q-space />
                      <div class="text-body2">{{ resourceUsage.network }}%</div>
                    </div>
                    <q-linear-progress
                      :value="resourceUsage.network / 100"
                      color="orange"
                      size="8px"
                      class="q-mt-xs"
                    />
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="text-h6">
              <q-icon name="lightbulb" class="q-mr-sm" />
              Optimization Recommendations
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="recommendations.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="check_circle" size="2rem" color="positive" class="q-mb-sm" />
              <div>No optimization recommendations at this time</div>
            </div>
            <q-list v-else>
              <q-item v-for="rec in recommendations" :key="rec.id">
                <q-item-section avatar>
                  <q-icon
                    :name="getRecommendationIcon(rec.type)"
                    :color="getRecommendationColor(rec.type)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ rec.title }}</q-item-label>
                  <q-item-label caption>{{ rec.description }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="column q-gutter-xs">
                    <q-chip
                      :color="getImpactColor(rec.impact)"
                      text-color="white"
                      size="sm"
                    >
                      {{ rec.impact }} Impact
                    </q-chip>
                    <q-btn
                      label="Apply"
                      size="sm"
                      color="primary"
                      outline
                      @click="applyRecommendation(rec)"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Preview Dialog -->
    <q-dialog v-model="showPreviewDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Measurement Preview: {{ previewMeasurementName }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showPreviewDialog = false" />
        </q-card-section>
        <q-card-section class="scroll">
          <div v-if="previewData" class="row q-gutter-md">
            <!-- Preview content would go here -->
            <div class="col-12">
              <q-table
                :rows="previewData.sampleData"
                :columns="previewData.columns"
                flat
                dense
                :pagination="{ rowsPerPage: 50 }"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  measurements: {
    type: Array,
    default: () => []
  },
  schema: {
    type: Object,
    default: null
  },
  source: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['analyze-measurement', 'preview-measurement'])

// Reactive data
const $q = useQuasar()
const selectedMeasurements = ref([])
const analysisType = ref('comprehensive')
const timeRange = ref('24h')
const analyzing = ref(false)
const refreshing = ref(false)
const showPreviewDialog = ref(false)
const previewMeasurementName = ref('')
const previewData = ref(null)

const analysisResults = ref(null)
const comparisonData = ref([])
const fieldDistribution = ref([])
const qualityInsights = ref([])
const performanceMetrics = ref([])
const recommendations = ref([])

// Resource usage (would come from API)
const resourceUsage = ref({
  memory: 65,
  cpu: 42,
  network: 28
})

// Computed properties
const measurementOptions = computed(() => {
  return props.measurements.map(measurement => ({
    label: measurement,
    value: measurement
  }))
})

const analysisOptions = [
  { label: 'Comprehensive Analysis', value: 'comprehensive' },
  { label: 'Performance Analysis', value: 'performance' },
  { label: 'Quality Analysis', value: 'quality' },
  { label: 'Schema Analysis', value: 'schema' }
]

const timeRangeOptions = [
  { label: 'Last Hour', value: '1h' },
  { label: 'Last 24 Hours', value: '24h' },
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' }
]

const comparisonColumns = [
  {
    name: 'measurement',
    label: 'Measurement',
    field: 'measurement',
    align: 'left',
    sortable: true
  },
  {
    name: 'tags',
    label: 'Tags',
    field: 'tags',
    align: 'center',
    sortable: true
  },
  {
    name: 'fields',
    label: 'Fields',
    field: 'fields',
    align: 'center',
    sortable: true
  },
  {
    name: 'size',
    label: 'Data Size',
    field: 'size',
    align: 'center',
    sortable: true
  },
  {
    name: 'quality',
    label: 'Quality Score',
    field: 'quality',
    align: 'center',
    sortable: true
  },
  {
    name: 'responseTime',
    label: 'Avg Response (ms)',
    field: 'responseTime',
    align: 'center',
    sortable: true
  }
]

// Methods
const getTagsCount = (measurement) => {
  return props.schema?.tags?.[measurement]?.length || 0
}

const getFieldsCount = (measurement) => {
  return props.schema?.fields?.[measurement]?.length || 0
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getQualityColor = (score) => {
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
}

const getFieldTypeIcon = (type) => {
  const icons = {
    number: '123',
    string: 'abc',
    boolean: 'toggle_on',
    datetime: 'schedule'
  }
  return icons[type] || 'help'
}

const getFieldTypeColor = (type) => {
  const colors = {
    number: 'blue',
    string: 'green',
    boolean: 'orange',
    datetime: 'purple'
  }
  return colors[type] || 'grey'
}

const getInsightIcon = (type) => {
  const icons = {
    warning: 'warning',
    error: 'error',
    info: 'info',
    success: 'check_circle'
  }
  return icons[type] || 'help'
}

const getInsightColor = (type) => {
  const colors = {
    warning: 'warning',
    error: 'negative',
    info: 'info',
    success: 'positive'
  }
  return colors[type] || 'grey'
}

const getPerformanceScore = (avgTime) => {
  // Convert response time to score (lower is better)
  if (avgTime <= 100) return 100
  if (avgTime <= 500) return 80
  if (avgTime <= 1000) return 60
  if (avgTime <= 2000) return 40
  return 20
}

const getPerformanceColor = (avgTime) => {
  if (avgTime <= 100) return 'positive'
  if (avgTime <= 500) return 'warning'
  return 'negative'
}

const getRecommendationIcon = (type) => {
  const icons = {
    performance: 'speed',
    quality: 'verified',
    storage: 'storage',
    network: 'network_check'
  }
  return icons[type] || 'lightbulb'
}

const getRecommendationColor = (type) => {
  const colors = {
    performance: 'blue',
    quality: 'green',
    storage: 'orange',
    network: 'purple'
  }
  return colors[type] || 'grey'
}

const getImpactColor = (impact) => {
  const colors = {
    High: 'positive',
    Medium: 'warning',
    Low: 'info'
  }
  return colors[impact] || 'grey'
}

const updateAnalysis = () => {
  if (selectedMeasurements.value.length > 0) {
    runAnalysis()
  }
}

const runAnalysis = async () => {
  if (selectedMeasurements.value.length === 0) {
    $q.notify({
      type: 'warning',
      message: 'Please select at least one measurement to analyze'
    })
    return
  }

  analyzing.value = true

  try {
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Generate mock analysis results
    analysisResults.value = {
      totalMeasurements: selectedMeasurements.value.length,
      totalDataSize: Math.random() * 1000000000, // Random bytes
      avgResponseTime: Math.floor(Math.random() * 500 + 100),
      dataPoints: Math.floor(Math.random() * 100000 + 10000)
    }

    // Generate comparison data
    comparisonData.value = selectedMeasurements.value.map(measurement => ({
      measurement,
      tags: getTagsCount(measurement),
      fields: getFieldsCount(measurement),
      size: Math.random() * 50000000,
      quality: Math.floor(Math.random() * 30 + 70),
      responseTime: Math.floor(Math.random() * 400 + 100)
    }))

    // Generate field distribution
    fieldDistribution.value = [
      { name: 'Voltage Fields', type: 'number', count: 15, percentage: 35 },
      { name: 'Current Fields', type: 'number', count: 12, percentage: 28 },
      { name: 'Status Fields', type: 'string', count: 8, percentage: 19 },
      { name: 'Timestamp Fields', type: 'datetime', count: 5, percentage: 12 },
      { name: 'Boolean Fields', type: 'boolean', count: 3, percentage: 6 }
    ]

    // Generate quality insights
    qualityInsights.value = [
      {
        id: 1,
        type: 'warning',
        title: 'Missing Data Points',
        description: 'Some measurements have gaps in data',
        severity: 'Medium'
      },
      {
        id: 2,
        type: 'info',
        title: 'High Data Variance',
        description: 'Voltage readings show high variance',
        severity: 'Low'
      }
    ]

    // Generate performance metrics
    performanceMetrics.value = selectedMeasurements.value.map(measurement => ({
      measurement,
      avgTime: Math.floor(Math.random() * 300 + 50),
      maxTime: Math.floor(Math.random() * 800 + 200)
    }))

    // Generate recommendations
    recommendations.value = [
      {
        id: 1,
        type: 'performance',
        title: 'Add Database Index',
        description: 'Adding an index on timestamp field could improve query performance',
        impact: 'High'
      },
      {
        id: 2,
        type: 'quality',
        title: 'Data Validation Rules',
        description: 'Implement validation rules for voltage range checks',
        impact: 'Medium'
      }
    ]

    $q.notify({
      type: 'positive',
      message: 'Analysis completed successfully',
      caption: `Analyzed ${selectedMeasurements.value.length} measurement(s)`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Analysis failed',
      caption: error.message
    })
  } finally {
    analyzing.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    if (selectedMeasurements.value.length > 0) {
      await runAnalysis()
    }
  } finally {
    refreshing.value = false
  }
}

const previewMeasurement = async (measurementName) => {
  previewMeasurementName.value = measurementName

  // Generate mock preview data
  previewData.value = {
    columns: [
      { name: 'timestamp', label: 'Timestamp', field: 'timestamp', align: 'left' },
      { name: 'rack', label: 'Rack', field: 'rack', align: 'center' },
      { name: 'voltage', label: 'Voltage', field: 'voltage', align: 'center' },
      { name: 'current', label: 'Current', field: 'current', align: 'center' }
    ],
    sampleData: Array.from({ length: 20 }, (_, i) => ({
      timestamp: new Date(Date.now() - i * 60000).toISOString(),
      rack: Math.floor(Math.random() * 10 + 1),
      voltage: (Math.random() * 5 + 45).toFixed(2),
      current: (Math.random() * 10 + 5).toFixed(2)
    }))
  }

  showPreviewDialog.value = true
  emit('preview-measurement', measurementName)
}

const applyRecommendation = (recommendation) => {
  $q.notify({
    type: 'info',
    message: `Applying recommendation: ${recommendation.title}`,
    caption: 'This feature is coming soon'
  })
}

// Lifecycle
onMounted(() => {
  // Auto-select first measurement if available
  if (props.measurements.length > 0) {
    selectedMeasurements.value = [props.measurements[0]]
    runAnalysis()
  }
})

// Watchers
watch(() => props.measurements, (newMeasurements) => {
  if (newMeasurements.length > 0 && selectedMeasurements.value.length === 0) {
    selectedMeasurements.value = [newMeasurements[0]]
    runAnalysis()
  }
})
</script>

<style scoped>
.measurements-analysis {
  width: 100%;
}

.text-h5 {
  font-weight: 600;
}

.q-chip {
  font-size: 11px;
}

.q-linear-progress {
  border-radius: 4px;
}
</style>
