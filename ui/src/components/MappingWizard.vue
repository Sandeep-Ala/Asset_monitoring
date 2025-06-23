<!-- src/components/MappingWizard.vue - Fixed duplicate variable declarations -->
<template>
  <q-dialog v-model="show" maximized>
    <q-card class="column">
      <!-- Header with Progress -->
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Mapping Wizard</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="cancelWizard" />
      </q-card-section>

      <!-- Progress Bar -->
      <q-card-section class="q-pb-none">
        <q-linear-progress
          :value="currentStep / 4"
          color="primary"
          class="q-mb-md"
        />
        <div class="row justify-between text-caption text-grey-6">
          <span>Step {{ currentStep }} of 4</span>
          <span>{{ getStepTitle(currentStep) }}</span>
        </div>
      </q-card-section>

      <!-- Main Content -->
      <q-card-section class="col">
        <div class="row full-height">
          <!-- Step Content -->
          <div class="col">
            <!-- Step 1: Equipment Selection -->
            <div v-if="currentStep === 1">
              <div class="text-h5 q-mb-md">Select Equipment</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Choose the equipment that this data source will be mapped to.
              </div>

              <!-- Equipment Search -->
              <q-input
                v-model="equipmentSearch"
                placeholder="Search equipment..."
                outlined
                dense
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="search" />
                </template>
              </q-input>

              <!-- Equipment Type Filter -->
              <q-select
                v-model="equipmentTypeFilter"
                :options="equipmentTypes"
                label="Filter by type"
                outlined
                dense
                clearable
                class="q-mb-lg"
              />

              <!-- Equipment Grid -->
              <div class="row q-gutter-md">
                <div
                  v-for="equipment in filteredEquipments"
                  :key="equipment.equipment_id"
                  class="col-12 col-md-6 col-lg-4"
                >
                  <q-card
                    flat
                    bordered
                    clickable
                    :class="{
                      'bg-primary text-white': mappingForm.equipment_id === equipment.equipment_id
                    }"
                    @click="selectEquipment(equipment)"
                  >
                    <q-card-section>
                      <div class="text-h6">{{ equipment.equipment_name }}</div>
                      <div class="text-caption">{{ equipment.equipment_type }}</div>
                      <div class="text-body2 q-mt-sm">{{ equipment.location }}</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Step 2: Measurement Selection -->
            <div v-if="currentStep === 2">
              <div class="text-h5 q-mb-md">Select Measurement</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Choose the measurement from your data source to map.
              </div>

              <!-- Measurement Search -->
              <q-input
                v-model="measurementSearch"
                placeholder="Search measurements..."
                outlined
                dense
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="search" />
                </template>
              </q-input>

              <!-- Discover Button -->
              <q-btn
                v-if="!measurements.length"
                label="Discover Measurements"
                icon="search"
                color="primary"
                @click="discoverMeasurements"
                :loading="loadingMeasurements"
                class="q-mb-lg"
              />

              <!-- Measurements List -->
              <q-list v-if="measurements.length" bordered>
                <q-item
                  v-for="measurement in filteredMeasurements"
                  :key="measurement"
                  clickable
                  :active="mappingForm.measurement_name === measurement"
                  @click="selectMeasurement(measurement)"
                >
                  <q-item-section avatar>
                    <q-icon name="table_chart" />
                  </q-item-section>

                  <q-item-section>
                    <q-item-label>{{ measurement }}</q-item-label>
                  </q-item-section>

                  <q-item-section side>
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click.stop="showMeasurementPreview(measurement)"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Step 3: Tag Mapping -->
            <div v-if="currentStep === 3">
              <div class="text-h5 q-mb-md">Map Tags</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Map discovered tags to equipment filters and attributes.
              </div>

              <!-- Discover Tags Button -->
              <q-btn
                v-if="!discoveredTags.length"
                label="Discover Tags"
                icon="search"
                color="primary"
                @click="discoverTags"
                :loading="discoveringTags"
                class="q-mb-lg"
              />

              <!-- Tag Mappings -->
              <div v-if="discoveredTags.length">
                <q-list bordered>
                  <q-item
                    v-for="tag in discoveredTags"
                    :key="tag"
                  >
                    <q-item-section>
                      <q-item-label>{{ tag }}</q-item-label>
                      <q-item-label caption>Data source tag</q-item-label>
                    </q-item-section>

                    <q-item-section side style="min-width: 200px">
                      <q-select
                        v-model="mappingForm.tag_mappings[tag]"
                        :options="equipmentFilters"
                        option-label="display_name"
                        option-value="filter_key"
                        label="Map to filter"
                        outlined
                        dense
                        clearable
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>

            <!-- Step 4: Field Mapping -->
            <div v-if="currentStep === 4">
              <div class="text-h5 q-mb-md">Map Fields</div>
              <div class="text-body1 text-grey-6 q-mb-lg">
                Map discovered fields to equipment signals and measurements.
              </div>

              <!-- Discover Fields Button -->
              <q-btn
                v-if="!discoveredFields.length"
                label="Discover Fields"
                icon="search"
                color="primary"
                @click="discoverFields"
                :loading="discoveringFields"
                class="q-mb-lg"
              />

              <!-- Field Mappings -->
              <div v-if="discoveredFields.length">
                <q-list bordered>
                  <q-item
                    v-for="field in discoveredFields"
                    :key="field"
                  >
                    <q-item-section>
                      <q-item-label>{{ field }}</q-item-label>
                      <q-item-label caption>Data source field</q-item-label>
                    </q-item-section>

                    <q-item-section side style="min-width: 200px">
                      <q-select
                        v-model="mappingForm.field_mappings[field]"
                        :options="equipmentSignals"
                        option-label="signal_name"
                        option-value="signal_key"
                        label="Map to signal"
                        outlined
                        dense
                        clearable
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </div>
        </div>
      </q-card-section>

      <!-- Actions -->
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
          v-if="currentStep < 4"
          label="Next"
          color="primary"
          @click="nextStep"
          :disable="!canProceedToNext"
        />

        <q-btn
          v-if="currentStep === 4"
          label="Create Mapping"
          color="positive"
          @click="createMapping"
          :loading="creatingMapping"
        />
      </q-card-actions>
    </q-card>

    <!-- Preview Dialog -->
    <q-dialog v-model="showPreview">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ currentPreviewMeasurement }}</div>
        </q-card-section>

        <q-card-section>
          <!-- Preview content -->
          <MeasurementPreview
            :measurement="currentPreviewMeasurement"
            :source="source"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showPreview = false" />
          <q-btn
            label="Select"
            color="primary"
            @click="selectMeasurement(currentPreviewMeasurement); showPreview = false"
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

// Import sub-components
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
const validationResults = ref({})

// Preview - FIXED: Renamed variables to avoid conflicts
const showPreview = ref(false)
const currentPreviewMeasurement = ref('')  // RENAMED from previewMeasurement

// Computed properties
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const equipmentTypes = computed(() => {
  const types = [...new Set(props.equipments?.map(eq => eq.equipment_type) || [])]
  return types.map(type => ({ label: type, value: type }))
})

const filteredEquipments = computed(() => {
  let filtered = props.equipments || []

  if (equipmentSearch.value) {
    const query = equipmentSearch.value.toLowerCase()
    filtered = filtered.filter(eq =>
      eq.equipment_name.toLowerCase().includes(query) ||
      eq.location.toLowerCase().includes(query)
    )
  }

  if (equipmentTypeFilter.value) {
    filtered = filtered.filter(eq => eq.equipment_type === equipmentTypeFilter.value)
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

const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!mappingForm.value.equipment_id
    case 2:
      return !!mappingForm.value.measurement_name
    case 3:
      return true // Tags are optional
    case 4:
      return true // Fields are optional
    default:
      return false
  }
})

// Methods
const getStepTitle = (step) => {
  const titles = {
    1: 'Equipment Selection',
    2: 'Measurement Selection',
    3: 'Tag Mapping',
    4: 'Field Mapping'
  }
  return titles[step] || ''
}

const selectEquipment = async (equipment) => {
  mappingForm.value.equipment_id = equipment.equipment_id

  // Load equipment filters and signals
  await Promise.all([
    loadEquipmentFilters(equipment.equipment_id),
    loadEquipmentSignals(equipment.equipment_id)
  ])
}

const selectMeasurement = (measurement) => {
  mappingForm.value.measurement_name = measurement
}

const discoverMeasurements = async () => {
  if (!props.source) return

  loadingMeasurements.value = true
  console.log(props.source)
  try {
    const response = await axios.get(`http://localhost:8000/datasources/${props.source.source_id}/discover/measurements`)
    measurements.value = response.data.measurements || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover measurements'
    })
  } finally {
    loadingMeasurements.value = false
  }
}

const discoverTags = async () => {
  if (!mappingForm.value.measurement_name) return

  discoveringTags.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: props.source.source_type,
        connection_config :props.source,
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
  if (!mappingForm.value.measurement_name) return

  discoveringFields.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_id: props.source.source_id,
      measurement: mappingForm.value.measurement_name
    })

    discoveredFields.value = response.data.fields || []
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover fields'
    })
  } finally {
    discoveringFields.value = false
  }
}

const loadEquipmentFilters = async (equipmentId) => {
  try {
    const response = await axios.get(`http://localhost:8000/equipments/${equipmentId}/filters`)
    equipmentFilters.value = response.data.filters || []
  } catch (error) {
    $q.notify({
      type: 'warning',
      message: 'Failed to load equipment filters'
    })
  }
}

const loadEquipmentSignals = async (equipmentId) => {
  try {
    const response = await axios.get(`http://localhost:8000/equipments/${equipmentId}/signals`)
    equipmentSignals.value = response.data.signals || []
  } catch (error) {
    $q.notify({
      type: 'warning',
      message: 'Failed to load equipment signals'
    })
  }
}

const nextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
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

// FIXED: Renamed function to avoid conflict
const showMeasurementPreview = (measurement) => {
  currentPreviewMeasurement.value = measurement  // FIXED: Use renamed variable
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

// Initialize data when component mounts
onMounted(() => {
  if (props.discoveredSchema?.measurements) {
    measurements.value = props.discoveredSchema.measurements
  }
})

// Watch for source changes
watch(() => props.source, () => {
  if (props.source && show.value) {
    discoverMeasurements()
  }
})
</script>
