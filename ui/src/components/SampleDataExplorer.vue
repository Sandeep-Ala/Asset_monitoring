<!-- ui/src/components/SampleDataExplorer.vue -->
<template>
  <div class="sample-data-explorer q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Sample Data</div>
        <div class="text-subtitle2 text-grey-6">
          {{ data.length }} sample records from {{ measurement }}
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Refresh Sample"
          icon="refresh"
          color="primary"
          outline
          @click="$emit('refresh')"
          :loading="loading"
        />
        <q-btn
          label="Export Sample"
          icon="file_download"
          color="secondary"
          outline
          @click="exportSample"
        />
        <q-btn
          label="Get More Data"
          icon="add"
          color="positive"
          outline
          @click="getMoreData"
          :loading="loadingMore"
        />
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="table_rows" size="2rem" color="blue" class="q-mb-sm" />
            <div class="text-h6">{{ data.length }}</div>
            <div class="text-caption text-grey-6">Total Records</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="view_column" size="2rem" color="green" class="q-mb-sm" />
            <div class="text-h6">{{ columnCount }}</div>
            <div class="text-caption text-grey-6">Columns</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="assessment" size="2rem" color="orange" class="q-mb-sm" />
            <div class="text-h6">{{ dataCompleteness }}%</div>
            <div class="text-caption text-grey-6">Data Completeness</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="memory" size="2rem" color="purple" class="q-mb-sm" />
            <div class="text-h6">{{ dataSize }}</div>
            <div class="text-caption text-grey-6">Estimated Size</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Analysis Tabs -->
    <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
      <q-tab name="table" label="Data Table" icon="table_view" />
      <q-tab name="columns" label="Column Analysis" icon="view_column" />
      <q-tab name="quality" label="Data Quality" icon="verified" />
      <q-tab name="statistics" label="Statistics" icon="bar_chart" />
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-tab-panels v-model="activeTab" animated class="q-mt-md">
      <!-- Data Table Tab -->
      <q-tab-panel name="table">
        <SampleDataTable
          :data="data"
          :compact="false"
          :loading="loading"
        />
      </q-tab-panel>

      <!-- Column Analysis Tab -->
      <q-tab-panel name="columns">
        <div class="row q-gutter-md">
          <div class="col-12">
            <q-input
              v-model="columnSearchQuery"
              placeholder="Search columns..."
              outlined
              dense
              clearable
            >
              <template #prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>

          <div class="col-12">
            <q-list separator bordered>
              <q-item
                v-for="column in filteredColumns"
                :key="column.name"
                clickable
                @click="analyzeColumn(column)"
              >
                <q-item-section avatar>
                  <q-avatar :color="getColumnTypeColor(column.type)" text-color="white" size="md">
                    <q-icon :name="getColumnTypeIcon(column.type)" />
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label class="text-h6">{{ column.name }}</q-item-label>
                  <q-item-label caption>
                    {{ column.type }} • {{ column.nullCount }} nulls • {{ column.uniqueCount }} unique values
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="column q-gutter-xs">
                    <q-chip
                      :color="getQualityColor(column.quality)"
                      text-color="white"
                      size="sm"
                    >
                      {{ column.quality }}% Quality
                    </q-chip>

                    <div class="row q-gutter-xs">
                      <q-btn
                        icon="analytics"
                        flat
                        round
                        size="sm"
                        @click.stop="analyzeColumn(column)"
                        title="Analyze Column"
                      />
                      <q-btn
                        icon="show_chart"
                        flat
                        round
                        size="sm"
                        @click.stop="showColumnChart(column)"
                        title="Show Chart"
                      />
                      <q-btn
                        icon="info"
                        flat
                        round
                        size="sm"
                        @click.stop="showColumnDetails(column)"
                        title="Column Details"
                      />
                    </div>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>
      </q-tab-panel>

      <!-- Data Quality Tab -->
      <q-tab-panel name="quality">
        <div class="row q-gutter-lg">
          <!-- Overall Quality Score -->
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section class="text-center">
                <q-circular-progress
                  :value="overallQuality"
                  size="120px"
                  :thickness="0.2"
                  color="primary"
                  track-color="grey-3"
                  class="q-mb-md"
                >
                  <div class="text-h4">{{ Math.round(overallQuality) }}%</div>
                </q-circular-progress>
                <div class="text-h6">Overall Quality Score</div>
                <div class="text-caption text-grey-6">Data completeness and consistency</div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Quality Metrics -->
          <div class="col-12 col-md-8">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Quality Metrics</div>

                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="check_circle" color="positive" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Complete Records</q-item-label>
                      <q-item-label caption>Records with all non-null values</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="positive" text-color="white">
                        {{ completeRecords }} / {{ data.length }}
                      </q-chip>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="content_copy" color="blue" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Duplicate Records</q-item-label>
                      <q-item-label caption>Potentially duplicate rows</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="blue" text-color="white">
                        {{ duplicateRecords }}
                      </q-chip>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="error" color="negative" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Data Issues</q-item-label>
                      <q-item-label caption>Columns with quality issues</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="negative" text-color="white">
                        {{ issueColumns }}
                      </q-chip>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="schedule" color="orange" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Data Freshness</q-item-label>
                      <q-item-label caption>Time since last update</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="orange" text-color="white">
                        {{ dataFreshness }}
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Quality Issues -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Quality Issues</div>

                <q-list v-if="qualityIssues.length > 0" separator>
                  <q-item
                    v-for="issue in qualityIssues"
                    :key="issue.column + issue.type"
                  >
                    <q-item-section avatar>
                      <q-icon
                        :name="getIssueIcon(issue.severity)"
                        :color="getIssueColor(issue.severity)"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ issue.column }}: {{ issue.description }}</q-item-label>
                      <q-item-label caption>{{ issue.details }}</q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <q-chip
                        :color="getIssueColor(issue.severity)"
                        text-color="white"
                        size="sm"
                      >
                        {{ issue.severity }}
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-lg text-grey-6">
                  <q-icon name="verified" size="3rem" class="q-mb-md text-positive" />
                  <div class="text-h6">No Quality Issues Found</div>
                  <div class="text-body2">Your data appears to be in good condition</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Statistics Tab -->
      <q-tab-panel name="statistics">
        <div class="row q-gutter-md">
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Numeric Columns Summary</div>

                <q-list v-if="numericColumns.length > 0">
                  <q-item v-for="column in numericColumns" :key="column.name">
                    <q-item-section>
                      <q-item-label>{{ column.name }}</q-item-label>
                      <q-item-label caption>
                        Mean: {{ column.stats.mean }} •
                        Min: {{ column.stats.min }} •
                        Max: {{ column.stats.max }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-md text-grey-6">
                  <q-icon name="functions" size="2rem" class="q-mb-sm" />
                  <div>No numeric columns found</div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Text Columns Summary</div>

                <q-list v-if="textColumns.length > 0">
                  <q-item v-for="column in textColumns" :key="column.name">
                    <q-item-section>
                      <q-item-label>{{ column.name }}</q-item-label>
                      <q-item-label caption>
                        Unique: {{ column.stats.unique }} •
                        Avg Length: {{ column.stats.avgLength }} •
                        Max Length: {{ column.stats.maxLength }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-md text-grey-6">
                  <q-icon name="text_fields" size="2rem" class="q-mb-sm" />
                  <div>No text columns found</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>

    <!-- Column Details Dialog -->
    <q-dialog v-model="showColumnDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Column Details: {{ selectedColumn?.name }}</div>
        </q-card-section>

        <q-card-section v-if="selectedColumn">
          <div class="row q-gutter-lg">
            <div class="col-12 col-md-6">
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="label" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Column Name</q-item-label>
                    <q-item-label>{{ selectedColumn.name }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="category" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Data Type</q-item-label>
                    <q-item-label>{{ selectedColumn.type }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="format_list_numbered" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Unique Values</q-item-label>
                    <q-item-label>{{ selectedColumn.uniqueCount }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="error_outline" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Null Values</q-item-label>
                    <q-item-label>{{ selectedColumn.nullCount }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">Sample Values</div>
              <q-list dense>
                <q-item v-for="value in selectedColumn.sampleValues" :key="value">
                  <q-item-section>
                    <q-chip size="sm" color="blue-grey" text-color="white">
                      {{ formatValue(value) }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Analyze"
            icon="analytics"
            color="primary"
            outline
            @click="analyzeColumn(selectedColumn)"
          />
          <q-btn label="Close" flat @click="showColumnDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Import sub-components
import SampleDataTable from 'src/components/SampleDataTable.vue'

// Props
const props = defineProps({
  data: Array,
  measurement: String,
  loading: Boolean
})

// Emits
const emit = defineEmits(['refresh'])

// Reactive data
const $q = useQuasar()
const activeTab = ref('table')
const columnSearchQuery = ref('')
const loadingMore = ref(false)
const showColumnDialog = ref(false)
const selectedColumn = ref(null)

// Computed properties
const columnCount = computed(() => {
  if (props.data.length === 0) return 0
  return Object.keys(props.data[0]).length
})

const dataCompleteness = computed(() => {
  if (props.data.length === 0) return 0

  const totalCells = props.data.length * columnCount.value
  const nonNullCells = props.data.reduce((count, row) => {
    return count + Object.values(row).filter(val => val != null).length
  }, 0)

  return Math.round((nonNullCells / totalCells) * 100)
})

const dataSize = computed(() => {
  const bytes = JSON.stringify(props.data).length
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
})

const columns = computed(() => {
  if (props.data.length === 0) return []

  const firstRow = props.data[0]
  return Object.keys(firstRow).map(columnName => {
    const columnData = props.data.map(row => row[columnName])
    const nonNullData = columnData.filter(val => val != null)

    return {
      name: columnName,
      type: getColumnType(columnName),
      nullCount: columnData.length - nonNullData.length,
      uniqueCount: new Set(nonNullData).size,
      quality: Math.round((nonNullData.length / columnData.length) * 100),
      sampleValues: [...new Set(nonNullData)].slice(0, 10)
    }
  })
})

const filteredColumns = computed(() => {
  if (!columnSearchQuery.value) return columns.value

  const query = columnSearchQuery.value.toLowerCase()
  return columns.value.filter(column =>
    column.name.toLowerCase().includes(query)
  )
})

const numericColumns = computed(() => {
  return columns.value
    .filter(col => col.type === 'number')
    .map(col => {
      const values = props.data
        .map(row => row[col.name])
        .filter(val => typeof val === 'number')

      return {
        ...col,
        stats: {
          mean: values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2) : 0,
          min: values.length > 0 ? Math.min(...values) : 0,
          max: values.length > 0 ? Math.max(...values) : 0
        }
      }
    })
})

const textColumns = computed(() => {
  return columns.value
    .filter(col => col.type === 'string')
    .map(col => {
      const values = props.data
        .map(row => row[col.name])
        .filter(val => typeof val === 'string')

      return {
        ...col,
        stats: {
          unique: new Set(values).size,
          avgLength: values.length > 0 ? Math.round(values.reduce((sum, val) => sum + val.length, 0) / values.length) : 0,
          maxLength: values.length > 0 ? Math.max(...values.map(val => val.length)) : 0
        }
      }
    })
})

const overallQuality = computed(() => {
  if (columns.value.length === 0) return 0
  const totalQuality = columns.value.reduce((sum, col) => sum + col.quality, 0)
  return totalQuality / columns.value.length
})

const completeRecords = computed(() => {
  return props.data.filter(row =>
    Object.values(row).every(val => val != null)
  ).length
})

const duplicateRecords = computed(() => {
  const seen = new Set()
  let duplicates = 0

  props.data.forEach(row => {
    const key = JSON.stringify(row)
    if (seen.has(key)) {
      duplicates++
    } else {
      seen.add(key)
    }
  })

  return duplicates
})

const issueColumns = computed(() => {
  return columns.value.filter(col => col.quality < 90).length
})

const dataFreshness = computed(() => {
  // This would typically be calculated based on timestamp columns
  return 'Real-time'
})

const qualityIssues = computed(() => {
  const issues = []

  columns.value.forEach(column => {
    if (column.quality < 50) {
      issues.push({
        column: column.name,
        severity: 'critical',
        description: 'High null value percentage',
        details: `${Math.round(100 - column.quality)}% of values are null`
      })
    } else if (column.quality < 90) {
      issues.push({
        column: column.name,
        severity: 'warning',
        description: 'Some missing values',
        details: `${Math.round(100 - column.quality)}% of values are null`
      })
    }

    if (column.uniqueCount === 1 && column.nullCount === 0) {
      issues.push({
        column: column.name,
        severity: 'info',
        description: 'Constant value',
        details: 'All values are identical'
      })
    }
  })

  return issues
})

// Methods
onMounted(() => {
  // Initialize any needed data
})

const getColumnType = (columnName) => {
  if (props.data.length === 0) return 'unknown'

  const samples = props.data.slice(0, 10).map(row => row[columnName])
  const nonNullSamples = samples.filter(val => val != null)

  if (nonNullSamples.length === 0) return 'unknown'

  const firstValue = nonNullSamples[0]
  if (typeof firstValue === 'boolean') return 'boolean'
  if (typeof firstValue === 'number') return 'number'
  if (typeof firstValue === 'string' && !isNaN(Date.parse(firstValue))) return 'datetime'
  return 'string'
}

const getColumnTypeColor = (type) => {
  const colors = {
    'number': 'green',
    'string': 'blue',
    'boolean': 'purple',
    'datetime': 'orange',
    'unknown': 'grey'
  }
  return colors[type] || 'grey'
}

const getColumnTypeIcon = (type) => {
  const icons = {
    'number': 'functions',
    'string': 'text_fields',
    'boolean': 'toggle_on',
    'datetime': 'schedule',
    'unknown': 'help'
  }
  return icons[type] || 'help'
}

const getQualityColor = (quality) => {
  if (quality >= 90) return 'positive'
  if (quality >= 70) return 'warning'
  return 'negative'
}

const getIssueIcon = (severity) => {
  const icons = {
    'critical': 'error',
    'warning': 'warning',
    'info': 'info'
  }
  return icons[severity] || 'info'
}

const getIssueColor = (severity) => {
  const colors = {
    'critical': 'negative',
    'warning': 'warning',
    'info': 'info'
  }
  return colors[severity] || 'info'
}

const formatValue = (value) => {
  if (typeof value === 'string' && value.length > 30) {
    return value.substring(0, 30) + '...'
  }
  return String(value)
}

const analyzeColumn = (column) => {
  $q.notify({
    type: 'info',
    message: `Analyzing column: ${column.name}`,
    caption: 'Detailed analysis coming soon'
  })
}

const showColumnChart = (column) => {
  $q.notify({
    type: 'info',
    message: `Chart for column: ${column.name}`,
    caption: 'Chart visualization coming soon'
  })
}

const showColumnDetails = (column) => {
  selectedColumn.value = column
  showColumnDialog.value = true
}

const getMoreData = async () => {
  loadingMore.value = true

  try {
    // Simulate getting more data
    await new Promise(resolve => setTimeout(resolve, 1000))

    $q.notify({
      type: 'info',
      message: 'Get more data functionality coming soon'
    })
  } finally {
    loadingMore.value = false
  }
}

const exportSample = () => {
  const csvContent = convertToCSV(props.data)
  downloadCSV(csvContent, `${props.measurement || 'sample'}_data.csv`)

  $q.notify({
    type: 'positive',
    message: 'Sample data exported successfully',
    icon: 'file_download'
  })
}

const convertToCSV = (data) => {
  if (data.length === 0) return ''

  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row =>
    Object.values(row).map(value => {
      if (value == null) return ''
      const stringValue = String(value)
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`
      }
      return stringValue
    }).join(',')
  )

  return [headers, ...rows].join('\n')
}

const downloadCSV = (content, filename) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')

  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}
</script>

<style scoped>
.sample-data-explorer {
  background-color: #fafafa;
  min-height: 100%;
}

.stat-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

/* Custom scrollbar */
.q-list {
  max-height: 400px;
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .row.q-gutter-md {
    margin: -8px;
  }

  .row.q-gutter-md > div {
    padding: 8px;
  }
}
</style>
