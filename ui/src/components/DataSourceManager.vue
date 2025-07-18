<!-- components/DataSourceManager.vue - Fixed for InfluxDB Schema Display -->
<template>
  <div class="datasource-manager">
    <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify">
      <q-tab name="connections" label="Connections" icon="link" />
      <q-tab name="schema" label="Schema Discovery" icon="schema" />
    </q-tabs>

    <q-tab-panels v-model="activeTab" animated>
      <!-- Connections Tab -->
      <q-tab-panel name="connections">
        <div class="row q-gutter-md">
          <!-- Connection Form -->
          <div class="col-12 col-md-6">
            <q-card>
              <q-card-section>
                <div class="text-h6">{{ editMode ? 'Edit' : 'Add' }} Connection</div>
              </q-card-section>
              <q-separator />
              <q-card-section>
                <ConnectionForm
                  ref="connectionForm"
                  :edit-mode="editMode"
                  :initial-connection="selectedConnection"
                  @connection-saved="handleConnectionSaved"
                  @connection-tested="handleTestConnection"
                  @cancel-edit="handleCancelEdit"
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Connection List -->
          <div class="col-12 col-md-6">
            <q-card>
              <q-card-section>
                <div class="text-h6">Existing Connections</div>
                <div class="text-caption text-grey-7">{{ connections.length }} total connections</div>
              </q-card-section>
              <q-separator />
              <q-card-section class="q-pa-none">
                <ConnectionList
                  :connections="connections"
                  :loading="connectionsLoading"
                  @edit-connection="handleEditConnection"
                  @delete-connection="handleDeleteConnection"
                  @test-connection="handleTestExistingConnection"
                  @discover-schema="handleDiscoverSchema"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Schema Discovery Tab -->
      <q-tab-panel name="schema">
        <div class="row q-gutter-md">
          <!-- Connection Selector -->
          <div class="col-12">
            <q-card>
              <q-card-section>
                <div class="row items-center q-gutter-md">
                  <div class="col">
                    <q-select
                      v-model="selectedSchemaConnection"
                      :options="activeConnections"
                      option-label="name"
                      option-value="id"
                      label="Select Connection for Schema Discovery"
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
              </q-card-section>
            </q-card>
          </div>

          <!-- Schema Display -->
          <div class="col-12" v-if="selectedSchemaConnection">
            <div class="row q-gutter-md">
              <!-- Tables/Measurements List -->
              <div class="col-12 col-md-4">
                <q-card>
                  <q-card-section>
                    <div class="text-h6">{{ getSchemaListTitle() }}</div>
                    <div class="text-caption text-grey-7">{{ getSchemaListCount() }}</div>
                  </q-card-section>
                  <q-separator />
                  <q-card-section class="q-pa-none">
                    <q-list bordered separator v-if="hasSchemaItems()">
                      <!-- SQLite/Parquet Tables -->
                      <q-item
                        v-for="table in schemaData.tables || []"
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

                      <!-- InfluxDB Measurements -->
                      <q-item
                        v-for="measurement in schemaData.measurements || []"
                        :key="measurement.name"
                        clickable
                        v-ripple
                        :active="selectedTable?.name === measurement.name"
                        @click="selectTable(measurement)"
                      >
                        <q-item-section avatar>
                          <q-icon name="timeline" color="orange" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ measurement.name }}</q-item-label>
                          <q-item-label caption>
                            {{ measurement.field_count || 0 }} fields • {{ measurement.tag_count || 0 }} tags
                            <span v-if="measurement.sample_count" class="q-ml-sm">
                              • {{ formatSampleCount(measurement.sample_count) }} samples
                            </span>
                          </q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <div class="column q-gutter-xs">
                            <q-chip size="xs" color="green" text-color="white">
                              {{ measurement.field_count || 0 }}F
                            </q-chip>
                            <q-chip size="xs" color="orange" text-color="white">
                              {{ measurement.tag_count || 0 }}T
                            </q-chip>
                          </div>
                        </q-item-section>
                      </q-item>
                    </q-list>
                    <div v-else-if="schemaLoading" class="q-pa-md text-center">
                      <q-spinner-dots size="40px" color="primary" />
                      <div class="q-mt-sm">Loading schema...</div>
                    </div>
                    <div v-else-if="selectedSchemaConnection && !schemaLoading" class="q-pa-md text-center text-grey-7">
                      <q-icon name="warning" size="32px" class="q-mb-sm" />
                      <div>No {{ getSchemaItemType() }} found or failed to load schema</div>
                      <q-btn flat color="primary" @click="loadSchema" class="q-mt-sm">
                        Retry
                      </q-btn>
                    </div>
                    <div v-else class="q-pa-md text-center text-grey-7">
                      Select a connection to view {{ getSchemaItemType() }}
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Columns/Fields List -->
              <div class="col-12 col-md-8">
                <q-card>
                  <q-card-section>
                    <div class="text-h6">
                      {{ getDetailsTitle() }}
                      <span v-if="selectedTable" class="text-caption">
                        - {{ selectedTable.name }}
                      </span>
                    </div>
                    <div class="text-caption text-grey-7" v-if="selectedTable">
                      {{ getDetailsCount() }} • Click item for details
                    </div>
                  </q-card-section>
                  <q-separator />
                  <q-card-section class="q-pa-none">
                    <!-- SQLite/Parquet Columns -->
                    <q-table
                      v-if="selectedTable?.columns && !isInfluxDB()"
                      :rows="selectedTable.columns"
                      :columns="columnTableColumns"
                      row-key="name"
                      flat
                      :pagination="{ rowsPerPage: 0 }"
                      hide-pagination
                    >
                      <template v-slot:body-cell-data_type="props">
                        <q-td :props="props">
                          <q-chip
                            size="sm"
                            :color="getDataTypeColor(props.value)"
                            text-color="white"
                            dense
                          >
                            {{ props.value }}
                          </q-chip>
                        </q-td>
                      </template>
                      <template v-slot:body-cell-category="props">
                        <q-td :props="props">
                          <q-chip
                            size="sm"
                            :color="getCategoryColor(props.value)"
                            text-color="white"
                            dense
                          >
                            {{ props.value }}
                          </q-chip>
                        </q-td>
                      </template>
                    </q-table>

                    <!-- InfluxDB Fields and Tags -->
                    <div v-else-if="selectedTable?.fields && isInfluxDB()" class="q-pa-md">
                      <div class="row q-gutter-md">
                        <!-- Fields (Numeric Data) -->
                        <div class="col-12" v-if="getFields().length > 0">
                          <div class="text-subtitle1 text-green-8 q-mb-md">
                            <q-icon name="functions" class="q-mr-sm" />
                            Fields ({{ getFields().length }})
                          </div>
                          <q-list bordered separator>
                            <q-item v-for="field in getFields()" :key="`field-${field.name}`">
                              <q-item-section avatar>
                                <q-icon name="functions" color="green" />
                              </q-item-section>
                              <q-item-section>
                                <q-item-label>{{ field.name }}</q-item-label>
                                <q-item-label caption>{{ field.type || 'number' }} • Used for numeric time-series data</q-item-label>
                              </q-item-section>
                              <q-item-section side>
                                <q-chip size="sm" color="green" text-color="white" dense>
                                  field
                                </q-chip>
                              </q-item-section>
                            </q-item>
                          </q-list>
                        </div>

                        <!-- Tags (Labels for Filtering) -->
                        <div class="col-12" v-if="getTags().length > 0">
                          <div class="text-subtitle1 text-orange-8 q-mb-md">
                            <q-icon name="label" class="q-mr-sm" />
                            Tags ({{ getTags().length }})
                          </div>
                          <q-list bordered separator>
                            <q-item v-for="tag in getTags()" :key="`tag-${tag.name}`">
                              <q-item-section avatar>
                                <q-icon name="label" color="orange" />
                              </q-item-section>
                              <q-item-section>
                                <q-item-label>{{ tag.name }}</q-item-label>
                                <q-item-label caption>string • Used for filtering and grouping data</q-item-label>
                              </q-item-section>
                              <q-item-section side>
                                <q-chip size="sm" color="orange" text-color="white" dense>
                                  tag
                                </q-chip>
                              </q-item-section>
                            </q-item>
                          </q-list>
                        </div>

                        <!-- Timestamp -->
                        <div class="col-12">
                          <div class="text-subtitle1 text-blue-8 q-mb-md">
                            <q-icon name="schedule" class="q-mr-sm" />
                            Timestamp
                          </div>
                          <q-list bordered>
                            <q-item>
                              <q-item-section avatar>
                                <q-icon name="schedule" color="blue" />
                              </q-item-section>
                              <q-item-section>
                                <q-item-label>_time</q-item-label>
                                <q-item-label caption>timestamp • Time dimension for time-series data</q-item-label>
                              </q-item-section>
                              <q-item-section side>
                                <q-chip size="sm" color="blue" text-color="white" dense>
                                  timestamp
                                </q-chip>
                              </q-item-section>
                            </q-item>
                          </q-list>
                        </div>
                      </div>
                    </div>

                    <!-- Empty State -->
                    <div v-else-if="selectedTable && !schemaLoading" class="q-pa-xl text-center text-grey-7">
                      <q-icon name="info" size="48px" class="q-mb-md" />
                      <div class="text-h6">No Details Available</div>
                      <div class="text-body2">
                        Unable to load {{ isInfluxDB() ? 'fields and tags' : 'columns' }} for this {{ getSchemaItemType() }}
                      </div>
                    </div>

                    <!-- No Selection State -->
                    <div v-else-if="!selectedTable && !schemaLoading" class="q-pa-xl text-center text-grey-7">
                      <q-icon name="arrow_back" size="48px" class="q-mb-md" />
                      <div class="text-h6">Select {{ getSchemaItemType() }}</div>
                      <div class="text-body2">
                        Choose a {{ getSchemaItemType() }} from the list to view its {{ isInfluxDB() ? 'fields and tags' : 'columns' }}
                      </div>
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
    },

    selectedConnectionInfo() {
      if (!this.selectedSchemaConnection) return null
      return this.connections.find(conn => conn.id === this.selectedSchemaConnection)
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

    async handleConnectionSaved(connection) {
      try {
        await this.loadConnections()
        this.editMode = false
        this.selectedConnection = null

        this.$emit(this.editMode ? 'connection-updated' : 'connection-created', connection)
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

          // Emit schema discovered event with corrected data structure
          const totalItems = this.isInfluxDB()
            ? this.schemaData.measurements?.length || 0
            : this.schemaData.tables?.length || 0

          const totalDetails = this.isInfluxDB()
            ? this.schemaData.measurements?.reduce((sum, m) => sum + (m.field_count || 0) + (m.tag_count || 0), 0) || 0
            : this.schemaData.tables?.reduce((sum, table) => sum + (table.total_columns || 0), 0) || 0

          this.$emit('schema-discovered', {
            totalTables: totalItems,
            totalColumns: totalDetails
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

    // Schema Display Helpers
    isInfluxDB() {
      return this.selectedConnectionInfo?.db_type === 'influxdb'
    },

    hasSchemaItems() {
      if (this.isInfluxDB()) {
        return this.schemaData.measurements && this.schemaData.measurements.length > 0
      } else {
        return this.schemaData.tables && this.schemaData.tables.length > 0
      }
    },

    getSchemaListTitle() {
      if (this.isInfluxDB()) {
        return 'Measurements'
      } else if (this.selectedConnectionInfo?.db_type === 'parquet') {
        return 'Equipment Groups'
      } else {
        return 'Tables'
      }
    },

    getSchemaListCount() {
      if (this.isInfluxDB()) {
        return `${this.schemaData.measurements?.length || 0} measurements found`
      } else {
        return `${this.schemaData.tables?.length || 0} tables found`
      }
    },

    getSchemaItemType() {
      if (this.isInfluxDB()) {
        return 'measurements'
      } else if (this.selectedConnectionInfo?.db_type === 'parquet') {
        return 'equipment groups'
      } else {
        return 'tables'
      }
    },

    getDetailsTitle() {
      if (this.isInfluxDB()) {
        return 'Fields & Tags'
      } else {
        return 'Columns'
      }
    },

    getDetailsCount() {
      if (this.isInfluxDB() && this.selectedTable?.fields) {
        const fields = this.getFields().length
        const tags = this.getTags().length
        return `${fields} fields, ${tags} tags`
      } else if (this.selectedTable?.columns) {
        return `${this.selectedTable.columns.length} columns`
      }
      return '0 items'
    },

    // InfluxDB specific methods
    getFields() {
      if (!this.selectedTable?.fields) return []
      return this.selectedTable.fields.filter(f => f.category === 'field')
    },

    getTags() {
      if (!this.selectedTable?.fields) return []
      return this.selectedTable.fields.filter(f => f.category === 'tag')
    },

    formatSampleCount(count) {
      if (typeof count === 'number') {
        if (count >= 1000000) {
          return (count / 1000000).toFixed(1) + 'M'
        } else if (count >= 1000) {
          return (count / 1000).toFixed(1) + 'K'
        }
        return count.toString()
      }
      return count || '0'
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
