// src/utils/dataFormatter.js
// FIXED VERSION - Backend Data Structure Support
// Handles backend data transformation with proper Chart.js format

import { format, parseISO, isValid } from 'date-fns'

// ==================== CONSTANTS ====================

// Professional color palette (16 colors) - Grafana inspired
export const CHART_COLORS = [
  '#2196F3', // Blue (matches your data)
  '#FF6B6B', // Red
  '#4ECDC4', // Teal
  '#45B7D1', // Light Blue
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

// ==================== CORE TRANSFORMATION ====================

/**
 * Transform backend widget data to Chart.js format
 * FIXED: Now handles backend structure with separate labels and datasets arrays
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

    // Extract labels and datasets from backend
    const backendLabels = backendData.labels || []
    const backendDatasets = backendData.datasets || []

    console.log('📋 Processing data:', {
      labelsCount: backendLabels.length,
      datasetsCount: backendDatasets.length,
      firstLabel: backendLabels[0],
      firstDataset: backendDatasets[0]?.label
    })

    // Transform timestamps to Date objects for Chart.js
    const chartLabels = transformTimestamps(backendLabels, backendData)

    // Transform datasets with proper data point mapping
    const chartDatasets = backendDatasets.map((dataset, index) => {
      return transformDataset(dataset, chartLabels, backendLabels, index, widgetConfig, options)
    })

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
      labels: chartLabels.length,
      datasets: chartDatasets.length,
      totalPoints: metadata.totalPoints,
      firstDataPoint: chartDatasets[0]?.data[0]
    })

    return {
      labels: chartLabels,
      datasets: chartDatasets,
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
 * Transform individual dataset with proper data point mapping
 * @param {Object} dataset - Backend dataset object
 * @param {Array} chartLabels - Transformed chart labels (Date objects)
 * @param {Array} backendLabels - Original backend labels
 * @param {number} index - Dataset index for styling
 * @param {Object} widgetConfig - Widget configuration
 * @param {Object} options - Additional options
 * @returns {Object} Chart.js dataset
 */
function transformDataset(dataset, chartLabels, backendLabels, index, widgetConfig = {}, options = {}) {
  try {
    const {
      label = `Signal ${index + 1}`,
      data = [],
      unit = '',
      borderColor,
      backgroundColor,
      ...otherProps
    } = dataset

    // Map data values to chart labels
    const chartData = mapDataToLabels(data, chartLabels, backendLabels)

    // Generate colors if not provided
    const color = borderColor || getSignalColor(index)
    const bgColor = backgroundColor || `${color}20` // Add transparency

    // Extract styling configuration
    const stylingConfig = widgetConfig?.styling_config || {}
    const lineStyle = getLineStyle(stylingConfig?.line_style, index)

    console.log(`📊 Transformed dataset "${label}":`, {
      originalDataLength: data.length,
      chartDataLength: chartData.length,
      unit: unit,
      color: color
    })

    return {
      label: formatSignalLabel(label, unit),
      data: chartData,

      // Color and styling
      borderColor: color,
      backgroundColor: stylingConfig.fill_area ? bgColor : 'transparent',
      pointBackgroundColor: color,
      pointBorderColor: '#ffffff',

      // Line styling
      borderWidth: stylingConfig.line_width || 2,
      tension: stylingConfig.curve_smooth || 0.1,
      fill: stylingConfig.fill_area || false,

      // Point styling
      pointRadius: stylingConfig.show_points !== false ? (stylingConfig.point_radius || 3) : 0,
      pointHoverRadius: stylingConfig.show_points !== false ? 6 : 0,
      pointBorderWidth: 1,

      // Line style pattern
      ...lineStyle,

      // Metadata
      unit: unit,
      originalLength: data.length,

      // Pass through other properties
      ...otherProps
    }

  } catch (error) {
    console.error('❌ Dataset transformation failed:', error)
    return {
      label: `Error: ${dataset?.label || 'Unknown'}`,
      data: [],
      borderColor: '#ff0000',
      backgroundColor: 'transparent'
    }
  }
}

/**
 * Map data values to chart labels creating {x, y} objects for Chart.js
 * @param {Array} dataValues - Array of numeric values
 * @param {Array} chartLabels - Array of Date objects
 * @param {Array} backendLabels - Original backend labels
 * @returns {Array} Array of {x, y} objects for Chart.js
 */
function mapDataToLabels(dataValues, chartLabels, backendLabels) {
  if (!Array.isArray(dataValues) || !Array.isArray(chartLabels)) {
    console.warn('⚠️ Invalid data or labels for mapping:', {
      dataValues: Array.isArray(dataValues),
      chartLabels: Array.isArray(chartLabels)
    })
    return []
  }

  const minLength = Math.min(dataValues.length, chartLabels.length)

  return Array.from({ length: minLength }, (_, i) => ({
    x: chartLabels[i],
    y: dataValues[i]
  }))
}

/**
 * Transform timestamp labels for Chart.js time scale
 * @param {Array} timestamps - Array of timestamp strings (e.g., ["04:52:00", "05:07:09"])
 * @param {Object} backendData - Backend data for context
 * @returns {Array} Array of Date objects for Chart.js
 */
function transformTimestamps(timestamps, backendData = {}) {
  if (!Array.isArray(timestamps)) {
    console.warn('⚠️ Invalid timestamps array:', timestamps)
    return []
  }

  // Get the base date from timeRange if available
  const baseDate = getBaseDate(backendData)

  return timestamps.map((timestamp, index) => {
    try {
      // Handle different timestamp formats
      if (timestamp instanceof Date) {
        return timestamp
      }

      if (typeof timestamp === 'string') {
        // ISO format (with date)
        if (timestamp.includes('T') || timestamp.includes('-')) {
          const parsed = parseISO(timestamp)
          if (isValid(parsed)) {
            return parsed
          }
        }

        // Time only format (HH:mm:ss) - combine with base date
        if (timestamp.match(/^\d{2}:\d{2}:\d{2}$/)) {
          const [hours, minutes, seconds] = timestamp.split(':')
          const date = new Date(baseDate)
          date.setHours(parseInt(hours), parseInt(minutes), parseInt(seconds), 0)
          return date
        }

        // Fallback to native Date parsing
        const fallback = new Date(timestamp)
        if (isValid(fallback)) {
          return fallback
        }
      }

      console.warn(`⚠️ Could not parse timestamp at index ${index}:`, timestamp)
      return new Date()

    } catch (error) {
      console.warn('⚠️ Timestamp parsing error:', timestamp, error)
      return new Date()
    }
  })
}

/**
 * Get base date for time-only timestamps
 * @param {Object} backendData - Backend data object
 * @returns {Date} Base date to use for time-only timestamps
 */
function getBaseDate(backendData) {
  try {
    // Try to get date from widget_info query or timeRange
    const queryString = backendData.widget_info?.query_executed
    if (queryString) {
      const dateMatch = queryString.match(/TIMESTAMP '(\d{4}-\d{2}-\d{2})/)
      if (dateMatch) {
        return new Date(dateMatch[1] + 'T00:00:00.000Z')
      }
    }

    // Try timeRange start
    if (backendData.timeRange?.start) {
      return new Date(backendData.timeRange.start)
    }

    // Default to today
    return new Date()
  } catch (error) {
    console.warn('⚠️ Could not determine base date:', error)
    return new Date()
  }
}

// ==================== STYLING UTILITIES ====================

/**
 * Get signal color by index
 * @param {number} index - Dataset index
 * @param {number} alpha - Alpha transparency (0-1)
 * @returns {string} Color string
 */
export function getSignalColor(index, alpha = 1) {
  const color = CHART_COLORS[index % CHART_COLORS.length]

  if (alpha === 1) {
    return color
  }

  // Convert hex to rgba with alpha
  const hex = color.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * Get line style configuration
 * @param {string} styleType - Style type ('solid', 'dashed', etc.)
 * @param {number} index - Dataset index for fallback
 * @returns {Object} Chart.js line style configuration
 */
function getLineStyle(styleType, index = 0) {
  const styles = {
    'solid': {},
    'dashed': { borderDash: [5, 5] },
    'dotted': { borderDash: [2, 2] },
    'dashdot': { borderDash: [10, 5, 2, 5] },
    'dashdotdot': { borderDash: [15, 3, 3, 3] }
  }

  // Use specified style or default based on index
  return styles[styleType] || LINE_STYLES[index % LINE_STYLES.length] || {}
}

/**
 * Format signal label with unit
 * @param {string} label - Signal label
 * @param {string} unit - Signal unit
 * @returns {string} Formatted label
 */
function formatSignalLabel(label, unit) {
  if (!unit) return label
  return `${label} (${unit})`
}

// ==================== FORMATTING UTILITIES ====================

/**
 * Format numeric value for display
 * @param {number} value - Numeric value
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted value
 */
export function formatNumericValue(value, precision = 2) {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A'
  }

  const absValue = Math.abs(value)

  if (absValue >= 1000000) {
    return `${(value / 1000000).toFixed(precision)}M`
  } else if (absValue >= 1000) {
    return `${(value / 1000).toFixed(precision)}K`
  } else if (absValue < 0.01 && absValue > 0) {
    return value.toExponential(precision)
  } else {
    return value.toFixed(precision)
  }
}

/**
 * Format window period for display
 * @param {Object} windowInfo - Window information object
 * @returns {string} Formatted window period
 */
export function formatWindowPeriod(windowInfo) {
  if (!windowInfo) return 'Auto'

  try {
    if (windowInfo.window_period) {
      return windowInfo.window_period
    }

    if (windowInfo.window_seconds) {
      const seconds = windowInfo.window_seconds
      if (seconds >= 3600) {
        return `${(seconds / 3600).toFixed(1)}h`
      } else if (seconds >= 60) {
        return `${(seconds / 60).toFixed(1)}m`
      } else {
        return `${seconds.toFixed(1)}s`
      }
    }

    return 'Auto'
  } catch (error) {
    console.warn('⚠️ Window period formatting error:', error)
    return 'Error'
  }
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
        if (!Array.isArray(dataset.data)) {
          issues.push(`Dataset ${index}: Data must be an array`)
        } else if (dataset.data.length === 0) {
          issues.push(`Dataset ${index}: No data points`)
        } else if (chartData.labels.length > 0 && dataset.data.length !== chartData.labels.length) {
          issues.push(`Dataset ${index}: Data length (${dataset.data.length}) doesn't match labels length (${chartData.labels.length})`)
        }
      })
    }

    return { valid: issues.length === 0, issues }

  } catch (error) {
    console.error('❌ Chart data validation error:', error)
    return { valid: false, issues: [`Validation error: ${error.message}`] }
  }
}

// ==================== MOCK DATA GENERATION ====================

/**
 * Generate mock chart data for testing
 * @param {Object} options - Mock data options
 * @returns {Object} Mock Chart.js data
 */
export function generateMockChartData(options = {}) {
  const {
    pointCount = 50,
    signalCount = 2,
    signalNames = ['Temperature', 'Humidity'],
    units = ['°C', '%'],
    timeRange = {
      start: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      end: new Date().toISOString()
    }
  } = options

  // Generate time series labels
  const startTime = new Date(timeRange.start)
  const endTime = new Date(timeRange.end)
  const timeStep = (endTime - startTime) / (pointCount - 1)

  const labels = Array.from({ length: pointCount }, (_, i) =>
    new Date(startTime.getTime() + i * timeStep)
  )

  // Generate datasets
  const datasets = Array.from({ length: signalCount }, (_, i) => ({
    label: signalNames[i] || `Signal ${i + 1}`,
    data: labels.map((label, j) => ({
      x: label,
      y: Math.random() * 100 + 50 + Math.sin(j / 10) * 20
    })),
    borderColor: getSignalColor(i),
    backgroundColor: getSignalColor(i, 0.1),
    borderWidth: 2,
    fill: false,
    tension: 0.1,
    pointRadius: 3,
    unit: units[i] || '',
    ...getLineStyle(null, i)
  }))

  return {
    labels,
    datasets,
    isEmpty: false,
    metadata: {
      totalPoints: pointCount,
      timeRange: timeRange,
      mock: true
    }
  }
}

// ==================== EXPORTS ====================

export default {
  // Core transformation
  transformWidgetDataToChart,

  // Styling utilities
  getSignalColor,
  formatSignalLabel,

  // Formatting utilities
  formatNumericValue,
  formatWindowPeriod,

  // Validation
  validateChartData,

  // Mock data
  generateMockChartData,

  // Constants
  CHART_COLORS,
  LINE_STYLES
}
