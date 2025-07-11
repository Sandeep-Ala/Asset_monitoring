<!-- components/DataSourceManager.vue -->
<template>
  <div class="datasource-manager">
    <!-- Tab Navigation -->
    <q-tabs
      v-model="activeTab"
      dense
      class="text-grey"
      active-color="primary"
      indicator-color="primary"
      align="justify"
      narrow-indicator
    >
      <q-tab name="connections" label="Connections" icon="link" />
      <q-tab name="schema" label="Schema Discovery" icon="schema" />
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-tab-panels v-model="activeTab" animated>
      <!-- Connections Tab -->
      <q-tab-panel name="connections" class="q-pa-none">
        <div class="row q-gutter-md q-pa-md">
          <!-- Connection Form -->
          <div class="col-12 col-md-4">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-primary">
                  <q-icon name="add_circle" class="q-mr-sm" />
                  {{ editMode ? 'Edit Connection' : 'New Connection' }}
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section>
                <ConnectionForm
                  ref="connectionForm"
                  :edit-mode="editMode"
                  :connection-data="selectedConnection"
                  @save="handleSaveConnection"
                  @cancel="handleCancelEdit"
                  @test="handleTestConnection"
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Connection List -->
          <div class="col-12 col-md-8">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-primary">
                  <q-icon name="list" class="q-mr-sm" />
                  Existing Connections
                  <q-btn
                    flat
                    round
                    icon="refresh"
                    size="sm"
                    class="q-ml-sm"
                    @click="loadConnections"
                    :loading="connectionsLoading"
                  >
                    <q-tooltip>Refresh connections</q-tooltip>
                  </q-btn>
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="q-pa-none">
                <ConnectionList
                  :connections="connections"
                  :loading="connectionsLoading"
                  @edit="handleEditConnection"
                  @delete="handleDeleteConnection"
                  @test="handleTestExistingConnection"
                  @discover-schema="handleDiscoverSchema"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Schema Discovery Tab -->
      <q-tab-panel name="schema" class="q-pa-md">
        <div class="row q-gutter-md">
          <!-- Connection Selector -->
          <div class="col-12">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-primary">
                  <q-icon name="schema" class="q-mr-sm" />
                  Schema Discovery
                </div>
                <div class="q-mt-md">
                  <div class="row q-gutter-md items-center">
                    <div class="col">
                      <q-select
                        v-model="selectedSchemaConnection"
                        :options="activeConnections"
                        option-label="name"
                        option-value="id"
                        label="Select Active Connection"
                        outlined
                        map-options
                        emit-value
                        @update:model-value="loadSchema"
                      >
                        <template v-slot:option="scope">
                          <q-item v-bind="scope.itemProps">
                            <q-item-section avatar>
                              <q-icon :name="getDbTypeIcon(scope.opt.db_type)" />
                            </q-item-section>
                            <q-item-section>
                              <q-item-label>{{ scope.opt.name }}</q-item-label>
                              <q-item-label caption>{{ scope.opt.db_type }} • {{ scope.opt.status }}</q-item-label>
                            </q-item-section>
                          </q-item>
                        </template>
                      </q-select>
                    </div>
                    <div class="col-auto">
                      <q-toggle
                        v-model="quickAnalysisMode"
                        label="Quick Mode"
                        color="primary"
                        @update:model-value="onAnalysisModeChange"
                      />
                      <div class="text-caption text-grey-6">
                        {{ quickAnalysisMode ? 'Fast analysis (limited details)' : 'Full analysis (slower)' }}
                      </div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Display -->
          <div class="col-12" v-if="selectedSchemaConnection">
            <div class="row q-gutter-md">
              <!-- Tables List -->
              <div class="col-12 col-md-4">
                <q-card>
                  <q-card-section>
                    <div class="text-h6">Tables</div>
                    <div class="text-caption text-grey-7">{{ schemaData.tables?.length || 0 }} tables found</div>
                  </q-card-section>
                  <q-separator />
                  <q-card-section class="q-pa-none">
                    <q-list bordered separator v-if="schemaData.tables?.length">
                      <q-item
                        v-for="table in schemaData.tables"
                        :key="table.name"
                        clickable
                        v-ripple
                        :active="selectedTable?.name === table.name"
                        @click="selectTable(table)"
                      >
                        <q-item-section avatar>
                          <q-icon name="table_chart" color="primary" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ table.name }}</q-item-label>
                          <q-item-label caption>{{ table.row_count }} rows • {{ table.total_columns || table.columns?.length || 0 }} columns</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <q-chip size="xs" color="blue" text-color="white">
                            {{ table.total_columns || table.columns?.length || 0 }}
                          </q-chip>
                        </q-item-section>
                      </q-item>
                    </q-list>
                    <div v-else-if="schemaLoading" class="q-pa-md text-center">
                      <q-spinner-dots size="40px" color="primary" />
                      <div class="q-mt-sm">Loading schema...</div>
                    </div>
                    <div v-else-if="selectedSchemaConnection && !schemaLoading" class="q-pa-md text-center text-grey-7">
                      <q-icon name="warning" size="32px" class="q-mb-sm" />
                      <div>No tables found or failed to load schema</div>
                      <q-btn flat color="primary" @click="loadSchema" class="q-mt-sm">
                        Retry
                      </q-btn>
                    </div>
                    <div v-else class="q-pa-md text-center text-grey-7">
                      Select a connection to view tables
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Columns List -->
              <div class="col-12 col-md-8">
                <q-card>
                  <q-card-section>
                    <div class="text-h6">
                      Columns
                      <span v-if="selectedTable" class="text-caption">
                        - {{ selectedTable.name }}
                      </span>
                    </div>
                    <div class="text-caption text-grey-7" v-if="selectedTable">
                      {{ selectedTable.columns?.length || 0 }} columns • Click column for suggestions
                    </div>
                  </q-card-section>
                  <q-separator />
                  <q-card-section class="q-pa-none">
                    <q-table
                      v-if="selectedTable?.columns"
                      :rows="selectedTable.columns"
                      :columns="columnTableColumns"
                      row-key="name"
                      flat
                      :pagination="{ rowsPerPage: 10 }"
                      dense
                    >
                      <template v-slot:body-cell-name="props">
                        <q-td :props="props">
                          <div class="text-weight-medium">{{ props.value }}</div>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-data_type="props">
                        <q-td :props="props">
                          <q-chip size="sm" :color="getDataTypeColor(props.value)" text-color="white">
                            {{ props.value }}
                          </q-chip>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-category="props">
                        <q-td :props="props">
                          <q-chip size="sm" :color="getCategoryColor(props.value)" text-color="white">
                            {{ props.value }}
                          </q-chip>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-suggested_for="props">
                        <q-td :props="props">
                          <div class="q-gutter-xs">
                            <q-chip
                              v-for="suggestion in props.value"
                              :key="suggestion"
                              size="xs"
                              color="green"
                              text-color="white"
                            >
                              {{ suggestion }}
                            </q-chip>
                          </div>
                        </q-td>
                      </template>
                    </q-table>
                    <div v-else-if="!selectedTable" class="q-pa-md text-center text-grey-7">
                      Select a table to view columns
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script>
import { dataSourceAPI } from 'src/services/Api'
import ConnectionForm from './ConnectionForm.vue'
import ConnectionList from './ConnectionList.vue'

export default {
  name: 'DataSourceManager',
  components: {
    ConnectionForm,
    ConnectionList
  },
  emits: ['connection-created', 'connection-updated', 'connection-deleted', 'schema-discovered'],
  data() {
    return {
      activeTab: 'connections',
      connections: [],
      connectionsLoading: false,
      editMode: false,
      selectedConnection: null,

      // Schema discovery
      selectedSchemaConnection: null,
      schemaData: {},
      selectedTable: null,
      schemaLoading: false,
      quickAnalysisMode: true, // Default to quick mode for performance

      // Column table configuration
      columnTableColumns: [
        { name: 'name', label: 'Column Name', field: 'name', align: 'left', sortable: true },
        { name: 'data_type', label: 'Data Type', field: 'data_type', align: 'center', sortable: true },
        { name: 'category', label: 'Category', field: 'category', align: 'center', sortable: true },
        { name: 'distinct_count', label: 'Distinct', field: 'distinct_count', align: 'center', sortable: true },
        { name: 'suggested_for', label: 'Suggested For', field: 'suggested_for', align: 'left' }
      ]
    }
  },
  computed: {
    activeConnections() {
      return this.connections.filter(conn => conn.status === 'active')
    }
  },
  async mounted() {
    await this.loadConnections()
  },
  methods: {
    // Connection Management
    async loadConnections() {
      this.connectionsLoading = true
      try {
        const response = await dataSourceAPI.getAllConnections()
        this.connections = response.data
      } catch (error) {
        this.$q.notify({
          type: 'negative',
          message: 'Failed to load connections: ' + error.message
        })
      } finally {
        this.connectionsLoading = false
      }
    },

    async handleSaveConnection(connectionData) {
      try {
        let response
        if (this.editMode) {
          // Update connection
          const updateData = {
            name: connectionData.name,
            description: connectionData.description,
            db_type: connectionData.db_type
          }
          response = await dataSourceAPI.updateConnection(this.selectedConnection.id, updateData)

          // Save configuration
          if (connectionData.config && Object.keys(connectionData.config).length > 0) {
            await dataSourceAPI.saveConnectionConfigs(this.selectedConnection.id, connectionData.config)
          }

          this.$emit('connection-updated', response.data)
        } else {
          // Create connection
          const createData = {
            name: connectionData.name,
            description: connectionData.description,
            db_type: connectionData.db_type
          }

          console.log('🚀 Creating connection:', createData)
          response = await dataSourceAPI.createConnection(createData)
          console.log('✅ Connection created:', response.data)

          // Save configuration
          if (connectionData.config && Object.keys(connectionData.config).length > 0) {
            console.log('🔧 Saving config for connection:', response.data.id, connectionData.config)
            await dataSourceAPI.saveConnectionConfigs(response.data.id, connectionData.config)
            console.log('✅ Config saved')
          }

          this.$emit('connection-created', response.data)
        }

        // Refresh connections list
        await this.loadConnections()

        // Reset form
        this.handleCancelEdit()

        this.$q.notify({
          type: 'positive',
          message: `Connection ${this.editMode ? 'updated' : 'created'} successfully!`
        })

      } catch (error) {
        console.error('❌ Error saving connection:', error)
        this.$q.notify({
          type: 'negative',
          message: `Failed to ${this.editMode ? 'update' : 'create'} connection: ` + (error.response?.data?.detail || error.message)
        })
      }
    },

    handleEditConnection(connection) {
      this.editMode = true
      this.selectedConnection = { ...connection }
    },

    handleCancelEdit() {
      this.editMode = false
      this.selectedConnection = null
      this.$refs.connectionForm?.resetForm()
    },

    async handleDeleteConnection(connection) {
      this.$q.dialog({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete connection "${connection.name}"?`,
        cancel: true,
        persistent: true
      }).onOk(async () => {
        try {
          await dataSourceAPI.deleteConnection(connection.id)
          this.$emit('connection-deleted', connection.name)
          await this.loadConnections()
        } catch (error) {
          this.$q.notify({
            type: 'negative',
            message: 'Failed to delete connection: ' + error.message
          })
        }
      })
    },

    async handleTestConnection(testData) {
      // This is handled by the ConnectionForm component
      await this.loadConnections() // Refresh to get updated status
    },

    async handleTestExistingConnection(connection) {
      try {
        const configResponse = await dataSourceAPI.getConnectionConfigsDict(connection.id)
        const testData = {
          connection_id: connection.id,
          config: configResponse.data
        }

        const response = await dataSourceAPI.testConnection(testData)

        this.$q.notify({
          type: response.data.success ? 'positive' : 'negative',
          message: response.data.message
        })

        await this.loadConnections()
      } catch (error) {
        this.$q.notify({
          type: 'negative',
          message: 'Failed to test connection: ' + error.message
        })
      }
    },

    async handleDiscoverSchema(connection) {
      this.selectedSchemaConnection = connection.id
      this.activeTab = 'schema'
      await this.loadSchema()
    },

    // Schema Discovery
    async loadSchema() {
      if (!this.selectedSchemaConnection) {
        console.log('⚠️ No schema connection selected')
        return
      }

      console.log('🔍 Loading schema for connection:', this.selectedSchemaConnection)
      this.schemaLoading = true
      this.selectedTable = null

      try {
        const response = await dataSourceAPI.getCompleteSchema(this.selectedSchemaConnection, this.quickAnalysisMode)
        console.log('📊 Schema response:', response.data)

        if (response.data.success) {
          this.schemaData = response.data.data
          console.log('✅ Schema loaded:', this.schemaData)

          this.$emit('schema-discovered', {
            totalTables: this.schemaData.tables?.length || 0,
            totalColumns: this.schemaData.tables?.reduce((sum, table) => sum + (table.total_columns || 0), 0) || 0
          })
        } else {
          throw new Error(response.data.message)
        }
      } catch (error) {
        console.error('❌ Schema loading error:', error)
        this.$q.notify({
          type: 'negative',
          message: 'Failed to load schema: ' + (error.response?.data?.detail || error.message)
        })
        this.schemaData = {}
      } finally {
        this.schemaLoading = false
      }
    },

    selectTable(table) {
      this.selectedTable = table
    },

    onAnalysisModeChange() {
      // Reload schema if connection is selected and mode changes
      if (this.selectedSchemaConnection) {
        this.loadSchema()
      }
    },

    // Helper methods
    getDbTypeIcon(dbType) {
      const icons = {
        sqlite3: 'storage',
        influxdb: 'timeline',
        parquet: 'folder'
      }
      return icons[dbType] || 'database'
    },

    getDataTypeColor(dataType) {
      const colorMap = {
        'INTEGER': 'blue',
        'TEXT': 'green',
        'REAL': 'orange',
        'BLOB': 'purple',
        'boolean': 'red'
      }
      return colorMap[dataType] || 'grey'
    },

    getCategoryColor(category) {
      const colorMap = {
        'timestamp': 'purple',
        'identifier': 'blue',
        'boolean': 'red',
        'numeric': 'orange',
        'categorical_numeric': 'teal',
        'categorical_text': 'green',
        'text': 'grey',
        'unknown': 'grey-5'
      }
      return colorMap[category] || 'grey'
    }
  }
}
</script>

<style scoped>
.datasource-manager {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.q-tab-panels {
  background: transparent;
}

.q-tab-panel {
  padding: 0;
}

/* Custom styling for the schema table */
:deep(.q-table) {
  background: transparent;
}

:deep(.q-table thead th) {
  background: #f5f5f5;
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .row.q-gutter-md .col-md-4,
  .row.q-gutter-md .col-md-8 {
    width: 100%;
  }
}
</style>
