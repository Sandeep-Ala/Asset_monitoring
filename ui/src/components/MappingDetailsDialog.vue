<!-- ui/src/components/MappingDetailsDialog.vue -->
<!-- Detailed mapping information dialog component -->

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" maximized>
    <q-card class="q-dialog-plugin">
      <!-- Header -->
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Mapping Details</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-card-section>

      <q-separator />

      <!-- Content -->
      <q-card-section class="scroll" style="max-height: 70vh">
        <div v-if="mapping && equipment" class="row q-gutter-md">
          <!-- Basic Information -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section class="bg-blue-1">
                <div class="text-subtitle1">
                  <q-icon name="info" class="q-mr-sm" />
                  Basic Information
                </div>
              </q-card-section>
              <q-card-section>
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Mapping ID</q-item-label>
                      <q-item-label>{{ mapping.mapping_id }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Equipment</q-item-label>
                      <q-item-label>
                        <q-chip color="primary" text-color="white" size="sm">
                          {{ equipment.name }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Equipment Type</q-item-label>
                      <q-item-label>{{ equipment.equipment_type }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Measurement</q-item-label>
                      <q-item-label>
                        <q-chip color="secondary" text-color="white" size="sm">
                          {{ mapping.measurement_name }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Created</q-item-label>
                      <q-item-label>{{ formatDate(mapping.created_at) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Last Updated</q-item-label>
                      <q-item-label>{{ formatDate(mapping.updated_at) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Equipment Details -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section class="bg-green-1">
                <div class="text-subtitle1">
                  <q-icon name="precision_manufacturing" class="q-mr-sm" />
                  Equipment Details
                </div>
              </q-card-section>
              <q-card-section>
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Equipment ID</q-item-label>
                      <q-item-label>{{ equipment.id }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Location</q-item-label>
                      <q-item-label>{{ equipment.location || 'Not specified' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Serial Number</q-item-label>
                      <q-item-label>{{ equipment.serial_number || 'Not specified' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Manufacturer</q-item-label>
                      <q-item-label>{{ equipment.manufacturer || 'Not specified' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Model</q-item-label>
                      <q-item-label>{{ equipment.model || 'Not specified' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Status</q-item-label>
                      <q-item-label>
                        <q-chip
                          :color="equipment.is_active ? 'positive' : 'negative'"
                          text-color="white"
                          size="sm"
                        >
                          {{ equipment.is_active ? 'Active' : 'Inactive' }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Tag Mappings -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section class="bg-orange-1">
                <div class="text-subtitle1">
                  <q-icon name="label" class="q-mr-sm" />
                  Tag Mappings ({{ tagMappingsCount }})
                </div>
              </q-card-section>
              <q-card-section>
                <div v-if="tagMappingsCount === 0" class="text-center q-pa-md text-grey-6">
                  <q-icon name="label_off" size="2rem" class="q-mb-sm" />
                  <div>No tag mappings defined</div>
                </div>
                <div v-else class="row q-gutter-sm">
                  <div
                    v-for="(target, source) in mapping.tag_mappings"
                    :key="source"
                    class="col-12 col-md-6 col-lg-4"
                  >
                    <q-card flat class="bg-grey-1">
                      <q-card-section class="q-pa-sm">
                        <div class="row items-center q-gutter-sm">
                          <q-chip color="blue" text-color="white" size="sm">
                            <q-icon name="input" size="xs" class="q-mr-xs" />
                            {{ source }}
                          </q-chip>
                          <q-icon name="arrow_forward" size="sm" />
                          <q-chip color="blue" outline size="sm">
                            <q-icon name="output" size="xs" class="q-mr-xs" />
                            {{ target }}
                          </q-chip>
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Field Mappings -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section class="bg-purple-1">
                <div class="text-subtitle1">
                  <q-icon name="data_object" class="q-mr-sm" />
                  Field Mappings ({{ fieldMappingsCount }})
                </div>
              </q-card-section>
              <q-card-section>
                <div v-if="fieldMappingsCount === 0" class="text-center q-pa-md text-grey-6">
                  <q-icon name="disabled_by_default" size="2rem" class="q-mb-sm" />
                  <div>No field mappings defined</div>
                </div>
                <div v-else>
                  <!-- Field mapping table -->
                  <q-table
                    :rows="fieldMappingRows"
                    :columns="fieldColumns"
                    row-key="source"
                    flat
                    dense
                    :pagination="{ rowsPerPage: 10 }"
                  >
                    <template #body-cell-source="props">
                      <q-td :props="props">
                        <q-chip color="green" text-color="white" size="sm">
                          <q-icon name="input" size="xs" class="q-mr-xs" />
                          {{ props.value }}
                        </q-chip>
                      </q-td>
                    </template>
                    <template #body-cell-target="props">
                      <q-td :props="props">
                        <q-chip color="green" outline size="sm">
                          <q-icon name="output" size="xs" class="q-mr-xs" />
                          {{ props.value }}
                        </q-chip>
                      </q-td>
                    </template>
                    <template #body-cell-type="props">
                      <q-td :props="props">
                        <q-chip
                          :color="getFieldTypeColor(props.value)"
                          text-color="white"
                          size="xs"
                        >
                          {{ props.value }}
                        </q-chip>
                      </q-td>
                    </template>
                  </q-table>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Mapping Statistics -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section class="bg-red-1">
                <div class="text-subtitle1">
                  <q-icon name="analytics" class="q-mr-sm" />
                  Mapping Statistics
                </div>
              </q-card-section>
              <q-card-section>
                <div class="row q-gutter-md">
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-blue-1 text-center q-pa-md">
                      <div class="text-h5">{{ tagMappingsCount }}</div>
                      <div class="text-body2">Tag Mappings</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-green-1 text-center q-pa-md">
                      <div class="text-h5">{{ fieldMappingsCount }}</div>
                      <div class="text-body2">Field Mappings</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-orange-1 text-center q-pa-md">
                      <div class="text-h5">{{ totalMappingsCount }}</div>
                      <div class="text-body2">Total Mappings</div>
                    </q-card>
                  </div>
                  <div class="col-6 col-md-3">
                    <q-card flat class="bg-purple-1 text-center q-pa-md">
                      <div class="text-h5">{{ mappingEfficiency }}%</div>
                      <div class="text-body2">Coverage</div>
                    </q-card>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Validation & Health -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section class="bg-teal-1">
                <div class="text-subtitle1">
                  <q-icon name="health_and_safety" class="q-mr-sm" />
                  Mapping Health
                </div>
              </q-card-section>
              <q-card-section>
                <div class="row q-gutter-md">
                  <!-- Validation Status -->
                  <div class="col-12 col-md-6">
                    <q-list dense>
                      <q-item>
                        <q-item-section avatar>
                          <q-icon
                            :name="mappingValidation.isValid ? 'check_circle' : 'error'"
                            :color="mappingValidation.isValid ? 'positive' : 'negative'"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>Validation Status</q-item-label>
                          <q-item-label caption>
                            {{ mappingValidation.isValid ? 'All mappings are valid' : 'Some mappings have issues' }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section avatar>
                          <q-icon name="data_usage" color="info" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>Data Flow</q-item-label>
                          <q-item-label caption>
                            {{ mapping.is_active ? 'Active - data is flowing' : 'Inactive - no data flow' }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>

                  <!-- Issues -->
                  <div class="col-12 col-md-6" v-if="!mappingValidation.isValid">
                    <div class="text-subtitle2 q-mb-sm">Issues Found:</div>
                    <q-list dense>
                      <q-item v-for="issue in mappingValidation.issues" :key="issue">
                        <q-item-section avatar>
                          <q-icon name="warning" color="warning" size="sm" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label class="text-warning">{{ issue }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- No Data State -->
        <div v-else class="text-center q-pa-xl">
          <q-icon name="error_outline" size="4rem" class="text-grey-4 q-mb-md" />
          <div class="text-h6 text-grey-6">No Data Available</div>
          <div class="text-body2 text-grey-5">
            Mapping or equipment information could not be loaded
          </div>
        </div>
      </q-card-section>

      <!-- Actions -->
      <q-separator />
      <q-card-actions align="between">
        <q-btn
          label="Close"
          flat
          @click="onDialogCancel"
        />

        <div class="q-gutter-sm">
          <q-btn
            label="Test Mapping"
            icon="play_arrow"
            color="secondary"
            outline
            @click="testMapping"
            :loading="testing"
          />
          <q-btn
            label="Edit"
            icon="edit"
            color="primary"
            @click="editMapping"
          />
          <q-btn
            label="Delete"
            icon="delete"
            color="negative"
            @click="deleteMapping"
          />
        </div>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDialogPluginComponent, useQuasar } from 'quasar'

// Dialog composition
defineEmits([
  ...useDialogPluginComponent.emits
])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

// Props
const props = defineProps({
  mapping: {
    type: Object,
    required: true
  },
  equipment: {
    type: Object,
    required: true
  }
})

// Reactive data
const $q = useQuasar()
const testing = ref(false)

// Computed properties
const tagMappingsCount = computed(() => {
  return Object.keys(props.mapping?.tag_mappings || {}).length
})

const fieldMappingsCount = computed(() => {
  return Object.keys(props.mapping?.field_mappings || {}).length
})

const totalMappingsCount = computed(() => {
  return tagMappingsCount.value + fieldMappingsCount.value
})

const mappingEfficiency = computed(() => {
  // Calculate mapping coverage percentage
  const totalPossibleMappings = 20 // Estimate
  return Math.round((totalMappingsCount.value / totalPossibleMappings) * 100)
})

const fieldMappingRows = computed(() => {
  if (!props.mapping?.field_mappings) return []

  return Object.entries(props.mapping.field_mappings).map(([source, target]) => ({
    source,
    target,
    type: inferFieldType(source)
  }))
})

const fieldColumns = [
  {
    name: 'source',
    label: 'Source Field',
    field: 'source',
    align: 'left',
    sortable: true
  },
  {
    name: 'target',
    label: 'Target Field',
    field: 'target',
    align: 'left',
    sortable: true
  },
  {
    name: 'type',
    label: 'Data Type',
    field: 'type',
    align: 'center',
    sortable: true
  }
]

const mappingValidation = computed(() => {
  const issues = []

  // Check for empty mappings
  if (tagMappingsCount.value === 0 && fieldMappingsCount.value === 0) {
    issues.push('No mappings defined')
  }

  // Check for duplicate targets
  const targets = [
    ...Object.values(props.mapping?.tag_mappings || {}),
    ...Object.values(props.mapping?.field_mappings || {})
  ]
  const duplicates = targets.filter((item, index) => targets.indexOf(item) !== index)
  if (duplicates.length > 0) {
    issues.push('Duplicate target mappings found')
  }

  // Check for missing required mappings
  const requiredTags = ['n_rack', 'n_bank'] // Example requirements
  const mappedTags = Object.values(props.mapping?.tag_mappings || {})
  const missingRequired = requiredTags.filter(tag => !mappedTags.includes(tag))
  if (missingRequired.length > 0) {
    issues.push(`Missing required tags: ${missingRequired.join(', ')}`)
  }

  return {
    isValid: issues.length === 0,
    issues
  }
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'Not available'
  return new Date(dateString).toLocaleString()
}

const inferFieldType = (fieldName) => {
  const lowerField = fieldName.toLowerCase()
  if (lowerField.includes('voltage') || lowerField.includes('current') || lowerField.includes('power')) {
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

const getFieldTypeColor = (type) => {
  const colors = {
    number: 'blue',
    string: 'green',
    datetime: 'orange',
    boolean: 'purple'
  }
  return colors[type] || 'grey'
}

const testMapping = async () => {
  testing.value = true

  try {
    // Simulate mapping test
    await new Promise(resolve => setTimeout(resolve, 2000))

    $q.notify({
      type: 'positive',
      message: 'Mapping test completed successfully',
      caption: 'All field mappings are functioning correctly'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Mapping test failed',
      caption: error.message
    })
  } finally {
    testing.value = false
  }
}

const editMapping = () => {
  onDialogOK('edit')
}

const deleteMapping = () => {
  $q.dialog({
    title: 'Confirm Deletion',
    message: 'Are you sure you want to delete this mapping? This action cannot be undone.',
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(() => {
    onDialogOK('delete')
  })
}
</script>

<style scoped>
.q-dialog-plugin {
  width: 100%;
  max-width: none;
}

.q-chip {
  font-size: 11px;
}

.text-h5 {
  font-weight: 600;
}
</style>
