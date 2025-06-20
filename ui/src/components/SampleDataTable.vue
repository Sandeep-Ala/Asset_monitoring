<!-- ui/src/components/SampleDataTable.vue -->
<template>
  <div class="sample-data-table">
    <div v-if="data.length === 0" class="text-center q-pa-lg text-grey-6">
      <q-icon name="table_view" size="3rem" class="q-mb-md" />
      <div class="text-h6">No Sample Data</div>
      <div class="text-body2">No data available to display</div>
    </div>

    <div v-else>
      <!-- Table Controls -->
      <div v-if="!compact" class="row items-center justify-between q-mb-md">
        <div class="row items-center q-gutter-md">
          <q-input
            v-model="searchQuery"
            placeholder="Search data..."
            outlined
            dense
            clearable
            style="min-width: 200px"
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-select
            v-model="selectedColumns"
            :options="columnOptions"
            label="Show Columns"
            outlined
            dense
            multiple
            use-chips
            style="min-width: 200px"
          />
        </div>

        <div class="row q-gutter-sm">
          <q-btn
            label="Export CSV"
            icon="file_download"
            color="secondary"
            outline
            size="sm"
            @click="exportToCsv"
          />

          <q-btn
            label="Copy Data"
            icon="content_copy"
            color="blue-grey"
            outline
            size="sm"
            @click="copyToClipboard"
          />
        </div>
      </div>

      <!-- Data Table -->
      <q-table
        :rows="filteredData"
        :columns="displayColumns"
        row-key="index"
        :pagination="tablePagination"
        :loading="loading"
        flat
        bordered
        :dense="compact"
        :virtual-scroll="data.length > 100"
        :rows-per-page-options="compact ? [5, 10] : [10, 25, 50, 100]"
        class="data-table"
      >
        <!-- Header slot for custom styling -->
        <template #header="props">
          <q-tr :props="props">
            <q-th
              v-for="col in props.cols"
              :key="col.name"
              :props="props"
              class="table-header"
            >
              <div class="row items-center">
                <span>{{ col.label }}</span>
                <q-icon
                  v-if="getColumnType(col.name) !== 'string'"
                  :name="getColumnTypeIcon(col.name)"
                  :color="getColumnTypeColor(col.name)"
                  size="xs"
                  class="q-ml-xs"
                  :title="getColumnType(col.name)"
                />
              </div>
            </q-th>
          </q-tr>
        </template>

        <!-- Body slot for custom cell rendering -->
        <template #body-cell="props">
          <q-td :props="props" :class="getCellClass(props.col.name, props.value)">
            <div class="cell-content">
              <!-- Null/undefined values -->
              <span v-if="props.value == null" class="text-grey-5 text-italic">
                null
              </span>

              <!-- Boolean values -->
              <q-chip
                v-else-if="typeof props.value === 'boolean'"
                :color="props.value ? 'positive' : 'negative'"
                text-color="white"
                size="sm"
              >
                {{ props.value }}
              </q-chip>

              <!-- Numeric values -->
              <span
                v-else-if="typeof props.value === 'number'"
                :class="getNumericClass(props.value)"
              >
                {{ formatNumber(props.value) }}
              </span>

              <!-- Date/time values -->
              <span
                v-else-if="isDateColumn(props.col.name)"
                :title="props.value"
              >
                {{ formatDateTime(props.value) }}
              </span>

              <!-- Long text values -->
              <div
                v-else-if="typeof props.value === 'string' && props.value.length > 50"
                class="text-truncate"
                :title="props.value"
              >
                {{ props.value.substring(0, 50) }}...
                <q-btn
                  icon="open_in_full"
                  flat
                  round
                  size="xs"
                  @click="showFullText(props.value, props.col.label)"
                />
              </div>

              <!-- Regular string values -->
              <span v-else>{{ props.value }}</span>

              <!-- Copy button for non-compact mode -->
              <q-btn
                v-if="!compact && props.value != null"
                icon="content_copy"
                flat
                round
                size="xs"
                class="copy-btn"
                @click="copyValue(props.value)"
              />
            </div>
          </q-td>
        </template>

        <!-- No data slot -->
        <template #no-data>
          <div class="full-width row flex-center text-grey-6 q-gutter-sm">
            <q-icon size="2em" name="search_off" />
            <span>No matching data found</span>
          </div>
        </template>
      </q-table>

      <!-- Data Summary -->
      <div v-if="!compact" class="row items-center justify-between q-mt-md">
        <div class="text-caption text-grey-6">
          Showing {{ filteredData.length }} of {{ data.length }} records
          {{ selectedColumns.length < columns.length ? `• ${selectedColumns.length} of ${columns.length} columns` : '' }}
        </div>

        <div class="row items-center q-gutter-md">
          <!-- Data types legend -->
          <div class="row items-center q-gutter-xs">
            <q-chip size="xs" color="blue" text-color="white">
              <q-icon name="abc" size="xs" />
              Text
            </q-chip>
            <q-chip size="xs" color="green" text-color="white">
              <q-icon name="123" size="xs" />
              Number
            </q-chip>
            <q-chip size="xs" color="orange" text-color="white">
              <q-icon name="schedule" size="xs" />
              Date
            </q-chip>
            <q-chip size="xs" color="purple" text-color="white">
              <q-icon name="toggle_on" size="xs" />
              Boolean
            </q-chip>
          </div>
        </div>
      </div>
    </div>

    <!-- Full Text Dialog -->
    <q-dialog v-model="showTextDialog">
      <q-card style="min-width: 500px; max-width: 80vw">
        <q-card-section>
          <div class="text-h6">{{ textDialogTitle }}</div>
        </q-card-section>

        <q-card-section>
          <q-input
            :model-value="textDialogContent"
            type="textarea"
            rows="10"
            outlined
            readonly
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Copy"
            icon="content_copy"
            color="primary"
            outline
            @click="copyValue(textDialogContent)"
          />
          <q-btn label="Close" flat @click="showTextDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  compact: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Reactive data
const $q = useQuasar()
const searchQuery = ref('')
const selectedColumns = ref([])
const showTextDialog = ref(false)
const textDialogContent = ref('')
const textDialogTitle = ref('')

// Table pagination
const tablePagination = ref({
  sortBy: null,
  descending: false,
  page: 1,
  rowsPerPage: props.compact ? 5 : 10
})

// Computed properties
const columns = computed(() => {
  if (props.data.length === 0) return []

  const firstRow = props.data[0]
  return Object.keys(firstRow).map(key => ({
    name: key,
    label: key,
    field: key,
    align: 'left',
    sortable: true,
    headerStyle: 'font-weight: bold;'
  }))
})

const columnOptions = computed(() => {
  return columns.value.map(col => ({
    label: col.label,
    value: col.name
  }))
})

const displayColumns = computed(() => {
  if (selectedColumns.value.length === 0) {
    return columns.value
  }
  return columns.value.filter(col => selectedColumns.value.includes(col.name))
})

const filteredData = computed(() => {
  if (!searchQuery.value) return indexedData.value

  const query = searchQuery.value.toLowerCase()
  return indexedData.value.filter(row => {
    return Object.values(row).some(value => {
      if (value == null) return false
      return String(value).toLowerCase().includes(query)
    })
  })
})

const indexedData = computed(() => {
  return props.data.map((row, index) => ({
    ...row,
    index: index + 1
  }))
})

// Methods
onMounted(() => {
  // Initialize with all columns selected
  selectedColumns.value = columns.value.map(col => col.name)
})

const getColumnType = (columnName) => {
  if (props.data.length === 0) return 'string'

  // Sample a few values to determine type
  const samples = props.data.slice(0, 5).map(row => row[columnName])
  const nonNullSamples = samples.filter(val => val != null)

  if (nonNullSamples.length === 0) return 'string'

  const firstValue = nonNullSamples[0]

  if (typeof firstValue === 'boolean') return 'boolean'
  if (typeof firstValue === 'number') return 'number'
  if (isDateColumn(columnName)) return 'datetime'

  return 'string'
}

const getColumnTypeIcon = (columnName) => {
  const type = getColumnType(columnName)
  const icons = {
    'string': 'abc',
    'number': '123',
    'boolean': 'toggle_on',
    'datetime': 'schedule'
  }
  return icons[type] || 'help'
}

const getColumnTypeColor = (columnName) => {
  const type = getColumnType(columnName)
  const colors = {
    'string': 'blue',
    'number': 'green',
    'boolean': 'purple',
    'datetime': 'orange'
  }
  return colors[type] || 'grey'
}

const isDateColumn = (columnName) => {
  const dateColumns = ['timestamp', 'created_at', 'updated_at', 'date', 'time']
  return dateColumns.some(col => columnName.toLowerCase().includes(col))
}

const getCellClass = (columnName, value) => {
  const classes = ['table-cell']

  if (value == null) {
    classes.push('null-value')
  } else if (typeof value === 'number') {
    classes.push('numeric-value')
  } else if (typeof value === 'boolean') {
    classes.push('boolean-value')
  }

  return classes.join(' ')
}

const getNumericClass = (value) => {
  if (value < 0) return 'text-negative'
  if (value > 100) return 'text-positive'
  return ''
}

const formatNumber = (value) => {
  if (value == null) return ''

  // Format large numbers with commas
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString()
  }

  // Format decimals with reasonable precision
  if (value % 1 !== 0) {
    return value.toFixed(3).replace(/\.?0+$/, '')
  }

  return String(value)
}

const formatDateTime = (value) => {
  if (!value) return ''

  try {
    const date = new Date(value)
    if (isNaN(date.getTime())) return value

    // If it's today, show time only
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const valueDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())

    if (valueDate.getTime() === today.getTime()) {
      return date.toLocaleTimeString()
    }

    // Otherwise show date and time
    return date.toLocaleString()
  } catch {
    return value
  }
}

const showFullText = (text, columnName) => {
  textDialogContent.value = text
  textDialogTitle.value = `Full Content - ${columnName}`
  showTextDialog.value = true
}

const copyValue = async (value) => {
  try {
    await navigator.clipboard.writeText(String(value))
    $q.notify({
      type: 'positive',
      message: 'Copied to clipboard',
      icon: 'content_copy',
      timeout: 1000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy',
      icon: 'error'
    })
  }
}

const copyToClipboard = async () => {
  try {
    const csvContent = convertToCSV(filteredData.value, displayColumns.value)
    await navigator.clipboard.writeText(csvContent)
    $q.notify({
      type: 'positive',
      message: 'Data copied to clipboard',
      icon: 'content_copy'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy data'
    })
  }
}

const exportToCsv = () => {
  const csvContent = convertToCSV(filteredData.value, displayColumns.value)
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')

  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `sample_data_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    $q.notify({
      type: 'positive',
      message: 'Data exported successfully',
      icon: 'file_download'
    })
  }
}

const convertToCSV = (data, columns) => {
  if (data.length === 0) return ''

  // Create header row
  const headers = columns.map(col => col.label).join(',')

  // Create data rows
  const rows = data.map(row => {
    return columns.map(col => {
      const value = row[col.field]
      if (value == null) return ''

      // Escape commas and quotes in CSV
      const stringValue = String(value)
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`
      }
      return stringValue
    }).join(',')
  })

  return [headers, ...rows].join('\n')
}
</script>

<style scoped>
.sample-data-table {
  width: 100%;
}

.data-table {
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  background-color: #f5f5f5;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-cell {
  position: relative;
  padding: 8px 12px;
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 24px;
}

.copy-btn {
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 8px;
}

.table-cell:hover .copy-btn {
  opacity: 1;
}

.null-value {
  background-color: rgba(158, 158, 158, 0.1);
}

.numeric-value {
  text-align: right;
  font-family: monospace;
}

.boolean-value {
  text-align: center;
}

.text-truncate {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Custom scrollbar for table */
.q-table__container {
  max-height: 60vh;
}

.q-table__container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.q-table__container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.q-table__container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.q-table__container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .cell-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .copy-btn {
    margin-left: 0;
    margin-top: 4px;
  }

  .text-truncate {
    max-width: 150px;
  }
}
</style>
