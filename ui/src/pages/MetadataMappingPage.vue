<!-- pages/MetadataMappingPage.vue -->
<template>
  <q-page class="q-pa-md">
    <!-- Page Header -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card flat bordered class="bg-blue-1">
          <q-card-section>
            <div class="text-h5 text-primary">
              <q-icon name="drag_indicator" class="q-mr-sm" />
              Metadata Mapping
            </div>
            <div class="text-subtitle2 text-grey-7">
              Drag tables to create equipment, drag columns to define filters and signals
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Connection Selector -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center q-gutter-md">
              <div class="col">
                <q-select
                  v-model="selectedConnection"
                  :options="activeConnections"
                  option-label="name"
                  option-value="id"
                  label="Select Data Source Connection"
                  outlined
                  map-options
                  emit-value
                  @update:model-value="loadConnectionSchema"
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
                <q-btn
                  v-if="hasUnsavedChanges"
                  color="primary"
                  icon="save"
                  label="Save All Mappings"
                  @click="saveAllMappings"
                  :loading="saving"
                />
                <q-btn
                  v-if="hasAnyMappings"
                  flat
                  color="grey"
                  icon="clear_all"
                  label="Clear All"
                  @click="clearAllMappings"
                  class="q-ml-sm"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Main Mapping Interface -->
    <div v-if="selectedConnection && schemaData.tables" class="row q-gutter-md">
      <!-- Source Panel -->
      <div class="col-12 col-lg-4">
        <SourcePanel
          :schema-data="schemaData"
          :selected-table="selectedTable"
          @table-selected="onTableSelected"
          @table-drag-start="onTableDragStart"
          @column-drag-start="onColumnDragStart"
        />
      </div>

      <!-- Target Panels -->
      <div class="col-12 col-lg-8">
        <TargetPanel
          :master-model="masterModel"
          :equipment-list="equipmentList"
          :filters-list="filtersList"
          :multi-tab-data="multiTabData"
          :selected-table="selectedTable"
          @equipment-drop="onEquipmentDrop"
          @filter-drop="onFilterDrop"
          @multi-tab-drop="onMultiTabDrop"
          @equipment-edit="onEquipmentEdit"
          @equipment-remove="onEquipmentRemove"
          @filter-remove="onFilterRemove"
          @multi-tab-remove="onMultiTabRemove"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="row q-gutter-md">
      <div class="col-12">
        <q-card class="q-pa-xl text-center">
          <q-icon name="schema" size="64px" color="grey-4" />
          <div class="text-h6 text-grey-6 q-mt-md">No Connection Selected</div>
          <div class="text-body2 text-grey-7 q-mb-md">
            Select a data source connection to start mapping metadata
          </div>
          <q-btn
            color="primary"
            label="Go to Data Sources"
            icon="storage"
            @click="$router.push('/datasources')"
          />
        </q-card>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="row q-gutter-md">
      <div class="col-12">
        <q-card class="q-pa-xl text-center">
          <q-spinner-gears size="64px" color="primary" />
          <div class="text-h6 q-mt-md">Loading Schema...</div>
        </q-card>
      </div>
    </div>

    <!-- Validation Dialog -->
    <q-dialog v-model="showValidationDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6 text-negative">Validation Errors</div>
        </q-card-section>
        <q-card-section>
          <q-list>
            <q-item v-for="error in validationErrors" :key="error">
              <q-item-section avatar>
                <q-icon name="error" color="negative" />
              </q-item-section>
              <q-item-section>{{ error }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="OK" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { dataSourceAPI, metaAPI } from 'src/services/api'
import SourcePanel from 'components/SourcePanel.vue'
import TargetPanel from 'components/TargetPanel.vue'

export default {
  name: 'MetadataMappingPage',
  components: {
    SourcePanel,
    TargetPanel
  },
  data() {
    return {
      loading: false,
      saving: false,
      selectedConnection: null,
      connections: [],
      schemaData: {},
      selectedTable: null,

      // Mapping data
      masterModel: null, // Auto-created from first table
      equipmentList: [], // Array of equipment mapped from tables
      filtersList: [], // Array of filter columns
      multiTabData: {
        signals: [],
        specs: [],
        docs: []
      },

      // Validation
      showValidationDialog: false,
      validationErrors: [],

      // State tracking
      hasUnsavedChanges: false
    }
  },
  computed: {
    activeConnections() {
      return this.connections.filter(conn => conn.status === 'active')
    },

    hasAnyMappings() {
      return this.equipmentList.length > 0 ||
             this.filtersList.length > 0 ||
             Object.values(this.multiTabData).some(arr => arr.length > 0)
    }
  },
  async mounted() {
    await this.loadConnections()
  },
  methods: {
    async loadConnections() {
      this.loading = true
      try {
        const response = await dataSourceAPI.getAllConnections()
        this.connections = response.data
      } catch (error) {
        this.$q.notify({
          type: 'negative',
          message: 'Failed to load connections: ' + error.message
        })
      } finally {
        this.loading = false
      }
    },

    async loadConnectionSchema() {
      if (!this.selectedConnection) return

      this.loading = true
      try {
        const response = await dataSourceAPI.getCompleteSchema(this.selectedConnection, true)
        if (response.data.success) {
          this.schemaData = response.data.data
          this.clearAllMappings()
        } else {
          throw new Error(response.data.message)
        }
      } catch (error) {
        this.$q.notify({
          type: 'negative',
          message: 'Failed to load schema: ' + error.message
        })
      } finally {
        this.loading = false
      }
    },

    onTableSelected(table) {
      this.selectedTable = table
    },

    onTableDragStart(table) {
      console.log('🚀 Table drag started:', table.name)
    },

    onColumnDragStart(column) {
      console.log('🚀 Column drag started:', column.name)
    },

    onEquipmentDrop(table) {
      console.log('📦 Equipment drop:', table)

      // Auto-create master model if not exists
      if (!this.masterModel && table) {
        this.masterModel = {
          name: table.name,
          source_table: table.name,
          enable: 1
        }
        console.log('🏭 Auto-created master model:', this.masterModel)
      }

      // Generate equipment name
      const baseName = table.name.replace('t_', '').replace('_', '-')
      const existingCount = this.equipmentList.filter(eq =>
        eq.source_table === table.name
      ).length
      const equipmentName = `${baseName}-${existingCount + 1}`

      // Add equipment
      const equipment = {
        id: Date.now(), // Temporary ID
        name: equipmentName,
        source_table: table.name,
        model_id: null, // Will be set after master model is saved
        location: '',
        enable: 1,
        isNew: true
      }

      this.equipmentList.push(equipment)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Equipment "${equipmentName}" added`,
        timeout: 2000
      })
    },

    onFilterDrop(column) {
      console.log('🔧 Filter drop:', column)

      // Check if already exists
      const exists = this.filtersList.some(f =>
        f.source_column === column.name && f.source_table === this.selectedTable?.name
      )

      if (exists) {
        this.$q.notify({
          type: 'warning',
          message: `Filter "${column.name}" already exists`
        })
        return
      }

      const filter = {
        id: Date.now(),
        filter_key: column.name,
        filter_value: `{${column.name}}`, // Placeholder for dynamic values
        source_table: this.selectedTable?.name,
        source_column: column.name,
        data_type: column.data_type,
        isNew: true
      }

      this.filtersList.push(filter)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Filter "${column.name}" added`,
        timeout: 2000
      })
    },

    onMultiTabDrop(data) {
      console.log('📊 Multi-tab drop:', data)
      const { column, tabType } = data

      // Check if already exists in any tab
      const allTabData = [...this.multiTabData.signals, ...this.multiTabData.specs, ...this.multiTabData.docs]
      const exists = allTabData.some(item =>
        item.source_column === column.name && item.source_table === this.selectedTable?.name
      )

      if (exists) {
        this.$q.notify({
          type: 'warning',
          message: `Column "${column.name}" already mapped`
        })
        return
      }

      let item
      if (tabType === 'signals') {
        item = {
          id: Date.now(),
          key: column.name,
          value: column.name,
          unit: column.unit || '',
          desc: `Signal from ${column.name}`,
          source_table: this.selectedTable?.name,
          source_column: column.name,
          data_type: column.data_type,
          enable: 1,
          isNew: true
        }
      } else if (tabType === 'specs') {
        item = {
          id: Date.now(),
          key: column.name,
          value: '',
          desc: `Specification for ${column.name}`,
          unit: column.unit || '',
          source_table: this.selectedTable?.name,
          source_column: column.name,
          enable: 1,
          isNew: true
        }
      } else if (tabType === 'docs') {
        item = {
          id: Date.now(),
          path: '',
          desc: `Documentation for ${column.name}`,
          source_table: this.selectedTable?.name,
          source_column: column.name,
          isNew: true
        }
      }

      this.multiTabData[tabType].push(item)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `${tabType.charAt(0).toUpperCase() + tabType.slice(1)} "${column.name}" added`,
        timeout: 2000
      })
    },

    onEquipmentEdit(equipment, newName) {
      const index = this.equipmentList.findIndex(eq => eq.id === equipment.id)
      if (index !== -1) {
        this.equipmentList[index].name = newName
        this.hasUnsavedChanges = true
      }
    },

    onEquipmentRemove(equipment) {
      const index = this.equipmentList.findIndex(eq => eq.id === equipment.id)
      if (index !== -1) {
        this.equipmentList.splice(index, 1)
        this.hasUnsavedChanges = true
      }
    },

    onFilterRemove(filter) {
      const index = this.filtersList.findIndex(f => f.id === filter.id)
      if (index !== -1) {
        this.filtersList.splice(index, 1)
        this.hasUnsavedChanges = true
      }
    },

    onMultiTabRemove(data) {
      const { item, tabType } = data
      const index = this.multiTabData[tabType].findIndex(i => i.id === item.id)
      if (index !== -1) {
        this.multiTabData[tabType].splice(index, 1)
        this.hasUnsavedChanges = true
      }
    },

    validateMappings() {
      const errors = []

      if (!this.masterModel) {
        errors.push('Master Model is required')
      }

      if (this.equipmentList.length === 0) {
        errors.push('At least one Equipment must be defined')
      }

      // Validate equipment names are unique
      const equipmentNames = this.equipmentList.map(eq => eq.name)
      const duplicateNames = equipmentNames.filter((name, index) =>
        equipmentNames.indexOf(name) !== index
      )
      if (duplicateNames.length > 0) {
        errors.push(`Duplicate equipment names: ${duplicateNames.join(', ')}`)
      }

      return errors
    },

    async saveAllMappings() {
      // Validate before saving
      this.validationErrors = this.validateMappings()
      if (this.validationErrors.length > 0) {
        this.showValidationDialog = true
        return
      }

      this.saving = true
      try {
        // Save master model first
        let masterModelResponse
        if (this.masterModel) {
          masterModelResponse = await metaAPI.createMasterModel(this.masterModel)
          console.log('✅ Master model saved:', masterModelResponse.data)
        }

        // Save equipment
        for (const equipment of this.equipmentList) {
          if (equipment.isNew) {
            const equipmentData = {
              ...equipment,
              model_id: masterModelResponse.data.model_id
            }
            delete equipmentData.id
            delete equipmentData.isNew
            delete equipmentData.source_table

            const response = await metaAPI.createEquipment(equipmentData)
            console.log('✅ Equipment saved:', response.data)

            // Save filters for this equipment
            const equipmentFilters = this.filtersList.filter(f => f.source_table === equipment.source_table)
            for (const filter of equipmentFilters) {
              if (filter.isNew) {
                const filterData = {
                  eqp_id: response.data.id,
                  filter_key: filter.filter_key,
                  filter_value: filter.filter_value
                }
                await metaAPI.createFilter(filterData)
                console.log('✅ Filter saved:', filterData)
              }
            }

            // Save multi-tab data for this equipment
            const allMultiTabItems = [
              ...this.multiTabData.signals.map(s => ({...s, type: 'signal'})),
              ...this.multiTabData.specs.map(s => ({...s, type: 'spec'})),
              ...this.multiTabData.docs.map(d => ({...d, type: 'doc'}))
            ]

            for (const item of allMultiTabItems) {
              if (item.isNew && item.source_table === equipment.source_table) {
                const itemData = { ...item, eqp_id: response.data.id }
                delete itemData.id
                delete itemData.isNew
                delete itemData.source_table
                delete itemData.source_column
                delete itemData.type

                if (item.type === 'signal') {
                  await metaAPI.createSignal(itemData)
                } else if (item.type === 'spec') {
                  await metaAPI.createSpec(itemData)
                } else if (item.type === 'doc') {
                  await metaAPI.createDoc(itemData)
                }
                console.log('✅ Multi-tab item saved:', item.type, itemData)
              }
            }
          }
        }

        this.hasUnsavedChanges = false

        this.$q.notify({
          type: 'positive',
          message: 'All mappings saved successfully!',
          timeout: 3000
        })

      } catch (error) {
        console.error('❌ Save error:', error)
        this.$q.notify({
          type: 'negative',
          message: 'Failed to save mappings: ' + (error.response?.data?.detail || error.message)
        })
      } finally {
        this.saving = false
      }
    },

    clearAllMappings() {
      this.masterModel = null
      this.equipmentList = []
      this.filtersList = []
      this.multiTabData = {
        signals: [],
        specs: [],
        docs: []
      }
      this.selectedTable = null
      this.hasUnsavedChanges = false
    },

    getDbTypeIcon(dbType) {
      const icons = {
        sqlite3: 'storage',
        influxdb: 'timeline',
        parquet: 'folder'
      }
      return icons[dbType] || 'database'
    }
  }
}
</script>

<style scoped>
.q-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
