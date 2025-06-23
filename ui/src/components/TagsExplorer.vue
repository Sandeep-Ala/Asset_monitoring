<!-- ui/src/components/TagsExplorer.vue -->
<template>
  <div class="tags-explorer q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Tag Columns</div>
        <div class="text-subtitle2 text-grey-6">
          {{ tags.length }} tag columns for filtering and grouping data
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Refresh Tags"
          icon="refresh"
          color="primary"
          outline
          @click="$emit('refresh')"
          :loading="loading"
        />
        <q-btn
          label="Export Tags"
          icon="file_download"
          color="secondary"
          outline
          @click="exportTags"
        />
        <q-btn
          label="Analyze All"
          icon="analytics"
          color="positive"
          outline
          @click="analyzeAllTags"
          :loading="analyzing"
        />
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-input
          v-model="searchQuery"
          placeholder="Search tag columns..."
          outlined
          dense
          clearable
        >
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>

      <div class="col-12 col-md-3">
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

      <div class="col-12 col-md-3">
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
    </div>

    <!-- Tags Content -->
    <div v-if="filteredTags.length === 0" class="text-center q-pa-xl">
      <q-icon name="label_off" size="4rem" class="text-grey-4 q-mb-md" />
      <div class="text-h6 text-grey-6 q-mb-sm">No Tag Columns Found</div>
      <div class="text-body2 text-grey-5 q-mb-lg">
        {{ searchQuery ? 'Try adjusting your search criteria' : 'No tag columns available for this measurement' }}
      </div>
      <q-btn
        label="Discover Tags"
        icon="search"
        color="primary"
        @click="$emit('refresh')"
        :loading="loading"
      />
    </div>

    <!-- Card View -->
    <div v-else-if="viewMode === 'cards'" class="row q-gutter-md">
      <div
        v-for="tag in paginatedTags"
        :key="tag"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <q-card class="tag-card" flat bordered>
          <q-card-section>
            <!-- Header -->
            <div class="row items-center justify-between q-mb-md">
              <q-avatar
                color="blue"
                text-color="white"
                size="md"
              >
                <q-icon name="label" />
              </q-avatar>

              <q-btn-dropdown
                icon="more_vert"
                flat
                round
                size="sm"
              >
                <q-list>
                  <q-item clickable @click="viewTagDetails(tag)">
                    <q-item-section avatar>
                      <q-icon name="info" />
                    </q-item-section>
                    <q-item-section>View Details</q-item-section>
                  </q-item>

                  <q-item clickable @click="copyTagName(tag)">
                    <q-item-section avatar>
                      <q-icon name="content_copy" />
                    </q-item-section>
                    <q-item-section>Copy Name</q-item-section>
                  </q-item>

                  <q-item clickable @click="analyzeTag(tag)">
                    <q-item-section avatar>
                      <q-icon name="analytics" />
                    </q-item-section>
                    <q-item-section>Analyze Tag</q-item-section>
                  </q-item>

                  <q-item clickable @click="showTagValues(tag)">
                    <q-item-section avatar>
                      <q-icon name="list" />
                    </q-item-section>
                    <q-item-section>Show Values</q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
            </div>

            <!-- Tag Info -->
            <div>
              <div class="text-h6 q-mb-xs">{{ tag }}</div>
              <div class="text-caption text-grey-6">
                Tag column for filtering data
              </div>
            </div>

            <!-- Tag Statistics -->
            <div class="q-mt-md">
              <q-list dense>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="storage" color="blue" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Data Type</q-item-label>
                    <q-item-label>{{ getTagDataType(tag) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="list" color="green" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Unique Values</q-item-label>
                    <q-item-label>{{ getTagUniqueCount(tag) }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="assessment" color="orange" size="sm" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Non-null Values</q-item-label>
                    <q-item-label>{{ getTagValueCount(tag) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Sample Values -->
            <div v-if="getTagSampleValues(tag).length > 0" class="q-mt-sm">
              <div class="text-caption text-grey-6 q-mb-xs">Sample Values:</div>
              <div class="row q-gutter-xs">
                <q-chip
                  v-for="value in getTagSampleValues(tag).slice(0, 3)"
                  :key="value"
                  size="sm"
                  color="blue"
                  text-color="white"
                >
                  {{ formatValue(value) }}
                </q-chip>
              </div>
            </div>

            <!-- Quality Indicator -->
            <div class="q-mt-md">
              <q-linear-progress
                :value="getTagQuality(tag) / 100"
                color="positive"
                size="8px"
                class="q-mb-xs"
              />
              <div class="text-caption text-center">
                Data Quality: {{ getTagQuality(tag) }}%
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
        class="tags-table"
      >
        <template #body-cell-name="props">
          <q-td :props="props">
            <div class="row items-center q-gutter-sm">
              <q-avatar
                color="blue"
                text-color="white"
                size="sm"
              >
                <q-icon name="label" />
              </q-avatar>
              <div>
                <div class="text-weight-medium">{{ props.value }}</div>
                <div class="text-caption text-grey-6">Tag column</div>
              </div>
            </div>
          </q-td>
        </template>

        <template #body-cell-dataType="props">
          <q-td :props="props">
            <q-chip
              color="blue"
              text-color="white"
              size="sm"
            >
              {{ props.value }}
            </q-chip>
          </q-td>
        </template>

        <template #body-cell-uniqueCount="props">
          <q-td :props="props">
            <q-chip
              color="green"
              text-color="white"
              size="sm"
            >
              {{ props.value }}
            </q-chip>
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
                color="blue"
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
                @click="viewTagDetails(props.row.tag)"
              />
              <q-btn
                icon="analytics"
                flat
                round
                size="sm"
                @click="analyzeTag(props.row.tag)"
              />
              <q-btn
                icon="list"
                flat
                round
                size="sm"
                @click="showTagValues(props.row.tag)"
              />
              <q-btn
                icon="content_copy"
                flat
                round
                size="sm"
                @click="copyTagName(props.row.tag)"
              />
            </div>
          </q-td>
        </template>
      </q-table>
    </div>

    <!-- Pagination for Card View -->
    <div v-if="viewMode === 'cards' && filteredTags.length > pageSize" class="row justify-center q-mt-lg">
      <q-pagination
        v-model="currentPage"
        :max="totalPages"
        :max-pages="6"
        direction-links
        boundary-links
      />
    </div>

    <!-- Tag Details Dialog -->
    <q-dialog v-model="showDetailsDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Tag Details: {{ selectedTag }}</div>
        </q-card-section>

        <q-card-section v-if="selectedTag">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="label" color="blue" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Tag Name</q-item-label>
                <q-item-label>{{ selectedTag }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="category" color="green" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Data Type</q-item-label>
                <q-item-label>{{ getTagDataType(selectedTag) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="list" color="orange" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Unique Values</q-item-label>
                <q-item-label>{{ getTagUniqueCount(selectedTag) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="assessment" color="purple" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Non-null Values</q-item-label>
                <q-item-label>{{ getTagValueCount(selectedTag) }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <!-- Sample Values -->
          <div v-if="getTagSampleValues(selectedTag).length > 0" class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Sample Values</div>
            <div class="row q-gutter-xs">
              <q-chip
                v-for="value in getTagSampleValues(selectedTag)"
                :key="value"
                size="sm"
                color="blue"
                text-color="white"
              >
                {{ formatValue(value) }}
              </q-chip>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Analyze"
            icon="analytics"
            color="primary"
            outline
            @click="analyzeTag(selectedTag)"
          />
          <q-btn
            label="Copy Name"
            icon="content_copy"
            color="secondary"
            outline
            @click="copyTagName(selectedTag)"
          />
          <q-btn label="Close" flat @click="showDetailsDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Tag Values Dialog -->
    <q-dialog v-model="showValuesDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Tag Values: {{ selectedTag }}</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="valuesSearchQuery"
            placeholder="Search values..."
            outlined
            dense
            clearable
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-list class="q-mt-md" separator>
            <q-item v-for="value in filteredTagValues" :key="value">
              <q-item-section>
                <q-item-label>{{ formatValue(value) }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn
                  icon="content_copy"
                  flat
                  round
                  size="sm"
                  @click="copyValue(value)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showValuesDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  tags: Array,
  sampleData: Array,
  loading: Boolean
})

// Emits
const emit = defineEmits(['refresh'])

// Reactive data
const $q = useQuasar()
const searchQuery = ref('')
const sortBy = ref('name')
const viewMode = ref('cards')
const currentPage = ref(1)
const pageSize = 12
const analyzing = ref(false)

// Dialogs
const showDetailsDialog = ref(false)
const showValuesDialog = ref(false)
const selectedTag = ref(null)
const valuesSearchQuery = ref('')

// Table pagination
const tablePagination = ref({
  rowsPerPage: 10
})

// Options
const sortOptions = [
  { label: 'Name (A-Z)', value: 'name' },
  { label: 'Name (Z-A)', value: 'name-desc' },
  { label: 'Quality Score', value: 'quality' },
  { label: 'Unique Values', value: 'unique' }
]

const viewModeOptions = [
  { label: 'Cards', value: 'cards' },
  { label: 'Table', value: 'table' }
]

// Computed properties
const filteredTags = computed(() => {
  let filtered = props.tags

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tag => tag.toLowerCase().includes(query))
  }

  // Apply sorting
  if (sortBy.value === 'name') {
    filtered.sort((a, b) => a.localeCompare(b))
  } else if (sortBy.value === 'name-desc') {
    filtered.sort((a, b) => b.localeCompare(a))
  } else if (sortBy.value === 'quality') {
    filtered.sort((a, b) => getTagQuality(b) - getTagQuality(a))
  } else if (sortBy.value === 'unique') {
    filtered.sort((a, b) => getTagUniqueCount(b) - getTagUniqueCount(a))
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredTags.value.length / pageSize)
})

const paginatedTags = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredTags.value.slice(start, end)
})

const tableColumns = [
  {
    name: 'name',
    label: 'Tag Name',
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
    name: 'uniqueCount',
    label: 'Unique Values',
    field: 'uniqueCount',
    align: 'center',
    sortable: true
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
  return filteredTags.value.map(tag => ({
    tag: tag,
    name: tag,
    dataType: getTagDataType(tag),
    uniqueCount: getTagUniqueCount(tag),
    quality: getTagQuality(tag),
    sampleValues: getTagSampleValues(tag).slice(0, 3)
  }))
})

const filteredTagValues = computed(() => {
  if (!selectedTag.value) return []

  const values = getTagSampleValues(selectedTag.value)
  if (!valuesSearchQuery.value) return values

  const query = valuesSearchQuery.value.toLowerCase()
  return values.filter(value =>
    String(value).toLowerCase().includes(query)
  )
})

// Methods
const getTagDataType = (tag) => {
  if (!props.sampleData || props.sampleData.length === 0) return 'Unknown'

  const values = props.sampleData.map(row => row[tag]).filter(val => val != null)
  if (values.length === 0) return 'Unknown'

  const firstValue = values[0]
  if (typeof firstValue === 'number') return 'Number'
  if (typeof firstValue === 'boolean') return 'Boolean'
  return 'String'
}

const getTagUniqueCount = (tag) => {
  if (!props.sampleData || props.sampleData.length === 0) return 0

  const values = props.sampleData.map(row => row[tag]).filter(val => val != null)
  return new Set(values).size
}

const getTagValueCount = (tag) => {
  if (!props.sampleData || props.sampleData.length === 0) return 0

  const values = props.sampleData.map(row => row[tag]).filter(val => val != null)
  return values.length
}

const getTagSampleValues = (tag) => {
  if (!props.sampleData || props.sampleData.length === 0) return []

  const values = props.sampleData.map(row => row[tag]).filter(val => val != null)
  const uniqueValues = [...new Set(values)]
  return uniqueValues.slice(0, 10)
}

const getTagQuality = (tag) => {
  if (!props.sampleData || props.sampleData.length === 0) return 0

  const totalRows = props.sampleData.length
  const nonNullValues = props.sampleData.filter(row => row[tag] != null).length

  return Math.round((nonNullValues / totalRows) * 100)
}

const formatValue = (value) => {
  if (typeof value === 'string' && value.length > 20) {
    return value.substring(0, 20) + '...'
  }
  return String(value)
}

const viewTagDetails = (tag) => {
  selectedTag.value = tag
  showDetailsDialog.value = true
}

const analyzeTag = async (tag) => {
  analyzing.value = true
  try {
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 1000))

    $q.notify({
      type: 'positive',
      message: `Analysis completed for tag: ${tag}`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to analyze tag'
    })
  } finally {
    analyzing.value = false
  }
}

const showTagValues = (tag) => {
  selectedTag.value = tag
  valuesSearchQuery.value = ''
  showValuesDialog.value = true
}

const copyTagName = async (tag) => {
  try {
    await navigator.clipboard.writeText(tag)
    $q.notify({
      type: 'positive',
      message: 'Tag name copied to clipboard',
      icon: 'content_copy',
      timeout: 1000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy tag name'
    })
  }
}

const copyValue = async (value) => {
  try {
    await navigator.clipboard.writeText(String(value))
    $q.notify({
      type: 'positive',
      message: 'Value copied to clipboard',
      icon: 'content_copy',
      timeout: 1000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy value'
    })
  }
}

const analyzeAllTags = async () => {
  analyzing.value = true

  try {
    // Simulate analysis of all tags
    await new Promise(resolve => setTimeout(resolve, 2000))

    $q.notify({
      type: 'positive',
      message: `Analyzed ${filteredTags.value.length} tags`,
      caption: 'Analysis completed successfully'
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to analyze tags'
    })
  } finally {
    analyzing.value = false
  }
}

const exportTags = () => {
  const exportData = filteredTags.value.map(tag => ({
    name: tag,
    dataType: getTagDataType(tag),
    uniqueValues: getTagUniqueCount(tag),
    nonNullValues: getTagValueCount(tag),
    qualityScore: getTagQuality(tag),
    sampleValues: getTagSampleValues(tag).join('; ')
  }))

  const csvContent = convertToCSV(exportData)
  downloadCSV(csvContent, 'tags_export.csv')

  $q.notify({
    type: 'positive',
    message: 'Tags exported successfully',
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
.tags-explorer {
  background-color: #fafafa;
  min-height: 100%;
}

.tag-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  border: 2px solid transparent;
}

.tag-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-color: rgba(33, 150, 243, 0.3);
}

.tags-table {
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

/* Custom scrollbar */
.q-list {
  max-height: 300px;
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
  .tag-card {
    margin-bottom: 16px;
  }

  .row.q-gutter-md {
    margin: -8px;
  }

  .row.q-gutter-md > div {
    padding: 8px;
  }
}
</style>
