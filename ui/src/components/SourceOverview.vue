<!-- ui/src/components/SchemaOverview.vue -->
<!-- Schema summary dashboard component -->

<template>
  <div class="schema-overview">
    <!-- Quick Stats Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-6 col-md-3">
        <q-card flat class="bg-blue-1 text-center q-pa-md">
          <q-icon name="table_chart" size="2rem" color="blue" class="q-mb-sm" />
          <div class="text-h4">{{ measurementsCount }}</div>
          <div class="text-body2">Measurements</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-green-1 text-center q-pa-md">
          <q-icon name="label" size="2rem" color="green" class="q-mb-sm" />
          <div class="text-h4">{{ totalTags }}</div>
          <div class="text-body2">Tags</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-orange-1 text-center q-pa-md">
          <q-icon name="data_object" size="2rem" color="orange" class="q-mb-sm" />
          <div class="text-h4">{{ totalFields }}</div>
          <div class="text-body2">Fields</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-purple-1 text-center q-pa-md">
          <q-icon name="speed" size="2rem" color="purple" class="q-mb-sm" />
          <div class="text-h4">{{ schemaScore }}%</div>
          <div class="text-body2">Schema Quality</div>
        </q-card>
      </div>
    </div>

    <!-- Schema Health Status -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="text-h6">
              <q-icon name="health_and_safety" class="q-mr-sm" />
              Schema Health Status
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <!-- Health Indicators -->
              <div class="col-12 col-md-8">
                <div class="row q-gutter-sm">
                  <div class="col-6 col-md-3">
                    <div class="text-center">
                      <q-circular-progress
                        :value="healthMetrics.completeness"
                        size="60px"
                        :thickness="0.15"
                        color="green"
                        track-color="grey-3"
                        show-value
                        font-size="12px"
                      />
                      <div class="text-caption q-mt-xs">Completeness</div>
                    </div>
                  </div>
                  <div class="col-6 col-md-3">
                    <div class="text-center">
                      <q-circular-progress
                        :value="healthMetrics.consistency"
                        size="60px"
                        :thickness="0.15"
                        color="blue"
                        track-color="grey-3"
                        show-value
                        font-size="12px"
                      />
                      <div class="text-caption q-mt-xs">Consistency</div>
                    </div>
                  </div>
                  <div class="col-6 col-md-3">
                    <div class="text-center">
                      <q-circular-progress
                        :value="healthMetrics.validity"
                        size="60px"
                        :thickness="0.15"
                        color="orange"
                        track-color="grey-3"
                        show-value
                        font-size="12px"
                      />
                      <div class="text-caption q-mt-xs">Validity</div>
                    </div>
                  </div>
                  <div class="col-6 col-md-3">
                    <div class="text-center">
                      <q-circular-progress
                        :value="healthMetrics.freshness"
                        size="60px"
                        :thickness="0.15"
                        color="red"
                        track-color="grey-3"
                        show-value
                        font-size="12px"
                      />
                      <div class="text-caption q-mt-xs">Freshness</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quick Actions -->
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">Quick Actions</div>
                <div class="column q-gutter-sm">
                  <q-btn
                    label="Refresh Schema"
                    icon="refresh"
                    color="primary"
                    size="sm"
                    @click="refreshSchema"
                    :loading="refreshing"
                  />
                  <q-btn
                    label="Export Schema"
                    icon="download"
                    color="secondary"
                    outline
                    size="sm"
                    @click="exportSchema"
                  />
                  <q-btn
                    label="Run Quality Check"
                    icon="verified"
                    color="warning"
                    outline
                    size="sm"
                    @click="runQualityCheck"
                    :loading="checkingQuality"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Measurements Overview -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">
              <q-icon name="table_chart" class="q-mr-sm" />
              Measurements Overview
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="!schema || !schema.measurements || schema.measurements.length === 0"
                 class="text-center q-pa-lg">
              <q-icon name="table_chart" size="3rem" class="text-grey-4 q-mb-md" />
              <div class="text-h6 text-grey-6">No Measurements Found</div>
              <div class="text-body2 text-grey-5 q-mb-lg">
                Run schema discovery to find available measurements
              </div>
              <q-btn
                label="Discover Measurements"
                icon="search"
                color="primary"
                @click="discoverMeasurements"
                :loading="discovering"
              />
            </div>
            <div v-else>
              <q-table
                :rows="measurementRows"
                :columns="measurementColumns"
                row-key="name"
                flat
                :pagination="{ rowsPerPage: 10 }"
              >
                <template #body-cell-name="props">
                  <q-td :props="props">
                    <q-chip color="primary" text-color="white" size="sm">
                      {{ props.value }}
                    </q-chip>
                  </q-td>
                </template>
                <template #body-cell-tags="props">
                  <q-td :props="props">
                    <q-chip color="green" outline size="sm">
                      {{ props.value }} tags
                    </q-chip>
                  </q-td>
                </template>
                <template #body-cell-fields="props">
                  <q-td :props="props">
                    <q-chip color="orange" outline size="sm">
                      {{ props.value }} fields
                    </q-chip>
                  </q-td>
                </template>
                <template #body-cell-actions="props">
                  <q-td :props="props">
                    <div class="q-gutter-sm">
                      <q-btn
                        icon="visibility"
                        flat
                        round
                        size="sm"
                        color="primary"
                        @click="discoverMeasurement(props.row.name)"
                      >
                        <q-tooltip>View Details</q-tooltip>
                      </q-btn>
                      <q-btn
                        icon="link"
                        flat
                        round
                        size="sm"
                        color="secondary"
                        @click="createMapping(props.row.name)"
                      >
                        <q-tooltip>Create Mapping</q-tooltip>
                      </q-btn>
                    </div>
                  </q-td>
                </template>
              </q-table>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Types Distribution -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="donut_small" class="q-mr-sm" />
              Data Types Distribution
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-sm">
              <div v-for="type in dataTypeStats" :key="type.name" class="col-6 col-md-12">
                <div class="row items-center q-gutter-sm">
                  <q-icon :name="getTypeIcon(type.name)" :color="getTypeColor(type.name)" />
                  <div class="text-body2">{{ type.name }}</div>
                  <q-space />
                  <q-chip :color="getTypeColor(type.name)" text-color="white" size="sm">
                    {{ type.count }}
                  </q-chip>
                </div>
                <q-linear-progress
                  :value="type.percentage / 100"
                  :color="getTypeColor(type.name)"
                  size="8px"
                  class="q-mt-xs"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Schema Issues -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-red-1">
            <div class="text-h6">
              <q-icon name="warning" class="q-mr-sm" />
              Schema Issues
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="schemaIssues.length === 0" class="text-center q-pa-md">
              <q-icon name="check_circle" size="2rem" color="positive" class="q-mb-sm" />
              <div class="text-body2 text-positive">No issues found</div>
            </div>
            <q-list v-else dense>
              <q-item v-for="issue in schemaIssues" :key="issue.id">
                <q-item-section avatar>
                  <q-icon
                    :name="getSeverityIcon(issue.severity)"
                    :color="getSeverityColor(issue.severity)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ issue.title }}</q-item-label>
                  <q-item-label caption>{{ issue.description }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn
                    icon="fix"
                    flat
                    round
                    size="sm"
                    color="primary"
                    @click="fixIssue(issue)"
                  >
                    <q-tooltip>Fix Issue</q-tooltip>
                  </q-btn>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-grey-1">
            <div class="text-h6">
              <q-icon name="history" class="q-mr-sm" />
              Recent Schema Activity
            </div>
          </q-card-section>
          <q-card-section>
            <q-timeline color="primary">
              <q-timeline-entry
                v-for="activity in recentActivity"
                :key="activity.id"
                :title="activity.title"
                :subtitle="activity.description"
                :icon="activity.icon"
                :color="activity.color"
              >
                <div class="text-caption text-grey-6">
                  {{ formatRelativeTime(activity.timestamp) }}
                </div>
              </q-timeline-entry>
            </q-timeline>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
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
const emit = defineEmits(['discover-measurement', 'create-mapping', 'refresh-schema'])

// Reactive data
const $q = useQuasar()
const refreshing = ref(false)
const discovering = ref(false)
const checkingQuality = ref(false)

// Health metrics (would come from API in real app)
const healthMetrics = ref({
  completeness: 85,
  consistency: 92,
  validity: 78,
  freshness: 95
})

// Schema issues (would come from API)
const schemaIssues = ref([
  {
    id: 1,
    severity: 'warning',
    title: 'Missing timestamp field',
    description: 'Some measurements lack proper timestamp fields'
  },
  {
    id: 2,
    severity: 'error',
    title: 'Duplicate field names',
    description: 'Field "voltage" appears in multiple measurements with different types'
  },
  {
    id: 3,
    severity: 'info',
    title: 'Optimization opportunity',
    description: 'Consider adding indexes for better query performance'
  }
])

// Recent activity (would come from API)
const recentActivity = ref([
  {
    id: 1,
    title: 'Schema Discovery',
    description: 'Discovered 5 new measurements',
    icon: 'search',
    color: 'primary',
    timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30 minutes ago
  },
  {
    id: 2,
    title: 'Quality Check',
    description: 'Schema quality improved to 85%',
    icon: 'verified',
    color: 'positive',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
  },
  {
    id: 3,
    title: 'Field Added',
    description: 'New field "temperature" detected',
    icon: 'add',
    color: 'secondary',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6) // 6 hours ago
  }
])

// Computed properties
const measurementsCount = computed(() => {
  return props.schema?.measurements?.length || 0
})

const totalTags = computed(() => {
  if (!props.schema?.tags) return 0
  return Object.values(props.schema.tags).reduce((sum, tags) => sum + tags.length, 0)
})

const totalFields = computed(() => {
  if (!props.schema?.fields) return 0
  return Object.values(props.schema.fields).reduce((sum, fields) => sum + fields.length, 0)
})

const schemaScore = computed(() => {
  const metrics = healthMetrics.value
  return Math.round((metrics.completeness + metrics.consistency + metrics.validity + metrics.freshness) / 4)
})

const measurementRows = computed(() => {
  if (!props.schema?.measurements) return []

  return props.schema.measurements.map(measurement => ({
    name: measurement,
    tags: props.schema.tags?.[measurement]?.length || 0,
    fields: props.schema.fields?.[measurement]?.length || 0,
    lastUpdated: new Date().toLocaleDateString()
  }))
})

const measurementColumns = [
  {
    name: 'name',
    label: 'Measurement',
    field: 'name',
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
    name: 'lastUpdated',
    label: 'Last Updated',
    field: 'lastUpdated',
    align: 'center',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Actions',
    field: 'actions',
    align: 'center'
  }
]

const dataTypeStats = computed(() => {
  // This would be calculated from actual schema data
  const stats = [
    { name: 'Number', count: 45, percentage: 60 },
    { name: 'String', count: 18, percentage: 24 },
    { name: 'Boolean', count: 8, percentage: 11 },
    { name: 'DateTime', count: 4, percentage: 5 }
  ]
  return stats
})

// Methods
const getTypeIcon = (type) => {
  const icons = {
    Number: '123',
    String: 'abc',
    Boolean: 'toggle_on',
    DateTime: 'schedule'
  }
  return icons[type] || 'help'
}

const getTypeColor = (type) => {
  const colors = {
    Number: 'blue',
    String: 'green',
    Boolean: 'orange',
    DateTime: 'purple'
  }
  return colors[type] || 'grey'
}

const getSeverityIcon = (severity) => {
  const icons = {
    error: 'error',
    warning: 'warning',
    info: 'info'
  }
  return icons[severity] || 'help'
}

const getSeverityColor = (severity) => {
  const colors = {
    error: 'negative',
    warning: 'warning',
    info: 'info'
  }
  return colors[severity] || 'grey'
}

const formatRelativeTime = (timestamp) => {
  const now = new Date()
  const diff = now - timestamp
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'Just now'
}

const refreshSchema = async () => {
  refreshing.value = true
  try {
    emit('refresh-schema')

    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 2000))

    $q.notify({
      type: 'positive',
      message: 'Schema refreshed successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to refresh schema',
      caption: error.message
    })
  } finally {
    refreshing.value = false
  }
}

const exportSchema = () => {
  const schemaData = {
    source: props.source,
    schema: props.schema,
    exportDate: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(schemaData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `schema-${props.source.source_name}-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Schema exported successfully'
  })
}

const runQualityCheck = async () => {
  checkingQuality.value = true
  try {
    // Simulate quality check
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Update health metrics
    healthMetrics.value = {
      completeness: Math.min(100, healthMetrics.value.completeness + Math.random() * 10),
      consistency: Math.min(100, healthMetrics.value.consistency + Math.random() * 5),
      validity: Math.min(100, healthMetrics.value.validity + Math.random() * 15),
      freshness: Math.min(100, healthMetrics.value.freshness + Math.random() * 3)
    }

    $q.notify({
      type: 'positive',
      message: 'Quality check completed',
      caption: `Schema score: ${schemaScore.value}%`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Quality check failed',
      caption: error.message
    })
  } finally {
    checkingQuality.value = false
  }
}

const discoverMeasurements = async () => {
  discovering.value = true
  try {
    emit('refresh-schema')
    await new Promise(resolve => setTimeout(resolve, 2000))
  } finally {
    discovering.value = false
  }
}

const discoverMeasurement = (measurementName) => {
  emit('discover-measurement', measurementName)
}

const createMapping = (measurementName) => {
  emit('create-mapping', measurementName)
}

const fixIssue = (issue) => {
  $q.notify({
    type: 'info',
    message: `Fixing issue: ${issue.title}`,
    caption: 'This feature is coming soon'
  })
}

// Lifecycle
onMounted(() => {
  // Initialize component
})
</script>

<style scoped>
.schema-overview {
  width: 100%;
}

.text-h4 {
  font-weight: 600;
}

.q-chip {
  font-size: 11px;
}

.q-timeline {
  padding: 0;
}
</style>
