<!-- components/SourcePanel.vue - Enhanced with InfluxDB Support -->
<template>
  <div class="source-panel">
    <!-- InfluxDB Measurements Panel -->
    <q-card v-if="dataSourceType === 'influxdb'" class="q-mb-md">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon name="timeline" class="q-mr-sm" />
          InfluxDB Measurements
          <q-chip size="sm" color="orange" text-color="white" class="q-ml-sm">
            {{ measurements.length }}
          </q-chip>
        </div>
        <div class="text-caption text-grey-7">
          Drag measurements to Equipment zone
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none">
        <q-list bordered separator v-if="measurements.length">
          <q-expansion-item
            v-for="measurement in measurements"
            :key="measurement.name"
            :label="measurement.name"
            :caption="`${measurement.field_count || 0} fields, ${measurement.tag_count || 0} tags`"
            icon="timeline"
            header-class="text-weight-medium"
            @click="selectMeasurement(measurement)"
          >
            <template v-slot:header>
              <q-item-section avatar>
                <q-icon name="drag_indicator" color="grey-6" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ measurement.name }}</q-item-label>
                <q-item-label caption>
                  {{ measurement.field_count || 0 }} fields • {{ measurement.tag_count || 0 }} tags
                  <span v-if="measurement.sample_count && measurement.sample_count !== 'N/A'" class="q-ml-sm">
                    • {{ formatSampleCount(measurement.sample_count) }} samples
                  </span>
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <div class="row q-gutter-xs">
                  <q-btn
                    size="sm"
                    flat
                    round
                    icon="drag_indicator"
                    color="primary"
                    draggable="true"
                    @dragstart="startMeasurementDrag($event, measurement)"
                    @dragend="endDrag"
                    title="Drag to create equipment"
                    class="cursor-grab"
                  />
                  <q-icon
                    name="arrow_forward"
                    color="primary"
                    v-if="selectedTable?.name === measurement.name"
                  />
                </div>
              </q-item-section>
            </template>

            <!-- Fields and Tags -->
            <div class="q-pa-md">
              <!-- Fields Section -->
              <div v-if="getFields(measurement).length > 0" class="q-mb-md">
                <div class="text-subtitle2 text-green-7 q-mb-sm">
                  <q-icon name="functions" class="q-mr-xs" />
                  Fields ({{ getFields(measurement).length }})
                </div>
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="field in getFields(measurement)"
                    :key="`field-${field.name}`"
                    removable="false"
                    color="green-1"
                    text-color="green-8"
                    size="sm"
                    draggable="true"
                    @dragstart="startFieldDrag($event, field)"
                    @dragend="endDrag"
                    class="cursor-grab"
                  >
                    <q-icon name="functions" size="xs" class="q-mr-xs" />
                    {{ field.name }}
                  </q-chip>
                </div>
              </div>

              <!-- Tags Section -->
              <div v-if="getTags(measurement).length > 0">
                <div class="text-subtitle2 text-blue-7 q-mb-sm">
                  <q-icon name="local_offer" class="q-mr-xs" />
                  Tags ({{ getTags(measurement).length }})
                </div>
                <div class="row q-gutter-xs">
                  <q-chip
                    v-for="tag in getTags(measurement)"
                    :key="`tag-${tag.name}`"
                    removable="false"
                    color="blue-1"
                    text-color="blue-8"
                    size="sm"
                    draggable="true"
                    @dragstart="startFieldDrag($event, tag)"
                    @dragend="endDrag"
                    class="cursor-grab"
                  >
                    <q-icon name="local_offer" size="xs" class="q-mr-xs" />
                    {{ tag.name }}
                  </q-chip>
                </div>
              </div>

              <!-- No Fields/Tags Message -->
              <div v-if="getFields(measurement).length === 0 && getTags(measurement).length === 0" class="text-caption text-grey-6">
                <q-icon name="info" class="q-mr-xs" />
                No fields or tags found for this measurement
              </div>
            </div>
          </q-expansion-item>
        </q-list>

        <div v-else class="q-pa-md text-center text-grey-7">
          <q-icon name="timeline" size="32px" class="q-mb-sm" />
          <div>No measurements available</div>
        </div>
      </q-card-section>
    </q-card>

    <!-- SQLite/Parquet Tables Panel -->
    <q-card v-else class="q-mb-md">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon name="table_chart" class="q-mr-sm" />
          {{ dataSourceType === 'parquet' ? 'Equipment Groups' : 'Tables' }}
          <q-chip size="sm" color="blue" text-color="white" class="q-ml-sm">
            {{ tables.length }}
          </q-chip>
        </div>
        <div class="text-caption text-grey-7">
          Drag {{ dataSourceType === 'parquet' ? 'equipment groups' : 'tables' }} to Equipment zone
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-pa-none">
        <q-list bordered separator v-if="tables.length">
          <q-item
            v-for="table in tables"
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
                {{ getTableCaption(table) }}
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
          <div>No {{ dataSourceType === 'parquet' ? 'equipment groups' : 'tables' }} available</div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Columns/Fields Panel (for SQLite/Parquet) OR Fields/Tags Details (for InfluxDB) -->
    <q-card v-if="selectedTable">
      <q-card-section>
        <div class="text-h6 text-primary">
          <q-icon :name="dataSourceType === 'influxdb' ? 'view_module' : 'view_column'" class="q-mr-sm" />
          {{ dataSourceType === 'influxdb' ? 'Fields & Tags' : 'Columns' }}
          <q-chip size="sm" color="green" text-color="white" class="q-ml-sm">
            {{ getColumnCount() }}
          </q-chip>
        </div>
        <div class="text-caption text-grey-7">
          From {{ dataSourceType === 'influxdb' ? 'measurement' : (dataSourceType === 'parquet' ? 'equipment group' : 'table') }}: <strong>{{ selectedTable.name }}</strong>
        </div>
        <div class="text-caption text-grey-7">
          Drag {{ dataSourceType === 'influxdb' ? 'fields/tags' : 'columns' }} to Filters or Multi-Tab zones
        </div>
      </q-card-section>

      <q-separator />

      <!-- Column Filter (for non-InfluxDB) -->
      <q-card-section v-if="dataSourceType !== 'influxdb'">
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

      <q-separator v-if="dataSourceType !== 'influxdb'" />

      <q-card-section class="q-pa-none" style="max-height: 400px; overflow-y: auto;">
        <!-- InfluxDB Fields and Tags Display -->
        <div v-if="dataSourceType === 'influxdb'" class="q-pa-md">
          <!-- Fields Section -->
          <div v-if="getFields(selectedTable).length > 0" class="q-mb-md">
            <div class="text-subtitle2 text-green-7 q-mb-sm">
              <q-icon name="functions" class="q-mr-xs" />
              Fields ({{ getFields(selectedTable).length }}) - Numeric Data
            </div>
            <q-list separator>
              <q-item
                v-for="field in getFields(selectedTable)"
                :key="`field-${field.name}`"
                class="draggable-column"
                :draggable="true"
                @dragstart="startFieldDrag($event, field)"
                @dragend="endDrag"
              >
                <q-item-section avatar>
                  <q-icon name="drag_indicator" color="grey-6" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ field.name }}</q-item-label>
                  <q-item-label caption>
                    {{ field.type || 'number' }} • field • Use for signals/charts
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip size="xs" color="green" text-color="white">field</q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Tags Section -->
          <div v-if="getTags(selectedTable).length > 0">
            <div class="text-subtitle2 text-blue-7 q-mb-sm">
              <q-icon name="local_offer" class="q-mr-xs" />
              Tags ({{ getTags(selectedTable).length }}) - String Labels
            </div>
            <q-list separator>
              <q-item
                v-for="tag in getTags(selectedTable)"
                :key="`tag-${tag.name}`"
                class="draggable-column"
                :draggable="true"
                @dragstart="startFieldDrag($event, tag)"
                @dragend="endDrag"
              >
                <q-item-section avatar>
                  <q-icon name="drag_indicator" color="grey-6" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ tag.name }}</q-item-label>
                  <q-item-label caption>
                    {{ tag.type || 'string' }} • tag • Use for filtering/grouping
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip size="xs" color="blue" text-color="white">tag</q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>

        <!-- SQLite/Parquet Columns Display (Existing functionality preserved) -->
        <div v-else>
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
        </div>
      </q-card-section>
    </q-card>

    <!-- No Table Selected -->
    <q-card v-else>
      <q-card-section class="q-pa-xl text-center">
        <q-icon name="touch_app" size="48px" color="grey-4" />
        <div class="text-h6 text-grey-6 q-mt-md">
          Select {{ dataSourceType === 'influxdb' ? 'a Measurement' : (dataSourceType === 'parquet' ? 'an Equipment Group' : 'a Table') }}
        </div>
        <div class="text-body2 text-grey-7">
          Click on {{ dataSourceType === 'influxdb' ? 'a measurement' : 'a table' }} above to view its {{ dataSourceType === 'influxdb' ? 'fields and tags' : 'columns' }}
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
    dataSourceType: {
      type: String,
      default: 'sqlite3'
    },
    selectedTable: {
      type: Object,
      default: null
    }
  },
  emits: [
    'table-selected',
    'measurement-selected',
    'table-drag-start',
    'measurement-drag-start',
    'column-drag-start',
    'field-drag-start'
  ],
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
    // InfluxDB measurements
    measurements() {
      return this.schemaData?.measurements || []
    },

    // SQLite/Parquet tables
    tables() {
      return this.schemaData?.tables || []
    },

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
  watch: {
    selectedTable() {
      // Reset filters and selections when table changes
      this.columnFilter = ''
      this.selectedCategories = []
      this.selectedColumns = []
      this.selectAll = false
    },
    schemaData: {
      handler(newData) {
        console.log('📊 SourcePanel schemaData changed:', newData)
        if (this.dataSourceType === 'influxdb') {
          console.log('📊 InfluxDB measurements:', newData?.measurements)
        }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    // InfluxDB-specific methods
    getFields(measurement) {
      if (!measurement?.fields) {
        return []
      }
      return measurement.fields.filter(f => f.category === 'field')
    },

    getTags(measurement) {
      if (!measurement?.fields) {
        return []
      }
      return measurement.fields.filter(f => f.category === 'tag')
    },

    getColumnCount() {
      if (this.dataSourceType === 'influxdb') {
        return (this.getFields(this.selectedTable).length + this.getTags(this.selectedTable).length)
      }
      return this.selectedTable?.columns?.length || 0
    },

    selectTable(table) {
      console.log('📋 Table selected:', table)
      this.$emit('table-selected', table)
    },

    selectMeasurement(measurement) {
      console.log('📊 Measurement selected:', measurement)
      this.$emit('measurement-selected', measurement)
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

    startMeasurementDrag(event, measurement) {
      console.log('🚀 Starting measurement drag:', measurement.name)
      this.isDragging = true

      // Set drag data for InfluxDB measurement
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: 'measurement',
        data: {
          ...measurement,
          name: measurement.name,
          bucket: measurement.bucket,
          field_count: measurement.field_count || 0,
          tag_count: measurement.tag_count || 0
        }
      }))

      event.dataTransfer.effectAllowed = 'copy'
      event.target.classList.add('dragging')

      this.$emit('measurement-drag-start', measurement)
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

    startFieldDrag(event, field) {
      console.log('🚀 Starting field/tag drag:', field.name, 'category:', field.category)
      this.isDragging = true

      // Set drag data for InfluxDB field/tag
      event.dataTransfer.setData('application/json', JSON.stringify({
        type: field.category === 'tag' ? 'tag' : 'field',
        data: field,
        sourceTable: this.selectedTable?.name
      }))

      event.dataTransfer.effectAllowed = 'copy'
      event.target.classList.add('dragging')

      this.$emit('field-drag-start', field)
    },

    endDrag(event) {
      this.isDragging = false
      event.target.classList.remove('dragging')
    },

    // Multi-selection methods (for non-InfluxDB)
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

    // Helper methods
    formatRowCount(count) {
      if (typeof count === 'string') return count
      if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
      if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
      return count.toString()
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

    getTableCaption(table) {
      if (this.dataSourceType === 'parquet') {
        return `${table.file_count || 0} files`
      }
      return `${this.formatRowCount(table.row_count)} rows • ${table.total_columns || 0} columns`
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

/* InfluxDB specific styling */
.q-chip.cursor-grab {
  cursor: grab;
  user-select: none;
  transition: transform 0.1s ease;
}

.q-chip.cursor-grab:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.q-chip.cursor-grab:active {
  cursor: grabbing;
  transform: translateY(0);
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

/* InfluxDB measurement expansion styling */
.q-expansion-item {
  border-radius: 4px;
  margin-bottom: 4px;
}

.q-expansion-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Responsive design */
@media (max-width: 768px) {
  .source-panel .row {
    margin: 0;
  }

  .source-panel .col-12 {
    padding: 4px;
  }
}
</style>
