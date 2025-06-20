<!-- ui/src/components/SourceOverview.vue -->
<template>
  <div class="source-overview q-pa-lg">
    <!-- Header Stats -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <q-icon name="link" size="2rem" color="primary" class="q-mb-sm" />
            <div class="text-h6">{{ mappings.length }}</div>
            <div class="text-caption text-grey-6">Active Mappings</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <q-icon name="table_chart" size="2rem" color="blue" class="q-mb-sm" />
            <div class="text-h6">{{ discoveredMeasurements.length }}</div>
            <div class="text-caption text-grey-6">Measurements</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <q-icon
              :name="healthStatus?.healthy ? 'check_circle' : 'error'"
              size="2rem"
              :color="healthStatus?.healthy ? 'positive' : 'negative'"
              class="q-mb-sm"
            />
            <div class="text-h6">{{ healthStatus?.healthy ? 'Healthy' : 'Issues' }}</div>
            <div class="text-caption text-grey-6">Connection Status</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section class="text-center">
            <q-icon name="access_time" size="2rem" color="orange" class="q-mb-sm" />
            <div class="text-h6">{{ formatDate(source.updated_at) }}</div>
            <div class="text-caption text-grey-6">Last Updated</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Source Information -->
    <div class="row q-gutter-lg">
      <!-- Basic Information -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Source Information</div>

            <q-list>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="storage" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Source Name</q-item-label>
                  <q-item-label class="text-h6">{{ source.source_name }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="category" color="blue" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Source Type</q-item-label>
                  <q-item-label>{{ source.source_type.toUpperCase() }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon
                    :name="source.is_active ? 'check_circle' : 'pause_circle'"
                    :color="source.is_active ? 'positive' : 'warning'"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Status</q-item-label>
                  <q-item-label>
                    <q-chip
                      :color="source.is_active ? 'positive' : 'warning'"
                      text-color="white"
                      size="sm"
                    >
                      {{ source.is_active ? 'Active' : 'Inactive' }}
                    </q-chip>
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="schedule" color="grey" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Created</q-item-label>
                  <q-item-label>{{ formatDateTime(source.created_at) }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="update" color="grey" />
                </q-item-section>
                <q-item-section>
                  <q-item-label caption>Last Modified</q-item-label>
                  <q-item-label>{{ formatDateTime(source.updated_at) }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Connection Summary -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Connection Summary</div>
              <q-btn
                icon="refresh"
                flat
                round
                size="sm"
                @click="refreshHealth"
                :loading="refreshingHealth"
              />
            </div>

            <div v-if="connectionConfig">
              <!-- InfluxDB Config -->
              <div v-if="source.source_type === 'influxdb'">
                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="language" color="deep-purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Server URL</q-item-label>
                      <q-item-label>{{ connectionConfig.url }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="business" color="deep-purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Organization</q-item-label>
                      <q-item-label>{{ connectionConfig.org }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="folder" color="deep-purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Bucket</q-item-label>
                      <q-item-label>{{ connectionConfig.bucket }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="vpn_key" color="deep-purple" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Token</q-item-label>
                      <q-item-label>{{ maskToken(connectionConfig.token) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Parquet Config -->
              <div v-else-if="source.source_type === 'parquet'">
                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="folder_open" color="blue-grey" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Base Path</q-item-label>
                      <q-item-label>{{ connectionConfig.base_path }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="pattern" color="blue-grey" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>File Pattern</q-item-label>
                      <q-item-label>{{ connectionConfig.path_pattern }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item v-if="connectionConfig.date_column">
                    <q-item-section avatar>
                      <q-icon name="access_time" color="blue-grey" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label caption>Date Column</q-item-label>
                      <q-item-label>{{ connectionConfig.date_column }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Health Status -->
              <div class="q-mt-md">
                <q-card flat bordered :class="healthStatus?.healthy ? 'bg-green-1' : 'bg-red-1'">
                  <q-card-section>
                    <div class="row items-center">
                      <q-icon
                        :name="healthStatus?.healthy ? 'check_circle' : 'error'"
                        :color="healthStatus?.healthy ? 'positive' : 'negative'"
                        size="md"
                        class="q-mr-md"
                      />
                      <div class="col">
                        <div class="text-subtitle2">
                          {{ healthStatus?.healthy ? 'Connection Healthy' : 'Connection Issues' }}
                        </div>
                        <div class="text-caption text-grey-7">
                          Last checked: {{ formatDateTime(healthStatus?.lastChecked) || 'Never' }}
                        </div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row q-gutter-lg q-mt-lg">
      <!-- Mappings Summary -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Equipment Mappings</div>
              <q-btn
                label="Create New"
                icon="add"
                color="primary"
                size="sm"
                @click="$emit('create-mapping')"
              />
            </div>

            <div v-if="mappings.length === 0" class="text-center q-pa-lg text-grey-6">
              <q-icon name="link_off" size="3rem" class="q-mb-md" />
              <div class="text-h6">No Mappings</div>
              <div class="text-body2">Create mappings to connect this data source to equipment</div>
            </div>

            <q-list v-else separator>
              <q-item v-for="mapping in recentMappings" :key="mapping.mapping_id">
                <q-item-section avatar>
                  <q-avatar color="primary" text-color="white" size="sm">
                    <q-icon name="link" />
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ getEquipmentName(mapping.equipment_id) }}</q-item-label>
                  <q-item-label caption>
                    {{ mapping.measurement_name }} •
                    {{ Object.keys(mapping.tag_mappings || {}).length }} tags •
                    {{ Object.keys(mapping.field_mappings || {}).length }} fields
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="text-caption text-grey-6">
                    {{ formatDate(mapping.created_at) }}
                  </div>
                </q-item-section>
              </q-item>

              <q-item v-if="mappings.length > 3">
                <q-item-section class="text-center">
                  <q-btn
                    :label="`View all ${mappings.length} mappings`"
                    flat
                    color="primary"
                    @click="$emit('view-all-mappings')"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Schema Discovery -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6">Schema Discovery</div>
              <q-btn
                label="Explore"
                icon="search"
                color="secondary"
                size="sm"
                @click="$emit('explore-schema')"
              />
            </div>

            <div v-if="discoveredMeasurements.length === 0" class="text-center q-pa-lg text-grey-6">
              <q-icon name="search" size="3rem" class="q-mb-md" />
              <div class="text-h6">No Schema Data</div>
              <div class="text-body2">Discover measurements and schema structure</div>
            </div>

            <div v-else>
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="table_chart" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Measurements Discovered</q-item-label>
                    <q-item-label caption>{{ discoveredMeasurements.length }} tables/measurements found</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip color="blue" text-color="white" size="sm">
                      {{ discoveredMeasurements.length }}
                    </q-chip>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="label" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Tag Columns</q-item-label>
                    <q-item-label caption>Filterable tag columns across measurements</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip color="green" text-color="white" size="sm">
                      {{ totalTagsCount }}
                    </q-chip>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="insights" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Field Columns</q-item-label>
                    <q-item-label caption>Measurement value columns across measurements</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip color="orange" text-color="white" size="sm">
                      {{ totalFieldsCount }}
                    </q-chip>
                  </q-item-section>
                </q-item>
              </q-list>

              <!-- Recent Measurements -->
              <div class="q-mt-md">
                <div class="text-subtitle2 q-mb-sm">Recent Measurements</div>
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="measurement in discoveredMeasurements.slice(0, 4)"
                    :key="measurement"
                    :label="measurement"
                    color="blue-grey"
                    text-color="white"
                    size="sm"
                  />
                  <q-chip
                    v-if="discoveredMeasurements.length > 4"
                    :label="`+${discoveredMeasurements.length - 4} more`"
                    color="grey"
                    text-color="white"
                    size="sm"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row q-mt-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Quick Actions</div>

            <div class="row q-gutter-md">
              <q-btn
                label="Test Connection"
                icon="wifi_find"
                color="secondary"
                outline
                @click="$emit('test-connection')"
              />

              <q-btn
                label="Discover Schema"
                icon="search"
                color="primary"
                outline
                @click="$emit('discover-schema')"
              />

              <q-btn
                label="Create Mapping"
                icon="link"
                color="positive"
                outline
                @click="$emit('create-mapping')"
              />

              <q-btn
                label="Export Config"
                icon="file_download"
                color="blue-grey"
                outline
                @click="$emit('export-config')"
              />

              <q-btn
                label="Clone Source"
                icon="content_copy"
                color="orange"
                outline
                @click="$emit('clone-source')"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  source: Object,
  mappings: Array,
  healthStatus: Object
})

// Emits
const emit = defineEmits([
  'refresh',
  'test-connection',
  'discover-schema',
  'create-mapping',
  'view-all-mappings',
  'explore-schema',
  'export-config',
  'clone-source'
])

// Reactive data
const refreshingHealth = ref(false)
const discoveredMeasurements = ref([])
const equipmentNames = ref({})

// Computed properties
const connectionConfig = computed(() => {
  try {
    return JSON.parse(props.source.connection_config)
  } catch {
    return {}
  }
})

const recentMappings = computed(() => {
  return props.mappings.slice(0, 3)
})

const totalTagsCount = computed(() => {
  return props.mappings.reduce((total, mapping) => {
    return total + Object.keys(mapping.tag_mappings || {}).length
  }, 0)
})

const totalFieldsCount = computed(() => {
  return props.mappings.reduce((total, mapping) => {
    return total + Object.keys(mapping.field_mappings || {}).length
  }, 0)
})

// Methods
onMounted(() => {
  loadSchemaInfo()
  loadEquipmentNames()
})

const loadSchemaInfo = async () => {
  // This would typically load cached schema information
  // For now, we'll simulate it
  discoveredMeasurements.value = [
    'equipment_data',
    'sensor_readings',
    'battery_status',
    'environmental_data'
  ]
}

const loadEquipmentNames = async () => {
  // Load equipment names for mapping display
  const equipmentIds = [...new Set(props.mappings.map(m => m.equipment_id))]

  for (const id of equipmentIds) {
    try {
      // This would typically fetch from API
      equipmentNames.value[id] = `Equipment ${id}`
    } catch (error) {
      equipmentNames.value[id] = `Unknown Equipment`
    }
  }
}

const getEquipmentName = (equipmentId) => {
  return equipmentNames.value[equipmentId] || `Equipment ${equipmentId}`
}

const maskToken = (token) => {
  if (!token) return 'Not set'
  if (token.length <= 8) return '••••••••'
  return token.substring(0, 4) + '••••••••' + token.substring(token.length - 4)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Invalid date'
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return 'Invalid date'
  }
}

const refreshHealth = async () => {
  refreshingHealth.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    emit('refresh')
  } finally {
    refreshingHealth.value = false
  }
}
</script>

<style scoped>
.source-overview {
  background-color: #fafafa;
  min-height: 100%;
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-red-1 {
  background-color: rgba(244, 67, 54, 0.1);
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
</style>
