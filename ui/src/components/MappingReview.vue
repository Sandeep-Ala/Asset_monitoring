<!-- ui/src/components/MappingReview.vue -->
<template>
  <div class="mapping-review">
    <!-- Summary Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered class="summary-card">
          <q-card-section class="text-center">
            <q-icon name="precision_manufacturing" size="2rem" color="primary" class="q-mb-sm" />
            <div class="text-h6">{{ equipment?.name || 'Unknown' }}</div>
            <div class="text-caption text-grey-6">Target Equipment</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="summary-card">
          <q-card-section class="text-center">
            <q-icon name="table_chart" size="2rem" color="blue" class="q-mb-sm" />
            <div class="text-h6">{{ measurement }}</div>
            <div class="text-caption text-grey-6">Source Measurement</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="summary-card">
          <q-card-section class="text-center">
            <q-icon name="label" size="2rem" color="green" class="q-mb-sm" />
            <div class="text-h6">{{ tagMappingCount }}</div>
            <div class="text-caption text-grey-6">Tag Mappings</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="summary-card">
          <q-card-section class="text-center">
            <q-icon name="insights" size="2rem" color="orange" class="q-mb-sm" />
            <div class="text-h6">{{ fieldMappingCount }}</div>
            <div class="text-caption text-grey-6">Field Mappings</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Validation Results -->
    <div v-if="validationResults && Object.keys(validationResults).length > 0" class="q-mb-lg">
      <q-card flat bordered>
        <q-card-section class="bg-blue-1">
          <div class="text-h6">Validation Results</div>
          <div class="text-caption">Mapping validation and quality checks</div>
        </q-card-section>

        <q-card-section>
          <!-- Overall Status -->
          <div class="row items-center q-mb-md">
            <q-icon
              :name="validationResults.valid ? 'check_circle' : 'error'"
              :color="validationResults.valid ? 'positive' : 'negative'"
              size="md"
              class="q-mr-md"
            />
            <div>
              <div class="text-h6">
                {{ validationResults.valid ? 'Validation Passed' : 'Validation Issues Found' }}
              </div>
              <div class="text-caption text-grey-6">
                {{ validationResults.valid ? 'Mapping is ready for creation' : 'Please review the issues below' }}
              </div>
            </div>
          </div>

          <!-- Errors -->
          <div v-if="validationResults.errors && validationResults.errors.length > 0" class="q-mb-md">
            <div class="text-subtitle2 text-negative q-mb-sm">Errors</div>
            <q-list dense bordered>
              <q-item
                v-for="(error, index) in validationResults.errors"
                :key="index"
                class="bg-red-1"
              >
                <q-item-section avatar>
                  <q-icon name="error" color="negative" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ error }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Warnings -->
          <div v-if="validationResults.warnings && validationResults.warnings.length > 0" class="q-mb-md">
            <div class="text-subtitle2 text-warning q-mb-sm">Warnings</div>
            <q-list dense bordered>
              <q-item
                v-for="(warning, index) in validationResults.warnings"
                :key="index"
                class="bg-orange-1"
              >
                <q-item-section avatar>
                  <q-icon name="warning" color="warning" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ warning }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Validation Actions -->
          <div class="row q-gutter-sm">
            <q-btn
              label="Re-validate"
              icon="refresh"
              color="blue"
              outline
              @click="$emit('validate')"
            />
            <q-btn
              label="Test Mapping"
              icon="play_arrow"
              color="positive"
              outline
              @click="$emit('test-mapping')"
              :disable="!validationResults.valid"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Mapping Details -->
    <div class="row q-gutter-lg">
      <!-- Tag Mappings -->
      <div class="col-12 col-lg-6">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">Tag Mappings</div>
            <div class="text-caption">Source tags → Equipment filters</div>
          </q-card-section>

          <q-card-section v-if="tagMappingCount === 0" class="text-center q-pa-lg">
            <q-icon name="label_off" size="3rem" class="text-grey-4 q-mb-md" />
            <div class="text-h6 text-grey-6">No Tag Mappings</div>
            <div class="text-body2 text-grey-5">
              No tag mappings configured for this measurement
            </div>
          </q-card-section>

          <q-list v-else separator>
            <q-item v-for="(mapping, index) in tagMappingList" :key="index">
              <q-item-section avatar>
                <q-avatar color="blue" text-color="white" size="sm">
                  <q-icon name="label" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label class="mapping-flow">
                  <span class="source-field">{{ mapping.source }}</span>
                  <q-icon name="arrow_forward" size="sm" class="q-mx-sm" />
                  <span class="target-field">{{ mapping.target }}</span>
                </q-item-label>
                <q-item-label caption>{{ getMappingDescription('tag', mapping) }}</q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row items-center q-gutter-xs">
                  <q-chip
                    :color="getMappingQuality(mapping) === 'good' ? 'positive' : 'warning'"
                    text-color="white"
                    size="sm"
                  >
                    {{ getMappingQuality(mapping) }}
                  </q-chip>

                  <q-btn
                    icon="info"
                    flat
                    round
                    size="sm"
                    @click="showMappingInfo(mapping, 'tag')"
                  />
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <!-- Field Mappings -->
      <div class="col-12 col-lg-6">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="text-h6">Field Mappings</div>
            <div class="text-caption">Source fields → Equipment signals</div>
          </q-card-section>

          <q-card-section v-if="fieldMappingCount === 0" class="text-center q-pa-lg">
            <q-icon name="insights_off" size="3rem" class="text-grey-4 q-mb-md" />
            <div class="text-h6 text-grey-6">No Field Mappings</div>
            <div class="text-body2 text-grey-5">
              No field mappings configured for this measurement
            </div>
          </q-card-section>

          <q-list v-else separator>
            <q-item v-for="(mapping, index) in fieldMappingList" :key="index">
              <q-item-section avatar>
                <q-avatar color="orange" text-color="white" size="sm">
                  <q-icon name="insights" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label class="mapping-flow">
                  <span class="source-field">{{ mapping.source }}</span>
                  <q-icon name="arrow_forward" size="sm" class="q-mx-sm" />
                  <span class="target-field">{{ mapping.target }}</span>
                </q-item-label>
                <q-item-label caption>{{ getMappingDescription('field', mapping) }}</q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row items-center q-gutter-xs">
                  <q-chip
                    :color="getMappingQuality(mapping) === 'good' ? 'positive' : 'warning'"
                    text-color="white"
                    size="sm"
                  >
                    {{ getMappingQuality(mapping) }}
                  </q-chip>

                  <q-btn
                    icon="info"
                    flat
                    round
                    size="sm"
                    @click="showMappingInfo(mapping, 'field')"
                  />
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <!-- Equipment Details -->
    <div v-if="equipment" class="q-mt-lg">
      <q-card flat bordered>
        <q-card-section class="bg-blue-1">
          <div class="text-h6">Equipment Details</div>
          <div class="text-caption">Target equipment information and specifications</div>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-lg">
            <!-- Basic Info -->
            <div class="col-12 col-md-6">
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="badge" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Equipment ID</q-item-label>
                    <q-item-label>{{ equipment.id }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="business" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Name</q-item-label>
                    <q-item-label>{{ equipment.name }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="equipment.location">
                  <q-item-section avatar>
                    <q-icon name="place" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Location</q-item-label>
                    <q-item-label>{{ equipment.location }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item v-if="equipment.model_id">
                  <q-item-section avatar>
                    <q-icon name="category" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label caption>Model</q-item-label>
                    <q-item-label>Model {{ equipment.model_id }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Available Filters & Signals -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">Available Equipment Points</div>
              <div class="row q-gutter-md">
                <div class="col">
                  <q-chip color="blue" text-color="white" size="sm">
                    <q-icon name="filter_list" class="q-mr-xs" />
                    {{ getEquipmentFiltersCount() }} Filters
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="green" text-color="white" size="sm">
                    <q-icon name="sensors" class="q-mr-xs" />
                    {{ getEquipmentSignalsCount() }} Signals
                  </q-chip>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Mapping Configuration Summary -->
    <div class="q-mt-lg">
      <q-card flat bordered>
        <q-card-section class="bg-purple-1">
          <div class="text-h6">Configuration Summary</div>
          <div class="text-caption">Complete mapping configuration for review</div>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-lg">
            <!-- JSON Preview -->
            <div class="col-12 col-lg-6">
              <div class="text-subtitle2 q-mb-sm">Mapping Configuration</div>
              <q-input
                :model-value="formattedMappingConfig"
                type="textarea"
                rows="8"
                outlined
                readonly
                class="config-preview"
              />

              <div class="row q-gutter-sm q-mt-sm">
                <q-btn
                  label="Copy Config"
                  icon="content_copy"
                  size="sm"
                  outline
                  @click="copyConfig"
                />
                <q-btn
                  label="Export JSON"
                  icon="file_download"
                  size="sm"
                  outline
                  @click="exportConfig"
                />
              </div>
            </div>

            <!-- Mapping Statistics -->
            <div class="col-12 col-lg-6">
              <div class="text-subtitle2 q-mb-sm">Mapping Statistics</div>

              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="analytics" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Coverage Score</q-item-label>
                    <q-item-label caption>{{ coverageScore }}% of available points mapped</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-circular-progress
                      :value="coverageScore"
                      size="40px"
                      :thickness="0.3"
                      color="blue"
                      track-color="grey-3"
                    >
                      {{ Math.round(coverageScore) }}%
                    </q-circular-progress>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="auto_fix_high" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Auto-mapping Success</q-item-label>
                    <q-item-label caption>{{ autoMappingScore }}% automatically mapped</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-circular-progress
                      :value="autoMappingScore"
                      size="40px"
                      :thickness="0.3"
                      color="green"
                      track-color="grey-3"
                    >
                      {{ Math.round(autoMappingScore) }}%
                    </q-circular-progress>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="speed" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Quality Score</q-item-label>
                    <q-item-label caption>Overall mapping quality assessment</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-circular-progress
                      :value="qualityScore"
                      size="40px"
                      :thickness="0.3"
                      color="orange"
                      track-color="grey-3"
                    >
                      {{ Math.round(qualityScore) }}%
                    </q-circular-progress>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Mapping Info Dialog -->
    <q-dialog v-model="showInfoDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Mapping Details</div>
        </q-card-section>

        <q-card-section v-if="selectedMappingInfo">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="input" color="blue" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Source</q-item-label>
                <q-item-label>{{ selectedMappingInfo.source }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="output" color="green" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Target</q-item-label>
                <q-item-label>{{ selectedMappingInfo.target }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="category" color="orange" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Type</q-item-label>
                <q-item-label>{{ selectedMappingInfo.type }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="star" color="purple" />
              </q-item-section>
              <q-item-section>
                <q-item-label caption>Quality</q-item-label>
                <q-item-label>{{ getMappingQuality(selectedMappingInfo) }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <div class="text-body2 q-mt-md">
            {{ getMappingDescription(selectedMappingInfo.type, selectedMappingInfo) }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showInfoDialog = false" />
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
  equipment: Object,
  measurement: String,
  tagMappings: Object,
  fieldMappings: Object,
  validationResults: Object
})

// Emits
const emit = defineEmits(['validate', 'test-mapping'])

// Reactive data
const $q = useQuasar()
const showInfoDialog = ref(false)
const selectedMappingInfo = ref(null)

// Computed properties
const tagMappingCount = computed(() => {
  return Object.keys(props.tagMappings || {}).length
})

const fieldMappingCount = computed(() => {
  return Object.keys(props.fieldMappings || {}).length
})

const tagMappingList = computed(() => {
  return Object.entries(props.tagMappings || {}).map(([target, source]) => ({
    source,
    target,
    type: 'tag'
  }))
})

const fieldMappingList = computed(() => {
  return Object.entries(props.fieldMappings || {}).map(([target, source]) => ({
    source,
    target,
    type: 'field'
  }))
})

const formattedMappingConfig = computed(() => {
  const config = {
    equipment: {
      id: props.equipment?.id,
      name: props.equipment?.name
    },
    measurement: props.measurement,
    mappings: {
      tags: props.tagMappings || {},
      fields: props.fieldMappings || {}
    },
    created_at: new Date().toISOString()
  }

  return JSON.stringify(config, null, 2)
})

const coverageScore = computed(() => {
  // Calculate based on available vs mapped points
  const totalMappings = tagMappingCount.value + fieldMappingCount.value
  const totalAvailable = getEquipmentFiltersCount() + getEquipmentSignalsCount()

  if (totalAvailable === 0) return 0
  return Math.min((totalMappings / totalAvailable) * 100, 100)
})

const autoMappingScore = computed(() => {
  // Simulate auto-mapping success rate
  const totalMappings = tagMappingCount.value + fieldMappingCount.value
  if (totalMappings === 0) return 0

  // Count "good" mappings as auto-mapped
  const goodMappings = [...tagMappingList.value, ...fieldMappingList.value]
    .filter(mapping => getMappingQuality(mapping) === 'good').length

  return (goodMappings / totalMappings) * 100
})

const qualityScore = computed(() => {
  // Calculate overall quality based on validation and mapping quality
  const totalMappings = tagMappingCount.value + fieldMappingCount.value
  if (totalMappings === 0) return 0

  let score = 0

  // Base score from validation
  if (props.validationResults?.valid) {
    score += 50
  }

  // Score from mapping completeness
  if (fieldMappingCount.value > 0) {
    score += 30
  }

  if (tagMappingCount.value > 0) {
    score += 20
  }

  return Math.min(score, 100)
})

// Methods
const getMappingQuality = (mapping) => {
  // Simple heuristic for mapping quality
  const source = mapping.source.toLowerCase()
  const target = mapping.target.toLowerCase()

  // Exact match
  if (source === target) return 'good'

  // Similar names
  if (source.includes(target) || target.includes(source)) return 'good'

  // Common patterns
  const patterns = [
    ['soc', 'soc'],
    ['voltage', 'volt'],
    ['current', 'amp'],
    ['temperature', 'temp']
  ]

  const hasPattern = patterns.some(([p1, p2]) =>
    source.includes(p1) && target.includes(p2)
  )

  return hasPattern ? 'good' : 'fair'
}

const getMappingDescription = (type, mapping) => {
  if (type === 'tag') {
    return `Maps source tag "${mapping.source}" to equipment filter "${mapping.target}" for data filtering`
  } else {
    return `Maps source field "${mapping.source}" to equipment signal "${mapping.target}" for measurement values`
  }
}

const getEquipmentFiltersCount = () => {
  // This would typically come from equipment data
  return 5 // Mock value
}

const getEquipmentSignalsCount = () => {
  // This would typically come from equipment data
  return 8 // Mock value
}

const showMappingInfo = (mapping, type) => {
  selectedMappingInfo.value = { ...mapping, type }
  showInfoDialog.value = true
}

const copyConfig = async () => {
  try {
    await navigator.clipboard.writeText(formattedMappingConfig.value)
    $q.notify({
      type: 'positive',
      message: 'Configuration copied to clipboard',
      icon: 'content_copy'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy configuration'
    })
  }
}

const exportConfig = () => {
  const blob = new Blob([formattedMappingConfig.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `mapping_config_${props.equipment?.name || 'unknown'}_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Configuration exported successfully',
    icon: 'file_download'
  })
}
</script>

<style scoped>
.mapping-review {
  max-width: 100%;
}

.summary-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

.mapping-flow {
  display: flex;
  align-items: center;
  font-family: monospace;
}

.source-field {
  color: #1976d2;
  font-weight: 600;
}

.target-field {
  color: #388e3c;
  font-weight: 600;
}

.config-preview {
  font-family: monospace;
  font-size: 12px;
}

.config-preview .q-field__control {
  background-color: #f8f9fa;
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
</style>
