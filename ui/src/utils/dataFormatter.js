// src/utils/dataFormatter.js - FIXED VERSION
// Critical fixes for timestamp processing and chart data ordering
// FIXES: Time-only timestamps, chronological ordering, date range display

import { parseISO, isValid, format } from 'date-fns'

// ==================== PROFESSIONAL COLOR PALETTE ====================

const CHART_COLORS = [
  '#2196F3', // Blue
  '#4CAF50', // Green
  '#FF9800', // Orange
  '#9C27B0', // Purple
  '#F44336', // Red
  '#00BCD4', // Cyan
  '#FFEB3B', // Yellow
  '#795548', // Brown
  '#607D8B', // Blue Grey
  '#E91E63', // Pink
  '#3F51B5', // Indigo
  '#8BC34A', // Light Green
  '#FF5722', // Deep Orange
  '#673AB7', // Deep Purple
  '#009688', // Teal
  '#FFC107'  // Amber
]

const LINE_STYLES = [
  {},                                    // Solid
  { borderDash: [5, 5] },               // Dashed
  { borderDash: [2, 2] },               // Dotted
  { borderDash: [10, 5, 2, 5] },        // Dash-dot
  { borderDash: [15, 3, 3, 3] }         // Long dash-dot
]

// ==================== MAIN TRANSFORMATION FUNCTION ====================

/**
 * Transform backend widget data to Chart.js compatible format
 * FIXED: Proper timestamp handling for multi-day ranges and chronological ordering
 * @param {Object} backendData - Raw data from backend API
 * @param {Object} widgetConfig - Widget configuration
 * @param {Object} options - Transformation options
 * @returns {Object} Chart.js compatible data object
 */
export function transformWidgetDataToChart(backendData, widgetConfig = {}, options = {}) {
  console.log('🔄 Transforming backend data to Chart.js format')
  console.log('📊 Backend data structure:', {
    isEmpty: backendData?.isEmpty,
    datasets: backendData?.datasets?.length || 0,
    labels: backendData?.labels?.length || 0,
    totalPoints: backendData?.totalPoints
  })

  try {
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

    // CRITICAL FIX: Transform timestamps with proper date handling
    const chartLabels = transformTimestampsWithDates(backendLabels, backendData)

    // Transform datasets with proper data point mapping and ensure chronological order
    const chartDatasets = backendDatasets.map((dataset, index) => {
      return transformDataset(dataset, chartLabels, backendLabels, index, widgetConfig, options)
    })

    // CRITICAL FIX: Sort the entire chart data by timestamp to ensure chronological order
    const sortedChartData = sortChartDataChronologically(chartLabels, chartDatasets)

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
      labels: sortedChartData.labels.length,
      datasets: sortedChartData.datasets.length,
      totalPoints: metadata.totalPoints,
      firstDataPoint: sortedChartData.datasets[0]?.data[0],
      timeRange: {
        start: sortedChartData.labels[0],
        end: sortedChartData.labels[sortedChartData.labels.length - 1]
      }
    })

    return {
      labels: sortedChartData.labels,
      datasets: sortedChartData.datasets,
      isEmpty: false,
      metadata: metadata
    }

  } catch (error) {
    console.error('❌ Data transformation failed:', error)
    return {
      labels: [],
      datasets: [],
      isEmpty: true,
      message: `Transformation error: ${error.message}`,
      metadata: { totalPoints: 0 }
    }
  }
}

// ==================== CRITICAL FIX: TIMESTAMP TRANSFORMATION ====================

/**
 * Transform timestamp labels with proper date handling
 * FIXED: Handles time-only strings by combining with query date range
 * @param {Array} timestamps - Array of timestamp strings
 * @param {Object} backendData - Backend data for context
 * @returns {Array} Array of Date objects in chronological order
 */
function transformTimestampsWithDates(timestamps, backendData = {}) {
  if (!Array.isArray(timestamps)) {
    console.warn('⚠️ Invalid timestamps array:', timestamps)
    return []
  }

  console.log('🕒 Transforming timestamps:', {
    count: timestamps.length,
    firstTimestamp: timestamps[0],
    lastTimestamp: timestamps[timestamps.length - 1],
    hasTimeRange: !!backendData.timeRange
  })

  // CRITICAL FIX: Get the actual date range from the query or time range
  const dateContext = extractDateContext(backendData)

  return timestamps.map((timestamp, index) => {
    try {
      // Handle different timestamp formats
      if (timestamp instanceof Date) {
        return timestamp
      }

      if (typeof timestamp === 'string') {
        // Full ISO format (with date) - preferred
        if (timestamp.includes('T') || timestamp.includes('-')) {
          const parsed = parseISO(timestamp)
          if (isValid(parsed)) {
            return parsed
          }
        }

        // CRITICAL FIX: Time only format (HH:mm:ss) - combine with actual date range
        if (timestamp.match(/^\d{2}:\d{2}:\d{2}(\.\d+)?$/)) {
          return combineTimeWithDateRange(timestamp, index, timestamps.length, dateContext)
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
 * Extract date context from backend data
 * FIXED: Gets actual query date range instead of defaulting to today
 */
function extractDateContext(backendData) {
  try {
    // Try to get date range from widget_info query
    const queryString = backendData.widget_info?.query_executed
    if (queryString) {
      // Extract timestamps from query like: WHERE t_sampling_time >= '2025-03-01T08:20:00.000Z'
      const startMatch = queryString.match(/t_sampling_time >= '([^']+)'/)
      const endMatch = queryString.match(/t_sampling_time <= '([^']+)'/)

      if (startMatch && endMatch) {
        return {
          startDate: new Date(startMatch[1]),
          endDate: new Date(endMatch[1]),
          source: 'query'
        }
      }
    }

    // Try timeRange from API request
    if (backendData.timeRange?.start && backendData.timeRange?.end) {
      return {
        startDate: new Date(backendData.timeRange.start),
        endDate: new Date(backendData.timeRange.end),
        source: 'timeRange'
      }
    }

    // Fallback to current date
    console.warn('⚠️ Could not extract date context, using current date')
    return {
      startDate: new Date(),
      endDate: new Date(),
      source: 'fallback'
    }
  } catch (error) {
    console.warn('⚠️ Error extracting date context:', error)
    return {
      startDate: new Date(),
      endDate: new Date(),
      source: 'error'
    }
  }
}

/**
 * Combine time-only string with actual date range
 * CRITICAL FIX: Distributes times across the actual date range instead of using single day
 */
function combineTimeWithDateRange(timeString, index, totalPoints, dateContext) {
  try {
    const [hours, minutes, seconds] = timeString.split(':').map(Number)
    const milliseconds = seconds % 1 > 0 ? Math.round((seconds % 1) * 1000) : 0

    // CRITICAL FIX: Calculate actual date based on position in time range
    const startDate = dateContext.startDate
    const endDate = dateContext.endDate
    const totalDuration = endDate.getTime() - startDate.getTime()

    // Interpolate the date based on the index position
    const progress = totalPoints > 1 ? index / (totalPoints - 1) : 0
    const targetTimestamp = startDate.getTime() + (totalDuration * progress)
    const targetDate = new Date(targetTimestamp)

    // Set the specific time while keeping the interpolated date
    const result = new Date(targetDate)
    result.setHours(hours, minutes, Math.floor(seconds), milliseconds)

    return result
  } catch (error) {
    console.warn('⚠️ Error combining time with date range:', timeString, error)
    return new Date()
  }
}

// ==================== CRITICAL FIX: CHRONOLOGICAL SORTING ====================

/**
 * Sort chart data chronologically to prevent zig-zag patterns
 * FIXED: Sorts both labels and all dataset data points together
 */
function sortChartDataChronologically(labels, datasets) {
  try {
    // Create array of indices with timestamps for sorting
    const indexedData = labels.map((label, index) => ({
      timestamp: label,
      index: index
    }))

    // Sort by timestamp
    indexedData.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())

    // Extract sorted indices
    const sortedIndices = indexedData.map(item => item.index)

    // Apply sorted order to labels
    const sortedLabels = sortedIndices.map(index => labels[index])

    // Apply sorted order to all datasets
    const sortedDatasets = datasets.map(dataset => ({
      ...dataset,
      data: sortedIndices.map(index => dataset.data[index])
    }))

    console.log('🔄 Data sorted chronologically:', {
      originalOrder: labels.slice(0, 3).map(l => l.toISOString()),
      sortedOrder: sortedLabels.slice(0, 3).map(l => l.toISOString())
    })

    return {
      labels: sortedLabels,
      datasets: sortedDatasets
    }
  } catch (error) {
    console.error('❌ Error sorting chart data:', error)
    return { labels, datasets }
  }
}

// ==================== DATASET TRANSFORMATION ====================

/**
 * Transform a single dataset for Chart.js
 * @param {Object} dataset - Backend dataset
 * @param {Array} chartLabels - Transformed chart labels
 * @param {Array} backendLabels - Original backend labels
 * @param {number} index - Dataset index
 * @param {Object} widgetConfig - Widget configuration
 * @param {Object} options - Transformation options
 * @returns {Object} Chart.js dataset object
 */
function transformDataset(dataset, chartLabels, backendLabels, index, widgetConfig, options) {
  try {
    const data = dataset.data || []
    const label = dataset.label || `Signal ${index + 1}`
    const unit = dataset.unit || ''

    // Map data values to chart labels creating {x, y} objects for Chart.js
    const chartData = mapDataToLabels(data, chartLabels, backendLabels)

    // Get styling configuration
    const stylingConfig = widgetConfig?.styling_config || {}
    const color = getSignalColor(index)
    const lineStyle = getLineStyle(stylingConfig?.line_styles?.[index] || 'solid')

    console.log(`📊 Transformed dataset "${label}":`, {
      originalDataLength: data.length,
      chartDataLength: chartData.length,
      unit: unit,
      color: color
    })

    return {
      label: label,
      data: chartData,
      borderColor: color,
      backgroundColor: 'transparent',
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
      originalLength: data.length
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
 * @returns {Object} Chart.js line style configuration
 */
export function getLineStyle(styleType) {
  const styles = {
    'solid': {},
    'dashed': { borderDash: [5, 5] },
    'dotted': { borderDash: [2, 2] },
    'dashdot': { borderDash: [10, 5, 2, 5] },
    'longdash': { borderDash: [15, 3, 3, 3] }
  }

  return styles[styleType] || styles['solid']
}

// ==================== VALIDATION ====================

/**
 * Validate Chart.js data structure
 * @param {Object} chartData - Chart data to validate
 * @returns {boolean} True if valid
 */
export function validateChartData(chartData) {
  try {
    if (!chartData || typeof chartData !== 'object') {
      return false
    }

    if (chartData.isEmpty) {
      return true // Empty data is valid
    }

    // Check datasets
    if (!Array.isArray(chartData.datasets)) {
      console.warn('⚠️ Chart data validation failed: datasets is not an array')
      return false
    }

    // Validate each dataset
    for (const dataset of chartData.datasets) {
      if (!Array.isArray(dataset.data)) {
        console.warn('⚠️ Chart data validation failed: dataset.data is not an array')
        return false
      }

      // Check if data points have x,y structure for time series
      for (const point of dataset.data) {
        if (typeof point !== 'object' || !point.hasOwnProperty('x') || !point.hasOwnProperty('y')) {
          console.warn('⚠️ Chart data validation failed: data point missing x,y structure')
          return false
        }
      }
    }

    return true

  } catch (error) {
    console.error('❌ Chart data validation error:', error)
    return false
  }
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Format numeric value with intelligent notation
 * @param {number} value - Numeric value
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted value
 */
export function formatNumericValue(value, precision = 2) {
  if (typeof value !== 'number' || isNaN(value)) {
    return '0'
  }

  const absValue = Math.abs(value)

  if (absValue >= 1000000) {
    return (value / 1000000).toFixed(precision) + 'M'
  } else if (absValue >= 1000) {
    return (value / 1000).toFixed(precision) + 'K'
  } else {
    return value.toFixed(precision)
  }
}

/**
 * Generate mock chart data for testing
 * @param {Object} options - Mock data options
 * @returns {Object} Mock chart data
 */
export function generateMockChartData(options = {}) {
  const {
    pointCount = 50,
    signalCount = 1,
    timeRange = 24 * 60 * 60 * 1000, // 24 hours
    baseValue = 50,
    variance = 20
  } = options

  const startTime = new Date()
  const timeStep = timeRange / pointCount

  const labels = Array.from({ length: pointCount }, (_, i) =>
    new Date(startTime.getTime() + i * timeStep)
  )

  const datasets = Array.from({ length: signalCount }, (_, signalIndex) => ({
    label: `Signal ${signalIndex + 1}`,
    data: labels.map((time, i) => ({
      x: time,
      y: baseValue + Math.sin(i * 0.1) * variance + (Math.random() - 0.5) * 10
    })),
    borderColor: getSignalColor(signalIndex),
    backgroundColor: 'transparent',
    borderWidth: 2,
    tension: 0.1,
    pointRadius: 2
  }))

  return {
    labels,
    datasets,
    isEmpty: false,
    metadata: {
      totalPoints: pointCount * signalCount,
      timeRange: { start: startTime, end: labels[labels.length - 1] },
      isMockData: true
    }
  }
}
