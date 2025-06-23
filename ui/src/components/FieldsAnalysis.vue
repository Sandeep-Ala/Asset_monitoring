<!-- ui/src/components/FieldsAnalysis.vue -->
<!-- Cross-measurement field analysis component -->

<template>
  <div class="fields-analysis">
    <!-- Analysis Controls -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="text-h6">
              <q-icon name="data_object" class="q-mr-sm" />
              Field Analysis
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md items-end">
              <!-- Field Selection -->
              <div class="col-12 col-md-4">
                <q-select
                  v-model="selectedFields"
                  :options="fieldOptions"
                  label="Select Fields"
                  multiple
                  use-chips
                  outlined
                  dense
                  option-label="displayName"
                  option-value="id"
                  @update:model-value="updateAnalysis"
                >
                  <template #option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section avatar>
                        <q-icon :name="getFieldTypeIcon(scope.opt.type)" :color="getFieldTypeColor(scope.opt.type)" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.displayName }}</q-item-label>
                        <q-item-label caption>{{ scope.opt.measurement }} • {{ scope.opt.type }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>

              <!-- Analysis Method -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="analysisMethod"
                  :options="analysisMethodOptions"
                  label="Analysis Method"
                  outlined
                  dense
                  @update:model-value="updateAnalysis"
                />
              </div>

              <!-- Grouping -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="groupingMethod"
                  :options="groupingOptions"
                  label="Group By"
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
                    icon="analytics"
                    color="primary"
                    @click="runFieldAnalysis"
                    :loading="analyzing"
                    :disable="selectedFields.length === 0"
                  />
                  <q-btn
                    icon="refresh"
                    flat
                    round
                    @click="refreshAnalysis"
                    :loading="refreshing"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Analysis Summary -->
    <div v-if="analysisResults" class="row q-gutter-md q-mb-lg">
      <div class="col-6 col-md-3">
        <q-card flat class="bg-blue-1 text-center q-pa-md">
          <q-icon name="data_object" size="2rem" color="blue" class="q-mb-sm" />
          <div class="text-h5">{{ analysisResults.totalFields }}</div>
          <div class="text-body2">Fields Analyzed</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-green-1 text-center q-pa-md">
          <q-icon name="table_chart" size="2rem" color="green" class="q-mb-sm" />
          <div class="text-h5">{{ analysisResults.measurementsCount }}</div>
          <div class="text-body2">Measurements</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-orange-1 text-center q-pa-md">
          <q-icon name="trending_up" size="2rem" color="orange" class="q-mb-sm" />
          <div class="text-h5">{{ analysisResults.correlations }}</div>
          <div class="text-body2">Correlations</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-purple-1 text-center q-pa-md">
          <q-icon name="timeline" size="2rem" color="purple" class="q-mb-sm" />
          <div class="text-h5">{{ formatNumber(analysisResults.dataPoints) }}</div>
          <div class="text-body2">Data Points</div>
        </q-card>
      </div>
    </div>

    <!-- Field Comparison Table -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="compare_arrows" class="q-mr-sm" />
              Field Comparison
            </div>
          </q-card-section>
          <q-card-section>
            <q-table
              :rows="fieldComparisonData"
              :columns="comparisonColumns"
              row-key="fieldId"
              flat
              :pagination="{ rowsPerPage: 15 }"
              :loading="analyzing"
            >
              <template #body-cell-field="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-icon :name="getFieldTypeIcon(props.row.type)" :color="getFieldTypeColor(props.row.type)" />
                    <div>
                      <div class="text-body2">{{ props.row.fieldName }}</div>
                      <div class="text-caption text-grey-6">{{ props.row.measurement }}</div>
                    </div>
                  </div>
                </q-td>
              </template>
              <template #body-cell-type="props">
                <q-td :props="props">
                  <q-chip :color="getFieldTypeColor(props.value)" text-color="white" size="sm">
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>
              <template #body-cell-nulls="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-linear-progress
                      :value="props.value / 100"
                      :color="getNullsColor(props.value)"
                      size="20px"
                      style="width: 60px;"
                    />
                    <span class="text-caption">{{ props.value }}%</span>
                  </div>
                </q-td>
              </template>
              <template #body-cell-uniqueness="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-linear-progress
                      :value="props.value / 100"
                      color="blue"
                      size="20px"
                      style="width: 60px;"
                    />
                    <span class="text-caption">{{ props.value }}%</span>
                  </div>
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="q-gutter-xs">
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click="viewFieldDetails(props.row)"
                    >
                      <q-tooltip>View Details</q-tooltip>
                    </q-btn>
                    <q-btn
                      icon="bar_chart"
                      flat
                      round
                      size="sm"
                      @click="analyzeField(props.row)"
                    >
                      <q-tooltip>Analyze Field</q-tooltip>
                    </q-btn>
                    <q-btn
                      icon="compare"
                      flat
                      round
                      size="sm"
                      @click="compareFields(props.row)"
                    >
                      <q-tooltip>Compare Fields</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Statistical Analysis -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">
              <q-icon name="functions" class="q-mr-sm" />
              Statistical Summary
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="statisticalSummary.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="functions" size="2rem" class="q-mb-sm" />
              <div>No statistical data available</div>
            </div>
            <q-list v-else dense>
              <q-item v-for="stat in statisticalSummary" :key="stat.field">
                <q-item-section>
                  <q-item-label>{{ stat.field }}</q-item-label>
                  <q-item-label caption>
                    Mean: {{ stat.mean }} | Std: {{ stat.std }} | Range: {{ stat.range }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip :color="getVariabilityColor(stat.variability)" text-color="white" size="sm">
                    {{ stat.variability }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Correlation Matrix -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-purple-1">
            <div class="text-h6">
              <q-icon name="grid_on" class="q-mr-sm" />
              Field Correlations
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="correlationMatrix.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="grid_on" size="2rem" class="q-mb-sm" />
              <div>No correlation data available</div>
            </div>
            <div v-else class="correlation-grid">
              <div v-for="row in correlationMatrix" :key="row.field1" class="correlation-row">
                <div class="field-label">{{ row.field1 }}</div>
                <div class="correlations">
                  <div
                    v-for="corr in row.correlations"
                    :key="corr.field2"
                    class="correlation-cell"
                    :style="getCorrelationStyle(corr.value)"
                  >
                    <q-tooltip>
                      {{ row.field1 }} vs {{ corr.field2 }}: {{ corr.value }}
                    </q-tooltip>
                    {{ corr.value }}
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Quality Assessment -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-red-1">
            <div class="text-h6">
              <q-icon name="verified" class="q-mr-sm" />
              Data Quality Assessment
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <!-- Quality Metrics -->
              <div class="col-12 col-md-8">
                <div class="row q-gutter-md">
                  <div v-for="metric in qualityMetrics" :key="metric.name" class="col-6 col-md-3">
                    <div class="text-center">
                      <q-circular-progress
                        :value="metric.score"
                        size="80px"
                        :thickness="0.15"
                        :color="getQualityColor(metric.score)"
                        track-color="grey-3"
                        show-value
                        font-size="14px"
                      />
                      <div class="text-body2 q-mt-sm">{{ metric.name }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quality Issues -->
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">Quality Issues</div>
                <q-list dense>
                  <q-item v-for="issue in qualityIssues" :key="issue.id">
                    <q-item-section avatar>
                      <q-icon
                        :name="getSeverityIcon(issue.severity)"
                        :color="getSeverityColor(issue.severity)"
                        size="sm"
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="text-body2">{{ issue.description }}</q-item-label>
                      <q-item-label caption>{{ issue.field }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Field Relationships -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="text-h6">
              <q-icon name="account_tree" class="q-mr-sm" />
              Field Relationships
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="fieldRelationships.length === 0" class="text-center q-pa-lg text-grey-6">
              <q-icon name="account_tree" size="3rem" class="q-mb-md" />
              <div class="text-h6">No Relationships Found</div>
              <div class="text-body2 q-mb-lg">
                Run field analysis to discover relationships between fields
              </div>
            </div>
            <div v-else class="row q-gutter-md">
              <div v-for="relationship in fieldRelationships" :key="relationship.id" class="col-12 col-md-6">
                <q-card flat class="bg-grey-1">
                  <q-card-section>
                    <div class="row items-center q-gutter-sm q-mb-sm">
                      <q-chip color="primary" text-color="white" size="sm">
                        {{ relationship.field1 }}
                      </q-chip>
                      <q-icon :name="getRelationshipIcon(relationship.type)" />
                      <q-chip color="secondary" text-color="white" size="sm">
                        {{ relationship.field2 }}
                      </q-chip>
                    </div>
                    <div class="text-body2 q-mb-xs">{{ relationship.description }}</div>
                    <div class="row items-center justify-between">
                      <q-chip
                        :color="getStrengthColor(relationship.strength)"
                        text-color="white"
                        size="sm"
                      >
                        {{ relationship.strength }} Strength
                      </q-chip>
                      <q-btn
                        label="Details"
                        size="sm"
                        flat
                        color="primary"
                        @click="viewRelationshipDetails(relationship)"
                      />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Field Details Dialog -->
    <q-dialog v-model="showFieldDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Field Details: {{ selectedFieldDetails?.fieldName }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showFieldDialog = false" />
        </q-card-section>
        <q-card-section class="scroll">
          <div v-if="selectedFieldDetails">
            <!-- Field details content would go here -->
            <div class="row q-gutter-md">
              <div class="col-12 col-md-6">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle1 q-mb-md">Basic Information</div>
                    <q-list dense>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption>Field Name</q-item-label>
                          <q-item-label>{{ selectedFieldDetails.fieldName }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption>Measurement</q-item-label>
                          <q-item-label>{{ selectedFieldDetails.measurement }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption>Data Type</q-item-label>
                          <q-item-label>{{ selectedFieldDetails.type }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card-section>
                </q-card>
              </div>
              <!-- More field details would be added here -->
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  fields: {
    type: Array,
    default: () => []
  },
  schema: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['analyze-field', 'compare-fields'])

// Reactive data
const $q = useQuasar()
const selectedFields = ref([])
const analysisMethod = ref('statistical')
const groupingMethod = ref('measurement')
const analyzing = ref(false)
const refreshing = ref(false)
const showFieldDialog = ref(false)
const selectedFieldDetails = ref(null)

const analysisResults = ref(null)
const fieldComparisonData = ref([])
const statisticalSummary = ref([])
const correlationMatrix = ref([])
const qualityMetrics = ref([])
const qualityIssues = ref([])
const fieldRelationships = ref([])

// Computed properties
const fieldOptions = computed(() => {
  if (!props.schema?.fields) return []

  const fields = []
  Object.entries(props.schema.fields).forEach(([measurement, measurementFields]) => {
    measurementFields.forEach((field, index) => {
      fields.push({
        id: `${measurement}.${field.name || field}`,
        fieldName: field.name || field,
        measurement,
        type: field.type || inferFieldType(field.name || field),
        displayName: `${field.name || field} (${measurement})`
      })
    })
  })

  return fields
})

const analysisMethodOptions = [
  { label: 'Statistical Analysis', value: 'statistical' },
  { label: 'Correlation Analysis', value: 'correlation' },
  { label: 'Quality Analysis', value: 'quality' },
  { label: 'Trend Analysis', value: 'trend' }
]

const groupingOptions = [
  { label: 'By Measurement', value: 'measurement' },
  { label: 'By Data Type', value: 'type' },
  { label: 'By Field Name Pattern', value: 'pattern' },
  { label: 'No Grouping', value: 'none' }
]

const comparisonColumns = [
  {
    name: 'field',
    label: 'Field',
    field: 'field',
    align: 'left',
    sortable: true
  },
  {
    name: 'type',
    label: 'Type',
    field: 'type',
    align: 'center',
    sortable: true
  },
  {
    name: 'nulls',
    label: 'Null %',
    field: 'nulls',
    align: 'center',
    sortable: true
  },
  {
    name: 'uniqueness',
    label: 'Unique %',
    field: 'uniqueness',
    align: 'center',
    sortable: true
  },
  {
    name: 'avgValue',
    label: 'Avg Value',
    field: 'avgValue',
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

// Methods
const inferFieldType = (fieldName) => {
  const lowerField = fieldName.toLowerCase()
  if (lowerField.includes('voltage') || lowerField.includes('current') || lowerField.includes('temperature')) {
    return 'number'
  }
  if (lowerField.includes('time') || lowerField.includes('date')) {
    return 'datetime'
  }
  if (lowerField.includes('status') || lowerField.includes('state')) {
    return 'string'
  }
  return 'number'
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

const getNullsColor = (percentage) => {
  if (percentage <= 5) return 'positive'
  if (percentage <= 15) return 'warning'
  return 'negative'
}

const getVariabilityColor = (variability) => {
  const colors = {
    Low: 'positive',
    Medium: 'warning',
    High: 'negative'
  }
  return colors[variability] || 'grey'
}

const getQualityColor = (score) => {
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
}

const getSeverityIcon = (severity) => {
  const icons = {
    low: 'info',
    medium: 'warning',
    high: 'error'
  }
  return icons[severity] || 'help'
}

const getSeverityColor = (severity) => {
  const colors = {
    low: 'info',
    medium: 'warning',
    high: 'negative'
  }
  return colors[severity] || 'grey'
}

const getRelationshipIcon = (type) => {
  const icons = {
    correlation: 'trending_up',
    dependency: 'arrow_forward',
    similarity: 'compare_arrows'
  }
  return icons[type] || 'link'
}

const getStrengthColor = (strength) => {
  const colors = {
    Strong: 'positive',
    Medium: 'warning',
    Weak: 'info'
  }
  return colors[strength] || 'grey'
}

const getCorrelationStyle = (value) => {
  const absValue = Math.abs(parseFloat(value))
  const opacity = absValue
  const color = parseFloat(value) >= 0 ? '76, 175, 80' : '244, 67, 54' // green : red
  return {
    backgroundColor: `rgba(${color}, ${opacity})`,
    color: absValue > 0.5 ? 'white' : 'black'
  }
}

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const updateAnalysis = () => {
  if (selectedFields.value.length > 0) {
    runFieldAnalysis()
  }
}

const runFieldAnalysis = async () => {
  if (selectedFields.value.length === 0) {
    $q.notify({
      type: 'warning',
      message: 'Please select at least one field to analyze'
    })
    return
  }

  analyzing.value = true

  try {
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 2500))

    // Generate mock analysis results
    analysisResults.value = {
      totalFields: selectedFields.value.length,
      measurementsCount: new Set(selectedFields.value.map(f => f.split('.')[0])).size,
      correlations: Math.floor(Math.random() * 10 + 5),
      dataPoints: Math.floor(Math.random() * 500000 + 100000)
    }

    // Generate field comparison data
    fieldComparisonData.value = selectedFields.value.map(fieldId => {
      const [measurement, fieldName] = fieldId.split('.')
      const fieldInfo = fieldOptions.value.find(f => f.id === fieldId)

      return {
        fieldId,
        fieldName,
        measurement,
        type: fieldInfo?.type || 'number',
        nulls: Math.floor(Math.random() * 20),
        uniqueness: Math.floor(Math.random() * 40 + 60),
        avgValue: (Math.random() * 100).toFixed(2)
      }
    })

    // Generate statistical summary
    statisticalSummary.value = selectedFields.value
      .filter(fieldId => fieldOptions.value.find(f => f.id === fieldId)?.type === 'number')
      .map(fieldId => {
        const fieldName = fieldId.split('.')[1]
        return {
          field: fieldName,
          mean: (Math.random() * 100).toFixed(2),
          std: (Math.random() * 20).toFixed(2),
          range: `${(Math.random() * 50).toFixed(1)} - ${(Math.random() * 50 + 50).toFixed(1)}`,
          variability: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)]
        }
      })

    // Generate correlation matrix
    const numericFields = selectedFields.value.filter(fieldId =>
      fieldOptions.value.find(f => f.id === fieldId)?.type === 'number'
    )

    correlationMatrix.value = numericFields.slice(0, 4).map(field1 => ({
      field1: field1.split('.')[1],
      correlations: numericFields.slice(0, 4).map(field2 => ({
        field2: field2.split('.')[1],
        value: field1 === field2 ? '1.00' : (Math.random() * 2 - 1).toFixed(2)
      }))
    }))

    // Generate quality metrics
    qualityMetrics.value = [
      { name: 'Completeness', score: Math.floor(Math.random() * 20 + 80) },
      { name: 'Accuracy', score: Math.floor(Math.random() * 15 + 85) },
      { name: 'Consistency', score: Math.floor(Math.random() * 25 + 75) },
      { name: 'Validity', score: Math.floor(Math.random() * 30 + 70) }
    ]

    // Generate quality issues
    qualityIssues.value = [
      {
        id: 1,
        field: selectedFields.value[0]?.split('.')[1] || 'voltage',
        description: 'Outlier values detected',
        severity: 'medium'
      },
      {
        id: 2,
        field: selectedFields.value[1]?.split('.')[1] || 'current',
        description: 'Missing data points',
        severity: 'low'
      }
    ]

    // Generate field relationships
    if (selectedFields.value.length >= 2) {
      fieldRelationships.value = [
        {
          id: 1,
          field1: selectedFields.value[0].split('.')[1],
          field2: selectedFields.value[1].split('.')[1],
          type: 'correlation',
          description: 'Strong positive correlation detected',
          strength: 'Strong'
        },
        {
          id: 2,
          field1: selectedFields.value[0].split('.')[1],
          field2: selectedFields.value[Math.min(2, selectedFields.value.length - 1)].split('.')[1],
          type: 'dependency',
          description: 'Possible causal relationship',
          strength: 'Medium'
        }
      ]
    }

    $q.notify({
      type: 'positive',
      message: 'Field analysis completed successfully',
      caption: `Analyzed ${selectedFields.value.length} field(s)`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Field analysis failed',
      caption: error.message
    })
  } finally {
    analyzing.value = false
  }
}

const refreshAnalysis = async () => {
  refreshing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    if (selectedFields.value.length > 0) {
      await runFieldAnalysis()
    }
  } finally {
    refreshing.value = false
  }
}

const viewFieldDetails = (field) => {
  selectedFieldDetails.value = field
  showFieldDialog.value = true
}

const analyzeField = (field) => {
  emit('analyze-field', field)
}

const compareFields = (field) => {
  emit('compare-fields', [field, ...selectedFields.value.slice(0, 3)])
}

const viewRelationshipDetails = (relationship) => {
  $q.notify({
    type: 'info',
    message: `Relationship details: ${relationship.field1} ${relationship.type} ${relationship.field2}`,
    caption: 'Detailed relationship analysis coming soon'
  })
}

// Lifecycle
onMounted(() => {
  // Auto-select first few fields if available
  if (fieldOptions.value.length > 0) {
    selectedFields.value = fieldOptions.value.slice(0, 3).map(f => f.id)
    runFieldAnalysis()
  }
})
</script>

<style scoped>
.fields-analysis {
  width: 100%;
}

.correlation-grid {
  display: grid;
  gap: 8px;
}

.correlation-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 8px;
  align-items: center;
}

.field-label {
  font-size: 12px;
  font-weight: 500;
  text-align: right;
  padding-right: 8px;
}

.correlations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
  gap: 4px;
}

.correlation-cell {
  padding: 8px 4px;
  text-align: center;
  font-size: 11px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
}

.text-h5 {
  font-weight: 600;
}

.q-chip {
  font-size: 11px;
}
</style>
