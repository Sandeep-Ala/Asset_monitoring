<!-- components/TargetPanel.vue -->
<template>
  <div class="target-panel">
    <!-- Master Model Display -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card class="master-model-card">
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="precision_manufacturing" class="q-mr-sm" />
              Master Model
              <q-chip
                v-if="masterModel"
                size="sm"
                color="green"
                text-color="white"
                class="q-ml-sm"
              >
                Auto-created
              </q-chip>
            </div>
            <div class="text-caption text-grey-7">
              Auto-created from first table drag
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div v-if="masterModel" class="row items-center">
              <q-icon name="factory" color="primary" size="md" class="q-mr-md" />
              <div>
                <div class="text-h6">{{ masterModel.name }}</div>
                <div class="text-caption text-grey-7">
                  Source: {{ masterModel.source_table }}
                </div>
              </div>
            </div>
            <div v-else class="text-center text-grey-6 q-py-md">
              <q-icon name="info" size="md" class="q-mb-sm" />
              <div>Master Model will be auto-created when you drag a table to Equipment</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Equipment and Filters Row -->
    <div class="row q-gutter-md q-mb-md">
      <!-- Equipment Zone -->
      <div class="col-12 col-md-6">
        <q-card class="drop-zone-card">
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="precision_manufacturing" class="q-mr-sm" />
              Equipment
              <q-chip size="sm" color="blue" text-color="white" class="q-ml-sm">
                {{ equipmentList.length }}
              </q-chip>
            </div>
            <div class="text-caption text-grey-7">
              Drag tables here to create equipment
            </div>
          </q-card-section>

          <q-separator />

          <!-- Drop Zone -->
          <div
            class="equipment-drop-zone"
            :class="{ 'drag-over': equipmentDragOver }"
            @dragover.prevent="equipmentDragOver = true"
            @dragleave="equipmentDragOver = false"
            @drop="handleEquipmentDrop"
          >
            <!-- Equipment List -->
            <div v-if="equipmentList.length" class="q-pa-md">
              <q-list separator>
                <q-item
                  v-for="equipment in equipmentList"
                  :key="equipment.id"
                  class="equipment-item"
                >
                  <q-item-section avatar>
                    <q-icon name="settings" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ equipment.name }}</q-item-label>
                    <q-item-label caption>
                      From: {{ equipment.source_table }}
                      <span v-if="equipment.location"> • Location: {{ equipment.location }}</span>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="row q-gutter-xs">
                      <q-btn
                        round
                        flat
                        size="sm"
                        icon="edit"
                        color="primary"
                        @click="editEquipment(equipment)"
                      >
                        <q-tooltip>Edit equipment</q-tooltip>
                      </q-btn>
                      <q-btn
                        round
                        flat
                        size="sm"
                        icon="delete"
                        color="negative"
                        @click="removeEquipment(equipment)"
                      >
                        <q-tooltip>Remove</q-tooltip>
                      </q-btn>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Empty Drop Zone -->
            <div v-else class="empty-drop-zone q-pa-xl text-center">
              <q-icon name="add_circle_outline" size="48px" color="grey-4" />
              <div class="text-h6 text-grey-6 q-mt-md">Drop Tables Here</div>
              <div class="text-body2 text-grey-7">
                Drag tables from the left panel to create equipment
              </div>
            </div>
          </div>
        </q-card>
      </div>

      <!-- Filters Zone -->
      <div class="col-12 col-md-6">
        <q-card class="drop-zone-card">
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="filter_list" class="q-mr-sm" />
              Filters
              <q-chip size="sm" color="orange" text-color="white" class="q-ml-sm">
                {{ filtersList.length }}
              </q-chip>
            </div>
            <div class="text-caption text-grey-7">
              Drag any columns here (for GROUP BY operations)
            </div>
          </q-card-section>

          <q-separator />

          <!-- Drop Zone -->
          <div
            class="filters-drop-zone"
            :class="{ 'drag-over': filtersDragOver }"
            @dragover.prevent="filtersDragOver = true"
            @dragleave="filtersDragOver = false"
            @drop="handleFilterDrop"
          >
            <!-- Filters List -->
            <div v-if="filtersList.length" class="q-pa-md">
              <q-list separator>
                <q-item
                  v-for="filter in filtersList"
                  :key="filter.id"
                  class="filter-item"
                >
                  <q-item-section avatar>
                    <q-icon name="filter_alt" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ filter.filter_key }}</q-item-label>
                    <q-item-label caption>
                      {{ filter.data_type }} • Value: {{ filter.filter_value || 'Not set' }}
                      <br>Equipment: {{ getEquipmentName(filter.eqp_id) || 'No equipment' }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="row q-gutter-xs">
                      <q-btn
                        round
                        flat
                        size="sm"
                        icon="edit"
                        color="primary"
                        @click="editFilter(filter)"
                      >
                        <q-tooltip>Edit filter</q-tooltip>
                      </q-btn>
                      <q-btn
                        round
                        flat
                        size="sm"
                        icon="delete"
                        color="negative"
                        @click="removeFilter(filter)"
                      >
                        <q-tooltip>Remove</q-tooltip>
                      </q-btn>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>

              <!-- Add Manual Filter Button -->
              <div class="q-pa-sm">
                <q-btn
                  flat
                  color="primary"
                  icon="add"
                  label="Add Manual Filter"
                  @click="openManualFilterDialog"
                  size="sm"
                  class="full-width"
                />
              </div>
            </div>

            <!-- Empty Drop Zone -->
            <div v-else class="empty-drop-zone q-pa-xl text-center">
              <q-icon name="filter_list_off" size="48px" color="grey-4" />
              <div class="text-h6 text-grey-6 q-mt-md">Drop Filter Columns</div>
              <div class="text-body2 text-grey-7">
                Drag any columns for grouping operations
              </div>
              <q-btn
                flat
                color="primary"
                icon="add"
                label="Add Manual Filter"
                @click="openManualFilterDialog"
                class="q-mt-md"
              />
            </div>
          </div>
        </q-card>
      </div>
    </div>

    <!-- Multi-Tab Zone -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card class="drop-zone-card">
          <q-card-section>
            <div class="text-h6 text-primary">
              <q-icon name="dashboard" class="q-mr-sm" />
              Multi-Tab Data
              <q-chip size="sm" color="purple" text-color="white" class="q-ml-sm">
                {{ totalMultiTabItems }}
              </q-chip>
            </div>
            <div class="text-caption text-grey-7">
              Drag columns to Signals, Specs, or Docs tabs
            </div>
          </q-card-section>

          <q-separator />

          <!-- Tabs -->
          <q-tabs
            v-model="activeTab"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
          >
            <q-tab name="signals" label="Signals" icon="timeline">
              <q-badge color="red" floating v-if="multiTabData.signals.length">
                {{ multiTabData.signals.length }}
              </q-badge>
            </q-tab>
            <q-tab name="specs" label="Specifications" icon="engineering">
              <q-badge color="green" floating v-if="multiTabData.specs.length">
                {{ multiTabData.specs.length }}
              </q-badge>
            </q-tab>
            <q-tab name="docs" label="Documents" icon="description">
              <q-badge color="blue" floating v-if="multiTabData.docs.length">
                {{ multiTabData.docs.length }}
              </q-badge>
            </q-tab>
          </q-tabs>

          <q-separator />

          <!-- Tab Panels -->
          <q-tab-panels v-model="activeTab" animated>
            <!-- Signals Tab -->
            <q-tab-panel name="signals" class="q-pa-none">
              <div
                class="multi-tab-drop-zone"
                :class="{ 'drag-over': signalsDragOver }"
                @dragover.prevent="signalsDragOver = true"
                @dragleave="signalsDragOver = false"
                @drop="(e) => handleMultiTabDrop(e, 'signals')"
              >
                <div v-if="multiTabData.signals.length" class="q-pa-md">
                  <q-list separator>
                    <q-item
                      v-for="signal in multiTabData.signals"
                      :key="signal.id"
                      class="multi-tab-item"
                    >
                      <q-item-section avatar>
                        <q-icon name="timeline" color="red" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ signal.key }}</q-item-label>
                        <q-item-label caption>
                          {{ signal.data_type }} • {{ signal.desc }}
                          <span v-if="signal.unit"> • Unit: {{ signal.unit }}</span>
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn
                          round
                          flat
                          size="sm"
                          icon="delete"
                          color="negative"
                          @click="removeMultiTabItem(signal, 'signals')"
                        >
                          <q-tooltip>Remove</q-tooltip>
                        </q-btn>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <div v-else class="empty-drop-zone q-pa-xl text-center">
                  <q-icon name="timeline" size="48px" color="grey-4" />
                  <div class="text-h6 text-grey-6 q-mt-md">Drop Signal Columns</div>
                  <div class="text-body2 text-grey-7">
                    Drag columns for signal monitoring
                  </div>
                </div>
              </div>
            </q-tab-panel>

            <!-- Specifications Tab -->
            <q-tab-panel name="specs" class="q-pa-none">
              <div
                class="multi-tab-drop-zone"
                :class="{ 'drag-over': specsDragOver }"
                @dragover.prevent="specsDragOver = true"
                @dragleave="specsDragOver = false"
                @drop="(e) => handleMultiTabDrop(e, 'specs')"
              >
                <div v-if="multiTabData.specs.length" class="q-pa-md">
                  <q-list separator>
                    <q-item
                      v-for="spec in multiTabData.specs"
                      :key="spec.id"
                      class="multi-tab-item"
                    >
                      <q-item-section avatar>
                        <q-icon name="engineering" color="green" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ spec.key }}</q-item-label>
                        <q-item-label caption>{{ spec.desc }}</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn
                          round
                          flat
                          size="sm"
                          icon="delete"
                          color="negative"
                          @click="removeMultiTabItem(spec, 'specs')"
                        >
                          <q-tooltip>Remove</q-tooltip>
                        </q-btn>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <div v-else class="empty-drop-zone q-pa-xl text-center">
                  <q-icon name="engineering" size="48px" color="grey-4" />
                  <div class="text-h6 text-grey-6 q-mt-md">Drop Specification Columns</div>
                  <div class="text-body2 text-grey-7">
                    Drag columns to define equipment specifications
                  </div>
                </div>
              </div>
            </q-tab-panel>

            <!-- Documents Tab -->
            <q-tab-panel name="docs" class="q-pa-none">
              <div
                class="multi-tab-drop-zone"
                :class="{ 'drag-over': docsDragOver }"
                @dragover.prevent="docsDragOver = true"
                @dragleave="docsDragOver = false"
                @drop="(e) => handleMultiTabDrop(e, 'docs')"
              >
                <div v-if="multiTabData.docs.length" class="q-pa-md">
                  <q-list separator>
                    <q-item
                      v-for="doc in multiTabData.docs"
                      :key="doc.id"
                      class="multi-tab-item"
                    >
                      <q-item-section avatar>
                        <q-icon name="description" color="blue" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>{{ doc.desc }}</q-item-label>
                        <q-item-label caption>
                          Source: {{ doc.source_column }}
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-btn
                          round
                          flat
                          size="sm"
                          icon="delete"
                          color="negative"
                          @click="removeMultiTabItem(doc, 'docs')"
                        >
                          <q-tooltip>Remove</q-tooltip>
                        </q-btn>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <div v-else class="empty-drop-zone q-pa-xl text-center">
                  <q-icon name="description" size="48px" color="grey-4" />
                  <div class="text-h6 text-grey-6 q-mt-md">Drop Documentation Columns</div>
                  <div class="text-body2 text-grey-7">
                    Drag columns for documentation references
                  </div>
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>

    <!-- Equipment Edit Dialog -->
    <q-dialog v-model="showEditDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Edit Equipment</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="editingEquipmentName"
            label="Equipment Name *"
            outlined
            class="q-mb-md"
          />
          <q-input
            v-model="editingEquipmentLocation"
            label="Location (Optional)"
            outlined
            placeholder="Enter equipment location"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" @click="saveEquipmentEdit" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Filter Dialog -->
    <q-dialog v-model="showFilterDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ editingFilter?.id ? 'Edit' : 'Add' }} Filter</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="filterForm.filter_key"
            label="Filter Key *"
            outlined
            class="q-mb-md"
            :readonly="!!editingFilter?.source_column"
          />
          <q-input
            v-model="filterForm.filter_value"
            label="Filter Value *"
            outlined
            placeholder="Enter filter value (e.g., '1', 'active', etc.)"
            class="q-mb-md"
          />
          <q-select
            v-model="filterForm.eqp_id"
            :options="equipmentOptions"
            option-label="name"
            option-value="id"
            label="Link to Equipment *"
            outlined
            map-options
            emit-value
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup @click="resetFilterForm" />
          <q-btn flat label="Save" @click="saveFilter" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Manual Filter Dialog -->
    <q-dialog v-model="showAddManualFilter" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Manual Filter</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="manualFilterForm.filter_key"
            label="Filter Key *"
            outlined
            placeholder="Enter custom filter name"
            class="q-mb-md"
          />
          <q-input
            v-model="manualFilterForm.filter_value"
            label="Filter Value *"
            outlined
            placeholder="Enter filter value"
            class="q-mb-md"
          />
          <q-select
            v-model="manualFilterForm.eqp_id"
            :options="equipmentOptions"
            option-label="name"
            option-value="id"
            label="Link to Equipment *"
            outlined
            map-options
            emit-value
            :disable="equipmentList.length === 0"
            hint="Select which equipment this filter applies to"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup @click="resetManualFilterForm" />
          <q-btn flat label="Add" @click="addManualFilter" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Signal Unit Dialog -->
    <q-dialog v-model="showSignalDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Signal{{ pendingSignals.length > 1 ? 's' : '' }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="pendingSignals.length === 1" class="q-mb-md">
            <strong>Signal:</strong> {{ pendingSignals[0]?.name }}
          </div>
          <div v-else class="q-mb-md">
            <strong>Adding {{ pendingSignals.length }} signals:</strong>
            <div class="text-caption">{{ pendingSignals.map(s => s.name).join(', ') }}</div>
          </div>

          <q-input
            v-model="signalUnit"
            label="Unit (Optional)"
            outlined
            placeholder="e.g., V, A, °C, %"
            hint="Leave empty if no unit or different units for each signal"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup @click="resetSignalDialog" />
          <q-btn flat label="Add Signal{{ pendingSignals.length > 1 ? 's' : '' }}" @click="confirmAddSignals" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
export default {
  name: 'TargetPanel',
  props: {
    masterModel: {
      type: Object,
      default: null
    },
    equipmentList: {
      type: Array,
      default: () => []
    },
    filtersList: {
      type: Array,
      default: () => []
    },
    multiTabData: {
      type: Object,
      default: () => ({ signals: [], specs: [], docs: [] })
    },
    selectedTable: {
      type: Object,
      default: null
    }
  },
  emits: [
    'equipment-drop', 'filter-drop', 'multi-tab-drop',
    'equipment-edit', 'equipment-remove', 'filter-edit', 'filter-remove',
    'manual-filter-add', 'multi-tab-remove'
  ],
  data() {
    return {
      activeTab: 'signals',

      // Drag states
      equipmentDragOver: false,
      filtersDragOver: false,
      signalsDragOver: false,
      specsDragOver: false,
      docsDragOver: false,

      // Edit dialogs
      showEditDialog: false,
      editingEquipment: null,
      editingEquipmentName: '',
      editingEquipmentLocation: '',

      // Filter dialogs
      showFilterDialog: false,
      showAddManualFilter: false,
      editingFilter: null,
      filterForm: {
        filter_key: '',
        filter_value: '',
        eqp_id: null
      },
      manualFilterForm: {
        filter_key: '',
        filter_value: '',
        eqp_id: null
      },

      // Signal dialog
      showSignalDialog: false,
      pendingSignals: [],
      signalUnit: ''
    }
  },
  computed: {
    totalMultiTabItems() {
      return Object.values(this.multiTabData).reduce((sum, arr) => sum + arr.length, 0)
    },

    equipmentOptions() {
      console.log('🔍 Computing equipment options from:', this.equipmentList)
      const options = this.equipmentList.map(eq => ({
        id: eq.id,
        name: eq.name,
        label: eq.name, // Add label for q-select
        value: eq.id    // Add value for q-select
      }))
      console.log('🔍 Equipment options generated:', options)
      return options
    }
  },
  methods: {
    handleEquipmentDrop(event) {
      event.preventDefault()
      this.equipmentDragOver = false

      try {
        const dragData = JSON.parse(event.dataTransfer.getData('application/json'))

        if (dragData.type === 'table') {
          this.$emit('equipment-drop', dragData.data)
        } else {
          this.$q.notify({
            type: 'warning',
            message: 'Only tables can be dropped in Equipment zone'
          })
        }
      } catch (error) {
        console.error('Drop error:', error)
      }
    },

    handleFilterDrop(event) {
      event.preventDefault()
      this.filtersDragOver = false

      try {
        const dragData = JSON.parse(event.dataTransfer.getData('application/json'))

        if (dragData.type === 'column') {
          // Single column drop - show dialog for filter value and equipment selection
          this.showFilterValueDialog(dragData.data)
        } else if (dragData.type === 'multi-column') {
          // Multi-column drop - process each column
          this.showMultiFilterDialog(dragData.data)
        }
      } catch (error) {
        console.error('Filter drop error:', error)
      }
    },

    showFilterValueDialog(column) {
      this.filterForm = {
        filter_key: column.name,
        filter_value: '',
        eqp_id: this.equipmentList.length > 0 ? this.equipmentList[0].id : null,
        source_column: column.name,
        source_table: this.selectedTable?.name,
        data_type: column.data_type
      }
      this.editingFilter = null
      this.showFilterDialog = true
    },

    showMultiFilterDialog(columns) {
      // For multi-column, show dialog for first column, then auto-add others
      if (columns.length === 1) {
        this.showFilterValueDialog(columns[0])
      } else {
        // Add each column as separate filter with dialog for first one
        this.showFilterValueDialog(columns[0])
        // Auto-add remaining columns with default equipment and empty value
        const defaultEquipmentId = this.equipmentList.length > 0 ? this.equipmentList[0].id : null

        for (let i = 1; i < columns.length; i++) {
          this.$emit('filter-drop', {
            name: columns[i].name,
            data_type: columns[i].data_type,
            filter_value: '',
            eqp_id: defaultEquipmentId,
            source_table: this.selectedTable?.name,
            source_column: columns[i].name
          })
        }
      }
    },

    handleMultiTabDrop(event, tabType) {
      event.preventDefault()
      this[`${tabType}DragOver`] = false

      try {
        const dragData = JSON.parse(event.dataTransfer.getData('application/json'))

        if (dragData.type === 'column') {
          if (tabType === 'signals') {
            // Show unit dialog for signals
            this.pendingSignals = [dragData.data]
            this.showSignalDialog = true
          } else {
            this.$emit('multi-tab-drop', {
              column: dragData.data,
              tabType: tabType
            })
          }
        } else if (dragData.type === 'multi-column') {
          if (tabType === 'signals') {
            // Show unit dialog for multiple signals
            this.pendingSignals = dragData.data
            this.showSignalDialog = true
          } else {
            // Add multiple columns to other tabs
            dragData.data.forEach(column => {
              this.$emit('multi-tab-drop', {
                column: column,
                tabType: tabType
              })
            })
          }
        }
      } catch (error) {
        console.error('Multi-tab drop error:', error)
      }
    },

    editEquipment(equipment) {
      this.editingEquipment = equipment
      this.editingEquipmentName = equipment.name
      this.editingEquipmentLocation = equipment.location || ''
      this.showEditDialog = true
    },

    saveEquipmentEdit() {
      if (this.editingEquipmentName.trim()) {
        this.$emit('equipment-edit', this.editingEquipment, {
          name: this.editingEquipmentName.trim(),
          location: this.editingEquipmentLocation.trim()
        })
        this.showEditDialog = false
      }
    },

    // Filter management methods
    editFilter(filter) {
      this.editingFilter = filter
      this.filterForm = {
        filter_key: filter.filter_key,
        filter_value: filter.filter_value,
        eqp_id: filter.eqp_id
      }
      this.showFilterDialog = true
    },

    saveFilter() {
      if (this.filterForm.filter_key && this.filterForm.filter_value && this.filterForm.eqp_id) {
        if (this.editingFilter) {
          this.$emit('filter-edit', this.editingFilter, this.filterForm)
        } else {
          this.$emit('filter-drop', this.filterForm)
        }
        this.resetFilterForm()
        this.showFilterDialog = false
      }
    },

    resetFilterForm() {
      this.filterForm = {
        filter_key: '',
        filter_value: '',
        eqp_id: null
      }
      this.editingFilter = null
    },

    addManualFilter() {
      if (this.manualFilterForm.filter_key && this.manualFilterForm.filter_value && this.manualFilterForm.eqp_id) {
        this.$emit('manual-filter-add', this.manualFilterForm)
        this.resetManualFilterForm()
        this.showAddManualFilter = false
      }
    },

    resetManualFilterForm() {
      console.log('🔄 Resetting manual filter form')
      this.manualFilterForm = {
        filter_key: '',
        filter_value: '',
        eqp_id: null
      }
    },

    // Signal dialog methods
    confirmAddSignals() {
      this.pendingSignals.forEach(column => {
        this.$emit('multi-tab-drop', {
          column: { ...column, unit: this.signalUnit },
          tabType: 'signals'
        })
      })
      this.resetSignalDialog()
    },

    resetSignalDialog() {
      this.pendingSignals = []
      this.signalUnit = ''
      this.showSignalDialog = false
    },

    // Helper methods
    getEquipmentName(equipmentId) {
      const equipment = this.equipmentList.find(eq => eq.id === equipmentId)
      return equipment ? equipment.name : 'Unknown'
    },

    openManualFilterDialog() {
      console.log('🔧 Opening manual filter dialog')
      console.log('🔧 Available equipment:', this.equipmentList)

      if (this.equipmentList.length === 0) {
        this.$q.notify({
          type: 'warning',
          message: 'Please create equipment first before adding filters',
          timeout: 3000
        })
        return
      }

      // Reset form and set default equipment
      this.resetManualFilterForm()
      if (this.equipmentList.length > 0) {
        this.manualFilterForm.eqp_id = this.equipmentList[0].id
      }

      this.showAddManualFilter = true
      console.log('🔧 Manual filter dialog opened')
    },

    removeEquipment(equipment) {
      this.$emit('equipment-remove', equipment)
    },

    removeFilter(filter) {
      this.$emit('filter-remove', filter)
    },

    removeMultiTabItem(item, tabType) {
      this.$emit('multi-tab-remove', { item, tabType })
    }
  }
}
</script>

<style scoped>
.target-panel {
  height: 100%;
}

.drop-zone-card {
  border-radius: 12px;
  overflow: hidden;
}

.equipment-drop-zone,
.filters-drop-zone,
.multi-tab-drop-zone {
  min-height: 200px;
  transition: all 0.3s ease;
  border: 2px dashed transparent;
}

.drag-over {
  background: #e3f2fd;
  border-color: #2196f3;
  transform: scale(1.02);
}

.empty-drop-zone {
  min-height: 150px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.empty-drop-zone:hover {
  border-color: #bdbdbd;
  background: #fafafa;
}

.equipment-item,
.filter-item,
.multi-tab-item {
  transition: all 0.2s ease;
}

.equipment-item:hover,
.filter-item:hover,
.multi-tab-item:hover {
  background: #f0f8ff;
}

.master-model-card {
  background: linear-gradient(45deg, #f8f9fa, #e9ecef);
  border: 2px solid #dee2e6;
}

/* Tab animations */
.q-tab-panels {
  background: transparent;
}

.q-tab-panel {
  min-height: 200px;
}

/* Badge positioning */
.q-tab .q-badge {
  top: 8px;
  right: 8px;
}
</style>
