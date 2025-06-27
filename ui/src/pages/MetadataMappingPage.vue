<!-- pages/MetadataMappingPage.vue - COMPLETE VERSION 3 WITH SIGNAL VALUE ENHANCEMENT -->
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
              Drag tables to create equipment, drag columns or add manual entries for filters, signals, specs, and docs
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
    <div v-if="selectedConnection && schemaData.tables" class="q-gutter-md">
      <!-- Source Panel -->
       <div class="row ">
        <div class="col-6 col-lg-4 q-pa-xs ">
        <SourcePanel
          :schema-data="schemaData"
          :selected-table="selectedTable"
          @table-selected="onTableSelected"
          @table-drag-start="onTableDragStart"
          @column-drag-start="onColumnDragStart"
        />
      </div>

      <!-- Target Panels with enhanced signal handling -->
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
          @filter-edit="onFilterEdit"
          @filter-remove="onFilterRemove"
          @manual-filter-add="onManualFilterAdd"
          @manual-spec-add="onManualSpecAdd"
          @manual-doc-add="onManualDocAdd"
          @spec-edit="onSpecEdit"
          @doc-edit="onDocEdit"
          @multi-tab-remove="onMultiTabRemove"
        />
      </div>
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
      masterModel: null,
      equipmentList: [],
      filtersList: [],
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

      // Add equipment with location field
      const equipment = {
        id: Date.now(),
        name: equipmentName,
        source_table: table.name,
        model_id: null,
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

    onFilterDrop(data) {
      console.log('🔧 Filter drop:', data)

      const filterKey = data.filter_key || data.name
      const filterValue = data.filter_value || ''
      const equipmentId = data.eqp_id
      const sourceTable = data.source_table || this.selectedTable?.name
      const sourceColumn = data.source_column || data.name

      const existingFilter = this.filtersList.find(f =>
        f.filter_key === filterKey &&
        f.eqp_id === equipmentId &&
        f.source_table === sourceTable
      )

      if (existingFilter) {
        this.$q.notify({
          type: 'warning',
          message: `Filter "${filterKey}" already exists for this equipment`
        })
        return
      }

      const filter = {
        id: Date.now(),
        filter_key: filterKey,
        filter_value: filterValue,
        eqp_id: equipmentId,
        source_table: sourceTable,
        source_column: sourceColumn,
        data_type: data.data_type || 'text',
        isNew: true,
        isManual: data.isManual || false
      }

      this.filtersList.push(filter)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Filter "${filterKey}" added`,
        timeout: 2000
      })
    },

    onFilterEdit(filter, updatedData) {
      const index = this.filtersList.findIndex(f => f.id === filter.id)
      if (index !== -1) {
        this.filtersList[index] = { ...this.filtersList[index], ...updatedData }
        this.hasUnsavedChanges = true

        this.$q.notify({
          type: 'positive',
          message: `Filter "${filter.filter_key}" updated`,
          timeout: 2000
        })
      }
    },

    // Manual Filter Add Handler
    onManualFilterAdd(filterData) {
      console.log('🎯 Received manual-filter-add event:', filterData)

      // Validation
      if (!filterData.filter_key || !filterData.filter_value || !filterData.eqp_id) {
        this.$q.notify({
          type: 'negative',
          message: 'All filter fields are required'
        })
        return
      }

      // Check if manual filter with same key and equipment exists
      const exists = this.filtersList.some(f =>
        f.filter_key === filterData.filter_key &&
        f.eqp_id === filterData.eqp_id &&
        f.isManual
      )

      if (exists) {
        this.$q.notify({
          type: 'warning',
          message: `Manual filter "${filterData.filter_key}" already exists for this equipment`
        })
        return
      }

      const filter = {
        id: Date.now(),
        filter_key: filterData.filter_key,
        filter_value: filterData.filter_value,
        eqp_id: filterData.eqp_id,
        source_table: null,
        source_column: null,
        data_type: 'manual',
        isNew: true,
        isManual: true
      }

      this.filtersList.push(filter)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Manual filter "${filterData.filter_key}" added successfully!`,
        timeout: 3000
      })
    },

    // Manual Specification Add Handler
    onManualSpecAdd(specData) {
      console.log('🎯 Received manual-spec-add event:', specData)

      // Validation
      if (!specData.key || !specData.value || !specData.desc || !specData.eqp_id) {
        this.$q.notify({
          type: 'negative',
          message: 'Key, value, description, and equipment are required'
        })
        return
      }

      // Check if manual spec with same key and equipment exists
      const exists = this.multiTabData.specs.some(s =>
        s.key === specData.key &&
        s.eqp_id === specData.eqp_id &&
        s.isManual
      )

      if (exists) {
        this.$q.notify({
          type: 'warning',
          message: `Manual specification "${specData.key}" already exists for this equipment`
        })
        return
      }

      const spec = {
        id: Date.now(),
        key: specData.key,
        value: specData.value,
        desc: specData.desc,
        unit: specData.unit || '',
        eqp_id: specData.eqp_id,
        source_table: null, // Manual entry
        source_column: null,
        enable: 1,
        isNew: true,
        isManual: true
      }

      this.multiTabData.specs.push(spec)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Manual specification "${specData.key}" added successfully!`,
        timeout: 3000
      })

      console.log('✅ Manual specification added:', spec)
    },

    // Manual Document Add Handler
    onManualDocAdd(docData) {
      console.log('🎯 Received manual-doc-add event:', docData)

      // Validation
      if (!docData.path || !docData.desc || !docData.eqp_id) {
        this.$q.notify({
          type: 'negative',
          message: 'Path, description, and equipment are required'
        })
        return
      }

      // Check if manual doc with same path and equipment exists
      const exists = this.multiTabData.docs.some(d =>
        d.path === docData.path &&
        d.eqp_id === docData.eqp_id &&
        d.isManual
      )

      if (exists) {
        this.$q.notify({
          type: 'warning',
          message: `Manual document with path "${docData.path}" already exists for this equipment`
        })
        return
      }

      const doc = {
        id: Date.now(),
        path: docData.path,
        desc: docData.desc,
        eqp_id: docData.eqp_id,
        source_table: null, // Manual entry
        source_column: null,
        isNew: true,
        isManual: true
      }

      this.multiTabData.docs.push(doc)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `Manual document "${docData.desc}" added successfully!`,
        timeout: 3000
      })

      console.log('✅ Manual document added:', doc)
    },

    // Specification Edit Handler
    onSpecEdit(spec, updatedData) {
      console.log('🔧 Editing specification:', spec, updatedData)

      const index = this.multiTabData.specs.findIndex(s => s.id === spec.id)
      if (index !== -1) {
        this.multiTabData.specs[index] = { ...this.multiTabData.specs[index], ...updatedData }
        this.hasUnsavedChanges = true

        this.$q.notify({
          type: 'positive',
          message: `Specification "${spec.key}" updated`,
          timeout: 2000
        })
      }
    },

    // Document Edit Handler
    onDocEdit(doc, updatedData) {
      console.log('🔧 Editing document:', doc, updatedData)

      const index = this.multiTabData.docs.findIndex(d => d.id === doc.id)
      if (index !== -1) {
        this.multiTabData.docs[index] = { ...this.multiTabData.docs[index], ...updatedData }
        this.hasUnsavedChanges = true

        this.$q.notify({
          type: 'positive',
          message: `Document "${doc.desc}" updated`,
          timeout: 2000
        })
      }
    },

    // ENHANCED: Multi-Tab Drop Handler with Signal Value Support
    onMultiTabDrop(data) {
      console.log('📊 [ENHANCED] Multi-tab drop:', data)
      const { column, tabType } = data

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
        // ENHANCED: Signal creation with value field support
        console.log('📊 [ENHANCED] Creating signal with value:', column.value)
        console.log('📊 [ENHANCED] Creating signal with unit:', column.unit)

        item = {
          id: Date.now(),
          key: column.name,
          value: column.value || column.name, // FIXED: Always ensure value defaults to signal name
          unit: column.unit || '',
          desc: `Signal from ${column.name}`,
          source_table: this.selectedTable?.name,
          source_column: column.name,
          data_type: column.data_type,
          enable: 1,
          isNew: true,
          isManual: false // Dragged from column
        }

        console.log('📊 [ENHANCED] Created signal item:', item)
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
          isNew: true,
          isManual: false // Dragged from column
        }
      } else if (tabType === 'docs') {
        item = {
          id: Date.now(),
          path: '',
          desc: `Documentation for ${column.name}`,
          source_table: this.selectedTable?.name,
          source_column: column.name,
          isNew: true,
          isManual: false // Dragged from column
        }
      }

      this.multiTabData[tabType].push(item)
      this.hasUnsavedChanges = true

      this.$q.notify({
        type: 'positive',
        message: `${tabType.charAt(0).toUpperCase() + tabType.slice(1)} "${column.name}" added${tabType === 'signals' ? ` with value "${item.value}"` : ''}`,
        timeout: 3000
      })
    },

    onEquipmentEdit(equipment, updatedData) {
      const index = this.equipmentList.findIndex(eq => eq.id === equipment.id)
      if (index !== -1) {
        if (typeof updatedData === 'string') {
          this.equipmentList[index].name = updatedData
        } else {
          this.equipmentList[index].name = updatedData.name
          this.equipmentList[index].location = updatedData.location
        }
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

      const equipmentNames = this.equipmentList.map(eq => eq.name)
      const duplicateNames = equipmentNames.filter((name, index) =>
        equipmentNames.indexOf(name) !== index
      )
      if (duplicateNames.length > 0) {
        errors.push(`Duplicate equipment names: ${duplicateNames.join(', ')}`)
      }

      const invalidFilters = this.filtersList.filter(f => !f.filter_value || !f.eqp_id)
      if (invalidFilters.length > 0) {
        const filterNames = invalidFilters.map(f => f.filter_key).join(', ')
        errors.push(`Filters missing values or equipment assignment: ${filterNames}`)
      }

      const filterWithInvalidEquipment = this.filtersList.filter(f =>
        f.eqp_id && !this.equipmentList.some(eq => eq.id === f.eqp_id)
      )
      if (filterWithInvalidEquipment.length > 0) {
        const filterNames = filterWithInvalidEquipment.map(f => f.filter_key).join(', ')
        errors.push(`Filters linked to non-existent equipment: ${filterNames}`)
      }

      // Validate manual specifications
      const invalidSpecs = this.multiTabData.specs.filter(s =>
        s.isManual && (!s.key || !s.value || !s.desc || !s.eqp_id)
      )
      if (invalidSpecs.length > 0) {
        errors.push(`Some manual specifications are missing required fields`)
      }

      // Validate manual documents
      const invalidDocs = this.multiTabData.docs.filter(d =>
        d.isManual && (!d.path || !d.desc || !d.eqp_id)
      )
      if (invalidDocs.length > 0) {
        errors.push(`Some manual documents are missing required fields`)
      }

      // REMOVED: Signal value validation since it's now optional
      // const invalidSignals = this.multiTabData.signals.filter(s => !s.value)
      // if (invalidSignals.length > 0) {
      //   errors.push(`Some signals are missing required value field`)
      // }

      return errors
    },

    async saveAllMappings() {
      this.validationErrors = this.validateMappings()
      if (this.validationErrors.length > 0) {
        this.showValidationDialog = true
        return
      }

      this.saving = true
      try {
        let masterModelResponse
        if (this.masterModel) {
          masterModelResponse = await metaAPI.createMasterModel(this.masterModel)
          console.log('✅ Master model saved:', masterModelResponse.data)
        }

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
            const equipmentFilters = this.filtersList.filter(f => f.eqp_id === equipment.id)
            for (const filter of equipmentFilters) {
              if (filter.isNew) {
                const filterData = {
                  eqp_id: response.data.id,
                  filter_key: filter.filter_key,
                  filter_value: filter.filter_value
                }

                console.log('💾 Saving filter:', filterData)
                const filterResponse = await metaAPI.createFilter(filterData)
                console.log('✅ Filter saved successfully:', filterResponse.data)
              }
            }

            // Save specifications for this equipment
            const equipmentSpecs = this.multiTabData.specs.filter(s =>
              s.eqp_id === equipment.id || (!s.eqp_id && s.source_table === equipment.source_table)
            )
            for (const spec of equipmentSpecs) {
              if (spec.isNew) {
                const specData = {
                  eqp_id: response.data.id, // Use actual saved equipment ID
                  key: spec.key,
                  value: spec.value,
                  desc: spec.desc,
                  unit: spec.unit,
                  enable: spec.enable
                }

                console.log('📋 Saving specification:', specData)
                const specResponse = await metaAPI.createSpec(specData)
                console.log('✅ Specification saved successfully:', specResponse.data)
              }
            }

            // ENHANCED: Save signals with value field for this equipment
            const equipmentSignals = this.multiTabData.signals.filter(s =>
              s.eqp_id === equipment.id || (!s.eqp_id && s.source_table === equipment.source_table)
            )
            for (const signal of equipmentSignals) {
              if (signal.isNew) {
                const signalData = {
                  eqp_id: response.data.id, // Use actual saved equipment ID
                  key: signal.key,
                  value: signal.value, // ENHANCED: Include value field
                  unit: signal.unit,
                  desc: signal.desc,
                  enable: signal.enable
                }

                console.log('📊 [ENHANCED] Saving signal with value:', signalData)
                const signalResponse = await metaAPI.createSignal(signalData)
                console.log('✅ Signal saved successfully:', signalResponse.data)
              }
            }

            // Save documents for this equipment
            const equipmentDocs = this.multiTabData.docs.filter(d =>
              d.eqp_id === equipment.id || (!d.eqp_id && d.source_table === equipment.source_table)
            )
            for (const doc of equipmentDocs) {
              if (doc.isNew) {
                const docData = {
                  eqp_id: response.data.id, // Use actual saved equipment ID
                  path: doc.path,
                  desc: doc.desc
                }

                console.log('📄 Saving document:', docData)
                const docResponse = await metaAPI.createDoc(docData)
                console.log('✅ Document saved successfully:', docResponse.data)
              }
            }
          }
        }

        this.hasUnsavedChanges = false

        this.$q.notify({
          type: 'positive',
          message: `All mappings saved successfully! Signals use default values when not specified.`,
          timeout: 4000
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

/* Enhanced visual feedback for active areas */
.q-card:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
}

/* Responsive design adjustments */
@media (max-width: 768px) {
  .q-pa-md {
    padding: 8px;
  }

  .row.q-gutter-md > * {
    margin: 8px 0;
  }

  .col-lg-4,
  .col-lg-8 {
    width: 100%;
  }
}

/* Loading animations */
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.q-spinner-gears {
  animation: pulse 2s ease-in-out infinite;
}

/* Status indicators */
.text-primary {
  color: #1976d2 !important;
}

.text-positive {
  color: #21ba45 !important;
}

.text-negative {
  color: #c10015 !important;
}

/* Enhanced button styles */
.q-btn {
  border-radius: 8px;
  font-weight: 500;
}

.q-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

/* Card section enhancements */
.q-card-section {
  transition: background-color 0.2s ease;
}

/* Enhanced dialog styles */
.q-dialog .q-card {
  border-radius: 16px;
  overflow: hidden;
}

/* Notification enhancements */
.q-notification {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Empty state styling */
.q-icon[color="grey-4"] {
  opacity: 0.6;
}

/* Header gradient */
.bg-blue-1 {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #90caf9;
}

/* Connection selector card */
.q-select {
  border-radius: 8px;
}

/* Enhanced spacing */
.q-gutter-md > * + * {
  margin-left: 16px !important;
}

@media (max-width: 600px) {
  .q-gutter-md > * + * {
    margin-left: 0 !important;
    margin-top: 16px !important;
  }
}

/* Validation dialog styling */
.text-h6.text-negative {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-h6.text-negative::before {
  content: "⚠️";
  font-size: 1.2em;
}

/* Loading state enhancements */
.q-spinner-gears {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

/* Success state styling */
.text-positive {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Equipment list enhancements */
.q-chip {
  font-weight: 600;
  border-radius: 6px;
}

/* Tab content spacing */
.q-tab-panels {
  min-height: 400px;
}

/* Enhanced transitions */
* {
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

/* Focus states */
.q-field--focused .q-field__control {
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

/* Hover states for interactive elements */
.q-item:hover {
  background-color: rgba(25, 118, 210, 0.04);
}

/* Enhanced scrollbar for better UX */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Firefox scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}
</style>
