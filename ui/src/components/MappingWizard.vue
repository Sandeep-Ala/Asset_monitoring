<!-- ui/src/components/MappingWizard.vue -->
<template>
  <q-dialog v-model="show" maximized>
    <q-card>
      <!-- Header -->
      <q-card-section class="bg-primary text-white">
        <div class="row items-center">
          <div class="col">
            <div class="text-h6">Advanced Mapping Wizard</div>
            <div class="text-subtitle2">
              {{ source?.source_name }} → Equipment Mapping
            </div>
          </div>
          <div class="col-auto">
            <q-btn icon="close" flat round @click="cancelWizard" />
          </div>
        </div>
      </q-card-section>

      <!-- Progress -->
      <q-linear-progress
        :value="wizardProgress"
        color="primary"
        size="4px"
      />

      <!-- Main Content -->
      <q-card-section class="q-pa-none">
        <div class="row no-wrap" style="height: calc(100vh - 140px);">
          <!-- Steps Sidebar -->
          <div class="col-auto bg-grey-1 q-pa-md" style="min-width: 280px;">
            <q-stepper v-model="currentStep" vertical color="primary" flat>
              <q-step
                :name="1"
                title="Select Equipment"
                icon="precision_manufacturing"
                :done="currentStep > 1"
              >
                Choose the equipment to map data to
              </q-step>

              <q-step
                :name="2"
                title="Choose Measurement"
                icon="analytics"
                :done="currentStep > 2"
              >
                Select source measurement/table
              </q-step>

              <q-step
                :name="3"
                title="Map Tags"
                icon="label"
                :done="currentStep > 3"
              >
                Map tag columns for filtering
              </q-step>

              <q-step
                :name="4"
                title="Map Fields"
                icon="insights"
                :done="currentStep > 4"
              >
                Map field columns for measurements
              </q-step>

              <q-step
                :name="5"
                title="Validate & Create"
                icon="check_circle"
                :done="mappingCreated"
              >
                Review and create mapping
              </q-step>
            </q-stepper>
          </div>

          <!-- Main Content Area -->
          <div class="col q-pa-lg">
            <!-- Step 1: Equipment Selection -->
            <div v-if="currentStep === 1">
              <div class="text-h5 q-mb-md">Select Equipment</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Choose which equipment this data source will provide measurements for.
              </div>

              <div class="row q-gutter-md">
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="equipmentSearch"
                    placeholder="Search equipment..."
                    outlined
                    clearable
                  >
                    <template #prepend>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </div>

                <div class="col-12 col-md-6">
                  <q-select
                    v-model="equipmentTypeFilter"
                    :options="equipmentTypeOptions"
                    label="Filter by Type"
                    outlined
                    clearable
                    emit-value
                    map-options
                  />
                </div>
              </div>

              <div class="row q-gutter-md q-mt-md">
                <q-card
                  v-for="equipment in filteredEquipments"
                  :key="equipment.id"
                  class="col-12 col-md-5 col-lg-3 cursor-pointer equipment-card"
                  :class="mappingForm.equipment_id === equipment.id ? 'selected' : ''"
                  @click="selectEquipment(equipment)"
                >
                  <q-card-section class="text-center">
                    <q-avatar color="primary" text-color="white" size="3rem" class="q-mb-md">
                      <q-icon name="precision_manufacturing" />
                    </q-avatar>

                    <div class="text-h6 q-mb-xs">{{ equipment.name }}</div>
                    <div class="text-caption text-grey-6 q-mb-sm">{{ equipment.location || 'No location' }}</div>

                    <q-chip
                      color="blue-grey"
                      text-color="white"
                      size="sm"
                    >
                      ID: {{ equipment.id }}
                    </q-chip>
                  </q-card-section>

                  <q-card-section v-if="equipment.specs" class="q-pt-none">
                    <div class="text-subtitle2 q-mb-xs">Specifications:</div>
                    <div class="text-caption">
                      {{ Object.keys(equipment.specs).slice(0, 2).join(', ') }}
                      <span v-if="Object.keys(equipment.specs).length > 2">
                        +{{ Object.keys(equipment.specs).length - 2 }} more
                      </span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- Step 2: Measurement Selection -->
            <div v-if="currentStep === 2">
              <div class="text-h5 q-mb-md">Choose Measurement</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Select the measurement/table that contains data for {{ getSelectedEquipmentName() }}.
              </div>

              <div class="row q-gutter-md">
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="measurementSearch"
                    placeholder="Search measurements..."
                    outlined
                    clearable
                  >
                    <template #prepend>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </div>

                <div class="col-12 col-md-6">
                  <q-btn
                    label="Refresh Measurements"
                    icon="refresh"
                    color="secondary"
                    outline
                    @click="refreshMeasurements"
                    :loading="loadingMeasurements"
                  />
                </div>
              </div>

              <q-list separator bordered class="q-mt-md">
                <q-item
                  v-for="measurement in filteredMeasurements"
                  :key="measurement"
                  clickable
                  :class="mappingForm.measurement_name === measurement ? 'bg-blue-1' : ''"
                  @click="selectMeasurement(measurement)"
                >
                  <q-item-section avatar>
                    <q-avatar color="green" text-color="white" size="md">
                      <q-icon name="table_chart" />
                    </q-avatar>
                  </q-item-section>

                  <q-item-section>
                    <q-item-label class="text-h6">{{ measurement }}</q-item-label>
                    <q-item-label caption v-if="measurementInfo[measurement]">
                      {{ measurementInfo[measurement].tags || 0 }} tags •
                      {{ measurementInfo[measurement].fields || 0 }} fields •
                      Last updated: {{ measurementInfo[measurement].lastUpdate || 'Unknown' }}
                    </q-item-label>
                  </q-item-section>

                  <q-item-section side>
                    <q-btn
                      icon="preview"
                      flat
                      round
                      @click.stop="previewMeasurement(measurement)"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Step 3: Tag Mapping -->
            <div v-if="currentStep === 3">
              <div class="text-h5 q-mb-md">Map Tags</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Map source tags to equipment filter fields. Tags are used for filtering specific equipment instances.
              </div>

              <div class="row q-gutter-lg">
                <!-- Source Tags -->
                <div class="col-12 col-md-5">
                  <q-card flat bordered>
                    <q-card-section class="bg-blue-1">
                      <div class="text-h6">Source Tags</div>
                      <div class="text-caption">{{ discoveredTags.length }} available</div>
                    </q-card-section>

                    <q-card-section v-if="!discoveredTags.length" class="text-center q-pa-lg">
                      <q-icon name="search" size="2rem" class="text-grey-4 q-mb-md" />
                      <div class="text-body2 text-grey-6 q-mb-md">No tags discovered</div>
                      <q-btn
                        label="Discover Tags"
                        color="primary"
                        @click="discoverTags"
                        :loading="discoveringTags"
                      />
                    </q-card-section>

                    <q-list v-else separator>
                      <q-item
                        v-for="tag in discoveredTags"
                        :key="tag"
                        class="tag-item"
                        draggable
                        @dragstart="startDrag('tag', tag, $event)"
                      >
                        <q-item-section avatar>
                          <q-icon name="drag_indicator" class="drag-handle" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ tag }}</q-item-label>
                          <q-item-label caption>Tag Column</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <q-chip color="blue" text-color="white" size="sm">TAG</q-chip>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card>
                </div>

                <!-- Mapping Area -->
                <div class="col-12 col-md-2 flex flex-center">
                  <div class="text-center">
                    <q-icon name="arrow_forward" size="2rem" class="text-grey-5" />
                    <div class="text-body2 text-grey-6 q-mt-sm">Drag to map</div>
                  </div>
                </div>

                <!-- Equipment Filters -->
                <div class="col-12 col-md-5">
                  <q-card flat bordered>
                    <q-card-section class="bg-green-1">
                      <div class="text-h6">Equipment Filters</div>
                      <div class="text-caption">{{ equipmentFilters.length }} available</div>
                    </q-card-section>

                    <q-list separator>
                      <q-item
                        v-for="filter in equipmentFilters"
                        :key="filter.filter_key"
                        class="drop-zone"
                        @dragover.prevent
                        @drop="dropTag(filter.filter_key, $event)"
                        :class="getMappingClass('tag', filter.filter_key)"
                      >
                        <q-item-section avatar>
                          <q-icon name="filter_list" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ filter.filter_key }}</q-item-label>
                          <q-item-label caption>{{ filter.filter_value }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <div v-if="getTagMapping(filter.filter_key)">
                            <q-chip color="positive" text-color="white" size="sm">
                              {{ getTagMapping(filter.filter_key) }}
                            </q-chip>
                            <q-btn
                              icon="close"
                              flat
                              round
                              size="sm"
                              @click="removeTagMapping(filter.filter_key)"
                            />
                          </div>
                          <q-icon v-else name="add_circle_outline" class="text-grey-5" />
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card>
                </div>
              </div>

              <!-- Auto-mapping suggestions -->
              <div class="q-mt-lg">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="row items-center justify-between">
                      <div class="text-subtitle1">Auto-mapping Suggestions</div>
                      <q-btn
                        label="Apply All"
                        color="positive"
                        size="sm"
                        @click="applyAutoMappings('tags')"
                        :disable="!autoTagSuggestions.length"
                      />
                    </div>

                    <div v-if="autoTagSuggestions.length" class="q-mt-md">
                      <q-chip
                        v-for="suggestion in autoTagSuggestions"
                        :key="`${suggestion.source}-${suggestion.target}`"
                        :label="`${suggestion.source} → ${suggestion.target}`"
                        clickable
                        outline
                        color="positive"
                        class="q-ma-xs"
                        @click="applyTagMapping(suggestion.source, suggestion.target)"
                      />
                    </div>

                    <div v-else class="text-grey-6 q-mt-md">
                      No automatic mapping suggestions available
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- Step 4: Field Mapping -->
            <div v-if="currentStep === 4">
              <div class="text-h5 q-mb-md">Map Fields</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Map source fields to equipment signals. Fields contain the actual measurement values.
              </div>

              <div class="row q-gutter-lg">
                <!-- Source Fields -->
                <div class="col-12 col-md-5">
                  <q-card flat bordered>
                    <q-card-section class="bg-orange-1">
                      <div class="text-h6">Source Fields</div>
                      <div class="text-caption">{{ discoveredFields.length }} available</div>
                    </q-card-section>

                    <q-card-section v-if="!discoveredFields.length" class="text-center q-pa-lg">
                      <q-icon name="search" size="2rem" class="text-grey-4 q-mb-md" />
                      <div class="text-body2 text-grey-6 q-mb-md">No fields discovered</div>
                      <q-btn
                        label="Discover Fields"
                        color="primary"
                        @click="discoverFields"
                        :loading="discoveringFields"
                      />
                    </q-card-section>

                    <q-list v-else separator>
                      <q-item
                        v-for="field in discoveredFields"
                        :key="field.name"
                        class="field-item"
                        draggable
                        @dragstart="startDrag('field', field, $event)"
                      >
                        <q-item-section avatar>
                          <q-icon name="drag_indicator" class="drag-handle" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ field.name }}</q-item-label>
                          <q-item-label caption>{{ field.type || 'Unknown type' }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <q-chip color="orange" text-color="white" size="sm">FIELD</q-chip>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card>
                </div>

                <!-- Mapping Area -->
                <div class="col-12 col-md-2 flex flex-center">
                  <div class="text-center">
                    <q-icon name="arrow_forward" size="2rem" class="text-grey-5" />
                    <div class="text-body2 text-grey-6 q-mt-sm">Drag to map</div>
                  </div>
                </div>

                <!-- Equipment Signals -->
                <div class="col-12 col-md-5">
                  <q-card flat bordered>
                    <q-card-section class="bg-purple-1">
                      <div class="text-h6">Equipment Signals</div>
                      <div class="text-caption">{{ equipmentSignals.length }} available</div>
                    </q-card-section>

                    <q-list separator>
                      <q-item
                        v-for="signal in equipmentSignals"
                        :key="signal.key"
                        class="drop-zone"
                        @dragover.prevent
                        @drop="dropField(signal.key, $event)"
                        :class="getMappingClass('field', signal.key)"
                      >
                        <q-item-section avatar>
                          <q-icon name="sensors" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ signal.key }}</q-item-label>
                          <q-item-label caption>{{ signal.desc || signal.unit || 'Signal' }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <div v-if="getFieldMapping(signal.key)">
                            <q-chip color="positive" text-color="white" size="sm">
                              {{ getFieldMapping(signal.key) }}
                            </q-chip>
                            <q-btn
                              icon="close"
                              flat
                              round
                              size="sm"
                              @click="removeFieldMapping(signal.key)"
                            />
                          </div>
                          <q-icon v-else name="add_circle_outline" class="text-grey-5" />
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card>
                </div>
              </div>

              <!-- Auto-mapping suggestions -->
              <div class="q-mt-lg">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="row items-center justify-between">
                      <div class="text-subtitle1">Auto-mapping Suggestions</div>
                      <q-btn
                        label="Apply All"
                        color="positive"
                        size="sm"
                        @click="applyAutoMappings('fields')"
                        :disable="!autoFieldSuggestions.length"
                      />
                    </div>

                    <div v-if="autoFieldSuggestions.length" class="q-mt-md">
                      <q-chip
                        v-for="suggestion in autoFieldSuggestions"
                        :key="`${suggestion.source}-${suggestion.target}`"
                        :label="`${suggestion.source} → ${suggestion.target}`"
                        clickable
                        outline
                        color="positive"
                        class="q-ma-xs"
                        @click="applyFieldMapping(suggestion.source, suggestion.target)"
                      />
                    </div>

                    <div v-else class="text-grey-6 q-mt-md">
                      No automatic mapping suggestions available
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- Step 5: Validation & Create -->
            <div v-if="currentStep === 5">
              <div class="text-h5 q-mb-md">Review & Create Mapping</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Review your mapping configuration and create the final mapping.
              </div>

              <MappingReview
                :equipment="getSelectedEquipment()"
                :measurement="mappingForm.measurement_name"
                :tag-mappings="mappingForm.tag_mappings"
                :field-mappings="mappingForm.field_mappings"
                :validation-results="validationResults"
                @validate="validateMapping"
                @test-mapping="testMapping"
              />
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Footer Actions -->
      <q-separator />
      <q-card-actions class="q-pa-md">
        <q-btn
          label="Cancel"
          flat
          @click="cancelWizard"
        />

        <q-space />

        <q-btn
          v-if="currentStep > 1"
          label="Previous"
          flat
          @click="previousStep"
        />

        <q-btn
          v-if="currentStep < 5"
          label="Next"
          color="primary"
          @click="nextStep"
          :disable="!canProceedToNext"
        />

        <q-btn
          v-if="currentStep === 5"
          label="Create Mapping"
          color="positive"
          @click="createMapping"
          :loading="creatingMapping"
          :disable="!isValidMapping"
        />
      </q-card-actions>
    </q-card>

    <!-- Preview Dialog -->
    <q-dialog v-model="showPreview">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ previewMeasurement }}</div>
        </q-card-section>

        <q-card-section>
          <!-- Measurement preview content -->
          <MeasurementPreview
            :measurement="previewMeasurement"
            :source="source"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showPreview = false" />
          <q-btn
            label="Select"
            color="primary"
            @click="selectMeasurement(previewMeasurement); showPreview = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// // Import sub-components
import MappingReview from 'src/components/MappingReview.vue'
import MeasurementPreview from 'src/components/MeasurementPreview.vue'

// Props
const props = defineProps({
  modelValue: Boolean,
  source: Object,
  equipments: Array,
  discoveredSchema: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'mapping-created'])

// Reactive data
const $q = useQuasar()
const currentStep = ref(1)

// Form data
const mappingForm = ref({
  equipment_id: null,
  measurement_name: '',
  tag_mappings: {},
  field_mappings: {}
})

// UI states
const equipmentSearch = ref('')
const equipmentTypeFilter = ref('')
const measurementSearch = ref('')
const loadingMeasurements = ref(false)
const discoveringTags = ref(false)
const discoveringFields = ref(false)
const creatingMapping = ref(false)
const mappingCreated = ref(false)

// Data
const measurements = ref([])
const discoveredTags = ref([])
const discoveredFields = ref([])
const equipmentFilters = ref([])
const equipmentSignals = ref([])
const measurementInfo = ref({})
const validationResults = ref({})

// Preview
const showPreview = ref(false)
const previewMeasurement = ref('')

// Drag and drop
const draggedItem = ref(null)
const draggedType = ref('')

// Computed properties
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const wizardProgress = computed(() => currentStep.value / 5)

const filteredEquipments = computed(() => {
  let filtered = props.equipments || []

  if (equipmentSearch.value) {
    const query = equipmentSearch.value.toLowerCase()
    filtered = filtered.filter(eq =>
      eq.name.toLowerCase().includes(query) ||
      eq.location?.toLowerCase().includes(query)
    )
  }

  if (equipmentTypeFilter.value) {
    filtered = filtered.filter(eq => eq.model_id === equipmentTypeFilter.value)
  }

  return filtered
})

const filteredMeasurements = computed(() => {
  if (!measurementSearch.value) return measurements.value

  const query = measurementSearch.value.toLowerCase()
  return measurements.value.filter(measurement =>
    measurement.toLowerCase().includes(query)
  )
})

const equipmentTypeOptions = computed(() => {
  const types = new Set()
  props.equipments?.forEach(eq => {
    if (eq.model_id) types.add(eq.model_id)
  })
  return Array.from(types).map(id => ({ label: `Type ${id}`, value: id }))
})

const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!mappingForm.value.equipment_id
    case 2:
      return !!mappingForm.value.measurement_name
    case 3:
      return Object.keys(mappingForm.value.tag_mappings).length > 0 ||
             discoveredTags.value.length === 0
    case 4:
      return Object.keys(mappingForm.value.field_mappings).length > 0
    default:
      return true
  }
})

const isValidMapping = computed(() => {
  return mappingForm.value.equipment_id &&
         mappingForm.value.measurement_name &&
         (Object.keys(mappingForm.value.field_mappings).length > 0)
})

const autoTagSuggestions = computed(() => {
  const suggestions = []
  discoveredTags.value.forEach(tag => {
    equipmentFilters.value.forEach(filter => {
      if (isGoodMatch(tag, filter.filter_key)) {
        suggestions.push({ source: tag, target: filter.filter_key })
      }
    })
  })
  return suggestions
})

const autoFieldSuggestions = computed(() => {
  const suggestions = []
  discoveredFields.value.forEach(field => {
    equipmentSignals.value.forEach(signal => {
      if (isGoodMatch(field.name, signal.key)) {
        suggestions.push({ source: field.name, target: signal.key })
      }
    })
  })
  return suggestions
})

// Methods
onMounted(() => {
  if (props.discoveredSchema?.measurements) {
    measurements.value = props.discoveredSchema.measurements
  }
})

const selectEquipment = async (equipment) => {
  mappingForm.value.equipment_id = equipment.id

  // Load equipment filters and signals
  try {
    const [filtersResponse, signalsResponse] = await Promise.all([
      axios.get(`http://localhost:8000/equipments/${equipment.id}/filters`),
      axios.get(`http://localhost:8000/equipments/${equipment.id}/signals`)
    ])

    equipmentFilters.value = filtersResponse.data || []
    equipmentSignals.value = signalsResponse.data || []
  } catch (error) {
    console.warn('Failed to load equipment details:', error)
    equipmentFilters.value = []
    equipmentSignals.value = []
  }
}

const selectMeasurement = (measurement) => {
  mappingForm.value.measurement_name = measurement

  // Auto-discover tags and fields if available from schema
  if (props.discoveredSchema?.tags?.[measurement]) {
    discoveredTags.value = props.discoveredSchema.tags[measurement]
  }
  if (props.discoveredSchema?.fields?.[measurement]) {
    discoveredFields.value = props.discoveredSchema.fields[measurement]
  }
}

const getSelectedEquipment = () => {
  return props.equipments?.find(eq => eq.id === mappingForm.value.equipment_id)
}

const getSelectedEquipmentName = () => {
  return getSelectedEquipment()?.name || 'Selected Equipment'
}

const refreshMeasurements = async () => {
  if (!props.source) return

  loadingMeasurements.value = true
  try {
    const response = await axios.get(`http://localhost:8000/datasources/${props.source.source_id}/discover/measurements`)
    measurements.value = response.data.measurements || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to refresh measurements'
    })
  } finally {
    discoveringFields.value = false
  }
}

// Drag and drop functionality
const startDrag = (type, item, event) => {
  draggedType.value = type
  draggedItem.value = type === 'field' ? item.name : item
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', JSON.stringify({ type, item }))
}

const dropTag = (targetKey, event) => {
  event.preventDefault()
  if (draggedType.value === 'tag' && draggedItem.value) {
    applyTagMapping(draggedItem.value, targetKey)
  }
  draggedItem.value = null
  draggedType.value = ''
}

const dropField = (targetKey, event) => {
  event.preventDefault()
  if (draggedType.value === 'field' && draggedItem.value) {
    applyFieldMapping(draggedItem.value, targetKey)
  }
  draggedItem.value = null
  draggedType.value = ''
}

// Mapping management
const applyTagMapping = (sourceTag, targetFilter) => {
  mappingForm.value.tag_mappings = {
    ...mappingForm.value.tag_mappings,
    [targetFilter]: sourceTag
  }
}

const applyFieldMapping = (sourceField, targetSignal) => {
  mappingForm.value.field_mappings = {
    ...mappingForm.value.field_mappings,
    [targetSignal]: sourceField
  }
}

const removeTagMapping = (targetFilter) => {
  const newMappings = { ...mappingForm.value.tag_mappings }
  delete newMappings[targetFilter]
  mappingForm.value.tag_mappings = newMappings
}

const removeFieldMapping = (targetSignal) => {
  const newMappings = { ...mappingForm.value.field_mappings }
  delete newMappings[targetSignal]
  mappingForm.value.field_mappings = newMappings
}

const getTagMapping = (targetFilter) => {
  return mappingForm.value.tag_mappings[targetFilter]
}

const getFieldMapping = (targetSignal) => {
  return mappingForm.value.field_mappings[targetSignal]
}

const getMappingClass = (type, targetKey) => {
  const hasMapping = type === 'tag' ?
    getTagMapping(targetKey) :
    getFieldMapping(targetKey)

  return hasMapping ? 'mapped-item' : 'unmapped-item'
}

// Auto-mapping functionality
const isGoodMatch = (source, target) => {
  const sourceNorm = source.toLowerCase().replace(/[_-]/g, '')
  const targetNorm = target.toLowerCase().replace(/[_-]/g, '')

  // Exact match
  if (sourceNorm === targetNorm) return true

  // Common patterns
  const patterns = [
    { source: 'soc', target: 'soc' },
    { source: 'soh', target: 'soh' },
    { source: 'voltage', target: 'voltage' },
    { source: 'current', target: 'current' },
    { source: 'temperature', target: 'temp' },
    { source: 'temp', target: 'temperature' },
    { source: 'rack', target: 'rack' },
    { source: 'bank', target: 'bank' },
    { source: 'module', target: 'module' },
    { source: 'cell', target: 'cell' }
  ]

  return patterns.some(pattern =>
    sourceNorm.includes(pattern.source) && targetNorm.includes(pattern.target)
  )
}

const applyAutoMappings = (type) => {
  if (type === 'tags') {
    autoTagSuggestions.value.forEach(suggestion => {
      applyTagMapping(suggestion.source, suggestion.target)
    })
  } else if (type === 'fields') {
    autoFieldSuggestions.value.forEach(suggestion => {
      applyFieldMapping(suggestion.source, suggestion.target)
    })
  }
}

// Navigation
const nextStep = () => {
  if (currentStep.value < 5) {
    currentStep.value++

    // Auto-actions when entering certain steps
    if (currentStep.value === 3 && discoveredTags.value.length === 0) {
      discoverTags()
    } else if (currentStep.value === 4 && discoveredFields.value.length === 0) {
      discoverFields()
    } else if (currentStep.value === 5) {
      validateMapping()
    }
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// Validation and creation
const validateMapping = async () => {
  // Perform validation checks
  const results = {
    valid: true,
    warnings: [],
    errors: []
  }

  // Check for required mappings
  if (Object.keys(mappingForm.value.field_mappings).length === 0) {
    results.errors.push('At least one field mapping is required')
    results.valid = false
  }

  // Check for duplicate mappings
  const fieldValues = Object.values(mappingForm.value.field_mappings)
  if (fieldValues.length !== new Set(fieldValues).size) {
    results.warnings.push('Some source fields are mapped to multiple signals')
  }

  // Check for unmapped critical fields
  const criticalFields = ['voltage', 'current', 'soc', 'temperature']
  const mappedFields = Object.values(mappingForm.value.field_mappings)
  criticalFields.forEach(field => {
    if (!mappedFields.some(mapped => mapped.toLowerCase().includes(field))) {
      results.warnings.push(`Critical field '${field}' may not be mapped`)
    }
  })

  validationResults.value = results
}

const testMapping = async () => {
  // Test the mapping with sample data
  try {
    const response = await axios.post('http://localhost:8000/datasources/test-mapping', {
      source_id: props.source.source_id,
      measurement: mappingForm.value.measurement_name,
      tag_mappings: mappingForm.value.tag_mappings,
      field_mappings: mappingForm.value.field_mappings
    })

    $q.notify({
      type: 'positive',
      message: 'Mapping test successful'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Mapping test failed',
      caption: error.response?.data?.detail
    })
  }
}

const createMapping = async () => {
  creatingMapping.value = true

  try {
    const payload = {
      source_id: props.source.source_id,
      equipment_id: mappingForm.value.equipment_id,
      measurement_name: mappingForm.value.measurement_name,
      tag_mappings: mappingForm.value.tag_mappings,
      field_mappings: mappingForm.value.field_mappings
    }

    const response = await axios.post('http://localhost:8000/datasources/mappings', payload)

    mappingCreated.value = true

    $q.notify({
      type: 'positive',
      message: 'Mapping created successfully',
      icon: 'check_circle'
    })

    emit('mapping-created', response.data)

    // Close dialog after short delay
    setTimeout(() => {
      resetWizard()
      show.value = false
    }, 1500)

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to create mapping',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    creatingMapping.value = false
  }
}

// Preview functionality
const previewMeasurement = (measurement) => {
  previewMeasurement.value = measurement
  showPreview.value = true
}

// Wizard lifecycle
const resetWizard = () => {
  currentStep.value = 1
  mappingCreated.value = false
  mappingForm.value = {
    equipment_id: null,
    measurement_name: '',
    tag_mappings: {},
    field_mappings: {}
  }
  discoveredTags.value = []
  discoveredFields.value = []
  equipmentFilters.value = []
  equipmentSignals.value = []
  validationResults.value = {}
}

const cancelWizard = () => {
  $q.dialog({
    title: 'Cancel Mapping',
    message: 'Are you sure you want to cancel? All progress will be lost.',
    cancel: true,
    persistent: true
  }).onOk(() => {
    resetWizard()
    show.value = false
  })
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetWizard()
    if (props.discoveredSchema?.measurements) {
      measurements.value = props.discoveredSchema.measurements
    }
  }
})

watch(() => props.discoveredSchema, (newSchema) => {
  if (newSchema?.measurements) {
    measurements.value = newSchema.measurements
  }
})
</script>

<style scoped>
.equipment-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.equipment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.equipment-card.selected {
  border-color: var(--q-primary);
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.3);
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

.tag-item, .field-item {
  cursor: grab;
  transition: all 0.2s ease;
}

.tag-item:active, .field-item:active {
  cursor: grabbing;
}

.tag-item:hover, .field-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.drop-zone {
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.drop-zone:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.drop-zone.mapped-item {
  background-color: rgba(76, 175, 80, 0.1);
  border-color: rgba(76, 175, 80, 0.3);
}

.drop-zone.unmapped-item {
  background-color: rgba(255, 193, 7, 0.05);
}

.drag-handle {
  cursor: grab;
  color: #999;
}

.drag-handle:hover {
  color: #666;
}

.q-stepper {
  background: transparent;
}

.q-card {
  border-radius: 12px;
}

/* Scrollbar styling */
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
</style> {
    loadingMeasurements.value = false
  }
}

const discoverTags = async () => {
  if (!props.source || !mappingForm.value.measurement_name) return

  discoveringTags.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
      source_type: props.source.source_type,
      connection_config: JSON.parse(props.source.connection_config),
      measurement: mappingForm.value.measurement_name
    })

    discoveredTags.value = response.data.tags || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover tags'
    })
  } finally {
    discoveringTags.value = false
  }
}

const discoverFields = async () => {
  if (!props.source || !mappingForm.value.measurement_name) return

  discoveringFields.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_type: props.source.source_type,
      connection_config: JSON.parse(props.source.connection_config),
      measurement: mappingForm.value.measurement_name
    })

    discoveredFields.value = response.data.fields || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover fields'
    })
  } finally
