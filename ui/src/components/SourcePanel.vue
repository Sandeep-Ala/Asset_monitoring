<!-- components/SourcePanel.vue -->
<template>
  <div class="source-panel">
    <!-- Tables Panel -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon name="table_chart" class="q-mr-sm" />
          Tables
          <q-chip size="sm" color="blue" text-color="white" class="q-ml-sm">
            {{ schemaData.tables?.length || 0 }}
          </q-chip>
        </div>
        <div class="text-caption text-grey-7">
          Drag tables to Equipment zone
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none">
        <q-list bordered separator v-if="schemaData.tables?.length">
          <q-item
            v-for="table in schemaData.tables"
            :key="table.name"
            class="draggable-table"
            :class="{ 'selected-table': selectedTable?.name === table.name }"
            clickable
            v-ripple
            @click="selectTable(table)"
            :draggable="true"
            @dragstart="startTableDrag($event, table)"
            @dragend="endDrag"
          >
            <q-item-section avatar>
              <q-icon name="drag_indicator" color="grey-6" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ table.name }}</q-item-label>
              <q-item-label caption>
                {{ formatRowCount(table.row_count) }} rows • {{ table.total_columns || 0 }} columns
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon
                name="arrow_forward"
                color="primary"
                v-if="selectedTable?.name === table.name"
              />
            </q-item-section>

            <!-- Drag Preview -->
            <q-tooltip anchor="center right" self="center left" :offset="[10, 0]">
              Drag to Equipment zone to create equipment
            </q-tooltip>
          </q-item>
        </q-list>

        <div v-else class="q-pa-md text-center text-grey-7">
          <q-icon name="table_chart" size="32px" class="q-mb-sm" />
          <div>No tables available</div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Columns Panel -->
    <q-card v-if="selectedTable">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon name="view_column" class="q-mr-sm" />
          Columns
          <q-chip size="sm" color="green" text-color="white" class="q-ml-sm">
            {{ selectedTable.columns?.length || 0 }}
          </q-chip>
        </div>
        <div class="text-caption text-grey-7">
          From table: <strong>{{ selectedTable.name }}</strong>
        </div>
        <div class="text-caption text-grey-7">
          Drag columns to Filters or Multi-Tab zones
        </div>
      </q-card-section>

      <q-separator />

      <!-- Column Filter -->
      <q-card-section>
        <q-input
          v-model="columnFilter"
          label="Filter columns"
          outlined
          dense
          clearable
          class="q-mb-sm"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>

        <!-- Column Category Filter -->
        <div class="row q-gutter-xs">
          <q-btn
            v-for="category in availableCategories"
            :key="category"
            size="xs"
            :color="selectedCategories.includes(category) ? 'primary' : 'grey-4'"
            :text-color="selectedCategories.includes(category) ? 'white' : 'grey-8'"
            @click="toggleCategory(category)"
            :label="category"
            dense
          />
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none" style="max-height: 400px; overflow-y: auto;">
        <!-- Multi-select toolbar -->
        <div v-if="filteredColumns.length" class="q-pa-sm bg-grey-1 row items-center justify-between">
          <div class="row items-center q-gutter-sm">
            <q-checkbox
              v-model="selectAll"
              @update:model-value="toggleSelectAll"
              :indeterminate="someSelected && !allSelected"
            />
            <span class="text-caption">
              {{ selectedColumns.length }} of {{ filteredColumns.length }} selected
            </span>
          </div>
          <div class="row q-gutter-xs">
            <q-btn
              v-if="selectedColumns.length > 0"
              size="sm"
              color="primary"
              icon="drag_indicator"
              label="Drag Selected"
              :draggable="true"
              @dragstart="startMultiColumnDrag"
              @dragend="endDrag"
              class="multi-drag-btn"
            />
            <q-btn
              v-if="selectedColumns.length > 0"
              size="sm"
              flat
              icon="clear"
              @click="clearSelection"
            />
          </div>
        </div>

        <q-list bordered separator v-if="filteredColumns.length">
          <q-item
            v-for="column in filteredColumns"
            :key="column.name"
            class="draggable-column"
            :class="{ 'selected-column': selectedColumns.includes(column.name) }"
            :draggable="!selectedColumns.includes(column.name)"
            @dragstart="startColumnDrag($event, column)"
            @dragend="endDrag"
            @click="toggleColumnSelection(column.name)"
          >
            <q-item-section avatar>
              <q-checkbox
                :model-value="selectedColumns.includes(column.name)"
                @update:model-value="toggleColumnSelection(column.name)"
                @click.stop
              />
            </q-item-section>
            <q-item-section avatar>
              <q-icon name="drag_indicator" color="grey-6" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ column.name }}</q-item-label>
              <q-item-label caption>
                {{ column.data_type }} • {{ column.category }}
                <span v-if="column.distinctness_ratio !== undefined">
                  • {{ Math.round(column.distinctness_ratio * 100) }}% unique
                </span>
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <div class="column q-gutter-xs">
                <!-- Category chip -->
                <q-chip
                  size="xs"
                  :color="getCategoryColor(column.category)"
                  text-color="white"
                >
                  {{ column.category }}
                </q-chip>

                <!-- Suggestion chips -->
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="suggestion in column.suggested_for"
                    :key="suggestion"
                    size="xs"
                    color="green"
                    text-color="white"
                    icon="auto_awesome"
                  >
                    {{ suggestion }}
                  </q-chip>
                </div>
              </div>
            </q-item-section>

            <!-- Drag tooltip -->
            <q-tooltip anchor="center right" self="center left" :offset="[10, 0]">
              <div>
                <strong>{{ column.name }}</strong><br>
                Type: {{ column.data_type }}<br>
                Category: {{ column.category }}<br>
                <span v-if="column.suggested_for?.length">
                  Suggested for: {{ column.suggested_for.join(', ') }}
                </span>
              </div>
            </q-tooltip>
          </q-item>
        </q-list>

        <div v-else class="q-pa-md text-center text-grey-7">
          <q-icon name="filter_list_off" size="32px" class="q-mb-sm" />
          <div>No columns match your filter</div>
        </div>
      </q-card-section>
    </q-card>

    <!-- No Table Selected -->
    <q-card v-else>
      <q-card-section class="q-pa-xl text-center">
        <q-icon name="touch_app" size="48px" color="grey-4" />
        <div class="text-h6 text-grey-6 q-mt-md">Select a Table</div>
        <div class="text-body2 text-grey-7">
          Click on a table above to view its columns
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
export default {
  name: 'SourcePanel',
  props: {
    schemaData: {
      type: Object,
      default: () => ({})
    },
    selectedTable: {
      type: Object,
      default: null
    }
  },
  emits: ['table-selected', 'table-drag-start', 'column-drag-start'],
  data() {
    return {
      columnFilter: '',
      selectedCategories: [],
      isDragging: false,
      selectedColumns: [], // For multi-select
      selectAll: false
    }
  },
  computed: {
    availableCategories() {
      if (!this.selectedTable?.columns) return []

      const categories = [...new Set(this.selectedTable.columns.map(col => col.category))]
      return categories.filter(cat => cat && cat !== 'unknown')
    },

    filteredColumns() {
      if (!this.selectedTable?.columns) return []

      let columns = this.selectedTable.columns

      // Filter by text
      if (this.columnFilter) {
        const filter = this.columnFilter.toLowerCase()
        columns = columns.filter(col =>
          col.name.toLowerCase().includes(filter) ||
          col.category.toLowerCase().includes(filter) ||
          col.data_type.toLowerCase().includes(filter)
        )
      }

      // Filter by categories
      if (this.selectedCategories.length > 0) {
        columns = columns.filter(col => this.selectedCategories.includes(col.category))
      }

      return columns
    },

    someSelected() {
      return this.selectedColumns.length > 0 && this.selectedColumns.length < this.filteredColumns.length
    },

    allSelected() {
      return this.selectedColumns.length === this.filteredColumns.length && this.filteredColumns.length > 0
    }
  },
  methods: {
    selectTable(table) {
      this.$emit('table-selected', table)
    },

    startTableDrag(event, table) {
      console.log('🚀 Starting table drag:', table.name)
      this.isDragging = true

      // Set drag data
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: 'table',
        data: table
      }))

      // Set drag effect
      event.dataTransfer.effectAllowed = 'copy'

      // Add visual feedback
      event.target.classList.add('dragging')

      this.$emit('table-drag-start', table)
    },

    startColumnDrag(event, column) {
      console.log('🚀 Starting column drag:', column.name)
      this.isDragging = true

      // Set drag data
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: 'column',
        data: column,
        sourceTable: this.selectedTable?.name
      }))

      // Set drag effect
      event.dataTransfer.effectAllowed = 'copy'

      // Add visual feedback
      event.target.classList.add('dragging')

      this.$emit('column-drag-start', column)
    },

    endDrag(event) {
      this.isDragging = false
      event.target.classList.remove('dragging')
    },

    toggleColumnSelection(columnName) {
      const index = this.selectedColumns.indexOf(columnName)
      if (index > -1) {
        this.selectedColumns.splice(index, 1)
      } else {
        this.selectedColumns.push(columnName)
      }
      this.updateSelectAllState()
    },

    toggleSelectAll() {
      if (this.allSelected) {
        this.selectedColumns = []
      } else {
        this.selectedColumns = this.filteredColumns.map(col => col.name)
      }
      this.updateSelectAllState()
    },

    updateSelectAllState() {
      this.selectAll = this.allSelected
    },

    clearSelection() {
      this.selectedColumns = []
      this.selectAll = false
    },

    startMultiColumnDrag(event) {
      console.log('🚀 Starting multi-column drag:', this.selectedColumns.length, 'columns')
      this.isDragging = true

      const selectedColumnData = this.filteredColumns.filter(col =>
        this.selectedColumns.includes(col.name)
      )

      // Set drag data for multiple columns
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: 'multi-column',
        data: selectedColumnData,
        sourceTable: this.selectedTable?.name,
        count: selectedColumnData.length
      }))

      // Set drag effect
      event.dataTransfer.effectAllowed = 'copy'

      // Add visual feedback
      event.target.classList.add('dragging')

      this.$emit('column-drag-start', { type: 'multi', columns: selectedColumnData })
    },

    toggleCategory(category) {
      const index = this.selectedCategories.indexOf(category)
      if (index > -1) {
        this.selectedCategories.splice(index, 1)
      } else {
        this.selectedCategories.push(category)
      }
    },

    formatRowCount(count) {
      if (typeof count === 'string') return count
      if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
      if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
      return count.toString()
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
  },
  watch: {
    selectedTable() {
      // Reset filters and selections when table changes
      this.columnFilter = ''
      this.selectedCategories = []
      this.selectedColumns = []
      this.selectAll = false
    }
  }
}
</script>

<style scoped>
.source-panel {
  height: 100%;
}

.draggable-table, .draggable-column {
  cursor: grab;
  transition: all 0.2s ease;
}

.draggable-table:hover, .draggable-column:hover {
  background: #f0f8ff;
  transform: translateX(4px);
}

.draggable-table:active, .draggable-column:active {
  cursor: grabbing;
}

.dragging {
  opacity: 0.6;
  transform: rotate(2deg);
}

.selected-table {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

/* Custom scrollbar for columns */
.q-card-section::-webkit-scrollbar {
  width: 6px;
}

.q-card-section::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.q-card-section::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.q-card-section::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.selected-column {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.multi-drag-btn {
  cursor: grab;
}

.multi-drag-btn:active {
  cursor: grabbing;
}

/* Animation for drag feedback */
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
  100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
}

.draggable-table:hover .q-item-section.avatar,
.draggable-column:hover .q-item-section.avatar {
  animation: pulse 1.5s infinite;
}
</style>
