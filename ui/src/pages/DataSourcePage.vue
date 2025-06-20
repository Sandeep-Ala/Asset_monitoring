<!-- ui/src/pages/DataSourcePage.vue -->
<template>
  <q-page padding>
    <div class="row q-gutter-md">
      <!-- Left Panel - Data Sources List -->
      <div class="col-md-4 col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">Data Sources</div>
              <q-btn icon="add" color="primary" dense @click="showCreateDialog = true" />
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <q-list>
              <q-item
                v-for="source in dataSources"
                :key="source.source_id"
                clickable
                :active="selectedSource?.source_id === source.source_id"
                @click="selectDataSource(source)"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="source.source_type === 'influxdb' ? 'storage' : 'folder'"
                    :color="source.is_active ? 'green' : 'grey'"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ source.source_name }}</q-item-label>
                  <q-item-label caption>{{ source.source_type.toUpperCase() }}</q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn
                      icon="edit"
                      size="sm"
                      flat
                      dense
                      @click.stop="editDataSource(source)"
                    />
                    <q-btn
                      :icon="source.is_active ? 'pause' : 'play_arrow'"
                      size="sm"
                      flat
                      dense
                      :color="source.is_active ? 'orange' : 'green'"
                      @click.stop="toggleDataSource(source)"
                    />
                    <q-btn
                      icon="delete"
                      size="sm"
                      flat
                      dense
                      color="red"
                      @click.stop="deleteDataSource(source)"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Right Panel - Configuration -->
      <div class="col-md-8 col-12">
        <q-card v-if="selectedSource">
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">{{ selectedSource.source_name }}</div>
              <div class="row q-gutter-sm">
                <q-btn
                  label="Discover Schema"
                  icon="search"
                  color="primary"
                  @click="discoverSchema"
                  :loading="discovering"
                />
                <q-btn
                  label="Auto Map"
                  icon="auto_fix_high"
                  color="positive"
                  @click="autoMapMeasurements"
                  :loading="autoMapping"
                />
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <!-- Tabs for different views -->
          <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
            <q-tab name="connection" label="Connection" />
            <q-tab name="schema" label="Schema" />
            <q-tab name="mappings" label="Mappings" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="activeTab" animated>
            <!-- Connection Tab -->
            <q-tab-panel name="connection">
              <div class="q-pa-md">
                <q-form @submit.prevent="testConnection">
                  <div class="text-subtitle1 q-mb-md">Connection Details</div>

                  <div v-if="connectionConfig">
                    <div v-if="selectedSource.source_type === 'influxdb'">
                      <q-input v-model="connectionConfig.url" label="InfluxDB URL" readonly />
                      <q-input v-model="connectionConfig.org" label="Organization" readonly class="q-mt-sm" />
                      <q-input v-model="connectionConfig.bucket" label="Bucket" readonly class="q-mt-sm" />
                      <q-input v-model="connectionConfig.token" label="Token" type="password" readonly class="q-mt-sm" />
                    </div>

                    <div v-else-if="selectedSource.source_type === 'parquet'">
                      <q-input v-model="connectionConfig.base_path" label="Base Path" readonly />
                      <q-input v-model="connectionConfig.path_pattern" label="Path Pattern" readonly class="q-mt-sm" />
                    </div>
                  </div>

                  <div class="q-mt-md">
                    <q-btn
                      label="Test Connection"
                      type="submit"
                      color="primary"
                      :loading="testingConnection"
                    />
                  </div>
                </q-form>

                <!-- Connection Status -->
                <q-card v-if="connectionStatus" class="q-mt-md" :class="connectionStatus.success ? 'bg-green-1' : 'bg-red-1'">
                  <q-card-section>
                    <div class="row items-center">
                      <q-icon
                        :name="connectionStatus.success ? 'check_circle' : 'error'"
                        :color="connectionStatus.success ? 'green' : 'red'"
                        size="sm"
                        class="q-mr-sm"
                      />
                      <div class="text-body2">{{ connectionStatus.message }}</div>
                    </div>
                    <div v-if="connectionStatus.details" class="q-mt-sm">
                      <pre class="text-caption">{{ JSON.stringify(connectionStatus.details, null, 2) }}</pre>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </q-tab-panel>

            <!-- Schema Tab -->
            <q-tab-panel name="schema">
              <div class="q-pa-md">
                <div class="row q-gutter-md">
                  <!-- Measurements -->
                  <div class="col-12 col-md-4">
                    <q-card>
                      <q-card-section>
                        <div class="text-subtitle2">Measurements</div>
                        <q-list dense>
                          <q-item
                            v-for="measurement in discoveredSchema.measurements"
                            :key="measurement"
                            clickable
                            :active="selectedMeasurement === measurement"
                            @click="selectMeasurement(measurement)"
                          >
                            <q-item-section>{{ measurement }}</q-item-section>
                          </q-item>
                        </q-list>
                      </q-card-section>
                    </q-card>
                  </div>

                  <!-- Tags -->
                  <div class="col-12 col-md-4">
                    <q-card>
                      <q-card-section>
                        <div class="text-subtitle2">Tags</div>
                        <q-list dense>
                          <q-item v-for="tag in discoveredSchema.tags" :key="tag">
                            <q-item-section>
                              <q-chip size="sm" color="blue" text-color="white">{{ tag }}</q-chip>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-card-section>
                    </q-card>
                  </div>

                  <!-- Fields -->
                  <div class="col-12 col-md-4">
                    <q-card>
                      <q-card-section>
                        <div class="text-subtitle2">Fields</div>
                        <q-list dense>
                          <q-item v-for="field in discoveredSchema.fields" :key="field.name">
                            <q-item-section>
                              <div>{{ field.name }}</div>
                              <div class="text-caption text-grey">{{ field.type }}</div>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>

                <!-- Sample Data -->
                <q-card v-if="sampleData.length > 0" class="q-mt-md">
                  <q-card-section>
                    <div class="text-subtitle2">Sample Data</div>
                    <q-table
                      :rows="sampleData"
                      :columns="sampleColumns"
                      row-key="index"
                      dense
                      flat
                      :pagination="{ rowsPerPage: 5 }"
                    />
                  </q-card-section>
                </q-card>
              </div>
            </q-tab-panel>

            <!-- Mappings Tab -->
            <q-tab-panel name="mappings">
              <div class="q-pa-md">
                <div class="row items-center justify-between q-mb-md">
                  <div class="text-subtitle1">Equipment Mappings</div>
                  <q-btn
                    label="Create Mapping"
                    icon="add"
                    color="primary"
                    @click="showMappingDialog = true"
                  />
                </div>

                <q-list separator>
                  <q-item v-for="mapping in sourceMappings" :key="mapping.mapping_id">
                    <q-item-section>
                      <q-item-label>{{ getEquipmentName(mapping.equipment_id) }}</q-item-label>
                      <q-item-label caption>Measurement: {{ mapping.measurement_name }}</q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <div class="row q-gutter-xs">
                        <q-btn
                          icon="visibility"
                          size="sm"
                          flat
                          @click="viewMapping(mapping)"
                        />
                        <q-btn
                          icon="edit"
                          size="sm"
                          flat
                          @click="editMapping(mapping)"
                        />
                        <q-btn
                          icon="delete"
                          size="sm"
                          flat
                          color="red"
                          @click="deleteMapping(mapping)"
                        />
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>

        <!-- Empty State -->
        <q-card v-else>
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="storage" size="4rem" color="grey-5" />
            <div class="text-h6 text-grey-7 q-mt-md">No Data Source Selected</div>
            <div class="text-body2 text-grey-6">Select a data source from the list or create a new one</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Create/Edit Data Source Dialog -->
    <q-dialog v-model="showCreateDialog" persistent>
      <q-card style="min-width: 600px; max-width: 800px">
        <q-card-section>
          <div class="text-h6">{{ editingSource ? 'Edit' : 'Create' }} Data Source</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-form @submit.prevent="saveDataSource">
            <!-- Basic Information -->
            <div class="text-subtitle2 q-mb-md">Basic Information</div>

            <q-input
              v-model="dataSourceForm.source_name"
              label="Source Name"
              placeholder="Enter a descriptive name"
              required
              class="q-mb-md"
            />

            <q-select
              v-model="dataSourceForm.source_type"
              :options="sourceTypeOptions"
              label="Source Type"
              required
              class="q-mb-lg"
              @update:model-value="resetConnectionConfig"
            />

            <!-- InfluxDB Configuration -->
            <div v-if="dataSourceForm.source_type === 'influxdb'">
              <div class="text-subtitle2 q-mb-md">InfluxDB Connection Settings</div>

              <q-input
                v-model="dataSourceForm.connection_config.url"
                label="InfluxDB URL"
                placeholder="http://localhost:8086"
                hint="The base URL of your InfluxDB instance"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="link" />
                </template>
              </q-input>

              <q-input
                v-model="dataSourceForm.connection_config.org"
                label="Organization"
                placeholder="my-org"
                hint="Your InfluxDB organization name"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="business" />
                </template>
              </q-input>

              <q-input
                v-model="dataSourceForm.connection_config.bucket"
                label="Bucket"
                placeholder="my-bucket"
                hint="The bucket containing your time-series data"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="storage" />
                </template>
              </q-input>

              <q-input
                v-model="dataSourceForm.connection_config.token"
                label="Access Token"
                type="password"
                placeholder="Your InfluxDB access token"
                hint="API token with read permissions"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="key" />
                </template>
                <template #append>
                  <q-btn
                    :icon="showToken ? 'visibility_off' : 'visibility'"
                    flat
                    dense
                    @click="toggleTokenVisibility"
                  />
                </template>
              </q-input>
            </div>

            <!-- Parquet Configuration -->
            <div v-if="dataSourceForm.source_type === 'parquet'">
              <div class="text-subtitle2 q-mb-md">Parquet Files Configuration</div>

              <q-input
                v-model="dataSourceForm.connection_config.base_path"
                label="Base Path"
                placeholder="D:/Asset Monitoring System/Data-Backup"
                hint="Root directory containing your parquet files"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="folder" />
                </template>
                <template #append>
                  <q-btn
                    icon="folder_open"
                    flat
                    dense
                    @click="browseFolder"
                    title="Browse folder"
                  />
                </template>
              </q-input>

              <q-input
                v-model="dataSourceForm.connection_config.path_pattern"
                label="Path Pattern"
                placeholder="**/*.parquet"
                hint="Glob pattern to match parquet files"
                required
                class="q-mb-md"
              >
                <template #prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>

            <!-- Connection Test Result -->
            <q-card v-if="formConnectionStatus" class="q-mb-md" :class="formConnectionStatus.success ? 'bg-green-1' : 'bg-red-1'">
              <q-card-section>
                <div class="row items-center">
                  <q-icon
                    :name="formConnectionStatus.success ? 'check_circle' : 'error'"
                    :color="formConnectionStatus.success ? 'green' : 'red'"
                    size="sm"
                    class="q-mr-sm"
                  />
                  <div class="text-body2">{{ formConnectionStatus.message }}</div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Action Buttons -->
            <div class="row q-gutter-sm q-mt-lg">
              <q-btn
                label="Test Connection"
                icon="wifi_find"
                color="secondary"
                @click="testConnectionForm"
                :loading="testingConnectionForm"
                :disable="!isFormValid"
              />
              <q-spacer />
              <q-btn
                label="Cancel"
                flat
                @click="cancelDialog"
              />
              <q-btn
                label="Save"
                icon="save"
                type="submit"
                color="primary"
                :loading="savingDataSource"
                :disable="!isFormValid"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Mapping Dialog -->
    <MappingDialog
      v-model="showMappingDialog"
      :data-source="selectedSource"
      :measurements="discoveredSchema.measurements"
      :equipments="equipments"
      @mapping-created="onMappingCreated"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'
import MappingDialog from 'src/components/MappingDialog.vue'

// Reactive data
const $q = useQuasar()
const dataSources = ref([])
const selectedSource = ref(null)
const activeTab = ref('connection')
const showCreateDialog = ref(false)
const showMappingDialog = ref(false)
const editingSource = ref(null)

// Connection testing
const testingConnection = ref(false)
const connectionStatus = ref(null)
const connectionConfig = ref(null)

// Schema discovery
const discovering = ref(false)
const discoveredSchema = ref({
  measurements: [],
  tags: [],
  fields: []
})
const selectedMeasurement = ref(null)
const sampleData = ref([])

// Auto mapping
const autoMapping = ref(false)
const sourceMappings = ref([])
const equipments = ref([])

// Form data
const dataSourceForm = ref({
  source_name: '',
  source_type: '',
  connection_config: {}
})

const sourceTypeOptions = [
  { label: 'InfluxDB', value: 'influxdb' },
  { label: 'Parquet Files', value: 'parquet' }
]

const testingConnectionForm = ref(false)
const savingDataSource = ref(false)
const showToken = ref(false)
const formConnectionStatus = ref(null)

// Computed
const sampleColumns = computed(() => {
  if (sampleData.value.length === 0) return []
  return Object.keys(sampleData.value[0]).map(key => ({
    name: key,
    label: key,
    field: key,
    align: 'left'
  }))
})

const isFormValid = computed(() => {
  if (!dataSourceForm.value.source_name || !dataSourceForm.value.source_type) {
    return false
  }

  if (dataSourceForm.value.source_type === 'influxdb') {
    const config = dataSourceForm.value.connection_config
    return config.url && config.org && config.bucket && config.token
  }

  if (dataSourceForm.value.source_type === 'parquet') {
    const config = dataSourceForm.value.connection_config
    return config.base_path && config.path_pattern
  }

  return false
})

// Methods
onMounted(() => {
  fetchDataSources()
  fetchEquipments()
})

const fetchDataSources = async () => {
  try {
    const response = await axios.get('http://localhost:8000/datasources/')
    dataSources.value = response.data
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to fetch data sources' })
  }
}

const fetchEquipments = async () => {
  try {
    const response = await axios.get('http://localhost:8000/equipments')
    equipments.value = response.data
  } catch (error) {
    console.error('Failed to fetch equipments:', error)
  }
}

const selectDataSource = async (source) => {
  selectedSource.value = source
  connectionConfig.value = JSON.parse(source.connection_config)
  activeTab.value = 'connection'

  // Fetch mappings for this source
  await fetchSourceMappings(source.source_id)
}

const fetchSourceMappings = async (sourceId) => {
  try {
    const response = await axios.get(`http://localhost:8000/datasources/${sourceId}/mappings`)
    sourceMappings.value = response.data
  } catch (error) {
    console.error('Failed to fetch mappings:', error)
  }
}

const testConnection = async () => {
  if (!selectedSource.value) return

  testingConnection.value = true
  try {
    const response = await axios.post('http://localhost:8000/datasources/test-connection', {
      source_type: selectedSource.value.source_type,
      connection_config: connectionConfig.value
    })
    connectionStatus.value = response.data
  } catch (error) {
    connectionStatus.value = {
      success: false,
      message: 'Connection test failed',
      details: { error: error.message }
    }
  } finally {
    testingConnection.value = false
  }
}

const discoverSchema = async () => {
  if (!selectedSource.value) return

  discovering.value = true
  try {
    // Discover measurements
    const measurementsResponse = await axios.get(
      `http://localhost:8000/datasources/${selectedSource.value.source_id}/discover/measurements`
    )
    discoveredSchema.value.measurements = measurementsResponse.data.measurements

    if (discoveredSchema.value.measurements.length > 0) {
      await selectMeasurement(discoveredSchema.value.measurements[0])
    }

    activeTab.value = 'schema'
    $q.notify({ type: 'positive', message: 'Schema discovered successfully' })
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to discover schema' })
  } finally {
    discovering.value = false
  }
}

const selectMeasurement = async (measurement) => {
  selectedMeasurement.value = measurement

  try {
    // Discover tags and fields for this measurement
    const [tagsResponse, fieldsResponse, sampleResponse] = await Promise.all([
      axios.post('http://localhost:8000/datasources/discover/tags', {
        source_type: selectedSource.value.source_type,
        connection_config: connectionConfig.value,
        measurement
      }),
      axios.post('http://localhost:8000/datasources/discover/fields', {
        source_type: selectedSource.value.source_type,
        connection_config: connectionConfig.value,
        measurement
      }),
      axios.post('http://localhost:8000/datasources/discover/sample', {
        source_type: selectedSource.value.source_type,
        connection_config: connectionConfig.value,
        measurement
      })
    ])

    discoveredSchema.value.tags = tagsResponse.data.tags
    discoveredSchema.value.fields = fieldsResponse.data.fields
    sampleData.value = sampleResponse.data.sample_data
  } catch (error) {
    console.error('Failed to discover measurement details:', error)
  }
}

const autoMapMeasurements = async () => {
  if (!selectedSource.value) return

  autoMapping.value = true
  try {
    const response = await axios.post(
      `http://localhost:8000/datasources/${selectedSource.value.source_id}/auto-map`
    )

    $q.notify({
      type: 'positive',
      message: response.data.message
    })

    await fetchSourceMappings(selectedSource.value.source_id)
    activeTab.value = 'mappings'
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Auto-mapping failed' })
  } finally {
    autoMapping.value = false
  }
}

const editDataSource = (source) => {
  editingSource.value = source
  dataSourceForm.value = {
    source_name: source.source_name,
    source_type: source.source_type,
    connection_config: JSON.parse(source.connection_config)
  }
  showCreateDialog.value = true
}

const resetConnectionConfig = () => {
  formConnectionStatus.value = null // Clear previous test results

  if (dataSourceForm.value.source_type === 'influxdb') {
    dataSourceForm.value.connection_config = {
      url: 'http://localhost:8086',
      org: '',
      bucket: '',
      token: ''
    }
  } else if (dataSourceForm.value.source_type === 'parquet') {
    dataSourceForm.value.connection_config = {
      base_path: '',
      path_pattern: '**/*.parquet'
    }
  }
}

const toggleTokenVisibility = () => {
  showToken.value = !showToken.value
  // Update input type
  const tokenInput = document.querySelector('input[type="password"]')
  if (tokenInput) {
    tokenInput.type = showToken.value ? 'text' : 'password'
  }
}

const browseFolder = () => {
  // This would typically open a file browser
  // For now, show a notification that this feature is coming
  $q.notify({
    message: 'File browser integration coming soon. Please enter path manually.',
    type: 'info',
    icon: 'info'
  })
}

const testConnectionForm = async () => {
  testingConnectionForm.value = true
  formConnectionStatus.value = null

  try {
    const response = await axios.post('http://localhost:8000/datasources/test-connection', {
      source_type: dataSourceForm.value.source_type,
      connection_config: dataSourceForm.value.connection_config
    })

    formConnectionStatus.value = response.data

    $q.notify({
      type: response.data.success ? 'positive' : 'negative',
      message: response.data.message,
      icon: response.data.success ? 'check_circle' : 'error'
    })
  } catch (error) {
    formConnectionStatus.value = {
      success: false,
      message: 'Connection test failed',
      details: { error: error.message }
    }

    $q.notify({
      type: 'negative',
      message: 'Connection test failed',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    testingConnectionForm.value = false
  }
}

const saveDataSource = async () => {
  savingDataSource.value = true
  try {
    if (editingSource.value) {
      await axios.put(
        `http://localhost:8000/datasources/${editingSource.value.source_id}`,
        dataSourceForm.value
      )
      $q.notify({ type: 'positive', message: 'Data source updated' })
    } else {
      await axios.post('http://localhost:8000/datasources/', dataSourceForm.value)
      $q.notify({ type: 'positive', message: 'Data source created' })
    }

    await fetchDataSources()
    cancelDialog()
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to save data source' })
  } finally {
    savingDataSource.value = false
  }
}

const cancelDialog = () => {
  showCreateDialog.value = false
  editingSource.value = null
  formConnectionStatus.value = null
  dataSourceForm.value = {
    source_name: '',
    source_type: '',
    connection_config: {}
  }
}

const toggleDataSource = async (source) => {
  try {
    await axios.post(`http://localhost:8000/datasources/${source.source_id}/toggle`)
    await fetchDataSources()
    $q.notify({
      type: 'positive',
      message: `Data source ${source.is_active ? 'deactivated' : 'activated'}`
    })
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Failed to toggle data source' })
  }
}

const deleteDataSource = (source) => {
  $q.dialog({
    title: 'Confirm',
    message: `Are you sure you want to delete "${source.source_name}"?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await axios.delete(`http://localhost:8000/datasources/${source.source_id}`)
      await fetchDataSources()
      if (selectedSource.value?.source_id === source.source_id) {
        selectedSource.value = null
      }
      $q.notify({ type: 'positive', message: 'Data source deleted' })
    } catch (error) {
      $q.notify({ type: 'negative', message: 'Failed to delete data source' })
    }
  })
}

const deleteMapping = (mapping) => {
  $q.dialog({
    title: 'Confirm',
    message: 'Are you sure you want to delete this mapping?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await axios.delete(`http://localhost:8000/datasources/mappings/${mapping.mapping_id}`)
      await fetchSourceMappings(selectedSource.value.source_id)
      $q.notify({ type: 'positive', message: 'Mapping deleted' })
    } catch (error) {
      $q.notify({ type: 'negative', message: 'Failed to delete mapping' })
    }
  })
}

const getEquipmentName = (equipmentId) => {
  const equipment = equipments.value.find(eq => eq.id === equipmentId)
  return equipment ? equipment.name : `Equipment ${equipmentId}`
}

const viewMapping = (mapping) => {
  $q.dialog({
    title: 'Mapping Details',
    message: `
      Equipment: ${getEquipmentName(mapping.equipment_id)}
      Measurement: ${mapping.measurement_name}
      Tags: ${mapping.tag_mappings}
      Fields: ${mapping.field_mappings}
    `
  })
}

const editMapping = (mapping) => {
  // TODO: Implement edit mapping dialog
  $q.notify({ message: 'Edit mapping functionality coming soon' })
}

const onMappingCreated = async () => {
  await fetchSourceMappings(selectedSource.value.source_id)
}
</script>

<style scoped>
.q-card {
  border-radius: 8px;
}

.q-tab-panel {
  padding: 0;
}
</style>
