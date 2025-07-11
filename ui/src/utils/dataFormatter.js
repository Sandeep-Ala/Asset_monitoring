// src/utils/dataFormatter.js - FIXED VERSION
// Critical fixes for validation function and chart data processing
// FIXES: validateChartData function returning proper validation object

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

// ==================== CRITICAL FIX: CHART DATA VALIDATION ====================

/**
 * FIXED: Validate chart data structure for Chart.js compatibility
 * @param {Object} chartData - Chart data to validate
 * @returns {Object} Validation result with isValid, errors, and warnings
 */
export function validateChartData(chartData) {
  console.log('🔍 Validating chart data:', chartData)

  const errors = []
  const warnings = []

  if (!chartData) {
    errors.push('Chart data is null or undefined')
    return {
      isValid: false,
      errors,
      warnings,
      structure: { labelsCount: 0, datasetsCount: 0, totalDataPoints: 0, isEmpty: true }
    }
  }

  // Check for required Chart.js structure
  if (!Array.isArray(chartData.labels)) {
    errors.push('Missing or invalid labels array')
  }

  if (!Array.isArray(chartData.datasets)) {
    errors.push('Missing or invalid datasets array')
  }

  // Validate datasets structure
  if (chartData.datasets && Array.isArray(chartData.datasets)) {
    chartData.datasets.forEach((dataset, index) => {
      if (!dataset.label) {
        warnings.push(`Dataset ${index} missing label`)
      }
      if (!Array.isArray(dataset.data)) {
        errors.push(`Dataset ${index} has invalid data array`)
      }
      if (!dataset.borderColor && !dataset.backgroundColor) {
        warnings.push(`Dataset ${index} missing color configuration`)
      }
    })
  }

  // Check data consistency
  if (chartData.labels && chartData.datasets && Array.isArray(chartData.labels) && Array.isArray(chartData.datasets)) {
    const labelsCount = chartData.labels.length
    chartData.datasets.forEach((dataset, index) => {
      if (dataset.data && Array.isArray(dataset.data) && dataset.data.length !== labelsCount) {
        warnings.push(`Dataset ${index} data length (${dataset.data.length}) doesn't match labels length (${labelsCount})`)
      }
    })
  }

  const structure = {
    labelsCount: chartData.labels?.length || 0,
    datasetsCount: chartData.datasets?.length || 0,
    totalDataPoints: chartData.datasets?.reduce((total, dataset) =>
      total + (dataset.data?.length || 0), 0) || 0,
    isEmpty: chartData.isEmpty || false
  }

  const result = {
    isValid: errors.length === 0,
    errors,
    warnings,
    structure
  }

  console.log('✅ Chart data validation result:', result)
  return result
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

      console.warn('⚠️ Could not parse timestamp:', timestamp)
      return new Date()
    } catch (error) {
      console.warn('⚠️ Error parsing timestamp:', timestamp, error)
      return new Date()
    }
  })
}

/**
 * Extract date context from backend data
 */
function extractDateContext(backendData) {
  // Try to get date range from timeRange first
  if (backendData.timeRange) {
    const startDate = new Date(backendData.timeRange.start)
    const endDate = new Date(backendData.timeRange.end)

    if (isValid(startDate) && isValid(endDate)) {
      return { startDate, endDate }
    }
  }

  // Fallback to metadata
  if (backendData.metadata?.timeRange) {
    const startDate = new Date(backendData.metadata.timeRange.start)
    const endDate = new Date(backendData.metadata.timeRange.end)

    if (isValid(startDate) && isValid(endDate)) {
      return { startDate, endDate }
    }
  }

  // Default fallback
  const now = new Date()
  const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000)

  return {
    startDate: weekAgo,
    endDate: now
  }
}

/**
 * Combine time-only string with date range
 */
function combineTimeWithDateRange(timeString, index, totalPoints, dateContext) {
  try {
    const timeParts = timeString.split(':')
    const hours = parseInt(timeParts[0], 10)
    const minutes = parseInt(timeParts[1], 10)
    const secondsPart = timeParts[2] || '0'
    const seconds = parseFloat(secondsPart)
    const milliseconds = seconds >= Math.floor(seconds) ?
      Math.round((seconds % 1) * 1000) : 0

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
    const lineStyle = getLineStyle(stylingConfig?.lineStyles?.[index] || 'solid')

    console.log(`📊 Transformed dataset "${label}":`, {
      originalDataLength: data.length,
      chartDataLength: chartData.length,
      unit,
      color
    })

    return {
      label: unit ? `${label} (${unit})` : label,
      data: chartData,
      borderColor: color,
      backgroundColor: color + '20', // 20% opacity
      borderWidth: 2,
      pointRadius: stylingConfig?.pointRadius || 2,
      pointHoverRadius: stylingConfig?.pointRadius ? stylingConfig.pointRadius + 2 : 4,
      fill: false,
      tension: 0.1,
      ...lineStyle
    }
  } catch (error) {
    console.error('❌ Error transforming dataset:', error)
    return {
      label: 'Error Dataset',
      data: [],
      borderColor: '#f44336',
      backgroundColor: '#f4433620'
    }
  }
}

/**
 * Map data values to chart labels
 */
function mapDataToLabels(data, chartLabels, backendLabels) {
  if (!Array.isArray(data) || !Array.isArray(chartLabels)) {
    return []
  }

  return data.map((value, index) => {
    const timestamp = chartLabels[index] || new Date()
    return {
      x: timestamp,
      y: typeof value === 'number' ? value : parseFloat(value) || 0
    }
  })
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Get color for signal by index
 */
export function getSignalColor(index) {
  return CHART_COLORS[index % CHART_COLORS.length]
}

/**
 * Get line style configuration
 */
function getLineStyle(styleType) {
  switch (styleType) {
    case 'dashed': return LINE_STYLES[1]
    case 'dotted': return LINE_STYLES[2]
    case 'dash-dot': return LINE_STYLES[3]
    case 'long-dash': return LINE_STYLES[4]
    default: return LINE_STYLES[0] // solid
  }
}

/**
 * Format numeric value with appropriate units
 */
export function formatNumericValue(value, precision = 2) {
  if (typeof value !== 'number' || isNaN(value)) {
    return '0'
  }

  if (Math.abs(value) >= 1000000) {
    return (value / 1000000).toFixed(precision) + 'M'
  } else if (Math.abs(value) >= 1000) {
    return (value / 1000).toFixed(precision) + 'K'
  } else {
    return value.toFixed(precision)
  }
}

/**
 * Generate mock chart data for testing
 */
export function generateMockChartData(pointCount = 50) {
  const labels = []
  const data = []
  const now = new Date()

  for (let i = 0; i < pointCount; i++) {
    const timestamp = new Date(now - (pointCount - i) * 60000) // 1 minute intervals
    labels.push(timestamp)
    data.push({
      x: timestamp,
      y: Math.random() * 100 + Math.sin(i * 0.1) * 20
    })
  }

  return {
    labels,
    datasets: [{
      label: 'Mock Data',
      data,
      borderColor: getSignalColor(0),
      backgroundColor: getSignalColor(0) + '20',
      borderWidth: 2,
      pointRadius: 2,
      fill: false,
      tension: 0.1
    }],
    isEmpty: false,
    metadata: {
      totalPoints: pointCount,
      timeRange: {
        start: labels[0],
        end: labels[labels.length - 1]
      }
    }
  }
}

// Export all functions
export {
  CHART_COLORS,
  LINE_STYLES,
  // formatNumericValue
}
