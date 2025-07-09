// src/utils/dataFormatter.js
// Advanced Data Formatter for Chart.js Integration
// Handles backend data transformation with Grafana-level features

import { format, parseISO, isValid } from 'date-fns'

// ==================== CONSTANTS ====================

// Professional color palette (16 colors) - Grafana inspired
export const CHART_COLORS = [
  '#FF6B6B', // Red
  '#4ECDC4', // Teal
  '#45B7D1', // Blue
  '#96CEB4', // Light Green
  '#FFEAA7', // Yellow
  '#DDA0DD', // Plum
  '#98D8C8', // Mint
  '#F7DC6F', // Gold
  '#BB8FCE', // Lavender
  '#85C1E9', // Sky Blue
  '#F8C471', // Orange
  '#82E0AA', // Light Green
  '#F1948A', // Pink
  '#85C1E9', // Light Blue
  '#D7BDE2', // Light Purple
  '#A3E4D7'  // Light Cyan
]

// Line style patterns for multiple signals
export const LINE_STYLES = [
  { borderDash: [], label: 'solid' },
  { borderDash: [5, 5], label: 'dashed' },
  { borderDash: [2, 8], label: 'dotted' },
  { borderDash: [10, 5, 2, 5], label: 'dash-dot' },
  { borderDash: [15, 3, 3, 3], label: 'dash-dot-dot' }
]

// Chart.js point styles
export const POINT_STYLES = [
  'circle', 'cross', 'crossRot', 'dash', 'line', 'rect', 'rectRounded', 'rectRot', 'star', 'triangle'
]

// ==================== CORE DATA TRANSFORMATION ====================

/**
 * Transform backend widget data to Chart.js format
 * @param {Object} backendData - Data from /widgets/{widget_id}/data endpoint
 * @param {Object} widgetConfig - Widget configuration from wizard
 * @param {Object} options - Additional formatting options
 * @returns {Object} Chart.js compatible data structure
 */
export function transformWidgetDataToChart(backendData, widgetConfig = {}, options = {}) {
  try {
    console.log('🔄 Transforming backend data to Chart.js format')
    console.log('📊 Backend data structure:', {
      isEmpty: backendData?.isEmpty,
      datasets: backendData?.datasets?.length || 0,
      labels: backendData?.labels?.length || 0,
      totalPoints: backendData?.totalPoints
    })

    // Handle empty data
    if (backendData?.isEmpty || !backendData?.datasets || backendData.datasets.length === 0) {
      return {
        labels: [],
        datasets: [],
        isEmpty: true,
        message: backendData?.message || 'No data available for the selected time range',
        metadata: {
          totalPoints: 0,
          timeRange: backendData?.timeRange || null,
          windowInfo: backendData?.window_info || null
        }
      }
    }

    // Extract styling configuration
    const stylingConfig = widgetConfig?.styling_config || {}
    const globalOptions = {
      showPoints: stylingConfig.show_points !== false,
      fillArea: stylingConfig.fill_area || false,
      lineWidth: stylingConfig.line_width || 2,
      pointRadius: stylingConfig.point_radius || 3,
      tension: stylingConfig.curve_smooth || 0.1,
      ...options
    }

    // Transform labels (timestamps)
    const labels = transformTimestamps(backendData.labels)

    // Transform datasets (signals)
    const datasets = transformDatasets(backendData.datasets, stylingConfig, globalOptions)

    // Prepare metadata
    const metadata = {
      totalPoints: backendData.totalPoints || 0,
      timeRange: backendData.timeRange || null,
      windowInfo: backendData.window_info || null,
      widgetInfo: backendData.widget_info || null,
      actualPoints: backendData.actual_points || 0,
      transformedAt: new Date().toISOString()
    }

    console.log('✅ Data transformation complete:', {
      labels: labels.length,
      datasets: datasets.length,
      totalPoints: metadata.totalPoints
    })

    return {
      labels,
      datasets,
      isEmpty: false,
      metadata
    }

  } catch (error) {
    console.error('❌ Data transformation failed:', error)
    return {
      labels: [],
      datasets: [],
      isEmpty: true,
      message: `Data transformation error: ${error.message}`,
      metadata: {
        error: true,
        errorMessage: error.message
      }
    }
  }
}

/**
 * Transform timestamp labels for Chart.js time scale
 * @param {Array} timestamps - Array of ISO timestamp strings
 * @returns {Array} Parsed Date objects for Chart.js
 */
export function transformTimestamps(timestamps) {
  if (!Array.isArray(timestamps)) {
    console.warn('⚠️ Invalid timestamps array:', timestamps)
    return []
  }

  return timestamps
    .map(timestamp => {
      try {
        // Handle multiple timestamp formats
        if (timestamp instanceof Date) {
          return timestamp
        }

        if (typeof timestamp === 'string') {
          const parsed = parseISO(timestamp)
          if (isValid(parsed)) {
            return parsed
          }

          // Fallback to native Date parsing
          const fallback = new Date(timestamp)
          if (isValid(fallback)) {
            return fallback
          }
        }

        console.warn('⚠️ Invalid timestamp:', timestamp)
        return null
      } catch (error) {
        console.warn('⚠️ Timestamp parsing error:', timestamp, error)
        return null
      }
    })
    .filter(date => date !== null)
}

/**
 * Transform backend datasets to Chart.js datasets
 * @param {Array} backendDatasets - Backend dataset array
 * @param {Object} stylingConfig - Widget styling configuration
 * @param {Object} globalOptions - Global formatting options
 * @returns {Array} Chart.js dataset array
 */
export function transformDatasets(backendDatasets, stylingConfig = {}, globalOptions = {}) {
  if (!Array.isArray(backendDatasets)) {
    console.warn('⚠️ Invalid datasets array:', backendDatasets)
    return []
  }

  return backendDatasets.map((dataset, index) => {
    try {
      // Extract dataset properties
      const {
        label = `Signal ${index + 1}`,
        data = [],
        unit = '',
        borderColor,
        backgroundColor,
        ...otherProps
      } = dataset

      // Generate colors if not provided
      const color = borderColor || getSignalColor(index)
      const bgColor = backgroundColor || `${color}20` // Add transparency

      // Transform data points
      const transformedData = transformDataPoints(data)

      // Apply styling with Chart.js optimizations
      const chartDataset = {
        label: formatSignalLabel(label, unit),
        data: transformedData,

        // Color and styling
        borderColor: color,
        backgroundColor: globalOptions.fillArea ? bgColor : 'transparent',
        pointBackgroundColor: color,
        pointBorderColor: color,

        // Line styling
        borderWidth: globalOptions.lineWidth,
        tension: globalOptions.tension,
        fill: globalOptions.fillArea,

        // Point styling
        pointRadius: globalOptions.showPoints ? globalOptions.pointRadius : 0,
        pointHoverRadius: globalOptions.showPoints ? globalOptions.pointRadius + 2 : 0,
        pointHitRadius: 10, // Larger hit area for better interaction

        // Performance optimizations
        spanGaps: true, // Connect lines across null values
        stepped: false, // Smooth lines by default

        // Hover effects
        hoverBorderWidth: globalOptions.lineWidth + 1,
        hoverBackgroundColor: color,

        // Custom properties for legends and interactions
        unit: unit,
        originalLabel: label,
        signalIndex: index,
        datasetType: 'line',

        // Apply line style variation for multiple signals
        ...applyLineStyle(index),

        // Merge any additional properties from backend
        ...otherProps
      }

      return chartDataset

    } catch (error) {
      console.error('❌ Dataset transformation error:', error, dataset)

      // Return safe fallback dataset
      return {
        label: `Error: ${dataset?.label || `Signal ${index + 1}`}`,
        data: [],
        borderColor: CHART_COLORS[index % CHART_COLORS.length],
        backgroundColor: 'transparent',
        borderWidth: 1,
        pointRadius: 0,
        hidden: true // Hide error datasets by default
      }
    }
  })
}

/**
 * Transform individual data points for Chart.js
 * @param {Array} dataPoints - Raw data values
 * @returns {Array} Chart.js data points
 */
export function transformDataPoints(dataPoints) {
  if (!Array.isArray(dataPoints)) {
    console.warn('⚠️ Invalid data points:', dataPoints)
    return []
  }

  return dataPoints.map((value, index) => {
    try {
      // Handle null/undefined values
      if (value === null || value === undefined || value === '') {
        return null
      }

      // Convert to number
      const numValue = Number(value)

      // Validate number
      if (!isFinite(numValue)) {
        return null
      }

      return numValue

    } catch (error) {
      console.warn('⚠️ Data point conversion error:', value, error)
      return null
    }
  })
}

// ==================== STYLING UTILITIES ====================

/**
 * Get color for signal by index with intelligent assignment
 * @param {number} index - Signal index
 * @returns {string} Hex color code
 */
export function getSignalColor(index) {
  return CHART_COLORS[index % CHART_COLORS.length]
}

/**
 * Apply line style variation for multiple signals
 * @param {number} index - Dataset index
 * @returns {Object} Line style properties
 */
export function applyLineStyle(index) {
  const styleIndex = Math.floor(index / CHART_COLORS.length)
  const style = LINE_STYLES[styleIndex % LINE_STYLES.length]

  return {
    borderDash: style.borderDash,
    lineStyle: style.label
  }
}

/**
 * Format signal label with unit
 * @param {string} label - Signal name
 * @param {string} unit - Signal unit
 * @returns {string} Formatted label
 */
export function formatSignalLabel(label, unit) {
  if (!label) return 'Unknown Signal'

  if (unit && unit.trim()) {
    return `${label} (${unit.trim()})`
  }

  return label
}

/**
 * Generate dataset colors for multiple signals
 * @param {number} count - Number of datasets
 * @returns {Array} Array of color objects
 */
export function generateDatasetColors(count) {
  const colors = []

  for (let i = 0; i < count; i++) {
    const baseColor = getSignalColor(i)
    colors.push({
      border: baseColor,
      background: `${baseColor}20`,
      point: baseColor,
      hover: baseColor
    })
  }

  return colors
}

// ==================== FORMATTING UTILITIES ====================

/**
 * Format Chart.js tooltip content
 * @param {Object} context - Chart.js tooltip context
 * @returns {string} Formatted tooltip text
 */
export function formatTooltipValue(context) {
  try {
    const value = context.parsed?.y
    const unit = context.dataset?.unit || ''

    if (value === null || value === undefined) {
      return 'No data'
    }

    // Format number with appropriate precision
    const formattedValue = formatNumericValue(value)

    return unit ? `${formattedValue} ${unit}` : formattedValue

  } catch (error) {
    console.warn('⚠️ Tooltip formatting error:', error)
    return 'Error'
  }
}

/**
 * Format numeric values with intelligent precision
 * @param {number} value - Numeric value
 * @returns {string} Formatted number string
 */
export function formatNumericValue(value) {
  if (value === null || value === undefined || !isFinite(value)) {
    return 'N/A'
  }

  const absValue = Math.abs(value)

  // Very small numbers
  if (absValue < 0.001 && absValue > 0) {
    return value.toExponential(2)
  }

  // Small decimal numbers
  if (absValue < 1) {
    return value.toFixed(4)
  }

  // Regular numbers
  if (absValue < 1000) {
    return value.toFixed(2)
  }

  // Large numbers with K/M notation
  if (absValue >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }

  if (absValue >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }

  return value.toString()
}

/**
 * Format window period information for display
 * @param {Object} windowInfo - Window information from backend
 * @returns {string} Formatted window description
 */
export function formatWindowPeriod(windowInfo) {
  if (!windowInfo) return 'Unknown'

  try {
    const { window_period, window_seconds, estimated_points, auto_calculated } = windowInfo

    if (auto_calculated) {
      return `Auto: ${formatSeconds(window_seconds)} (${estimated_points} pts)`
    } else {
      return `${window_period} (${estimated_points} pts)`
    }

  } catch (error) {
    console.warn('⚠️ Window period formatting error:', error)
    return 'Error'
  }
}

/**
 * Format seconds to human readable string
 * @param {number} seconds - Number of seconds
 * @returns {string} Formatted duration string
 */
export function formatSeconds(seconds) {
  if (!seconds || seconds < 0) return '0s'

  const units = [
    { label: 'd', value: 86400 },
    { label: 'h', value: 3600 },
    { label: 'm', value: 60 },
    { label: 's', value: 1 }
  ]

  for (const unit of units) {
    if (seconds >= unit.value) {
      const value = Math.floor(seconds / unit.value)
      return `${value}${unit.label}`
    }
  }

  return `${seconds}s`
}

// ==================== VALIDATION UTILITIES ====================

/**
 * Validate Chart.js data structure
 * @param {Object} chartData - Chart.js data object
 * @returns {Object} Validation result
 */
export function validateChartData(chartData) {
  const issues = []

  try {
    // Check basic structure
    if (!chartData || typeof chartData !== 'object') {
      issues.push('Chart data must be an object')
      return { valid: false, issues }
    }

    // Check labels
    if (!Array.isArray(chartData.labels)) {
      issues.push('Labels must be an array')
    } else if (chartData.labels.length === 0) {
      issues.push('No data labels provided')
    }

    // Check datasets
    if (!Array.isArray(chartData.datasets)) {
      issues.push('Datasets must be an array')
    } else if (chartData.datasets.length === 0) {
      issues.push('No datasets provided')
    } else {
      // Validate each dataset
      chartData.datasets.forEach((dataset, index) => {
        if (!dataset.label) {
          issues.push(`Dataset ${index}: Missing label`)
        }

        if (!Array.isArray(dataset.data)) {
          issues.push(`Dataset ${index}: Data must be an array`)
        } else if (dataset.data.length !== chartData.labels.length) {
          issues.push(`Dataset ${index}: Data length (${dataset.data.length}) doesn't match labels length (${chartData.labels.length})`)
        }

        if (!dataset.borderColor) {
          issues.push(`Dataset ${index}: Missing border color`)
        }
      })
    }

    return {
      valid: issues.length === 0,
      issues: issues,
      datasetCount: chartData.datasets?.length || 0,
      pointCount: chartData.labels?.length || 0
    }

  } catch (error) {
    return {
      valid: false,
      issues: [`Validation error: ${error.message}`]
    }
  }
}

// ==================== MOCK DATA GENERATORS ====================

/**
 * Generate mock chart data for testing
 * @param {Object} options - Generation options
 * @returns {Object} Mock Chart.js data
 */
export function generateMockChartData(options = {}) {
  const {
    signalCount = 2,
    pointCount = 100,
    timeRange = { start: new Date(Date.now() - 3600000), end: new Date() },
    signalNames = ['Temperature', 'Humidity', 'Pressure', 'Voltage'],
    units = ['°C', '%', 'Pa', 'V']
  } = options

  // Generate timestamps
  const startTime = new Date(timeRange.start)
  const endTime = new Date(timeRange.end)
  const timeStep = (endTime - startTime) / (pointCount - 1)

  const labels = Array.from({ length: pointCount }, (_, i) =>
    new Date(startTime.getTime() + i * timeStep)
  )

  // Generate datasets
  const datasets = Array.from({ length: signalCount }, (_, i) => ({
    label: signalNames[i] || `Signal ${i + 1}`,
    data: Array.from({ length: pointCount }, () =>
      Math.random() * 100 + 50 + Math.sin(Date.now() / 10000) * 20
    ),
    borderColor: getSignalColor(i),
    backgroundColor: `${getSignalColor(i)}20`,
    borderWidth: 2,
    fill: false,
    tension: 0.1,
    pointRadius: 3,
    unit: units[i] || '',
    ...applyLineStyle(i)
  }))

  return {
    labels,
    datasets,
    isEmpty: false,
    metadata: {
      totalPoints: pointCount,
      timeRange: {
        start: startTime.toISOString(),
        end: endTime.toISOString()
      },
      mock: true
    }
  }
}

// ==================== EXPORTS ====================

export default {
  // Core transformation
  transformWidgetDataToChart,
  transformTimestamps,
  transformDatasets,
  transformDataPoints,

  // Styling utilities
  getSignalColor,
  applyLineStyle,
  formatSignalLabel,
  generateDatasetColors,

  // Formatting utilities
  formatTooltipValue,
  formatNumericValue,
  formatWindowPeriod,
  formatSeconds,

  // Validation
  validateChartData,

  // Mock data
  generateMockChartData,

  // Constants
  CHART_COLORS,
  LINE_STYLES,
  POINT_STYLES
}
