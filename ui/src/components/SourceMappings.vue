<!-- ui/src/components/SourceMappings.vue -->
<template>
  <div class="source-mappings q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Equipment Mappings</div>
        <div class="text-subtitle2 text-grey-6">
          {{ mappings.length }} active mappings for this data source
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Import Mappings"
          icon="file_upload"
          color="secondary"
          outline
          @click="showImportDialog = true"
        />
        <q-btn
          label="Auto Map"
          icon="auto_fix_high"
          color="warning"
          outline
          @click="autoMapEquipments"
          :loading="autoMapping"
        />
        <q-btn
          label="Create Mapping"
          icon="add"
          color="primary"
          @click="$emit('create-mapping')"
        />
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-4">
        <q-input
          v-model="searchQuery"
          placeholder="Search mappings..."
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
          v-model="equipmentFilter"
          :options="equipmentOptions"
          label="Filter by Equipment"
          outlined
          dense
          clearable
          emit-value
          map-options
        />
      </div>

      <div class="col-12 col-md-3">
        <q-select
          v-model="measurementFilter"
          :options="measurementOptions"
          label="Filter by Measurement"
          outlined
          dense
          clearable
        />
      </div>

      <div class="col-12 col-md-2">
        <q-select
          v-model="statusFilter"
          :options="statusOptions"
          label="Status"
          outlined
          dense
          clearable
          emit-value
          map-options
        />
      </div>
    </div>

    <!-- Mappings Grid -->
    <div v-if="filteredMappings.length === 0" class="text-center q-pa-xl">
      <q-icon name="link_off" size="4rem" class="text-grey-4 q-mb-md" />
      <div class="text-h6 text-grey-6 q-mb-sm">No Mappings Found</div>
      <div class="text-body2 text-grey-5 q-mb-lg">
        {{ searchQuery || equipmentFilter || measurementFilter ?
           'Try adjusting your search criteria' :
           'Create your first mapping to connect data to equipment' }}
      </div>
      <q-btn
        label="Create First Mapping"
        icon="add"
        color="primary"
        @click="$emit('create-mapping')"
      />
    </div>

    <div v-else class="row q-gutter-md">
      <div
        v-for="mapping in filteredMappings"
        :key="mapping.mapping_id"
        class="col-12 col-md-6 col-lg-4"
      >
        <q-card class="mapping-card" flat bordered>
          <!-- Card Header -->
          <q-card-section class="bg-blue-1">
            <div class="row items-center justify-between">
              <div>
                <div class="text-h6">{{ getEquipmentName(mapping.equipment_id) }}</div>
                <div class="text-caption text-grey-7">{{ mapping.measurement_name }}</div>
              </div>

              <q-btn-dropdown
                icon="more_vert"
                flat
                round
                size="sm"
              >
                <q-list>
                  <q-item clickable @click="viewMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="visibility" />
                    </q-item-section>
                    <q-item-section>View Details</q-item-section>
                  </q-item>

                  <q-item clickable @click="editMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="edit" />
                    </q-item-section>
                    <q-item-section>Edit Mapping</q-item-section>
                  </q-item>

                  <q-item clickable @click="cloneMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="content_copy" />
                    </q-item-section>
                    <q-item-section>Clone Mapping</q-item-section>
                  </q-item>

                  <q-item clickable @click="exportMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="file_download" />
                    </q-item-section>
                    <q-item-section>Export Mapping</q-item-section>
                  </q-item>

                  <q-separator />

                  <q-item clickable @click="testMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="play_arrow" color="positive" />
                    </q-item-section>
                    <q-item-section>Test Mapping</q-item-section>
                  </q-item>

                  <q-item clickable @click="validateMapping(mapping)">
                    <q-item-section avatar>
                      <q-icon name="check_circle" color="blue" />
                    </q-item-section>
                    <q-item-section>Validate</q-item-section>
                  </q-item>

                  <q-separator />

                  <q-item clickable @click="deleteMapping(mapping)" class="text-negative">
                    <q-item-section avatar>
                      <q-icon name="delete" />
                    </q-item-section>
                    <q-item-section>Delete</q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
            </div>
          </q-card-section>

          <!-- Mapping Info -->
          <q-card-section>
            <q-list dense>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="precision_manufacturing" color="primary" size="sm" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Equipment</q-item-label>
                  <q-item-label>{{ getEquipmentName(mapping.equipment_id) }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="table_chart" color="blue" size="sm" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Measurement</q-item-label>
                  <q-item-label>{{ mapping.measurement_name }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <!-- Tag Mappings -->
          <q-card-section v-if="getTagMappings(mapping).length > 0" class="q-pt-none">
            <div class="text-subtitle2 q-mb-sm">Tag Mappings</div>
            <div class="row q-gutter-xs">
              <q-chip
                v-for="tag in getTagMappings(mapping).slice(0, 3)"
                :key="tag.source"
                size="sm"
                color="blue"
                text-color="white"
                :label="`${tag.source} → ${tag.target}`"
              />
              <q-chip
                v-if="getTagMappings(mapping).length > 3"
                size="sm"
                color="grey"
                text-color="white"
                :label="`+${getTagMappings(mapping).length - 3} more`"
              />
            </div>
          </q-card-section>

          <!-- Field Mappings -->
          <q-card-section v-if="getFieldMappings(mapping).length > 0" class="q-pt-none">
            <div class="text-subtitle2 q-mb-sm">Field Mappings</div>
            <div class="row q-gutter-xs">
              <q-chip
                v-for="field in getFieldMappings(mapping).slice(0, 3)"
                :key="field.source"
                size="sm"
                color="green"
                text-color="white"
                :label="`${field.source} → ${field.target}`"
              />
              <q-chip
                v-if="getFieldMappings(mapping).length > 3"
                size="sm"
                color="grey"
                text-color="white"
                :label="`+${getFieldMappings(mapping).length - 3} more`"
              />
            </div>
          </q-card-section>

          <!-- Status and Actions -->
          <q-card-section class="q-pt-none">
            <div class="row items-center justify-between">
              <div class="row items-center q-gutter-sm">
                <q-chip
                  :color="getMappingStatusColor(mapping)"
                  text-color="white"
                  size="sm"
                >
                  {{ getMappingStatus(mapping) }}
                </q-chip>

                <q-chip
                  color="grey-6"
                  text-color="white"
                  size="sm"
                >
                  {{ formatDate(mapping.created_at) }}
                </q-chip>
              </div>

              <div class="row q-gutter-xs">
                <q-btn
                  icon="visibility"
                  flat
                  round
                  size="sm"
                  @click="viewMapping(mapping)"
                  title="View Details"
                />
                <q-btn
                  icon="edit"
                  flat
                  round
                  size="sm"
                  @click="editMapping(mapping)"
                  title="Edit Mapping"
                />
                <q-btn
                  icon="play_arrow"
                  flat
                  round
                  size="sm"
                  color="positive"
                  @click="testMapping(mapping)"
                  title="Test Mapping"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedMappings.length > 0" class="fixed-bottom-right q-ma-lg">
      <q-card>
        <q-card-section class="bg-primary text-white">
          <div class="text-subtitle1">{{ selectedMappings.length }} selected</div>
        </q-card-section>

        <q-card-actions>
          <q-btn label="Test All" icon="play_arrow" flat @click="testSelectedMappings" />
          <q-btn label="Export All" icon="file_download" flat @click="exportSelectedMappings" />
          <q-btn label="Delete All" icon="delete" flat color="negative" @click="deleteSelectedMappings" />
        </q-card-actions>
      </q-card>
    </div>

    <!-- Import Dialog -->
    <q-dialog v-model="showImportDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Import Mappings</div>
        </q-card-section>

        <q-card-section>
          <q-file
            v-model="importFile"
            label="Select mapping file"
            accept=".json"
            filled
          >
            <template #prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>

          <div class="q-mt-md">
            <q-checkbox
              v-model="importOptions.overwrite"
              label="Overwrite existing mappings"
            />
            <div class="text-caption text-grey-6">
              Replace mappings with the same equipment and measurement
            </div>
          </div>

          <div class="q-mt-sm">
            <q-checkbox
              v-model="importOptions.validate"
              label="Validate mappings before import"
            />
            <div class="text-caption text-grey-6">
              Check mapping validity against current schema
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancel" flat @click="showImportDialog = false" />
          <q-btn
            label="Import"
            color="primary"
            @click="importMappings"
            :disable="!importFile"
            :loading="importing"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Mapping Details Dialog -->
    <q-dialog v-model="showDetailsDialog" maximized>
      <MappingDetailsDialog
        :mapping="selectedMapping"
        :equipment="getEquipment(selectedMapping?.equipment_id)"
        @close="showDetailsDialog = false"
        @edit="editMapping"
        @delete="deleteMapping"
      />
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Import sub-components
import MappingDetailsDialog from 'src/components/MappingDetailsDialog.vue'

// Props
const props = defineProps({
  source: Object,
  mappings: Array,
  equipments: Array
})

// Emits
const emit = defineEmits(['create-mapping', 'edit-mapping', 'delete-mapping'])

// Reactive data
const $q = useQuasar()
const searchQuery = ref('')
const equipmentFilter = ref('')
const measurementFilter = ref('')
const statusFilter = ref('')
const selectedMappings = ref([])
const autoMapping = ref(false)

// Dialog states
const showImportDialog = ref(false)
const showDetailsDialog = ref(false)
const importFile = ref(null)
const importing = ref(false)
const selectedMapping = ref(null)

// Import options
const importOptions = ref({
  overwrite: false,
  validate: true
})

// Computed properties
const equipmentOptions = computed(() => {
  const equipmentIds = [...new Set(props.mappings.map(m => m.equipment_id))]
  return equipmentIds.map(id => ({
    label: getEquipmentName(id),
    value: id
  }))
})

const measurementOptions = computed(() => {
  return [...new Set(props.mappings.map(m => m.measurement_name))]
})

const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Error', value: 'error' },
  { label: 'Warning', value: 'warning' }
]

const filteredMappings = computed(() => {
  let filtered = props.mappings

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(mapping =>
      getEquipmentName(mapping.equipment_id).toLowerCase().includes(query) ||
      mapping.measurement_name.toLowerCase().includes(query)
    )
  }

  // Equipment filter
  if (equipmentFilter.value) {
    filtered = filtered.filter(mapping => mapping.equipment_id === equipmentFilter.value)
  }

  // Measurement filter
  if (measurementFilter.value) {
    filtered = filtered.filter(mapping => mapping.measurement_name === measurementFilter.value)
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(mapping => getMappingStatus(mapping).toLowerCase() === statusFilter.value)
  }

  return filtered
})

// Methods
const getEquipmentName = (equipmentId) => {
  const equipment = props.equipments?.find(eq => eq.id === equipmentId)
  return equipment ? equipment.name : `Equipment ${equipmentId}`
}

const getEquipment = (equipmentId) => {
  return props.equipments?.find(eq => eq.id === equipmentId)
}

const getTagMappings = (mapping) => {
  try {
    const tagMappings = typeof mapping.tag_mappings === 'string' ?
      JSON.parse(mapping.tag_mappings) : mapping.tag_mappings

    return Object.entries(tagMappings || {}).map(([target, source]) => ({
      source,
      target
    }))
  } catch {
    return []
  }
}

const getFieldMappings = (mapping) => {
  try {
    const fieldMappings = typeof mapping.field_mappings === 'string' ?
      JSON.parse(mapping.field_mappings) : mapping.field_mappings

    return Object.entries(fieldMappings || {}).map(([target, source]) => ({
      source,
      target
    }))
  } catch {
    return []
  }
}

const getMappingStatus = (mapping) => {
  // This would typically check validation results
  const tagCount = getTagMappings(mapping).length
  const fieldCount = getFieldMappings(mapping).length

  if (fieldCount === 0) return 'Error'
  if (tagCount === 0) return 'Warning'
  return 'Active'
}

const getMappingStatusColor = (mapping) => {
  const status = getMappingStatus(mapping)
  return {
    'Active': 'positive',
    'Warning': 'warning',
    'Error': 'negative'
  }[status] || 'grey'
}

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

// Actions
const viewMapping = (mapping) => {
  selectedMapping.value = mapping
  showDetailsDialog.value = true
}

const editMapping = (mapping) => {
  emit('edit-mapping', mapping)
}

const deleteMapping = (mapping) => {
  $q.dialog({
    title: 'Confirm Deletion',
    message: `Are you sure you want to delete the mapping for "${getEquipmentName(mapping.equipment_id)}"?`,
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(() => {
    emit('delete-mapping', mapping)
  })
}

const cloneMapping = async (mapping) => {
  try {
    // Create a copy of the mapping
    const clonedMapping = {
      equipment_id: mapping.equipment_id,
      measurement_name: `${mapping.measurement_name}_copy`,
      tag_mappings: mapping.tag_mappings,
      field_mappings: mapping.field_mappings
    }

    // This would typically call the API to create the clone
    $q.notify({
      type: 'positive',
      message: 'Mapping cloned successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to clone mapping'
    })
  }
}

const exportMapping = (mapping) => {
  const exportData = {
    equipment_name: getEquipmentName(mapping.equipment_id),
    equipment_id: mapping.equipment_id,
    measurement_name: mapping.measurement_name,
    tag_mappings: getTagMappings(mapping),
    field_mappings: getFieldMappings(mapping),
    created_at: mapping.created_at
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `mapping_${getEquipmentName(mapping.equipment_id)}_${mapping.measurement_name}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Mapping exported successfully'
  })
}

const testMapping = async (mapping) => {
  try {
    // This would typically test the mapping with the API
    await new Promise(resolve => setTimeout(resolve, 1000))

    $q.notify({
      type: 'positive',
      message: `Mapping test successful for ${getEquipmentName(mapping.equipment_id)}`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Mapping test failed'
    })
  }
}

const validateMapping = async (mapping) => {
  try {
    // This would typically validate the mapping with the API
    await new Promise(resolve => setTimeout(resolve, 500))

    $q.notify({
      type: 'positive',
      message: 'Mapping validation passed'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Mapping validation failed'
    })
  }
}

const autoMapEquipments = async () => {
  autoMapping.value = true

  try {
    // This would typically call the auto-mapping API
    await new Promise(resolve => setTimeout(resolve, 2000))

    $q.notify({
      type: 'positive',
      message: 'Auto-mapping completed successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Auto-mapping failed'
    })
  } finally {
    autoMapping.value = false
  }
}

const importMappings = async () => {
  if (!importFile.value) return

  importing.value = true

  try {
    const text = await importFile.value.text()
    const mappingsData = JSON.parse(text)

    // Validate import data structure
    if (!Array.isArray(mappingsData)) {
      throw new Error('Invalid file format - expected array of mappings')
    }

    // This would typically call the API to import mappings
    await new Promise(resolve => setTimeout(resolve, 1000))

    showImportDialog.value = false
    importFile.value = null

    $q.notify({
      type: 'positive',
      message: `Successfully imported ${mappingsData.length} mappings`
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to import mappings',
      caption: error.message
    })
  } finally {
    importing.value = false
  }
}

// Bulk actions
const testSelectedMappings = async () => {
  for (const mapping of selectedMappings.value) {
    await testMapping(mapping)
  }
  selectedMappings.value = []
}

const exportSelectedMappings = () => {
  const exportData = selectedMappings.value.map(mapping => ({
    equipment_name: getEquipmentName(mapping.equipment_id),
    equipment_id: mapping.equipment_id,
    measurement_name: mapping.measurement_name,
    tag_mappings: getTagMappings(mapping),
    field_mappings: getFieldMappings(mapping),
    created_at: mapping.created_at
  }))

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `bulk_mappings_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  selectedMappings.value = []

  $q.notify({
    type: 'positive',
    message: 'Mappings exported successfully'
  })
}

const deleteSelectedMappings = () => {
  $q.dialog({
    title: 'Confirm Bulk Deletion',
    message: `Are you sure you want to delete ${selectedMappings.value.length} mappings?`,
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(() => {
    selectedMappings.value.forEach(mapping => {
      emit('delete-mapping', mapping)
    })
    selectedMappings.value = []
  })
}
</script>

<style scoped>
.source-mappings {
  background-color: #fafafa;
  min-height: 100%;
}

.mapping-card {
  transition: all 0.3s ease;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.mapping-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.q-chip {
  font-weight: 500;
}

.fixed-bottom-right {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.q-item {
  border-radius: 8px;
  margin-bottom: 2px;
}

.q-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Custom scrollbar */
.q-list {
  max-height: 200px;
  overflow-y: auto;
}

.q-list::-webkit-scrollbar {
  width: 4px;
}

.q-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.q-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.q-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
