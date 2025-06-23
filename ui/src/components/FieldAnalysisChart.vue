<!-- ui/src/components/FieldAnalysisChart.vue -->
<!-- Field data visualization component -->

<template>
  <div class="field-analysis-chart">
    <!-- Chart Controls -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">
              <q-icon name="bar_chart" class="q-mr-sm" />
              Field Analysis Visualization
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md items-end">
              <!-- Chart Type -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="chartType"
                  :options="chartTypeOptions"
                  label="Chart Type"
                  outlined
                  dense
                  @update:model-value="updateChart"
                />
              </div>

              <!-- Visualization Mode -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="visualizationMode"
                  :options="visualizationOptions"
                  label="Visualization"
                  outlined
                  dense
                  @update:model-value="updateChart"
                />
              </div>

              <!-- Time Range -->
              <div class="col-12 col-md-3">
                <q-select
                  v-model="timeRange"
                  :options="timeRangeOptions"
                  label="Time Range"
                  outlined
                  dense
                  @update:model-value="updateChart"
                />
              </div>

              <!-- Actions -->
              <div class="col-12 col-md-3">
                <div class="row q-gutter-sm">
                  <q-btn
                    label="Update"
                    icon="refresh"
                    color="primary"
                    @click="refreshChart"
                    :loading="loading"
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
                    @click="exportChart"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Chart Display Area -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="timeline" class="q-mr-sm" />
              {{ getChartTitle() }}
            </div>
          </q-card-section>
          <q-card-section>
            <div class="chart-container" style="min-height: 400px;">
              <!-- Line Chart -->
              <div v-if="chartType === 'line'" class="line-chart">
                <div v-if="!chartData || chartData.length === 0" class="text-center q-pa-xl">
                  <q-icon name="show_chart" size="4rem" class="text-grey-4 q-mb-md" />
                  <div class="text-h6 text-grey-6">No Data Available</div>
                  <div class="text-body2 text-grey-5 q-mb-lg">
                    Select a field with time-series data to view trends
                  </div>
                </div>
                <div v-else class="chart-content">
                  <!-- Simplified SVG chart representation -->
                  <svg class="chart-svg" width="100%" height="300" viewBox="0 0 800 300">
                    <!-- Chart background grid -->
                    <defs>
                      <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#e0e0e0" stroke-width="1"/>
                      </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />

                    <!-- Chart axes -->
                    <line x1="60" y1="260" x2="740" y2="260" stroke="#333" stroke-width="2"/>
                    <line x1="60" y1="260" x2="60" y2="40" stroke="#333" stroke-width="2"/>

                    <!-- Chart line -->
                    <polyline
                      :points="chartPoints"
                      fill="none"
                      stroke="#2196F3"
                      stroke-width="3"
                    />

                    <!-- Data points -->
                    <circle
                      v-for="(point, index) in chartDataPoints"
                      :key="index"
                      :cx="point.x"
                      :cy="point.y"
                      r="4"
                      fill="#2196F3"
                      @click="showDataPoint(point, index)"
                      style="cursor: pointer;"
                    />

                    <!-- Axis labels -->
                    <text x="400" y="290" text-anchor="middle" class="chart-label">Time</text>
                    <text x="30" y="150" text-anchor="middle" transform="rotate(-90 30 150)" class="chart-label">{{ field?.fieldName || 'Value' }}</text>
                  </svg>
                </div>
              </div>

              <!-- Bar Chart -->
              <div v-else-if="chartType === 'bar'" class="bar-chart">
                <div class="chart-content">
                  <svg class="chart-svg" width="100%" height="300" viewBox="0 0 800 300">
                    <!-- Chart background -->
                    <rect width="100%" height="100%" fill="#fafafa" />

                    <!-- Chart axes -->
                    <line x1="60" y1="260" x2="740" y2="260" stroke="#333" stroke-width="2"/>
                    <line x1="60" y1="260" x2="60" y2="40" stroke="#333" stroke-width="2"/>

                    <!-- Bars -->
                    <rect
                      v-for="(bar, index) in barData"
                      :key="index"
                      :x="bar.x"
                      :y="bar.y"
                      :width="bar.width"
                      :height="bar.height"
                      :fill="bar.color"
                      @click="showBarData(bar, index)"
                      style="cursor: pointer;"
                    />

                    <!-- Bar labels -->
                    <text
                      v-for="(bar, index) in barData"
                      :key="`label-${index}`"
                      :x="bar.x + bar.width / 2"
                      :y="bar.y - 5"
                      text-anchor="middle"
                      class="bar-label"
                    >
                      {{ bar.value }}
                    </text>
                  </svg>
                </div>
              </div>

              <!-- Histogram -->
              <div v-else-if="chartType === 'histogram'" class="histogram-chart">
                <div class="chart-content">
                  <svg class="chart-svg" width="100%" height="300" viewBox="0 0 800 300">
                    <!-- Chart background -->
                    <rect width="100%" height="100%" fill="#fafafa" />

                    <!-- Chart axes -->
                    <line x1="60" y1="260" x2="740" y2="260" stroke="#333" stroke-width="2"/>
                    <line x1="60" y1="260" x2="60" y2="40" stroke="#333" stroke-width="2"/>

                    <!-- Histogram bars -->
                    <rect
                      v-for="(bin, index) in histogramBins"
                      :key="index"
                      :x="bin.x"
                      :y="bin.y"
                      :width="bin.width"
                      :height="bin.height"
                      fill="#4CAF50"
                      stroke="white"
                      stroke-width="1"
                      @click="showBinData(bin, index)"
                      style="cursor: pointer;"
                    />

                    <!-- Axis labels -->
                    <text x="400" y="290" text-anchor="middle" class="chart-label">Value Range</text>
                    <text x="30" y="150" text-anchor="middle" transform="rotate(-90 30 150)" class="chart-label">Frequency</text>
                  </svg>
                </div>
              </div>

              <!-- Scatter Plot -->
              <div v-else-if="chartType === 'scatter'" class="scatter-chart">
                <div class="chart-content">
                  <svg class="chart-svg" width="100%" height="300" viewBox="0 0 800 300">
                    <!-- Chart background -->
                    <rect width="100%" height="100%" fill="#fafafa" />

                    <!-- Chart axes -->
                    <line x1="60" y1="260" x2="740" y2="260" stroke="#333" stroke-width="2"/>
                    <line x1="60" y1="260" x2="60" y2="40" stroke="#333" stroke-width="2"/>

                    <!-- Scatter points -->
                    <circle
                      v-for="(point, index) in scatterPoints"
                      :key="index"
                      :cx="point.x"
                      :cy="point.y"
                      :r="point.size || 3"
                      :fill="point.color || '#FF9800'"
                      :opacity="point.opacity || 0.7"
                      @click="showScatterPoint(point, index)"
                      style="cursor: pointer;"
                    />

                    <!-- Trend line if enabled -->
                    <line
                      v-if="showTrendLine && trendLine"
                      :x1="trendLine.x1"
                      :y1="trendLine.y1"
                      :x2="trendLine.x2"
                      :y2="trendLine.y2"
                      stroke="#F44336"
                      stroke-width="2"
                      stroke-dasharray="5,5"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Chart Statistics -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="text-h6">
              <q-icon name="functions" class="q-mr-sm" />
              Statistical Summary
            </div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-6">
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Count</q-item-label>
                      <q-item-label>{{ statistics.count }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Mean</q-item-label>
                      <q-item-label>{{ statistics.mean }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Median</q-item-label>
                      <q-item-label>{{ statistics.median }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              <div class="col-6">
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Std Dev</q-item-label>
                      <q-item-label>{{ statistics.stdDev }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Min</q-item-label>
                      <q-item-label>{{ statistics.min }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Max</q-item-label>
                      <q-item-label>{{ statistics.max }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Chart Options -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-purple-1">
            <div class="text-h6">
              <q-icon name="tune" class="q-mr-sm" />
              Chart Options
            </div>
          </q-card-section>
          <q-card-section>
            <div class="column q-gutter-sm">
              <q-toggle
                v-model="showTrendLine"
                label="Show Trend Line"
                @update:model-value="updateChart"
              />
              <q-toggle
                v-model="showDataPoints"
                label="Show Data Points"
                @update:model-value="updateChart"
              />
              <q-toggle
                v-model="showGridLines"
                label="Show Grid Lines"
                @update:model-value="updateChart"
              />
              <q-toggle
                v-model="showLegend"
                label="Show Legend"
                @update:model-value="updateChart"
              />
              <q-toggle
                v-model="animateChart"
                label="Animate Chart"
                @update:model-value="updateChart"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Insights -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="text-h6">
              <q-icon name="insights" class="q-mr-sm" />
              Data Insights
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="insights.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="lightbulb" size="2rem" class="q-mb-sm" />
              <div>No insights available</div>
              <div class="text-caption">Chart analysis will generate insights automatically</div>
            </div>
            <q-list v-else dense>
              <q-item v-for="insight in insights" :key="insight.id">
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
                  <q-chip
                    :color="getInsightColor(insight.type)"
                    text-color="white"
                    size="sm"
                  >
                    {{ insight.confidence }}%
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Fullscreen Dialog -->
    <q-dialog v-model="showFullscreen" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ getChartTitle() }} - Full View</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showFullscreen = false" />
        </q-card-section>
        <q-card-section class="scroll">
          <!-- Enhanced full-screen chart would go here -->
          <div class="text-center q-pa-xl">
            <q-icon name="bar_chart" size="6rem" class="text-grey-4 q-mb-md" />
            <div class="text-h5 text-grey-6">Enhanced Chart View</div>
            <div class="text-body1 text-grey-5">
              Full-featured chart with advanced analytics and interactivity
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Data Point Details Dialog -->
    <q-dialog v-model="showDataDialog">
      <q-card style="min-width: 300px">
        <q-card-section>
          <div class="text-h6">Data Point Details</div>
        </q-card-section>
        <q-card-section v-if="selectedDataPoint">
          <q-list dense>
            <q-item>
              <q-item-section>
                <q-item-label caption>Value</q-item-label>
                <q-item-label>{{ selectedDataPoint.value }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label caption>Timestamp</q-item-label>
                <q-item-label>{{ selectedDataPoint.timestamp }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="selectedDataPoint.context">
              <q-item-section>
                <q-item-label caption>Context</q-item-label>
                <q-item-label>{{ selectedDataPoint.context }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showDataDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  field: {
    type: Object,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  sampleData: {
    type: Array,
    default: () => []
  }
})

// Reactive data
const $q = useQuasar()
const chartType = ref('line')
const visualizationMode = ref('timeseries')
const timeRange = ref('24h')
const loading = ref(false)
const showFullscreen = ref(false)
const showDataDialog = ref(false)
const selectedDataPoint = ref(null)

// Chart options
const showTrendLine = ref(true)
const showDataPoints = ref(true)
const showGridLines = ref(true)
const showLegend = ref(false)
const animateChart = ref(true)

// Chart data
const chartData = ref([])
const chartDataPoints = ref([])
const barData = ref([])
const histogramBins = ref([])
const scatterPoints = ref([])
const trendLine = ref(null)
const statistics = ref({})
const insights = ref([])

// Computed properties
const chartTypeOptions = [
  { label: 'Line Chart', value: 'line' },
  { label: 'Bar Chart', value: 'bar' },
  { label: 'Histogram', value: 'histogram' },
  { label: 'Scatter Plot', value: 'scatter' }
]

const visualizationOptions = [
  { label: 'Time Series', value: 'timeseries' },
  { label: 'Distribution', value: 'distribution' },
  { label: 'Correlation', value: 'correlation' },
  { label: 'Trend Analysis', value: 'trend' }
]

const timeRangeOptions = [
  { label: 'Last Hour', value: '1h' },
  { label: 'Last 24 Hours', value: '24h' },
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'All Time', value: 'all' }
]

const chartPoints = computed(() => {
  return chartDataPoints.value.map(point => `${point.x},${point.y}`).join(' ')
})

// Methods
const getChartTitle = () => {
  const titles = {
    line: 'Time Series Analysis',
    bar: 'Value Distribution',
    histogram: 'Data Distribution',
    scatter: 'Correlation Analysis'
  }
  return `${props.field?.fieldName || 'Field'} - ${titles[chartType.value] || 'Chart'}`
}

const generateChartData = () => {
  const dataPoints = props.sampleData.length > 0 ? props.sampleData : generateSampleData()

  // Generate line chart data
  chartDataPoints.value = dataPoints.map((point, index) => ({
    x: 80 + (index * 600 / Math.max(dataPoints.length - 1, 1)),
    y: 260 - ((point.value - statistics.value.min) / (statistics.value.max - statistics.value.min)) * 200,
    value: point.value,
    timestamp: point.timestamp,
    index
  }))

  // Generate bar chart data
  const categories = groupDataByCategory(dataPoints)
  barData.value = Object.entries(categories).map(([category, values], index) => ({
    x: 80 + index * 80,
    y: 260 - (values.length / Math.max(...Object.values(categories).map(v => v.length)) * 200),
    width: 60,
    height: (values.length / Math.max(...Object.values(categories).map(v => v.length)) * 200),
    color: `hsl(${index * 60}, 70%, 50%)`,
    value: values.length,
    category
  }))

  // Generate histogram bins
  const bins = createHistogramBins(dataPoints, 10)
  histogramBins.value = bins.map((bin, index) => ({
    x: 80 + index * 60,
    y: 260 - (bin.count / Math.max(...bins.map(b => b.count)) * 200),
    width: 55,
    height: (bin.count / Math.max(...bins.map(b => b.count)) * 200),
    count: bin.count,
    range: `${bin.min.toFixed(1)}-${bin.max.toFixed(1)}`
  }))

  // Generate scatter points (correlation with time)
  scatterPoints.value = dataPoints.map((point, index) => ({
    x: 80 + (index / Math.max(dataPoints.length - 1, 1)) * 600,
    y: 260 - ((point.value - statistics.value.min) / (statistics.value.max - statistics.value.min)) * 200,
    size: 4 + Math.random() * 3,
    color: `hsl(${(point.value / statistics.value.max) * 240}, 70%, 50%)`,
    opacity: 0.7,
    value: point.value,
    timestamp: point.timestamp
  }))

  // Generate trend line
  if (chartDataPoints.value.length > 1) {
    const firstPoint = chartDataPoints.value[0]
    const lastPoint = chartDataPoints.value[chartDataPoints.value.length - 1]
    trendLine.value = {
      x1: firstPoint.x,
      y1: firstPoint.y,
      x2: lastPoint.x,
      y2: lastPoint.y
    }
  }
}

const generateSampleData = () => {
  const data = []
  const now = Date.now()
  const fieldName = props.field?.fieldName?.toLowerCase() || 'value'

  // Generate different patterns based on field type
  for (let i = 0; i < 50; i++) {
    let value

    if (fieldName.includes('voltage')) {
      value = 45 + Math.sin(i * 0.2) * 5 + Math.random() * 2
    } else if (fieldName.includes('current')) {
      value = 10 + Math.cos(i * 0.3) * 3 + Math.random() * 1
    } else if (fieldName.includes('temperature')) {
      value = 25 + Math.sin(i * 0.1) * 8 + Math.random() * 3
    } else {
      value = 50 + Math.random() * 100
    }

    data.push({
      value: Math.max(0, value),
      timestamp: new Date(now - (49 - i) * 60000).toISOString()
    })
  }

  return data
}

const calculateStatistics = (data) => {
  if (data.length === 0) return {}

  const values = data.map(d => d.value).sort((a, b) => a - b)
  const sum = values.reduce((a, b) => a + b, 0)
  const mean = sum / values.length
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length

  return {
    count: values.length,
    mean: mean.toFixed(2),
    median: values[Math.floor(values.length / 2)].toFixed(2),
    stdDev: Math.sqrt(variance).toFixed(2),
    min: Math.min(...values).toFixed(2),
    max: Math.max(...values).toFixed(2)
  }
}

const groupDataByCategory = (data) => {
  // Simple categorization based on value ranges
  const categories = { Low: [], Medium: [], High: [] }
  const max = Math.max(...data.map(d => d.value))

  data.forEach(point => {
    if (point.value < max * 0.33) categories.Low.push(point)
    else if (point.value < max * 0.67) categories.Medium.push(point)
    else categories.High.push(point)
  })

  return categories
}

const createHistogramBins = (data, binCount) => {
  const values = data.map(d => d.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const binSize = (max - min) / binCount

  const bins = []
  for (let i = 0; i < binCount; i++) {
    const binMin = min + i * binSize
    const binMax = min + (i + 1) * binSize
    const count = values.filter(v => v >= binMin && v < binMax).length
    bins.push({ min: binMin, max: binMax, count })
  }

  return bins
}

const generateInsights = (data) => {
  const insights = []

  if (data.length === 0) return insights

  // Trend analysis
  const firstHalf = data.slice(0, Math.floor(data.length / 2))
  const secondHalf = data.slice(Math.floor(data.length / 2))
  const firstAvg = firstHalf.reduce((sum, d) => sum + d.value, 0) / firstHalf.length
  const secondAvg = secondHalf.reduce((sum, d) => sum + d.value, 0) / secondHalf.length

  if (secondAvg > firstAvg * 1.1) {
    insights.push({
      id: 1,
      type: 'trend',
      title: 'Increasing Trend Detected',
      description: `Values have increased by ${((secondAvg - firstAvg) / firstAvg * 100).toFixed(1)}% over time`,
      confidence: 85
    })
  } else if (secondAvg < firstAvg * 0.9) {
    insights.push({
      id: 2,
      type: 'trend',
      title: 'Decreasing Trend Detected',
      description: `Values have decreased by ${((firstAvg - secondAvg) / firstAvg * 100).toFixed(1)}% over time`,
      confidence: 85
    })
  }

  // Outlier detection
  const mean = data.reduce((sum, d) => sum + d.value, 0) / data.length
  const stdDev = Math.sqrt(data.reduce((sum, d) => sum + Math.pow(d.value - mean, 2), 0) / data.length)
  const outliers = data.filter(d => Math.abs(d.value - mean) > 2 * stdDev)

  if (outliers.length > 0) {
    insights.push({
      id: 3,
      type: 'outlier',
      title: 'Outliers Detected',
      description: `Found ${outliers.length} data points that deviate significantly from the mean`,
      confidence: 92
    })
  }

  // Seasonality detection (simplified)
  if (data.length > 20) {
    const peaks = findPeaks(data.map(d => d.value))
    if (peaks.length > 3) {
      insights.push({
        id: 4,
        type: 'pattern',
        title: 'Cyclic Pattern Detected',
        description: `Data shows recurring patterns with approximately ${Math.floor(data.length / peaks.length)} point intervals`,
        confidence: 78
      })
    }
  }

  return insights
}

const findPeaks = (values) => {
  const peaks = []
  for (let i = 1; i < values.length - 1; i++) {
    if (values[i] > values[i - 1] && values[i] > values[i + 1]) {
      peaks.push(i)
    }
  }
  return peaks
}

const getInsightIcon = (type) => {
  const icons = {
    trend: 'trending_up',
    outlier: 'warning',
    pattern: 'waves',
    quality: 'verified'
  }
  return icons[type] || 'info'
}

const getInsightColor = (type) => {
  const colors = {
    trend: 'primary',
    outlier: 'warning',
    pattern: 'secondary',
    quality: 'positive'
  }
  return colors[type] || 'grey'
}

const updateChart = () => {
  const dataPoints = props.sampleData.length > 0 ? props.sampleData : generateSampleData()
  chartData.value = dataPoints
  statistics.value = calculateStatistics(dataPoints)
  generateChartData()
  insights.value = generateInsights(dataPoints)
}

const refreshChart = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateChart()

    $q.notify({
      type: 'positive',
      message: 'Chart updated successfully'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to update chart',
      caption: error.message
    })
  } finally {
    loading.value = false
  }
}

const openFullscreen = () => {
  showFullscreen.value = true
}

const exportChart = () => {
  // Create downloadable data
  const data = {
    field: props.field,
    chartType: chartType.value,
    data: chartData.value,
    statistics: statistics.value,
    insights: insights.value,
    exportDate: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.field?.fieldName || 'field'}-analysis-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Chart data exported successfully'
  })
}

const showDataPoint = (point, index) => {
  selectedDataPoint.value = {
    value: point.value?.toFixed(2) || 'N/A',
    timestamp: point.timestamp || `Point ${index + 1}`,
    context: `Data point ${index + 1} of ${chartDataPoints.value.length}`
  }
  showDataDialog.value = true
}

const showBarData = (bar, index) => {
  selectedDataPoint.value = {
    value: bar.value,
    timestamp: bar.category,
    context: `Category: ${bar.category} with ${bar.value} items`
  }
  showDataDialog.value = true
}

const showBinData = (bin, index) => {
  selectedDataPoint.value = {
    value: bin.count,
    timestamp: bin.range,
    context: `Value range ${bin.range} contains ${bin.count} data points`
  }
  showDataDialog.value = true
}

const showScatterPoint = (point, index) => {
  selectedDataPoint.value = {
    value: point.value?.toFixed(2) || 'N/A',
    timestamp: point.timestamp || `Point ${index + 1}`,
    context: `Scatter point ${index + 1} - correlation analysis`
  }
  showDataDialog.value = true
}

// Watchers
watch(() => props.field, () => {
  updateChart()
}, { immediate: false })

watch(() => props.sampleData, () => {
  updateChart()
}, { deep: true })

// Lifecycle
onMounted(() => {
  updateChart()
})
</script>

<style scoped>
.field-analysis-chart {
  width: 100%;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.chart-content {
  width: 100%;
  height: 100%;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.chart-label {
  font-size: 12px;
  fill: #666;
  font-family: 'Roboto', sans-serif;
}

.bar-label {
  font-size: 11px;
  fill: #333;
  font-weight: 500;
}

.line-chart, .bar-chart, .histogram-chart, .scatter-chart {
  width: 100%;
  height: 300px;
}

.q-chip {
  font-size: 11px;
}

/* Chart animations */
.chart-svg circle,
.chart-svg rect,
.chart-svg polyline {
  transition: all 0.3s ease;
}

.chart-svg circle:hover,
.chart-svg rect:hover {
  opacity: 0.8;
  transform: scale(1.1);
}

/* Responsive design */
@media (max-width: 600px) {
  .chart-svg {
    height: 250px;
  }

  .chart-label {
    font-size: 10px;
  }

  .bar-label {
    font-size: 9px;
  }
}
</style>
