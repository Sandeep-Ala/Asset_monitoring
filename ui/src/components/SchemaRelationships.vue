<!-- ui/src/components/SchemaRelationships.vue -->
<!-- Schema relationship visualization component -->

<template>
  <div class="schema-relationships">
    <!-- Visualization Controls -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-purple-1">
            <div class="text-h6">
              <q-icon name="account_tree" class="q-mr-sm" />
              Schema Relationships
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md items-end">
              <!-- Visualization Type -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="visualizationType"
                  :options="visualizationOptions"
                  label="Visualization Type"
                  outlined
                  dense
                  @update:model-value="updateVisualization"
                />
              </div>

              <!-- Relationship Filter -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="relationshipFilter"
                  :options="relationshipFilterOptions"
                  label="Show Relationships"
                  outlined
                  dense
                  @update:model-value="updateVisualization"
                />
              </div>

              <!-- Complexity Level -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="complexityLevel"
                  :options="complexityOptions"
                  label="Detail Level"
                  outlined
                  dense
                  @update:model-value="updateVisualization"
                />
              </div>

              <!-- Actions -->
              <div class="col-12 col-md-3">
                <div class="row q-gutter-sm">
                  <q-btn
                    label="Analyze"
                    icon="analytics"
                    color="primary"
                    @click="analyzeRelationships"
                    :loading="analyzing"
                  />
                  <q-btn
                    icon="fullscreen"
                    flat
                    round
                    @click="openFullscreen"
                  />
                  <q-btn
                    icon="download"
                    flat
                    round
                    @click="exportVisualization"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Relationship Statistics -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-6 col-md-3">
        <q-card flat class="bg-blue-1 text-center q-pa-md">
          <q-icon name="table_chart" size="2rem" color="blue" class="q-mb-sm" />
          <div class="text-h5">{{ relationshipStats.measurements }}</div>
          <div class="text-body2">Measurements</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-green-1 text-center q-pa-md">
          <q-icon name="link" size="2rem" color="green" class="q-mb-sm" />
          <div class="text-h5">{{ relationshipStats.connections }}</div>
          <div class="text-body2">Connections</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-orange-1 text-center q-pa-md">
          <q-icon name="hub" size="2rem" color="orange" class="q-mb-sm" />
          <div class="text-h5">{{ relationshipStats.clusters }}</div>
          <div class="text-body2">Clusters</div>
        </q-card>
      </div>
      <div class="col-6 col-md-3">
        <q-card flat class="bg-purple-1 text-center q-pa-md">
          <q-icon name="insights" size="2rem" color="purple" class="q-mb-sm" />
          <div class="text-h5">{{ relationshipStats.complexity }}%</div>
          <div class="text-body2">Complexity</div>
        </q-card>
      </div>
    </div>

    <!-- Main Visualization Area -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="text-h6">
              <q-icon name="device_hub" class="q-mr-sm" />
              {{ getVisualizationTitle() }}
            </div>
          </q-card-section>
          <q-card-section>
            <div class="visualization-container" style="min-height: 400px;">
              <!-- Network Graph Visualization -->
              <div v-if="visualizationType === 'network'" class="network-graph">
                <div v-if="!relationships || relationships.length === 0" class="text-center q-pa-xl">
                  <q-icon name="account_tree" size="4rem" class="text-grey-4 q-mb-md" />
                  <div class="text-h6 text-grey-6">No Relationships Found</div>
                  <div class="text-body2 text-grey-5 q-mb-lg">
                    Run relationship analysis to discover connections between measurements
                  </div>
                  <q-btn
                    label="Analyze Relationships"
                    icon="analytics"
                    color="primary"
                    @click="analyzeRelationships"
                    :loading="analyzing"
                  />
                </div>
                <div v-else class="network-nodes">
                  <!-- Simplified network visualization -->
                  <div class="nodes-container">
                    <div
                      v-for="node in networkNodes"
                      :key="node.id"
                      class="network-node"
                      :style="getNodeStyle(node)"
                      @click="selectNode(node)"
                    >
                      <div class="node-content">
                        <q-icon :name="getNodeIcon(node.type)" size="sm" />
                        <div class="node-label">{{ node.label }}</div>
                      </div>
                      <q-tooltip>
                        {{ node.tooltip }}
                      </q-tooltip>
                    </div>
                  </div>
                  <!-- Connection lines would be drawn with SVG in a real implementation -->
                  <svg class="connection-lines" width="100%" height="100%" style="position: absolute; top: 0; left: 0; pointer-events: none;">
                    <line
                      v-for="connection in visibleConnections"
                      :key="connection.id"
                      :x1="connection.x1"
                      :y1="connection.y1"
                      :x2="connection.x2"
                      :y2="connection.y2"
                      :stroke="getConnectionColor(connection.strength)"
                      :stroke-width="getConnectionWidth(connection.strength)"
                      stroke-dasharray="5,5"
                    />
                  </svg>
                </div>
              </div>

              <!-- Hierarchical Tree Visualization -->
              <div v-else-if="visualizationType === 'hierarchy'" class="hierarchy-tree">
                <div class="tree-container">
                  <div v-for="level in hierarchyLevels" :key="level.name" class="tree-level">
                    <div class="level-header">
                      <q-chip :color="level.color" text-color="white" size="sm">
                        {{ level.name }}
                      </q-chip>
                    </div>
                    <div class="level-nodes">
                      <div
                        v-for="node in level.nodes"
                        :key="node.id"
                        class="hierarchy-node"
                        @click="selectNode(node)"
                      >
                        <q-card flat bordered>
                          <q-card-section class="q-pa-sm text-center">
                            <q-icon :name="getNodeIcon(node.type)" size="sm" class="q-mb-xs" />
                            <div class="text-caption">{{ node.label }}</div>
                          </q-card-section>
                        </q-card>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Matrix Visualization -->
              <div v-else-if="visualizationType === 'matrix'" class="relationship-matrix">
                <q-table
                  :rows="matrixData"
                  :columns="matrixColumns"
                  row-key="measurement"
                  flat
                  dense
                  hide-pagination
                >
                  <template #body-cell="props">
                    <q-td :props="props" v-if="props.col.name !== 'measurement'">
                      <div
                        class="matrix-cell"
                        :style="getMatrixCellStyle(props.value)"
                        @click="showRelationshipDetails(props.row.measurement, props.col.name, props.value)"
                      >
                        {{ formatMatrixValue(props.value) }}
                      </div>
                    </q-td>
                    <q-td :props="props" v-else>
                      <q-chip color="primary" text-color="white" size="sm">
                        {{ props.value }}
                      </q-chip>
                    </q-td>
                  </template>
                </q-table>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Relationship Details -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="insights" class="q-mr-sm" />
              Discovered Relationships
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="!relationships || relationships.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="link_off" size="2rem" class="q-mb-sm" />
              <div>No relationships discovered</div>
            </div>
            <q-list v-else dense>
              <q-item v-for="relationship in relationships" :key="relationship.id">
                <q-item-section avatar>
                  <q-icon
                    :name="getRelationshipIcon(relationship.type)"
                    :color="getRelationshipColor(relationship.type)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>
                    {{ relationship.source }} → {{ relationship.target }}
                  </q-item-label>
                  <q-item-label caption>
                    {{ relationship.description }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip
                    :color="getStrengthColor(relationship.strength)"
                    text-color="white"
                    size="sm"
                  >
                    {{ relationship.strength }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- Schema Insights -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="text-h6">
              <q-icon name="lightbulb" class="q-mr-sm" />
              Schema Insights
            </div>
          </q-card-section>
          <q-card-section>
            <q-list dense>
              <q-item v-for="insight in schemaInsights" :key="insight.id">
                <q-item-section avatar>
                  <q-icon
                    :name="getInsightIcon(insight.type)"
                    :color="getInsightColor(insight.type)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ insight.title }}</q-item-label>
                  <q-item-label caption>{{ insight.description }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn
                    icon="arrow_forward"
                    flat
                    round
                    size="sm"
                    @click="actOnInsight(insight)"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Analysis Results -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-red-1">
            <div class="text-h6">
              <q-icon name="assessment" class="q-mr-sm" />
              Relationship Analysis Results
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="!analysisResults" class="text-center q-pa-md text-grey-6">
              <q-icon name="assessment" size="2rem" class="q-mb-sm" />
              <div>No analysis results available</div>
              <div class="text-caption">Run relationship analysis to see detailed results</div>
            </div>
            <div v-else class="row q-gutter-md">
              <!-- Network Metrics -->
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">Network Metrics</div>
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Density</q-item-label>
                      <q-item-label>{{ analysisResults.density }}%</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Clustering Coefficient</q-item-label>
                      <q-item-label>{{ analysisResults.clustering }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Average Path Length</q-item-label>
                      <q-item-label>{{ analysisResults.pathLength }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Key Nodes -->
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">Key Measurements</div>
                <q-list dense>
                  <q-item v-for="node in analysisResults.keyNodes" :key="node.name">
                    <q-item-section>
                      <q-item-label>{{ node.name }}</q-item-label>
                      <q-item-label caption>{{ node.connections }} connections</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="primary" text-color="white" size="sm">
                        {{ node.importance }}
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- Recommendations -->
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">Recommendations</div>
                <q-list dense>
                  <q-item v-for="rec in analysisResults.recommendations" :key="rec.id">
                    <q-item-section avatar>
                      <q-icon
                        :name="getRecommendationIcon(rec.type)"
                        :color="getRecommendationColor(rec.type)"
                        size="sm"
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="text-body2">{{ rec.title }}</q-item-label>
                      <q-item-label caption>{{ rec.description }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Fullscreen Dialog -->
    <q-dialog v-model="showFullscreen" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Schema Relationships - Full View</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showFullscreen = false" />
        </q-card-section>
        <q-card-section class="scroll">
          <!-- Full visualization would go here -->
          <div class="text-center q-pa-xl">
            <q-icon name="account_tree" size="6rem" class="text-grey-4 q-mb-md" />
            <div class="text-h5 text-grey-6">Enhanced Visualization</div>
            <div class="text-body1 text-grey-5">
              Full-featured relationship visualization with interactive controls
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  schema: {
    type: Object,
    default: null
  },
  measurements: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['visualize-relationship'])

// Reactive data
const $q = useQuasar()
const visualizationType = ref('network')
const relationshipFilter = ref('all')
const complexityLevel = ref('medium')
const analyzing = ref(false)
const showFullscreen = ref(false)

const relationships = ref([])
const networkNodes = ref([])
const visibleConnections = ref([])
const hierarchyLevels = ref([])
const matrixData = ref([])
const schemaInsights = ref([])
const analysisResults = ref(null)

// Computed properties
const visualizationOptions = [
  { label: 'Network Graph', value: 'network' },
  { label: 'Hierarchy Tree', value: 'hierarchy' },
  { label: 'Relationship Matrix', value: 'matrix' }
]

const relationshipFilterOptions = [
  { label: 'All Relationships', value: 'all' },
  { label: 'Strong Only', value: 'strong' },
  { label: 'Direct Only', value: 'direct' },
  { label: 'Cross-Measurement', value: 'cross' }
]

const complexityOptions = [
  { label: 'Simple View', value: 'simple' },
  { label: 'Standard View', value: 'medium' },
  { label: 'Detailed View', value: 'complex' }
]

const relationshipStats = computed(() => {
  return {
    measurements: props.measurements?.length || 0,
    connections: relationships.value.length,
    clusters: Math.max(1, Math.floor(relationships.value.length / 3)),
    complexity: Math.min(100, relationships.value.length * 10)
  }
})

const matrixColumns = computed(() => {
  const columns = [
    {
      name: 'measurement',
      label: 'Measurement',
      field: 'measurement',
      align: 'left'
    }
  ]

  // Add columns for each measurement
  props.measurements?.forEach(measurement => {
    columns.push({
      name: measurement,
      label: measurement,
      field: measurement,
      align: 'center'
    })
  })

  return columns
})

// Methods
const getVisualizationTitle = () => {
  const titles = {
    network: 'Network Graph View',
    hierarchy: 'Hierarchical Tree View',
    matrix: 'Relationship Matrix View'
  }
  return titles[visualizationType.value] || 'Schema Visualization'
}

const getNodeIcon = (nodeType) => {
  const icons = {
    measurement: 'table_chart',
    field: 'data_object',
    tag: 'label',
    cluster: 'hub'
  }
  return icons[nodeType] || 'circle'
}

const getNodeStyle = (node) => {
  const baseSize = 80
  const size = baseSize + (node.importance || 0) * 20

  return {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: node.color || '#2196F3',
    position: 'absolute',
    left: `${node.x || Math.random() * 400}px`,
    top: `${node.y || Math.random() * 300}px`,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    border: '2px solid white',
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
  }
}

const getConnectionColor = (strength) => {
  const colors = {
    strong: '#4CAF50',
    medium: '#FF9800',
    weak: '#9E9E9E'
  }
  return colors[strength] || '#9E9E9E'
}

const getConnectionWidth = (strength) => {
  const widths = {
    strong: 3,
    medium: 2,
    weak: 1
  }
  return widths[strength] || 1
}

const getRelationshipIcon = (type) => {
  const icons = {
    shared_field: 'compare_arrows',
    similar_schema: 'similarity',
    dependency: 'arrow_forward',
    correlation: 'trending_up'
  }
  return icons[type] || 'link'
}

const getRelationshipColor = (type) => {
  const colors = {
    shared_field: 'blue',
    similar_schema: 'green',
    dependency: 'orange',
    correlation: 'purple'
  }
  return colors[type] || 'grey'
}

const getStrengthColor = (strength) => {
  const colors = {
    strong: 'positive',
    medium: 'warning',
    weak: 'info'
  }
  return colors[strength] || 'grey'
}

const getInsightIcon = (type) => {
  const icons = {
    optimization: 'speed',
    structure: 'account_tree',
    quality: 'verified',
    warning: 'warning'
  }
  return icons[type] || 'lightbulb'
}

const getInsightColor = (type) => {
  const colors = {
    optimization: 'primary',
    structure: 'secondary',
    quality: 'positive',
    warning: 'warning'
  }
  return colors[type] || 'grey'
}

const getRecommendationIcon = (type) => {
  const icons = {
    index: 'storage',
    merge: 'merge_type',
    split: 'call_split',
    optimize: 'tune'
  }
  return icons[type] || 'lightbulb'
}

const getRecommendationColor = (type) => {
  const colors = {
    index: 'blue',
    merge: 'green',
    split: 'orange',
    optimize: 'purple'
  }
  return colors[type] || 'grey'
}

const getMatrixCellStyle = (value) => {
  const numValue = parseFloat(value) || 0
  const opacity = Math.abs(numValue)
  const color = numValue > 0 ? '76, 175, 80' : '244, 67, 54' // green : red

  return {
    backgroundColor: `rgba(${color}, ${opacity})`,
    color: opacity > 0.5 ? 'white' : 'black',
    textAlign: 'center',
    padding: '8px',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}

const formatMatrixValue = (value) => {
  const numValue = parseFloat(value)
  return isNaN(numValue) ? '-' : numValue.toFixed(2)
}

const updateVisualization = () => {
  generateVisualizationData()
}

const analyzeRelationships = async () => {
  analyzing.value = true

  try {
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Generate mock relationships
    relationships.value = [
      {
        id: 1,
        source: 'battery_voltage',
        target: 'battery_current',
        type: 'correlation',
        strength: 'strong',
        description: 'Strong correlation between voltage and current measurements'
      },
      {
        id: 2,
        source: 'battery_voltage',
        target: 'cell_voltage',
        type: 'shared_field',
        strength: 'medium',
        description: 'Both measurements contain voltage-related fields'
      },
      {
        id: 3,
        source: 'temperature',
        target: 'battery_voltage',
        type: 'dependency',
        strength: 'weak',
        description: 'Temperature may affect voltage readings'
      }
    ]

    // Generate insights
    schemaInsights.value = [
      {
        id: 1,
        type: 'optimization',
        title: 'Merge Similar Measurements',
        description: 'Consider merging voltage-related measurements for better organization'
      },
      {
        id: 2,
        type: 'structure',
        title: 'Add Index',
        description: 'Create composite index on timestamp and rack_id for better performance'
      },
      {
        id: 3,
        type: 'quality',
        title: 'Data Validation',
        description: 'Implement cross-field validation between related measurements'
      }
    ]

    // Generate analysis results
    analysisResults.value = {
      density: 65,
      clustering: 0.72,
      pathLength: 2.1,
      keyNodes: [
        { name: 'battery_voltage', connections: 8, importance: 'High' },
        { name: 'temperature', connections: 5, importance: 'Medium' },
        { name: 'current', connections: 4, importance: 'Medium' }
      ],
      recommendations: [
        {
          id: 1,
          type: 'index',
          title: 'Add Database Index',
          description: 'Create index on frequently joined fields'
        },
        {
          id: 2,
          type: 'merge',
          title: 'Merge Measurements',
          description: 'Combine related voltage measurements'
        }
      ]
    }

    generateVisualizationData()

    $q.notify({
      type: 'positive',
      message: 'Relationship analysis completed',
      caption: `Found ${relationships.value.length} relationships`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Analysis failed',
      caption: error.message
    })
  } finally {
    analyzing.value = false
  }
}

const generateVisualizationData = () => {
  // Generate network nodes
  networkNodes.value = props.measurements?.map((measurement, index) => ({
    id: measurement,
    label: measurement,
    type: 'measurement',
    x: 100 + (index % 4) * 150,
    y: 100 + Math.floor(index / 4) * 120,
    color: ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'][index % 4],
    importance: Math.random(),
    tooltip: `${measurement} - ${Math.floor(Math.random() * 20 + 5)} fields`
  })) || []

  // Generate hierarchy levels
  hierarchyLevels.value = [
    {
      name: 'Source Systems',
      color: 'blue',
      nodes: [{ id: 'bms', label: 'BMS', type: 'system' }]
    },
    {
      name: 'Measurements',
      color: 'green',
      nodes: props.measurements?.slice(0, 4).map(m => ({ id: m, label: m, type: 'measurement' })) || []
    },
    {
      name: 'Field Groups',
      color: 'orange',
      nodes: [
        { id: 'voltage', label: 'Voltage', type: 'field' },
        { id: 'current', label: 'Current', type: 'field' },
        { id: 'temperature', label: 'Temp', type: 'field' }
      ]
    }
  ]

  // Generate matrix data
  matrixData.value = props.measurements?.map(measurement => {
    const row = { measurement }
    props.measurements.forEach(otherMeasurement => {
      if (measurement === otherMeasurement) {
        row[otherMeasurement] = 1.00
      } else {
        row[otherMeasurement] = (Math.random() * 2 - 1).toFixed(2)
      }
    })
    return row
  }) || []
}

const selectNode = (node) => {
  $q.notify({
    type: 'info',
    message: `Selected: ${node.label}`,
    caption: 'Node details would be shown here'
  })
}

const showRelationshipDetails = (source, target, strength) => {
  $q.notify({
    type: 'info',
    message: `Relationship: ${source} ↔ ${target}`,
    caption: `Strength: ${strength}`
  })
}

const actOnInsight = (insight) => {
  $q.notify({
    type: 'info',
    message: `Acting on: ${insight.title}`,
    caption: 'Implementation details would be shown here'
  })
}

const openFullscreen = () => {
  showFullscreen.value = true
}

const exportVisualization = () => {
  $q.notify({
    type: 'positive',
    message: 'Visualization exported',
    caption: 'Export functionality coming soon'
  })
}

// Lifecycle
onMounted(() => {
  if (props.measurements?.length > 0) {
    analyzeRelationships()
  }
})
</script>

<style scoped>
.schema-relationships {
  width: 100%;
}

.visualization-container {
  position: relative;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.network-graph {
  position: relative;
  height: 400px;
}

.nodes-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.network-node {
  transition: transform 0.2s ease;
}

.network-node:hover {
  transform: scale(1.1);
  z-index: 10;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  font-weight: 500;
}

.node-label {
  margin-top: 4px;
  text-align: center;
  word-break: break-word;
}

.hierarchy-tree {
  padding: 20px;
}

.tree-level {
  margin-bottom: 30px;
}

.level-header {
  text-align: center;
  margin-bottom: 15px;
}

.level-nodes {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.hierarchy-node {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.hierarchy-node:hover {
  transform: translateY(-2px);
}

.relationship-matrix {
  overflow-x: auto;
}

.matrix-cell {
  min-width: 60px;
  font-size: 11px;
  font-weight: 500;
}

.text-h5 {
  font-weight: 600;
}

.q-chip {
  font-size: 11px;
}
</style>
