<!-- ui/src/components/RawSchemaViewer.vue -->
<template>
  <div class="raw-schema-viewer q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Raw Schema</div>
        <div class="text-subtitle2 text-grey-6">
          Complete schema structure and metadata for {{ measurement }}
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Copy Schema"
          icon="content_copy"
          color="secondary"
          outline
          @click="copySchema"
        />
        <q-btn
          label="Export JSON"
          icon="file_download"
          color="primary"
          outline
          @click="exportSchema"
        />
        <q-btn
          label="Validate Schema"
          icon="verified"
          color="positive"
          outline
          @click="validateSchema"
          :loading="validating"
        />
      </div>
    </div>

    <!-- Schema Tabs -->
    <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
      <q-tab name="overview" label="Overview" icon="dashboard" />
      <q-tab name="json" label="JSON Schema" icon="code" />
      <q-tab name="metadata" label="Metadata" icon="info" />
      <q-tab name="validation" label="Validation" icon="verified" />
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-tab-panels v-model="activeTab" animated class="q-mt-md">
      <!-- Overview Tab -->
      <q-tab-panel name="overview">
        <div class="row q-gutter-lg">
          <!-- Schema Summary -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Schema Summary</div>

                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="table_chart" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Measurement</q-item-label>
                      <q-item-label>{{ measurement || 'Unknown' }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="label" color="blue" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Tag Columns</q-item-label>
                      <q-item-label>{{ tags.length }} columns</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="insights" color="green" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Field Columns</q-item-label>
                      <q-item-label>{{ fields.length }} columns</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="preview" color="orange" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Sample Records</q-item-label>
                      <q-item-label>{{ sampleData.length }} records</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="schedule" color="purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Last Discovered</q-item-label>
                      <q-item-label>{{ formatDateTime(discoveredAt) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Structure -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Schema Structure</div>

                <q-tree
                  :nodes="schemaTree"
                  node-key="id"
                  default-expand-all
                  icon="folder"
                  no-connectors
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Statistics -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Schema Statistics</div>

                <div class="row q-gutter-md">
                  <div class="col-12 col-md-3">
                    <q-card flat bordered class="bg-blue-1">
                      <q-card-section class="text-center">
                        <q-icon name="view_column" size="2rem" color="blue" class="q-mb-sm" />
                        <div class="text-h6">{{ totalColumns }}</div>
                        <div class="text-caption">Total Columns</div>
                      </q-card-section>
                    </q-card>
                  </div>

                  <div class="col-12 col-md-3">
                    <q-card flat bordered class="bg-green-1">
                      <q-card-section class="text-center">
                        <q-icon name="category" size="2rem" color="green" class="q-mb-sm" />
                        <div class="text-h6">{{ dataTypes.length }}</div>
                        <div class="text-caption">Data Types</div>
                      </q-card-section>
                    </q-card>
                  </div>

                  <div class="col-12 col-md-3">
                    <q-card flat bordered class="bg-orange-1">
                      <q-card-section class="text-center">
                        <q-icon name="memory" size="2rem" color="orange" class="q-mb-sm" />
                        <div class="text-h6">{{ estimatedSize }}</div>
                        <div class="text-caption">Schema Size</div>
                      </q-card-section>
                    </q-card>
                  </div>

                  <div class="col-12 col-md-3">
                    <q-card flat bordered class="bg-purple-1">
                      <q-card-section class="text-center">
                        <q-icon name="verified" size="2rem" color="purple" class="q-mb-sm" />
                        <div class="text-h6">{{ schemaComplexity }}</div>
                        <div class="text-caption">Complexity</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- JSON Schema Tab -->
      <q-tab-panel name="json">
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">JSON Schema Representation</div>
              <div class="row q-gutter-sm">
                <q-toggle
                  v-model="prettyPrint"
                  label="Pretty Print"
                  color="primary"
                />
                <q-toggle
                  v-model="showLineNumbers"
                  label="Line Numbers"
                  color="secondary"
                />
              </div>
            </div>

            <q-input
              :model-value="formattedSchema"
              type="textarea"
              :rows="schemaRows"
              outlined
              readonly
              class="schema-viewer"
              :class="{ 'line-numbers': showLineNumbers }"
            />

            <div class="row q-gutter-sm q-mt-md">
              <q-btn
                label="Copy JSON"
                icon="content_copy"
                color="primary"
                outline
                @click="copyJSON"
              />
              <q-btn
                label="Download JSON"
                icon="file_download"
                color="secondary"
                outline
                @click="downloadJSON"
              />
              <q-btn
                label="Validate JSON"
                icon="check"
                color="positive"
                outline
                @click="validateJSON"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-tab-panel>

      <!-- Metadata Tab -->
      <q-tab-panel name="metadata">
        <div class="row q-gutter-lg">
          <!-- Discovery Metadata -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Discovery Metadata</div>

                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="source" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Discovery Method</q-item-label>
                      <q-item-label>{{ discoveryMethod }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="schedule" color="blue" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Discovery Time</q-item-label>
                      <q-item-label>{{ discoveryTime }} ms</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="sampling" color="green" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Sample Size</q-item-label>
                      <q-item-label>{{ sampleSize }} records</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="check_circle" color="positive" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Schema Version</q-item-label>
                      <q-item-label>{{ schemaVersion }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Quality Metadata -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Quality Metadata</div>

                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="assessment" color="orange" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Completeness</q-item-label>
                      <q-item-label>{{ completeness }}%</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="precision_manufacturing" color="purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Consistency</q-item-label>
                      <q-item-label>{{ consistency }}%</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="verified" color="positive" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Validity</q-item-label>
                      <q-item-label>{{ validity }}%</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="speed" color="warning" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Overall Score</q-item-label>
                      <q-item-label>{{ overallScore }}%</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Evolution -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Schema Evolution</div>

                <q-timeline color="primary">
                  <q-timeline-entry
                    v-for="change in schemaChanges"
                    :key="change.id"
                    :title="change.title"
                    :subtitle="change.timestamp"
                    :icon="change.icon"
                    :color="change.color"
                  >
                    <div>{{ change.description }}</div>
                  </q-timeline-entry>
                </q-timeline>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Validation Tab -->
      <q-tab-panel name="validation">
        <div class="row q-gutter-lg">
          <!-- Validation Results -->
          <div class="col-12 col-md-8">
            <q-card flat bordered>
              <q-card-section>
                <div class="row items-center justify-between q-mb-md">
                  <div class="text-h6">Validation Results</div>
                  <q-btn
                    label="Run Validation"
                    icon="play_arrow"
                    color="primary"
                    @click="runValidation"
                    :loading="validating"
                  />
                </div>

                <div v-if="validationResults.length === 0" class="text-center q-pa-lg text-grey-6">
                  <q-icon name="verified" size="3rem" class="q-mb-md" />
                  <div class="text-h6">No Validation Run</div>
                  <div class="text-body2">Click "Run Validation" to check schema integrity</div>
                </div>

                <q-list v-else separator>
                  <q-item
                    v-for="result in validationResults"
                    :key="result.id"
                    :class="getValidationClass(result.type)"
                  >
                    <q-item-section avatar>
                      <q-icon
                        :name="getValidationIcon(result.type)"
                        :color="getValidationColor(result.type)"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ result.message }}</q-item-label>
                      <q-item-label caption>{{ result.details }}</q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <q-chip
                        :color="getValidationColor(result.type)"
                        text-color="white"
                        size="sm"
                      >
                        {{ result.type.toUpperCase() }}
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Validation Summary -->
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Validation Summary</div>

                <div class="text-center q-mb-md">
                  <q-circular-progress
                    :value="validationScore"
                    size="100px"
                    :thickness="0.2"
                    :color="getScoreColor(validationScore)"
                    track-color="grey-3"
                  >
                    <div class="text-h5">{{ Math.round(validationScore) }}%</div>
                  </q-circular-progress>
                  <div class="text-caption q-mt-sm">Schema Health Score</div>
                </div>

                <q-list dense>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="check_circle" color="positive" size="sm" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Passed</q-item-label>
                      <q-item-label>{{ passedValidations }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="warning" color="warning" size="sm" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Warnings</q-item-label>
                      <q-item-label>{{ warningValidations }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="error" color="negative" size="sm" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Errors</q-item-label>
                      <q-item-label>{{ errorValidations }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <!-- Validation Rules -->
            <q-card flat bordered class="q-mt-md">
              <q-card-section>
                <div class="text-h6 q-mb-md">Validation Rules</div>

                <q-list dense>
                  <q-item v-for="rule in validationRules" :key="rule.id">
                    <q-item-section avatar>
                      <q-checkbox
                        :model-value="rule.enabled"
                        @update:model-value="toggleRule(rule.id)"
                        color="primary"
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ rule.name }}</q-item-label>
                      <q-item-label caption>{{ rule.description }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  tags: Array,
  fields: Array,
  sampleData: Array,
  measurement: String
})

// Reactive data
const $q = useQuasar()
const activeTab = ref('overview')
const prettyPrint = ref(true)
const showLineNumbers = ref(true)
const validating = ref(false)
const validationResults = ref([])
const discoveredAt = ref(new Date())

// Validation rules
const validationRules = ref([
  {
    id: 'required_fields',
    name: 'Required Fields',
    description: 'Check for required field presence',
    enabled: true
  },
  {
    id: 'data_types',
    name: 'Data Type Consistency',
    description: 'Validate data type consistency',
    enabled: true
  },
  {
    id: 'null_values',
    name: 'Null Value Validation',
    description: 'Check for unexpected null values',
    enabled: true
  },
  {
    id: 'value_ranges',
    name: 'Value Range Validation',
    description: 'Validate numeric value ranges',
    enabled: false
  }
])

// Computed properties
const totalColumns = computed(() => {
  return props.tags.length + props.fields.length
})

const dataTypes = computed(() => {
  const types = new Set()

  // Analyze sample data to determine types
  if (props.sampleData.length > 0) {
    const firstRow = props.sampleData[0]
    Object.values(firstRow).forEach(value => {
      if (value !== null) {
        types.add(typeof value)
      }
    })
  }

  return Array.from(types)
})

const estimatedSize = computed(() => {
  const schemaString = JSON.stringify(rawSchema.value)
  const bytes = new Blob([schemaString]).size

  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
})

const schemaComplexity = computed(() => {
  const columnCount = totalColumns.value
  const typeCount = dataTypes.value.length
  const sampleSize = props.sampleData.length

  // Simple complexity calculation
  const complexity = Math.min(100, (columnCount * 2) + (typeCount * 5) + Math.log10(sampleSize + 1) * 10)

  if (complexity < 30) return 'Low'
  if (complexity < 70) return 'Medium'
  return 'High'
})

const rawSchema = computed(() => {
  return {
    measurement: props.measurement,
    version: '1.0',
    timestamp: discoveredAt.value.toISOString(),
    tags: props.tags.map(tag => ({
      name: tag,
      type: 'string',
      description: `Tag column: ${tag}`
    })),
    fields: props.fields.map(field => ({
      name: typeof field === 'string' ? field : field.name,
      type: typeof field === 'string' ? 'unknown' : field.type || 'unknown',
      description: typeof field === 'string' ? `Field column: ${field}` : field.description || `Field column: ${field.name}`
    })),
    sampleData: props.sampleData.slice(0, 3),
    metadata: {
      discoveryMethod: 'automatic',
      sampleSize: props.sampleData.length,
      totalColumns: totalColumns.value,
      dataTypes: dataTypes.value
    }
  }
})

const formattedSchema = computed(() => {
  return prettyPrint.value
    ? JSON.stringify(rawSchema.value, null, 2)
    : JSON.stringify(rawSchema.value)
})

const schemaRows = computed(() => {
  return Math.max(10, formattedSchema.value.split('\n').length)
})

const schemaTree = computed(() => {
  return [
    {
      id: 'measurement',
      label: `Measurement: ${props.measurement || 'Unknown'}`,
      icon: 'table_chart',
      children: [
        {
          id: 'tags',
          label: `Tags (${props.tags.length})`,
          icon: 'label',
          children: props.tags.map((tag, index) => ({
            id: `tag-${index}`,
            label: tag,
            icon: 'label'
          }))
        },
        {
          id: 'fields',
          label: `Fields (${props.fields.length})`,
          icon: 'insights',
          children: props.fields.map((field, index) => ({
            id: `field-${index}`,
            label: typeof field === 'string' ? field : field.name,
            icon: 'insights'
          }))
        },
        {
          id: 'sample',
          label: `Sample Data (${props.sampleData.length})`,
          icon: 'preview',
          children: []
        }
      ]
    }
  ]
})

// Metadata computed properties
const discoveryMethod = computed(() => 'Automatic Schema Discovery')
const discoveryTime = computed(() => Math.floor(Math.random() * 1000) + 200)
const sampleSize = computed(() => props.sampleData.length)
const schemaVersion = computed(() => '1.0.0')

const completeness = computed(() => {
  if (props.sampleData.length === 0) return 0

  const totalCells = props.sampleData.length * totalColumns.value
  const nonNullCells = props.sampleData.reduce((count, row) => {
    return count + Object.values(row).filter(val => val != null).length
  }, 0)

  return Math.round((nonNullCells / totalCells) * 100)
})

const consistency = computed(() => {
  // Mock consistency calculation
  return Math.max(85, Math.floor(Math.random() * 15) + 85)
})

const validity = computed(() => {
  // Mock validity calculation
  return Math.max(90, Math.floor(Math.random() * 10) + 90)
})

const overallScore = computed(() => {
  return Math.round((completeness.value + consistency.value + validity.value) / 3)
})

const schemaChanges = computed(() => [
  {
    id: 1,
    title: 'Schema Discovered',
    timestamp: formatDateTime(discoveredAt.value),
    description: 'Initial schema discovery completed',
    icon: 'search',
    color: 'primary'
  },
  {
    id: 2,
    title: 'Fields Analyzed',
    timestamp: formatDateTime(new Date(discoveredAt.value.getTime() + 60000)),
    description: `${props.fields.length} field columns identified`,
    icon: 'insights',
    color: 'positive'
  },
  {
    id: 3,
    title: 'Tags Processed',
    timestamp: formatDateTime(new Date(discoveredAt.value.getTime() + 120000)),
    description: `${props.tags.length} tag columns processed`,
    icon: 'label',
    color: 'info'
  }
])

// Validation computed properties
const validationScore = computed(() => {
  if (validationResults.value.length === 0) return 100

  const errors = errorValidations.value
  const warnings = warningValidations.value
  const total = validationResults.value.length

  return Math.max(0, 100 - (errors * 20) - (warnings * 5))
})

const passedValidations = computed(() => {
  return validationResults.value.filter(r => r.type === 'success').length
})

const warningValidations = computed(() => {
  return validationResults.value.filter(r => r.type === 'warning').length
})

const errorValidations = computed(() => {
  return validationResults.value.filter(r => r.type === 'error').length
})

// Methods
onMounted(() => {
  // Initialize component
})

const formatDateTime = (date) => {
  return new Date(date).toLocaleString()
}

const copySchema = async () => {
  try {
    await navigator.clipboard.writeText(formattedSchema.value)
    $q.notify({
      type: 'positive',
      message: 'Schema copied to clipboard',
      icon: 'content_copy'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy schema'
    })
  }
}

const exportSchema = () => {
  const blob = new Blob([formattedSchema.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `${props.measurement || 'schema'}_schema.json`
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

const validateSchema = async () => {
  validating.value = true

  try {
    await runValidation()
  } finally {
    validating.value = false
  }
}

const copyJSON = async () => {
  try {
    await navigator.clipboard.writeText(formattedSchema.value)
    $q.notify({
      type: 'positive',
      message: 'JSON copied to clipboard',
      icon: 'content_copy'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy JSON'
    })
  }
}

const downloadJSON = () => {
  exportSchema()
}

const validateJSON = () => {
  try {
    JSON.parse(formattedSchema.value)
    $q.notify({
      type: 'positive',
      message: 'JSON is valid',
      icon: 'check_circle'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Invalid JSON format',
      caption: error.message
    })
  }
}

const runValidation = async () => {
  validating.value = true
  validationResults.value = []

  try {
    // Simulate validation process
    await new Promise(resolve => setTimeout(resolve, 1500))

    const enabledRules = validationRules.value.filter(rule => rule.enabled)
    const results = []

    // Mock validation results
    if (enabledRules.find(r => r.id === 'required_fields')) {
      if (props.fields.length > 0) {
        results.push({
          id: 'required_fields_pass',
          type: 'success',
          message: 'Required fields validation passed',
          details: `Found ${props.fields.length} field columns`
        })
      } else {
        results.push({
          id: 'required_fields_fail',
          type: 'error',
          message: 'No field columns found',
          details: 'At least one field column is required'
        })
      }
    }

    if (enabledRules.find(r => r.id === 'data_types')) {
      const typeConsistency = dataTypes.value.length <= 5
      results.push({
        id: 'data_types_check',
        type: typeConsistency ? 'success' : 'warning',
        message: typeConsistency ? 'Data types are consistent' : 'Multiple data types detected',
        details: `Found ${dataTypes.value.length} different data types: ${dataTypes.value.join(', ')}`
      })
    }

    if (enabledRules.find(r => r.id === 'null_values')) {
      const nullPercentage = 100 - completeness.value
      if (nullPercentage < 10) {
        results.push({
          id: 'null_values_good',
          type: 'success',
          message: 'Low null value percentage',
          details: `Only ${nullPercentage.toFixed(1)}% null values`
        })
      } else if (nullPercentage < 30) {
        results.push({
          id: 'null_values_warning',
          type: 'warning',
          message: 'Moderate null value percentage',
          details: `${nullPercentage.toFixed(1)}% null values detected`
        })
      } else {
        results.push({
          id: 'null_values_error',
          type: 'error',
          message: 'High null value percentage',
          details: `${nullPercentage.toFixed(1)}% null values - data quality issues`
        })
      }
    }

    if (enabledRules.find(r => r.id === 'value_ranges')) {
      results.push({
        id: 'value_ranges_info',
        type: 'info',
        message: 'Value range validation',
        details: 'Value range validation completed successfully'
      })
    }

    validationResults.value = results

    $q.notify({
      type: 'positive',
      message: 'Schema validation completed',
      caption: `${results.length} checks performed`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Validation failed',
      caption: error.message
    })
  } finally {
    validating.value = false
  }
}

const getValidationIcon = (type) => {
  const icons = {
    'success': 'check_circle',
    'warning': 'warning',
    'error': 'error',
    'info': 'info'
  }
  return icons[type] || 'help'
}

const getValidationColor = (type) => {
  const colors = {
    'success': 'positive',
    'warning': 'warning',
    'error': 'negative',
    'info': 'info'
  }
  return colors[type] || 'grey'
}

const getValidationClass = (type) => {
  const classes = {
    'success': 'bg-green-1',
    'warning': 'bg-orange-1',
    'error': 'bg-red-1',
    'info': 'bg-blue-1'
  }
  return classes[type] || ''
}

const getScoreColor = (score) => {
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
}

const toggleRule = (ruleId) => {
  const rule = validationRules.value.find(r => r.id === ruleId)
  if (rule) {
    rule.enabled = !rule.enabled
  }
}
</script>

<style scoped>
.raw-schema-viewer {
  background-color: #fafafa;
  min-height: 100%;
}

.schema-viewer {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}

.schema-viewer .q-field__control {
  background-color: #f8f9fa;
}

.line-numbers {
  counter-reset: line;
}

.line-numbers .q-field__control::before {
  content: counter(line);
  counter-increment: line;
  position: absolute;
  left: 8px;
  color: #999;
  font-size: 11px;
  line-height: 1.4;
  pointer-events: none;
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-orange-1 {
  background-color: rgba(255, 152, 0, 0.1);
}

.bg-purple-1 {
  background-color: rgba(156, 39, 176, 0.1);
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

.q-tree {
  font-size: 14px;
}

.q-timeline-entry {
  margin-bottom: 16px;
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
.q-field__control {
  max-height: 600px;
  overflow-y: auto;
}

.q-field__control::-webkit-scrollbar {
  width: 8px;
}

.q-field__control::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.q-field__control::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.q-field__control::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .schema-viewer {
    font-size: 10px;
  }

  .row.q-gutter-lg {
    margin: -8px;
  }

  .row.q-gutter-lg > div {
    padding: 8px;
  }
}
</style>
