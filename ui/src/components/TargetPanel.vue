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
                        <q-tooltip>Edit name</q-tooltip>
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
                      {{ filter.data_type }} • From: {{ filter.source_table }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
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
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Empty Drop Zone -->
            <div v-else class="empty-drop-zone q-pa-xl text-center">
              <q-icon name="filter_list_off" size="48px" color="grey-4" />
              <div class="text-h6 text-grey-6 q-mt-md">Drop Filter Columns</div>
              <div class="text-body2 text-grey-7">
                Drag any columns for grouping operations
              </div>
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
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Edit Equipment Name</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="editingEquipmentName"
            label="Equipment Name"
            outlined
            autofocus
            @keyup.enter="saveEquipmentEdit"
          />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Save" @click="saveEquipmentEdit" />
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
    'equipment-edit', 'equipment-remove', 'filter-remove', 'multi-tab-remove'
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

      // Edit dialog
      showEditDialog: false,
      editingEquipment: null,
      editingEquipmentName: ''
    }
  },
  computed: {
    totalMultiTabItems() {
      return Object.values(this.multiTabData).reduce((sum, arr) => sum + arr.length, 0)
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
          this.$emit('filter-drop', dragData.data)
        }
      } catch (error) {
        console.error('Filter drop error:', error)
      }
    },

    handleMultiTabDrop(event, tabType) {
      event.preventDefault()
      this[`${tabType}DragOver`] = false

      try {
        const dragData = JSON.parse(event.dataTransfer.getData('application/json'))

        if (dragData.type === 'column') {
          this.$emit('multi-tab-drop', {
            column: dragData.data,
            tabType: tabType
          })
        }
      } catch (error) {
        console.error('Multi-tab drop error:', error)
      }
    },

    editEquipment(equipment) {
      this.editingEquipment = equipment
      this.editingEquipmentName = equipment.name
      this.showEditDialog = true
    },

    saveEquipmentEdit() {
      if (this.editingEquipmentName.trim()) {
        this.$emit('equipment-edit', this.editingEquipment, this.editingEquipmentName.trim())
        this.showEditDialog = false
      }
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
