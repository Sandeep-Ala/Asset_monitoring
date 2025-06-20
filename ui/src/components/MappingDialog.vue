<!-- ui/src/components/MappingDialog.vue -->
<template>
  <q-dialog v-model="show" persistent>
    <q-card style="min-width: 800px; max-width: 90vw">
      <q-card-section>
        <div class="text-h6">Create Equipment Mapping</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-stepper v-model="step" vertical color="primary" animated>
          <!-- Step 1: Select Equipment and Measurement -->
          <q-step :name="1" title="Select Equipment & Measurement" icon="settings" :done="step > 1">
            <div class="row q-gutter-md">
              <div class="col-5">
                <q-select
                  v-model="mappingForm.equipment_id"
                  :options="equipmentOptions"
                  label="Select Equipment"
                  option-value="id"
                  option-label="name"
                  emit-value
                  map-options
                  required
                />
              </div>

              <div class="col-5">
                <q-select
                  v-model="mappingForm.measurement_name"
                  :options="measurements"
                  label="Select Measurement"
                  required
                  @update:model-value="onMeasurementChange"
                />
              </div>
            </div>

            <q-stepper-navigation>
              <q-btn
                @click="nextStep"
                color="primary"
                label="Continue"
                :disable="!mappingForm.equipment_id || !mappingForm.measurement_name"
              />
            </q-stepper-navigation>
          </q-step>

          <!-- Step 2: Configure Tag Mappings -->
          <q-step :name="2" title="Configure Tag Mappings" icon="label" :done="step > 2">
            <div class="text-body2 q-mb-md">
              Map source tags to equipment filter fields. Tags are used for filtering data.
            </div>

            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2 q-mb-md">Available Tags from Source</div>

                <div v-if="discoveredTags.length === 0" class="text-center q-pa-md text-grey-6">
                  <q-icon name="info" size="sm" class="q-mr-sm" />
                  No tags discovered. Click "Discover Tags" to fetch them.
                  <div class="q-mt-sm">
                    <q-btn
                      label="Discover Tags"
                      size="sm"
                      color="primary"
                      @click="discoverTags"
                      :loading="discoveringTags"
                    />
                  </div>
                </div>

                <div v-else class="row q-gutter-sm">
                  <div v-for="tag in discoveredTags" :key="tag" class="col-12 col-md-6">
                    <q-input
                      v-model="mappingForm.tag_mappings[tag]"
                      :label="`Map '${tag}' to`"
                      placeholder="Enter equipment filter field name"
                      dense
                    >
                      <template #prepend>
                        <q-chip size="sm" color="blue" text-color="white">{{ tag }}</q-chip>
                      </template>
                      <template #append>
                        <q-btn
                          icon="auto_fix_high"
                          flat
                          dense
                          size="sm"
                          @click="autoMapTag(tag)"
                          :title="`Auto-map ${tag}`"
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <q-stepper-navigation>
              <q-btn flat @click="prevStep" color="primary" label="Back" class="q-mr-sm" />
              <q-btn @click="nextStep" color="primary" label="Continue" />
            </q-stepper-navigation>
          </q-step>

          <!-- Step 3: Configure Field Mappings -->
          <q-step :name="3" title="Configure Field Mappings" icon="insights" :done="step > 3">
            <div class="text-body2 q-mb-md">
              Map source fields to equipment signal fields. Fields contain the actual measurement values.
            </div>

            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2 q-mb-md">Available Fields from Source</div>

                <div v-if="discoveredFields.length === 0" class="text-center q-pa-md text-grey-6">
                  <q-icon name="info" size="sm" class="q-mr-sm" />
                  No fields discovered. Click "Discover Fields" to fetch them.
                  <div class="q-mt-sm">
                    <q-btn
                      label="Discover Fields"
                      size="sm"
                      color="primary"
                      @click="discoverFields"
                      :loading="discoveringFields"
                    />
                  </div>
                </div>

                <div v-else class="row q-gutter-sm">
                  <div v-for="field in discoveredFields" :key="field.name" class="col-12 col-md-6">
                    <q-input
                      v-model="mappingForm.field_mappings[field.name]"
                      :label="`Map '${field.name}' to`"
                      placeholder="Enter equipment signal field name"
                      dense
                    >
                      <template #prepend>
                        <q-chip size="sm" color="green" text-color="white">
                          {{ field.name }}
                          <q-tooltip>Type: {{ field.type }}</q-tooltip>
                        </q-chip>
                      </template>
                      <template #append>
                        <q-btn
                          icon="auto_fix_high"
                          flat
                          dense
                          size="sm"
                          @click="autoMapField(field.name)"
                          :title="`Auto-map ${field.name}`"
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <q-stepper-navigation>
              <q-btn flat @click="prevStep" color="primary" label="Back" class="q-mr-sm" />
              <q-btn @click="nextStep" color="primary" label="Continue" />
            </q-stepper-navigation>
          </q-step>

          <!-- Step 4: Review and Create -->
          <q-step :name="4" title="Review & Create" icon="check" :done="mappingCreated">
            <div class="text-body2 q-mb-md">
              Review your mapping configuration before creating.
            </div>

            <q-card flat bordered>
              <q-card-section>
                <div class="row q-gutter-md">
                  <!-- Basic Info -->
                  <div class="col-12">
                    <div class="text-subtitle2">Basic Information</div>
                    <q-list dense>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption>Equipment</q-item-label>
                          <q-item-label>{{ getEquipmentName(mappingForm.equipment_id) }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption>Measurement</q-item-label>
                          <q-item-label>{{ mappingForm.measurement_name }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>

                  <!-- Tag Mappings -->
                  <div class="col-12 col-md-6">
                    <div class="text-subtitle2">Tag Mappings</div>
                    <q-list dense>
                      <q-item v-for="(target, source) in mappingForm.tag_mappings" :key="source">
                        <q-item-section>
                          <div class="row items-center q-gutter-sm">
                            <q-chip size="sm" color="blue" text-color="white">{{ source }}</q-chip>
                            <q-icon name="arrow_forward" size="xs" />
                            <q-chip size="sm" color="blue" outline>{{ target || 'Not mapped' }}</q-chip>
                          </div>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>

                  <!-- Field Mappings -->
                  <div class="col-12 col-md-6">
                    <div class="text-subtitle2">Field Mappings</div>
                    <q-list dense>
                      <q-item v-for="(target, source) in mappingForm.field_mappings" :key="source">
                        <q-item-section>
                          <div class="row items-center q-gutter-sm">
                            <q-chip size="sm" color="green" text-color="white">{{ source }}</q-chip>
                            <q-icon name="arrow_forward" size="xs" />
                            <q-chip size="sm" color="green" outline>{{ target || 'Not mapped' }}</q-chip>
                          </div>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>
                </div>
              </q-card-section>
            </q-card>

            <q-stepper-navigation>
              <q-btn flat @click="prevStep" color="primary" label="Back" class="q-mr-sm" />
              <q-btn
                @click="createMapping"
                color="positive"
                label="Create Mapping"
                :loading="creatingMapping"
              />
            </q-stepper-navigation>
          </q-step>
        </q-stepper>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn label="Cancel" flat @click="cancelDialog" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Props
const props = defineProps({
  modelValue: Boolean,
  dataSource: Object,
  measurements: Array,
  equipments: Array
})

// Emits
const emit = defineEmits(['update:modelValue', 'mapping-created'])

// Reactive data
const $q = useQuasar()
const step = ref(1)
const creatingMapping = ref(false)
const mappingCreated = ref(false)

// Discovery states
const discoveringTags = ref(false)
const discoveringFields = ref(false)
const discoveredTags = ref([])
const discoveredFields = ref([])

// Form data
const mappingForm = ref({
  equipment_id: null,
  measurement_name: '',
  tag_mappings: {},
  field_mappings: {}
})

// Computed
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const equipmentOptions = computed(() => {
  return props.equipments.map(eq => ({
    id: eq.id,
    name: eq.name,
    label: `${eq.name} (${eq.location || 'No location'})`
  }))
})

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

// Methods
const resetForm = () => {
  step.value = 1
  mappingCreated.value = false
  discoveredTags.value = []
  discoveredFields.value = []
  mappingForm.value = {
    equipment_id: null,
    measurement_name: '',
    tag_mappings: {},
    field_mappings: {}
  }
}

const nextStep = () => {
  if (step.value < 4) {
    step.value++

    // Auto-discover when entering step 2 or 3
    if (step.value === 2 && discoveredTags.value.length === 0) {
      discoverTags()
    } else if (step.value === 3 && discoveredFields.value.length === 0) {
      discoverFields()
    }
  }
}

const prevStep = () => {
  if (step.value > 1) {
    step.value--
  }
}

const onMeasurementChange = () => {
  // Reset discovered data when measurement changes
  discoveredTags.value = []
  discoveredFields.value = []
  mappingForm.value.tag_mappings = {}
  mappingForm.value.field_mappings = {}
}

const discoverTags = async () => {
  if (!props.dataSource || !mappingForm.value.measurement_name) return

  discoveringTags.value = true
  try {
    const connectionConfig = JSON.parse(props.dataSource.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/discover/tags', {
      source_type: props.dataSource.source_type,
      connection_config: connectionConfig,
      measurement: mappingForm.value.measurement_name
    })

    discoveredTags.value = response.data.tags

    // Initialize tag mappings with auto-mapping
    const tagMappings = {}
    discoveredTags.value.forEach(tag => {
      tagMappings[tag] = autoMapTagName(tag)
    })
    mappingForm.value.tag_mappings = tagMappings

  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to discover tags' })
    console.error('Tag discovery error:', error)
  } finally {
    discoveringTags.value = false
  }
}

const discoverFields = async () => {
  if (!props.dataSource || !mappingForm.value.measurement_name) return

  discoveringFields.value = true
  try {
    const connectionConfig = JSON.parse(props.dataSource.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/discover/fields', {
      source_type: props.dataSource.source_type,
      connection_config: connectionConfig,
      measurement: mappingForm.value.measurement_name
    })

    discoveredFields.value = response.data.fields

    // Initialize field mappings with auto-mapping
    const fieldMappings = {}
    discoveredFields.value.forEach(field => {
      fieldMappings[field.name] = autoMapFieldName(field.name)
    })
    mappingForm.value.field_mappings = fieldMappings

  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to discover fields' })
    console.error('Field discovery error:', error)
  } finally {
    discoveringFields.value = false
  }
}

const autoMapTagName = (sourceTag) => {
  // Intelligent auto-mapping for tags
  const commonMappings = {
    'n_rack': 'n_rack',
    'n_bank': 'n_bank',
    'n_module': 'n_module',
    'n_cell': 'n_cell',
    'rack': 'n_rack',
    'bank': 'n_bank',
    'module': 'n_module',
    'cell': 'n_cell',
    'rack_id': 'n_rack',
    'bank_id': 'n_bank',
    'module_id': 'n_module',
    'cell_id': 'n_cell'
  }

  const lowerTag = sourceTag.toLowerCase()
  for (const [pattern, target] of Object.entries(commonMappings)) {
    if (lowerTag.includes(pattern) || lowerTag === pattern) {
      return target
    }
  }

  // Default to same name
  return sourceTag
}

const autoMapFieldName = (sourceField) => {
  // Intelligent auto-mapping for fields
  const commonMappings = {
    'soc': 'n_soc',
    'soh': 'n_soh',
    'voltage': 'n_voltage',
    'current': 'n_current',
    'temperature': 'n_temperature',
    'temp': 'n_temperature',
    'state_of_charge': 'n_soc',
    'state_of_health': 'n_soh',
    'volt': 'n_voltage',
    'amp': 'n_current',
    'capacity': 'n_capacity'
  }

  const lowerField = sourceField.toLowerCase()
  for (const [pattern, target] of Object.entries(commonMappings)) {
    if (lowerField.includes(pattern) || lowerField === pattern) {
      return target
    }
  }

  // If it starts with 'n_', keep as is
  if (lowerField.startsWith('n_')) {
    return sourceField
  }

  // Default to adding 'n_' prefix
  return `n_${sourceField}`
}

const autoMapTag = (sourceTag) => {
  mappingForm.value.tag_mappings[sourceTag] = autoMapTagName(sourceTag)
}

const autoMapField = (sourceField) => {
  mappingForm.value.field_mappings[sourceField] = autoMapFieldName(sourceField)
}

const createMapping = async () => {
  creatingMapping.value = true
  try {
    // Filter out empty mappings
    const cleanTagMappings = Object.fromEntries(
      Object.entries(mappingForm.value.tag_mappings).filter(([key, value]) => value && value.trim())
    )

    const cleanFieldMappings = Object.fromEntries(
      Object.entries(mappingForm.value.field_mappings).filter(([key, value]) => value && value.trim())
    )

    const payload = {
      source_id: props.dataSource.source_id,
      equipment_id: mappingForm.value.equipment_id,
      measurement_name: mappingForm.value.measurement_name,
      tag_mappings: cleanTagMappings,
      field_mappings: cleanFieldMappings
    }

    await axios.post('http://localhost:8000/datasources/mappings', payload)

    mappingCreated.value = true
    $q.notify({ type: 'positive', message: 'Mapping created successfully' })

    emit('mapping-created')

    // Close dialog after short delay
    setTimeout(() => {
      show.value = false
    }, 1500)

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to create mapping: ${error.response?.data?.detail || error.message}`
    })
    console.error('Mapping creation error:', error)
  } finally {
    creatingMapping.value = false
  }
}

const getEquipmentName = (equipmentId) => {
  const equipment = props.equipments.find(eq => eq.id === equipmentId)
  return equipment ? equipment.name : `Equipment ${equipmentId}`
}

const cancelDialog = () => {
  show.value = false
}
</script>

<style scoped>
.q-stepper {
  box-shadow: none;
}

.q-chip {
  font-size: 11px;
}

.q-step__content {
  padding-left: 0;
}

.q-stepper--vertical .q-stepper__step-inner {
  padding: 0 24px 24px 24px;
}
</style>
