<!-- ui/src/pages/DataSourcePage.vue -->
<template>
  <q-page class="q-pa-md">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h4 text-weight-bold">Data Sources</div>
        <div class="text-subtitle1 text-grey-6">
          Connect and manage your data sources for equipment monitoring
        </div>
      </div>
      <div class="row q-gutter-sm">
        <q-btn
          label="Import Config"
          icon="file_upload"
          color="secondary"
          outline
          @click="showImportDialog = true"
        />
        <q-btn
          label="New Data Source"
          icon="add"
          color="primary"
          @click="showCreateWizard = true"
        />
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card class="bg-primary text-white">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">{{ dataSources.length }}</div>
                <div class="text-caption">Total Sources</div>
              </div>
              <div class="col-auto">
                <q-icon name="storage" size="2rem" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card class="bg-positive text-white">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">{{ activeSourcesCount }}</div>
                <div class="text-caption">Active Sources</div>
              </div>
              <div class="col-auto">
                <q-icon name="check_circle" size="2rem" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card class="bg-info text-white">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">{{ totalMappingsCount }}</div>
                <div class="text-caption">Total Mappings</div>
              </div>
              <div class="col-auto">
                <q-icon name="link" size="2rem" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card class="bg-warning text-white">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">{{ healthySourcesCount }}</div>
                <div class="text-caption">Healthy Sources</div>
              </div>
              <div class="col-auto">
                <q-icon name="favorite" size="2rem" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Main Content -->
    <div class="row q-gutter-md">
      <!-- Left Panel - Data Sources List -->
      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">Data Sources</div>
              <q-btn
                icon="refresh"
                flat
                round
                size="sm"
                @click="refreshDataSources"
                :loading="loadingDataSources"
              />
            </div>
          </q-card-section>

          <q-separator />

          <!-- Search and Filter -->
          <q-card-section>
            <q-input
              v-model="searchQuery"
              placeholder="Search data sources..."
              dense
              clearable
            >
              <template #prepend>
                <q-icon name="search" />
              </template>
            </q-input>

            <div class="row q-gutter-xs q-mt-sm">
              <q-btn
                :label="`All (${dataSources.length})`"
                size="sm"
                :color="sourceFilter === 'all' ? 'primary' : 'grey-5'"
                flat
                @click="sourceFilter = 'all'"
              />
              <q-btn
                :label="`Active (${activeSourcesCount})`"
                size="sm"
                :color="sourceFilter === 'active' ? 'positive' : 'grey-5'"
                flat
                @click="sourceFilter = 'active'"
              />
              <q-btn
                :label="`Inactive (${dataSources.length - activeSourcesCount})`"
                size="sm"
                :color="sourceFilter === 'inactive' ? 'negative' : 'grey-5'"
                flat
                @click="sourceFilter = 'inactive'"
              />
            </div>
          </q-card-section>

          <q-separator />

          <!-- Data Sources List -->
          <q-card-section class="q-pa-none">
            <q-list separator>
              <q-item
                v-for="source in filteredDataSources"
                :key="source.source_id"
                clickable
                :class="selectedSource?.source_id === source.source_id ? 'bg-blue-1' : ''"
                @click="selectDataSource(source)"
              >
                <q-item-section avatar>
                  <q-avatar :color="getSourceTypeColor(source.source_type)" text-color="white" size="md">
                    <q-icon :name="getSourceTypeIcon(source.source_type)" />
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ source.source_name }}</q-item-label>
                  <q-item-label caption>
                    {{ source.source_type.toUpperCase() }} •
                    {{ formatDate(source.updated_at) }}
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="column items-end">
                    <q-chip
                      :color="source.is_active ? 'positive' : 'negative'"
                      text-color="white"
                      size="sm"
                    >
                      {{ source.is_active ? 'Active' : 'Inactive' }}
                    </q-chip>

                    <!-- Health Status -->
                    <div class="row q-gutter-xs q-mt-xs">
                      <q-icon
                        :name="getHealthIcon(source.source_id)"
                        :color="getHealthColor(source.source_id)"
                        size="sm"
                        :title="getHealthTooltip(source.source_id)"
                      />
                    </div>
                  </div>
                </q-item-section>

                <q-item-section side>
                  <q-btn-dropdown
                    icon="more_vert"
                    flat
                    round
                    size="sm"
                    @click.stop
                  >
                    <q-list>
                      <q-item clickable @click="editDataSource(source)">
                        <q-item-section avatar>
                          <q-icon name="edit" />
                        </q-item-section>
                        <q-item-section>Edit</q-item-section>
                      </q-item>

                      <q-item clickable @click="cloneDataSource(source)">
                        <q-item-section avatar>
                          <q-icon name="content_copy" />
                        </q-item-section>
                        <q-item-section>Clone</q-item-section>
                      </q-item>

                      <q-item clickable @click="exportDataSource(source)">
                        <q-item-section avatar>
                          <q-icon name="file_download" />
                        </q-item-section>
                        <q-item-section>Export</q-item-section>
                      </q-item>

                      <q-separator />

                      <q-item
                        clickable
                        @click="toggleDataSource(source)"
                        :class="source.is_active ? 'text-orange' : 'text-green'"
                      >
                        <q-item-section avatar>
                          <q-icon :name="source.is_active ? 'pause' : 'play_arrow'" />
                        </q-item-section>
                        <q-item-section>
                          {{ source.is_active ? 'Deactivate' : 'Activate' }}
                        </q-item-section>
                      </q-item>

                      <q-item clickable @click="deleteDataSource(source)" class="text-negative">
                        <q-item-section avatar>
                          <q-icon name="delete" />
                        </q-item-section>
                        <q-item-section>Delete</q-item-section>
                      </q-item>
                    </q-list>
                  </q-btn-dropdown>
                </q-item-section>
              </q-item>

              <q-item v-if="filteredDataSources.length === 0">
                <q-item-section class="text-center text-grey-6">
                  <div>
                    <q-icon name="storage" size="3rem" class="q-mb-md" />
                    <div class="text-h6">No data sources found</div>
                    <div class="text-body2">
                      {{ searchQuery ? 'Try adjusting your search' : 'Create your first data source to get started' }}
                    </div>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Right Panel - Source Details -->
      <div class="col-12 col-md-8">
        <q-card v-if="selectedSource">
          <!-- Source Header -->
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="row items-center q-gutter-md">
                <q-avatar :color="getSourceTypeColor(selectedSource.source_type)" text-color="white" size="lg">
                  <q-icon :name="getSourceTypeIcon(selectedSource.source_type)" />
                </q-avatar>
                <div>
                  <div class="text-h6">{{ selectedSource.source_name }}</div>
                  <div class="text-subtitle2 text-grey-6">
                    {{ selectedSource.source_type.toUpperCase() }} Data Source
                  </div>
                </div>
              </div>

              <div class="row q-gutter-sm">
                <q-btn
                  label="Test Connection"
                  icon="wifi_find"
                  color="secondary"
                  outline
                  @click="testSourceConnection"
                  :loading="testingConnection"
                />
                <q-btn
                  label="Discover Schema"
                  icon="search"
                  color="primary"
                  outline
                  @click="showSchemaExplorer = true"
                />
                <q-btn
                  label="Create Mapping"
                  icon="link"
                  color="positive"
                  @click="showMappingWizard = true"
                />
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <!-- Tabs -->
          <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
            <q-tab name="overview" label="Overview" icon="dashboard" />
            <q-tab name="connection" label="Connection" icon="settings" />
            <q-tab name="schema" label="Schema" icon="account_tree" />
            <q-tab name="mappings" label="Mappings" icon="link" />
            <q-tab name="health" label="Health" icon="monitor_heart" />
          </q-tabs>

          <q-separator />

          <!-- Tab Panels -->
          <q-tab-panels v-model="activeTab" animated>
            <!-- Overview Tab -->
            <q-tab-panel name="overview">
              <SourceOverview
                :source="selectedSource"
                :mappings="sourceMappings"
                :health-status="sourceHealthStatus[selectedSource.source_id]"
                @refresh="refreshSourceData"
              />
            </q-tab-panel>

            <!-- Connection Tab -->
            <q-tab-panel name="connection">
              <SourceConnection
                :source="selectedSource"
                @test-connection="testSourceConnection"
                @update-config="updateSourceConfig"
              />
            </q-tab-panel>

            <!-- Schema Tab -->
            <q-tab-panel name="schema">
              <SourceSchema
                :source="selectedSource"
                :discovered-schema="discoveredSchema"
                @discover="discoverSourceSchema"
                @refresh-schema="refreshSchema"
              />
            </q-tab-panel>

            <!-- Mappings Tab -->
            <q-tab-panel name="mappings">
              <SourceMappings
                :source="selectedSource"
                :mappings="sourceMappings"
                :equipments="equipments"
                @create-mapping="showMappingWizard = true"
                @edit-mapping="editMapping"
                @delete-mapping="deleteMapping"
              />
            </q-tab-panel>

            <!-- Health Tab -->
            <q-tab-panel name="health">
              <SourceHealth
                :source="selectedSource"
                :health-data="sourceHealthStatus[selectedSource.source_id]"
                @refresh-health="refreshHealthStatus"
              />
            </q-tab-panel>
          </q-tab-panels>
        </q-card>

        <!-- Empty State -->
        <q-card v-else>
          <q-card-section class="text-center q-pa-xl">
            <q-icon name="touch_app" size="4rem" class="text-grey-4 q-mb-md" />
            <div class="text-h6 text-grey-6 q-mb-sm">Select a Data Source</div>
            <div class="text-body2 text-grey-5">
              Choose a data source from the list to view its details and manage connections
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Dialogs and Components -->
    <DataSourceWizard
      v-model="showCreateWizard"
      :equipments="equipments"
      @source-created="onSourceCreated"
    />

    <SchemaExplorer
      v-model="showSchemaExplorer"
      :source="selectedSource"
      @schema-discovered="onSchemaDiscovered"
    />

    <MappingWizard
      v-model="showMappingWizard"
      :source="selectedSource"
      :equipments="equipments"
      :discovered-schema="discoveredSchema"
      @mapping-created="onMappingCreated"
    />

    <!-- Import Config Dialog -->
    <q-dialog v-model="showImportDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Import Configuration</div>
        </q-card-section>

        <q-card-section>
          <q-file
            v-model="importFile"
            label="Select configuration file"
            accept=".json"
            filled
          >
            <template #prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cancel" flat @click="showImportDialog = false" />
          <q-btn
            label="Import"
            color="primary"
            @click="importConfiguration"
            :disable="!importFile"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

// Import components (these will be created separately)
import DataSourceWizard from 'src/components/DataSourceWizard.vue'
import SchemaExplorer from 'src/components/SchemaExplorer.vue'
import MappingWizard from 'src/components/MappingWizard.vue'
import SourceOverview from 'src/components/SourceOverview.vue'
// import SourceConnection from 'src/components/SourceConnection.vue'
// import SourceSchema from 'src/components/SourceSchema.vue'
import SourceMappings from 'src/components/SourceMappings.vue'
// import SourceHealth from 'src/components/SourceHealth.vue'

// Reactive data
const $q = useQuasar()
const dataSources = ref([])
const selectedSource = ref(null)
const sourceMappings = ref([])
const equipments = ref([])

// UI State
const activeTab = ref('overview')
const searchQuery = ref('')
const sourceFilter = ref('all')
const loadingDataSources = ref(false)
const testingConnection = ref(false)

// Dialog states
const showCreateWizard = ref(false)
const showSchemaExplorer = ref(false)
const showMappingWizard = ref(false)
const showImportDialog = ref(false)
const importFile = ref(null)

// Schema and health data
const discoveredSchema = ref({
  measurements: [],
  tags: {},
  fields: {},
  sampleData: {}
})
const sourceHealthStatus = ref({})

// Computed properties
const activeSourcesCount = computed(() =>
  dataSources.value.filter(source => source.is_active).length
)

const totalMappingsCount = computed(() =>
  dataSources.value.reduce((total, source) => total + (source.mappings_count || 0), 0)
)

const healthySourcesCount = computed(() =>
  Object.values(sourceHealthStatus.value).filter(status => status?.healthy).length
)

const filteredDataSources = computed(() => {
  let filtered = dataSources.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(source =>
      source.source_name.toLowerCase().includes(query) ||
      source.source_type.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (sourceFilter.value === 'active') {
    filtered = filtered.filter(source => source.is_active)
  } else if (sourceFilter.value === 'inactive') {
    filtered = filtered.filter(source => !source.is_active)
  }

  return filtered
})

// Methods
onMounted(() => {
  fetchDataSources()
  fetchEquipments()
  startHealthMonitoring()
})

const fetchDataSources = async () => {
  loadingDataSources.value = true
  try {
    const response = await axios.get('http://localhost:8000/datasources/')
    dataSources.value = response.data

    // Fetch mapping counts for each source
    for (const source of dataSources.value) {
      try {
        const mappingsResponse = await axios.get(`http://localhost:8000/datasources/${source.source_id}/mappings`)
        source.mappings_count = mappingsResponse.data.length
      } catch (error) {
        source.mappings_count = 0
      }
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to fetch data sources',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    loadingDataSources.value = false
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
  activeTab.value = 'overview'
  await Promise.all([
    fetchSourceMappings(source.source_id),
    refreshHealthStatus(source.source_id)
  ])
}

const fetchSourceMappings = async (sourceId) => {
  try {
    const response = await axios.get(`http://localhost:8000/datasources/${sourceId}/mappings`)
    sourceMappings.value = response.data
  } catch (error) {
    console.error('Failed to fetch source mappings:', error)
    sourceMappings.value = []
  }
}

const refreshDataSources = async () => {
  await fetchDataSources()
  if (selectedSource.value) {
    // Update selected source data
    const updatedSource = dataSources.value.find(s => s.source_id === selectedSource.value.source_id)
    if (updatedSource) {
      selectedSource.value = updatedSource
    }
  }
}

const testSourceConnection = async () => {
  if (!selectedSource.value) return

  testingConnection.value = true
  try {
    const connectionConfig = JSON.parse(selectedSource.value.connection_config)
    const response = await axios.post('http://localhost:8000/datasources/test-connection', {
      source_type: selectedSource.value.source_type,
      connection_config: connectionConfig
    })

    $q.notify({
      type: response.data.success ? 'positive' : 'negative',
      message: response.data.message,
      icon: response.data.success ? 'check_circle' : 'error'
    })

    // Update health status
    sourceHealthStatus.value[selectedSource.value.source_id] = {
      healthy: response.data.success,
      lastChecked: new Date(),
      details: response.data
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Connection test failed',
      caption: error.response?.data?.detail || error.message
    })
  } finally {
    testingConnection.value = false
  }
}

const discoverSourceSchema = async () => {
  if (!selectedSource.value) return

  try {
    const response = await axios.get(`http://localhost:8000/datasources/${selectedSource.value.source_id}/discover/measurements`)
    discoveredSchema.value.measurements = response.data.measurements
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to discover schema',
      caption: error.response?.data?.detail || error.message
    })
  }
}

const refreshSchema = async () => {
  await discoverSourceSchema()
}

const refreshHealthStatus = async (sourceId) => {
  // This would typically check the actual connection health
  // For now, we'll use the last known status or mark as unknown
  if (!sourceHealthStatus.value[sourceId]) {
    sourceHealthStatus.value[sourceId] = {
      healthy: null,
      lastChecked: null,
      details: null
    }
  }
}

const startHealthMonitoring = () => {
  // Set up periodic health checks every 5 minutes
  setInterval(() => {
    dataSources.value.forEach(source => {
      if (source.is_active) {
        refreshHealthStatus(source.source_id)
      }
    })
  }, 5 * 60 * 1000) // 5 minutes
}

// Source type helpers
const getSourceTypeColor = (type) => {
  const colors = {
    influxdb: 'deep-purple',
    parquet: 'blue-grey'
  }
  return colors[type] || 'grey'
}

const getSourceTypeIcon = (type) => {
  const icons = {
    influxdb: 'timeline',
    parquet: 'folder_special'
  }
  return icons[type] || 'storage'
}

// Health status helpers
const getHealthIcon = (sourceId) => {
  const status = sourceHealthStatus.value[sourceId]
  if (!status || status.healthy === null) return 'help'
  return status.healthy ? 'check_circle' : 'error'
}

const getHealthColor = (sourceId) => {
  const status = sourceHealthStatus.value[sourceId]
  if (!status || status.healthy === null) return 'grey'
  return status.healthy ? 'positive' : 'negative'
}

const getHealthTooltip = (sourceId) => {
  const status = sourceHealthStatus.value[sourceId]
  if (!status || status.healthy === null) return 'Health status unknown'
  return status.healthy ? 'Connection healthy' : 'Connection issues detected'
}

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Event handlers
const onSourceCreated = async (newSource) => {
  await fetchDataSources()
  selectedSource.value = newSource
}

const onSchemaDiscovered = (schema) => {
  discoveredSchema.value = { ...discoveredSchema.value, ...schema }
}

const onMappingCreated = async () => {
  if (selectedSource.value) {
    await fetchSourceMappings(selectedSource.value.source_id)
  }
}

const refreshSourceData = async () => {
  if (selectedSource.value) {
    await Promise.all([
      fetchSourceMappings(selectedSource.value.source_id),
      refreshHealthStatus(selectedSource.value.source_id)
    ])
  }
}

// CRUD operations
const editDataSource = (source) => {
  // TODO: Implement edit functionality
  $q.notify({ message: 'Edit functionality coming soon', type: 'info' })
}

const cloneDataSource = async (source) => {
  try {
    const clonedData = {
      source_name: `${source.source_name} (Copy)`,
      source_type: source.source_type,
      connection_config: JSON.parse(source.connection_config)
    }

    const response = await axios.post('http://localhost:8000/datasources/', clonedData)
    await fetchDataSources()

    $q.notify({
      type: 'positive',
      message: 'Data source cloned successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to clone data source',
      caption: error.response?.data?.detail || error.message
    })
  }
}

const exportDataSource = (source) => {
  const exportData = {
    source_name: source.source_name,
    source_type: source.source_type,
    connection_config: JSON.parse(source.connection_config)
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${source.source_name.replace(/\s+/g, '_')}_config.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Configuration exported successfully'
  })
}

const importConfiguration = async () => {
  if (!importFile.value) return

  try {
    const text = await importFile.value.text()
    const config = JSON.parse(text)

    // Validate config structure
    if (!config.source_name || !config.source_type || !config.connection_config) {
      throw new Error('Invalid configuration file format')
    }

    const response = await axios.post('http://localhost:8000/datasources/', config)
    await fetchDataSources()

    showImportDialog.value = false
    importFile.value = null

    $q.notify({
      type: 'positive',
      message: 'Configuration imported successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to import configuration',
      caption: error.message
    })
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
    $q.notify({
      type: 'negative',
      message: 'Failed to toggle data source',
      caption: error.response?.data?.detail || error.message
    })
  }
}

const deleteDataSource = (source) => {
  $q.dialog({
    title: 'Confirm Deletion',
    message: `Are you sure you want to delete "${source.source_name}"? This action cannot be undone.`,
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(async () => {
    try {
      await axios.delete(`http://localhost:8000/datasources/${source.source_id}`)
      await fetchDataSources()

      if (selectedSource.value?.source_id === source.source_id) {
        selectedSource.value = null
      }

      $q.notify({
        type: 'positive',
        message: 'Data source deleted successfully'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Failed to delete data source',
        caption: error.response?.data?.detail || error.message
      })
    }
  })
}

const updateSourceConfig = async (config) => {
  // TODO: Implement config update
  $q.notify({ message: 'Config update functionality coming soon', type: 'info' })
}

const editMapping = (mapping) => {
  // TODO: Implement edit mapping functionality
  $q.notify({ message: 'Edit mapping functionality coming soon', type: 'info' })
}

const deleteMapping = (mapping) => {
  $q.dialog({
    title: 'Confirm Deletion',
    message: 'Are you sure you want to delete this mapping?',
    cancel: true,
    persistent: true,
    color: 'negative'
  }).onOk(async () => {
    try {
      await axios.delete(`http://localhost:8000/datasources/mappings/${mapping.mapping_id}`)
      await fetchSourceMappings(selectedSource.value.source_id)

      $q.notify({
        type: 'positive',
        message: 'Mapping deleted successfully'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Failed to delete mapping',
        caption: error.response?.data?.detail || error.message
      })
    }
  })
}
</script>

<style scoped>
.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-tab-panel {
  padding: 0;
}

.q-chip {
  font-weight: 500;
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

/* Custom scrollbar for lists */
.q-list {
  max-height: 400px;
  overflow-y: auto;
}

.q-list::-webkit-scrollbar {
  width: 4px;
}

.q-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.q-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.q-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
