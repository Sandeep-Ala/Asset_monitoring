<!-- ui/src/components/FieldsExplorer.vue -->
<template>
  <div class="fields-explorer q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Field Columns</div>
        <div class="text-subtitle2 text-grey-6">
          {{ fields.length }} field columns containing measurement values
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Refresh Fields"
          icon="refresh"
          color="primary"
          outline
          @click="$emit('refresh')"
          :loading="loading"
        />
        <q-btn
          label="Export Fields"
          icon="file_download"
          color="secondary"
          outline
          @click="exportFields"
        />
        <q-btn
          label="Analyze All"
          icon="analytics"
          color="positive"
          outline
          @click="analyzeAllFields"
          :loading="analyzing"
        />
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-4">
        <q-input
          v-model="searchQuery"
          placeholder="Search field columns..."
          outlined
          dense
          clearable
        >
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <div class="col-12 col-md-2">
        <q-select
          v-model="dataTypeFilter"
          :options="dataTypeOptions"
          label="Data Type"
          outlined
          dense
          clearable
          emit-value
          map-options
        />
      </div>

      <div class="col-12 col-md-2">
        <q-select
          v-model="sortBy"
          :options="sortOptions"
          label="Sort By"
          outlined
          dense
          emit-value
          map-options
        />
      </div>

      <div class="col-12 col-md-2">
        <q-select
          v-model="viewMode"
          :options="viewModeOptions"
          label="View Mode"
          outlined
          dense
          emit-value
          map-options
        />
      </div>

      <div class="col-12 col-md-2">
        <q-toggle
          v-model="showAdvancedStats"
          label="Advanced Stats"
          color="primary"
        />
      </div>
    </div>

    <!-- Fields Content -->
    <div v-if="filteredFields.length === 0" class="text-center q-pa-xl">
      <q-icon name="insights_off" size="4rem" class="text-grey-4 q-mb-md" />
      <div class="text-h6 text-grey-6 q-mb-sm">No Field Columns Found</div>
      <div class="text-body2 text-grey-5 q-mb-lg">
        {{ searchQuery ? 'Try adjusting your search criteria' : 'No field columns available for this measurement' }}
      </div>
      <q-btn
        label="Discover Fields"
        icon="search"
        color="primary"
        @click="$emit('refresh')"
        :loading="loading"
      />
    </div>

    <!-- Card View -->
    <div v-else-if="viewMode === 'cards'" class="row q-gutter-md">
      <div
        v-for="field in paginatedFields"
        :key="field.name || field"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <q-card class="field-card" flat bordered>
          <q-card-section>
            <!-- Header -->
            <div class="row items-center justify-between q-mb-md">
              <q-avatar
                :color="getFieldTypeColor(field)"
                text-color="white"
                size="md"
              >
                <q-icon :name="getFieldTypeIcon(field)" />
              </q-avatar>

              <q-btn-dropdown
                icon="more_vert"
                flat
                round
                size="sm"
              >
                <q-list>
                  <q-item clickable @click="viewFieldDetails(field)">
                    <q-item-section avatar>
                      <q-icon name="info" />
                    </q-item-section>
                    <q-item-section>View Details</q-item-section>
                  </q-item>

                  <q-item clickable @click="copyFieldName(field)">
                    <q-item-section avatar>
                      <q-icon name="content_copy" />
                    </q-item-section>
                    <q-item-section>Copy Name</q-item-section>
                  </q-item>

                  <q-item clickable @click="analyzeField(field)">
                    <q-item-section avatar>
                      <q-icon name="analytics" />
                    </q-item-section>
                    <q-item-section>Analyze Field</q-item-section>
                  </q-item>

                  <q-item clickable @click="showFieldChart(field)">
                    <q-item-section avatar>
                      <q-icon name="show_chart" />
                    </q-item-section>
                    <q-item-section>Show Chart</q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
            </div>

            <!-- Field Info -->
            <div>
              <div class="text-h6 q-mb-xs">{{ getFieldName(field) }}</div>
              <div class="text-caption text-grey-6">
                {{ getFieldType(field) }} • {{ getFieldDescription(field) }}
              </div>
            </div>

            <!-- Field Statistics -->
            <div class="q-mt-md">
              <q-list dense>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="storage" color="green" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Data Type</q-item-label>
                    <q-item-label>{{ getFieldDataType(field) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="isNumericField(field)">
                  <q-item-section avatar>
                    <q-icon name="straighten" color="blue" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Range</q-item-label>
                    <q-item-label>{{ getFieldRange(field) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="assessment" color="orange" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Non-null Values</q-item-label>
                    <q-item-label>{{ getFieldValueCount(field) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Advanced Statistics -->
            <div v-if="showAdvancedStats && isNumericField(field)" class="q-mt-md">
              <q-separator class="q-mb-sm" />
              <div class="text-caption text-grey-6 q-mb-xs">Statistical Analysis:</div>

              <div class="row q-gutter-xs">
                <q-chip size="sm" color="blue-grey" text-color="white">
                  Mean: {{ getFieldMean(field) }}
                </q-chip>
                <q-chip size="sm" color="blue-grey" text-color="white">
                  StdDev: {{ getFieldStdDev(field) }}
                </q-chip>
              </div>
            </div>

            <!-- Sample Values -->
            <div v-if="getFieldSampleValues(field).length > 0" class="q-mt-sm">
              <div class="text-caption text-grey-6 q-mb-xs">Sample Values:</div>
              <div class="row q-gutter-xs">
                <q-chip
                  v-for="value in getFieldSampleValues(field).slice(0, 3)"
                  :key="value"
                  size="sm"
                  color="green"
                  text-color="white"
                >
                  {{ formatValue(value) }}
                </q-chip>
              </div>
            </div>

            <!-- Quality Indicator -->
            <div class="q-mt-md">
              <q-linear-progress
                :value="getFieldQuality(field) / 100"
                color="positive"
                size="8px"
                class="q-mb-xs"
              />
              <div class="text-caption text-center">
                Data Quality: {{ getFieldQuality(field) }}%
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Table View -->
    <div v-else>
      <q-table
        :rows="tableRows"
        :columns="tableColumns"
        row-key="name"
        :pagination="tablePagination"
        flat
        bordered
        class="fields-table"
      >
        <template #body-cell-name="props">
          <q-td :props="props">
            <div class="row items-center q-gutter-sm">
              <q-avatar
                :color="getFieldTypeColor(props.row.field)"
                text-color="white"
                size="sm"
              >
                <q-icon :name="getFieldTypeIcon(props.row.field)" />
              </q-avatar>
              <div>
                <div class="text-weight-medium">{{ props.value }}</div>
                <div class="text-caption text-grey-6">{{ props.row.description }}</div>
              </div>
            </div>
          </q-td>
        </template>

        <template #body-cell-dataType="props">
          <q-td :props="props">
            <q-chip
              :color="getDataTypeColor(props.value)"
              text-color="white"
              size="sm"
            >
              {{ props.value }}
            </q-chip>
          </q-td>
        </template>

        <template #body-cell-range="props">
          <q-td :props="props">
            <span class="text-body2">{{ props.value || 'N/A' }}</span>
          </q-td>
        </template>

        <template #body-cell-quality="props">
          <q-td :props="props">
            <div class="row items-center q-gutter-sm">
              <q-linear-progress
                :value="props.value / 100"
                color="positive"
                size="4px"
                style="width: 60px"
              />
              <span class="text-caption">{{ props.value }}%</span>
            </div>
          </q-td>
        </template>

        <template #body-cell-sampleValues="props">
          <q-td :props="props">
            <div class="row q-gutter-xs">
              <q-chip
                v-for="value in props.value"
                :key="value"
                size="sm"
                color="green"
                text-color="white"
              >
                {{ formatValue(value) }}
              </q-chip>
            </div>
          </q-td>
        </template>

        <template #body-cell-actions="props">
          <q-td :props="props">
            <div class="row q-gutter-xs">
              <q-btn
                icon="info"
                flat
                round
                size="sm"
                @click="viewFieldDetails(props.row.field)"
              />
              <q-btn
                icon="analytics"
                flat
                round
                size="sm"
                @click="analyzeField(props.row.field)"
              />
              <q-btn
                icon="show_chart"
                flat
                round
                size="sm"
                @click="showFieldChart(props.row.field)"
              />
              <q-btn
                icon="content_copy"
                flat
                round
                size="sm"
                @click="copyFieldName(props.row.field)"
              />
            </div>
          </q-td>
        </template>
      </q-table>
    </div>

    <!-- Pagination for Card View -->
    <div v-if="viewMode === 'cards' && filteredFields.length > pageSize" class="row justify-center q-mt-lg">
      <q-pagination
        v-model="currentPage"
        :max="totalPages"
        :max-pages="6"
        direction-links
        boundary-links
      />
    </div>

    <!-- Field Details Dialog -->
    <q-dialog v-model="showDetailsDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Field Details: {{ getFieldName(selectedField) }}</div>
        </q-card-section>

        <q-card-section v-if="selectedField">
          <div class="row q-gutter-lg">
            <!-- Basic Info -->
            <div class="col-12 col-md-6">
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="insights" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Field Name</q-item-label>
                    <q-item-label>{{ getFieldName(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="category" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Data Type</q-item-label>
                    <q-item-label>{{ getFieldDataType(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="description" color="purple" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Description</q-item-label>
                    <q-item-label>{{ getFieldDescription(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="getFieldUnit(selectedField)">
                  <q-item-section avatar>
                    <q-icon name="straighten" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Unit</q-item-label>
                    <q-item-label>{{ getFieldUnit(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Statistics -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">Statistical Summary</div>

              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Non-null Values</q-item-label>
                    <q-item-label>{{ getFieldValueCount(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="isNumericField(selectedField)">
                  <q-item-section>
                    <q-item-label caption>Range</q-item-label>
                    <q-item-label>{{ getFieldRange(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="isNumericField(selectedField)">
                  <q-item-section>
                    <q-item-label caption>Mean</q-item-label>
                    <q-item-label>{{ getFieldMean(selectedField) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section>
                    <q-item-label caption>Data Quality</q-item-label>
                    <q-item-label>{{ getFieldQuality(selectedField) }}%</q-item-label>
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
            @click="analyzeField(selectedField)"
          />
          <q-btn
            label="Copy Name"
            icon="content_copy"
            color="secondary"
            outline
            @click="copyFieldName(selectedField)"
          />
          <q-btn label="Close" flat @click="showDetailsDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Field Analysis Dialog -->
    <q-dialog v-model="showAnalysisDialog" maximized>
      <q-card>
        <q-card-section class="bg-green text-white">
          <div class="row items-center">
            <div class="col">
              <div class="text-h6">Field Analysis: {{ getFieldName(selectedField) }}</div>
              <div class="text-subtitle2">Statistical analysis and data visualization</div>
            </div>
            <div class="col-auto">
              <q-btn icon="close" flat round @click="showAnalysisDialog = false" />
            </div>
          </div>
        </q-card-section>

        <q-card-section>
          <FieldAnalysisChart
            v-if="selectedField && fieldAnalysisData"
            :field="selectedField"
            :data="fieldAnalysisData"
            :sample-data="sampleData"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'

// Import sub-component
import FieldAnalysisChart from 'src/components/FieldAnalysisChart.vue'

// Props
const props = defineProps({
  fields: Array,
  sampleData: Array,
  loading: Boolean
})

// Emits
const emit = defineEmits(['refresh'])

// Reactive data
const $q = useQuasar()
const searchQuery = ref('')
const dataTypeFilter = ref('')
const sortBy = ref('name')
const viewMode = ref('cards')
const showAdvancedStats = ref(false)
const currentPage = ref(1)
const pageSize = 12
const analyzing = ref(false)

// Dialogs
const showDetailsDialog = ref(false)
const showAnalysisDialog = ref(false)
const selectedField = ref(null)
const fieldAnalysisData = ref(null)

// Table pagination
const tablePagination = ref({
  rowsPerPage: 10
})

// Options
const dataTypeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Number', value: 'number' },
  { label: 'String', value: 'string' },
  { label: 'Boolean', value: 'boolean' },
  { label: 'DateTime', value: 'datetime' }
]

const sortOptions = [
  { label: 'Name (A-Z)', value: 'name' },
  { label: 'Name (Z-A)', value: 'name-desc' },
  { label: 'Data Type', value: 'type' },
  { label: 'Quality Score', value: 'quality' }
]

const viewModeOptions = [
  { label: 'Cards', value: 'cards' },
  { label: 'Table', value: 'table' }
]

// Computed properties
const filteredFields = computed(() => {
  let filtered = props.fields

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(field => {
      const name = getFieldName(field).toLowerCase()
      const type = getFieldDataType(field).toLowerCase()
      const desc = getFieldDescription(field).toLowerCase()
      return name.includes(query) || type.includes(query) || desc.includes(query)
    })
  }

  // Apply data type filter
  if (dataTypeFilter.value) {
    filtered = filtered.filter(field =>
      getFieldDataType(field).toLowerCase() === dataTypeFilter.value
    )
  }

  // Apply sorting
  if (sortBy.value === 'name') {
    filtered.sort((a, b) => getFieldName(b).localeCompare(getFieldName(a)))
  } else if (sortBy.value === 'type') {
    filtered.sort((a, b) => getFieldDataType(a).localeCompare(getFieldDataType(b)))
  } else if (sortBy.value === 'quality') {
    filtered.sort((a, b) => getFieldQuality(b) - getFieldQuality(a))
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredFields.value.length / pageSize)
})

const paginatedFields = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredFields.value.slice(start, end)
})

const tableColumns = [
  {
    name: 'name',
    label: 'Field Name',
    field: 'name',
    align: 'left',
    sortable: true
  },
  {
    name: 'dataType',
    label: 'Data Type',
    field: 'dataType',
    align: 'center',
    sortable: true
  },
  {
    name: 'range',
    label: 'Range',
    field: 'range',
    align: 'center'
  },
  {
    name: 'quality',
    label: 'Quality',
    field: 'quality',
    align: 'center',
    sortable: true
  },
  {
    name: 'sampleValues',
    label: 'Sample Values',
    field: 'sampleValues',
    align: 'left'
  },
  {
    name: 'actions',
    label: 'Actions',
    field: 'actions',
    align: 'center'
  }
]

const tableRows = computed(() => {
  return filteredFields.value.map(field => ({
    field: field,
    name: getFieldName(field),
    description: getFieldDescription(field),
    dataType: getFieldDataType(field),
    range: isNumericField(field) ? getFieldRange(field) : null,
    quality: getFieldQuality(field),
    sampleValues: getFieldSampleValues(field).slice(0, 3)
  }))
})

// Methods
const getFieldName = (field) => {
  return field.name || field
}

const getFieldType = (field) => {
  return field.type || 'Unknown'
}

const getFieldDescription = (field) => {
  return field.description || field.desc || 'Measurement field'
}

const getFieldUnit = (field) => {
  return field.unit || null
}

const getFieldDataType = (field) => {
  // Analyze sample data to determine type
  if (!props.sampleData || props.sampleData.length === 0) return 'Unknown'

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => val != null)
  if (values.length === 0) return 'Unknown'

  const firstValue = values[0]
  if (typeof firstValue === 'number') return 'Number'
  if (typeof firstValue === 'boolean') return 'Boolean'

  // Check if it looks like a date
  if (typeof firstValue === 'string' && !isNaN(Date.parse(firstValue))) {
    return 'DateTime'
  }

  return 'String'
}

const isNumericField = (field) => {
  return getFieldDataType(field) === 'Number'
}

const getFieldValueCount = (field) => {
  if (!props.sampleData || props.sampleData.length === 0) return 0

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => val != null)
  return values.length
}

const getFieldRange = (field) => {
  if (!isNumericField(field) || !props.sampleData) return 'N/A'

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => typeof val === 'number')

  if (values.length === 0) return 'N/A'

  const min = Math.min(...values)
  const max = Math.max(...values)

  return `${formatValue(min)} - ${formatValue(max)}`
}

const getFieldMean = (field) => {
  if (!isNumericField(field) || !props.sampleData) return 'N/A'

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => typeof val === 'number')

  if (values.length === 0) return 'N/A'

  const mean = values.reduce((sum, val) => sum + val, 0) / values.length
  return formatValue(mean)
}

const getFieldStdDev = (field) => {
  if (!isNumericField(field) || !props.sampleData) return 'N/A'

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => typeof val === 'number')

  if (values.length < 2) return 'N/A'

  const mean = values.reduce((sum, val) => sum + val, 0) / values.length
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length
  const stdDev = Math.sqrt(variance)

  return formatValue(stdDev)
}

const getFieldSampleValues = (field) => {
  if (!props.sampleData || props.sampleData.length === 0) return []

  const fieldName = getFieldName(field)
  const values = props.sampleData.map(row => row[fieldName]).filter(val => val != null)
  const uniqueValues = [...new Set(values)]
  return uniqueValues.slice(0, 5)
}

const getFieldQuality = (field) => {
  if (!props.sampleData || props.sampleData.length === 0) return 0

  const fieldName = getFieldName(field)
  const totalRows = props.sampleData.length
  const nonNullValues = props.sampleData.filter(row => row[fieldName] != null).length

  // Base score on data completeness
  let score = (nonNullValues / totalRows) * 100

  // Adjust based on data type consistency
  if (isNumericField(field)) {
    const numericValues = props.sampleData.filter(row => typeof row[fieldName] === 'number').length
    score = (numericValues / totalRows) * 100
  }

  return Math.round(score)
}

const getFieldTypeColor = (field) => {
  const dataType = getFieldDataType(field)
  const colors = {
    'Number': 'green',
    'String': 'blue',
    'Boolean': 'purple',
    'DateTime': 'orange',
    'Unknown': 'grey'
  }
  return colors[dataType] || 'grey'
}

const getFieldTypeIcon = (field) => {
  const dataType = getFieldDataType(field)
  const icons = {
    'Number': 'functions',
    'String': 'text_fields',
    'Boolean': 'toggle_on',
    'DateTime': 'schedule',
    'Unknown': 'help'
  }
  return icons[dataType] || 'insights'
}

const getDataTypeColor = (dataType) => {
  const colors = {
    'Number': 'green',
    'String': 'blue',
    'Boolean': 'purple',
    'DateTime': 'orange',
    'Unknown': 'grey'
  }
  return colors[dataType] || 'grey'
}

const formatValue = (value) => {
  if (typeof value === 'number') {
    if (Math.abs(value) >= 1000) {
      return value.toLocaleString()
    }
    if (value % 1 !== 0) {
      return value.toFixed(3).replace(/\.?0+$/, '')
    }
  }
  return String(value)
}

const viewFieldDetails = (field) => {
  selectedField.value = field
  showDetailsDialog.value = true
}

const analyzeField = async (field) => {
  selectedField.value = field
  analyzing.value = true

  try {
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Generate analysis data
    fieldAnalysisData.value = generateFieldAnalysis(field)
    showAnalysisDialog.value = true

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to analyze field'
    })
  } finally {
    analyzing.value = false
  }
}

const generateFieldAnalysis = (field) => {
  const fieldName = getFieldName(field)

  if (!props.sampleData) return null

  const values = props.sampleData.map(row => row[fieldName]).filter(val => val != null)

  if (isNumericField(field)) {
    return {
      type: 'numeric',
      values: values,
      statistics: {
        count: values.length,
        mean: getFieldMean(field),
        stdDev: getFieldStdDev(field),
        min: Math.min(...values),
        max: Math.max(...values),
        median: calculateMedian(values)
      }
    }
  } else {
    const valueCounts = {}
    values.forEach(val => {
      valueCounts[val] = (valueCounts[val] || 0) + 1
    })

    return {
      type: 'categorical',
      valueCounts: valueCounts,
      uniqueValues: Object.keys(valueCounts).length,
      totalValues: values.length
    }
  }
}

const calculateMedian = (values) => {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)

  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2
  } else {
    return sorted[mid]
  }
}

const showFieldChart = (field) => {
  analyzeField(field)
}

const copyFieldName = async (field) => {
  try {
    await navigator.clipboard.writeText(getFieldName(field))
    $q.notify({
      type: 'positive',
      message: 'Field name copied to clipboard',
      icon: 'content_copy',
      timeout: 1000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy field name'
    })
  }
}

const analyzeAllFields = async () => {
  analyzing.value = true

  try {
    // Simulate analysis of all fields
    await new Promise(resolve => setTimeout(resolve, 2000))

    $q.notify({
      type: 'positive',
      message: `Analyzed ${filteredFields.value.length} fields`,
      caption: 'Statistical analysis completed'
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to analyze fields'
    })
  } finally {
    analyzing.value = false
  }
}

const exportFields = () => {
  const exportData = filteredFields.value.map(field => ({
    name: getFieldName(field),
    dataType: getFieldDataType(field),
    description: getFieldDescription(field),
    unit: getFieldUnit(field) || 'N/A',
    range: isNumericField(field) ? getFieldRange(field) : 'N/A',
    nonNullValues: getFieldValueCount(field),
    qualityScore: getFieldQuality(field),
    mean: isNumericField(field) ? getFieldMean(field) : 'N/A',
    stdDev: isNumericField(field) ? getFieldStdDev(field) : 'N/A',
    sampleValues: getFieldSampleValues(field).join('; ')
  }))

  const csvContent = convertToCSV(exportData)
  downloadCSV(csvContent, 'fields_export.csv')

  $q.notify({
    type: 'positive',
    message: 'Fields exported successfully',
    icon: 'file_download'
  })
}

const convertToCSV = (data) => {
  if (data.length === 0) return ''

  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row =>
    Object.values(row).map(value => {
      const stringValue = String(value)
      if (stringValue.includes(',') || stringValue.includes('"')) {
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
.fields-explorer {
  background-color: #fafafa;
  min-height: 100%;
}

.field-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  border: 2px solid transparent;
}

.field-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-color: rgba(76, 175, 80, 0.3);
}

.fields-table {
  border-radius: 8px;
  overflow: hidden;
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-chip {
  font-weight: 500;
}

.q-item {
  border-radius: 8px;
  margin-bottom: 2px;
}

.q-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Custom linear progress styling */
.q-linear-progress {
  border-radius: 4px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .field-card {
    margin-bottom: 16px;
  }

  .row.q-gutter-md {
    margin: -8px;
  }

  .row.q-gutter-md > div {
    padding: 8px;
  }
}
</style>a).localeCompare(getFieldName(b)))
  } else if (sortBy.value === 'name-desc') {
    filtered.sort((a, b) => getFieldName(
