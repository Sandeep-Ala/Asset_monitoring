// src/utils/chartUtils.js
// Chart Utilities and Helpers for Widget System
// Provides Chart.js configuration, data formatting, and utility functions

import { date } from 'quasar'

// ==================== CHART.JS CONFIGURATION ====================

/**
 * Default Chart.js configuration with optimizations for time-series data
 */
export const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    title: {
      display: true,
      font: {
        size: 16,
        weight: 'bold'
      }
    },
    legend: {
      display: true,
      position: 'top',
      onClick: (e, legendItem, legend) => {
        // Custom legend click to toggle dataset visibility
        const index = legendItem.datasetIndex
        const chart = legend.chart
        const meta = chart.getDatasetMeta(index)

        // Toggle visibility
        meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null
        chart.update()
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: '#666',
      borderWidth: 1,
      cornerRadius: 6,
      displayColors: true,
      callbacks: {
        title: function(context) {
          // Format timestamp in tooltip
          return formatTooltipTime(context[0].label)
        },
        label: function(context) {
          const label = context.dataset.label || ''
          const value = typeof context.parsed.y === 'number' ?
            context.parsed.y.toFixed(4) : context.parsed.y
          const unit = context.dataset.unit || ''
          return `${label}: ${value} ${unit}`.trim()
        }
      }
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'x',
        onZoomComplete: function({chart}) {
          // Emit zoom event for synchronization
          window.dispatchEvent(new CustomEvent('chartZoomed', {
            detail: {
              chartId: chart.canvas.id,
              scale: chart.scales.x
            }
          }))
        }
      },
      pan: {
        enabled: true,
        mode: 'x',
        onPanComplete: function({chart}) {
          // Emit pan event for synchronization
          window.dispatchEvent(new CustomEvent('chartPanned', {
            detail: {
              chartId: chart.canvas.id,
              scale: chart.scales.x
            }
          }))
        }
      }
    }
  },
  scales: {
    x: {
      type: 'time',
      display: true,
      title: {
        display: true,
        text: 'Time'
      },
      time: {
        tooltipFormat: 'MMM DD, YYYY HH:mm:ss',
        displayFormats: {
          millisecond: 'HH:mm:ss.SSS',
          second: 'HH:mm:ss',
          minute: 'HH:mm',
          hour: 'MMM DD, HH:mm',
          day: 'MMM DD',
          week: 'MMM DD',
          month: 'MMM YYYY',
          quarter: 'MMM YYYY',
          year: 'YYYY'
        }
      },
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Value'
      },
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.1)'
      },
      ticks: {
        callback: function(value) {
          // Format large numbers
          return formatAxisValue(value)
        }
      }
    }
  },
  elements: {
    point: {
      radius: 2,
      hoverRadius: 6,
      hitRadius: 10
    },
    line: {
      borderWidth: 2,
      tension: 0.1 // Smooth curves
    }
  },
  animation: {
    duration: 750,
    easing: 'easeInOutQuart'
  }
}

// ==================== COLOR MANAGEMENT ====================

/**
 * Professional color palette for multi-signal charts
 */
export const signalColorPalette = [
  '#2196F3', // Blue
  '#4CAF50', // Green
  '#FF9800', // Orange
  '#F44336', // Red
  '#9C27B0', // Purple
  '#00BCD4', // Cyan
  '#FF5722', // Deep Orange
  '#607D8B', // Blue Grey
  '#795548', // Brown
  '#E91E63', // Pink
  '#3F51B5', // Indigo
  '#009688', // Teal
  '#FFEB3B', // Yellow
  '#8BC34A', // Light Green
  '#FFC107', // Amber
  '#673AB7'  // Deep Purple
]

/**
 * Get color for signal by index with transparency options
 */
export function getSignalColor(index, alpha = 1) {
  const baseColor = signalColorPalette[index % signalColorPalette.length]

  if (alpha === 1) {
    return baseColor
  }

  // Convert hex to rgba
  const hex = baseColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * Generate color scheme for dataset based on styling config
 */
export function generateDatasetColors(stylingConfig, datasetIndex) {
  const customColors = stylingConfig?.colors || []

  if (customColors[datasetIndex]) {
    return {
      borderColor: customColors[datasetIndex],
      backgroundColor: getSignalColor(datasetIndex, 0.1)
    }
  }

  return {
    borderColor: getSignalColor(datasetIndex),
    backgroundColor: getSignalColor(datasetIndex, 0.1)
  }
}

// ==================== DATA TRANSFORMATION ====================

/**
 * Transform backend widget data to Chart.js format
 */
export function transformWidgetDataToChart(backendData, widgetConfig) {
  try {
    console.log('📊 Transforming widget data to Chart.js format:', backendData)

    if (!backendData || backendData.isEmpty) {
      return createEmptyChartData(backendData?.message || 'No data available')
    }

    const { labels, datasets } = backendData

    if (!labels || !datasets || datasets.length === 0) {
      return createEmptyChartData('Invalid data format')
    }

    // Transform datasets
    const transformedDatasets = datasets.map((dataset, index) => {
      const colors = generateDatasetColors(widgetConfig?.styling_config, index)
      const lineStyle = getLineStyle(widgetConfig?.styling_config?.lineStyles?.[index])

      return {
        label: dataset.label || `Signal ${index + 1}`,
        data: transformDataPoints(labels, dataset.data),
        borderColor: colors.borderColor,
        backgroundColor: colors.backgroundColor,
        borderWidth: 2,
        fill: false,
        tension: 0.1,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: colors.borderColor,
        pointBorderColor: '#fff',
        pointBorderWidth: 1,
        unit: dataset.unit || '',
        ...lineStyle
      }
    })

    return {
      datasets: transformedDatasets,
      isEmpty: false,
      metadata: {
        totalPoints: backendData.totalPoints || 0,
        timeRange: backendData.timeRange,
        windowInfo: backendData.window_info,
        widgetInfo: backendData.widget_info
      }
    }

  } catch (error) {
    console.error('❌ Error transforming chart data:', error)
    return createEmptyChartData('Data transformation error')
  }
}

/**
 * Transform data points to Chart.js time format
 */
function transformDataPoints(labels, dataValues) {
  if (!labels || !dataValues) return []

  return labels.map((label, index) => ({
    x: parseTimestamp(label),
    y: dataValues[index]
  }))
}

/**
 * Parse timestamp to Date object for Chart.js
 */
function parseTimestamp(timestamp) {
  try {
    // Handle various timestamp formats
    if (timestamp instanceof Date) {
      return timestamp
    }

    if (typeof timestamp === 'string') {
      // ISO format
      if (timestamp.includes('T')) {
        return new Date(timestamp)
      }

      // Time only format (HH:mm:ss)
      if (timestamp.match(/^\d{2}:\d{2}:\d{2}$/)) {
        const today = new Date()
        const [hours, minutes, seconds] = timestamp.split(':')
        return new Date(today.getFullYear(), today.getMonth(), today.getDate(), hours, minutes, seconds)
      }
    }

    // Fallback
    return new Date(timestamp)
  } catch (error) {
    console.warn('⚠️ Failed to parse timestamp:', timestamp, error)
    return new Date()
  }
}

/**
 * Get line style configuration
 */
function getLineStyle(styleType) {
  const styles = {
    'solid': {},
    'dashed': { borderDash: [5, 5] },
    'dotted': { borderDash: [2, 2] },
    'dashdot': { borderDash: [10, 5, 2, 5] }
  }

  return styles[styleType] || styles['solid']
}

/**
 * Create empty chart data structure
 */
function createEmptyChartData(message = 'No data available') {
  return {
    datasets: [],
    isEmpty: true,
    message: message,
    metadata: {
      totalPoints: 0,
      timeRange: null,
      windowInfo: null,
      widgetInfo: null
    }
  }
}

// ==================== TIME FORMATTING ====================

/**
 * Format timestamp for chart axis labels
 */
export function formatAxisTime(timestamp, timeRange) {
  try {
    const date = new Date(timestamp)
    const duration = timeRange ? new Date(timeRange.end) - new Date(timeRange.start) : 0

    // Auto-format based on time range duration
    if (duration <= 60 * 60 * 1000) { // 1 hour or less
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } else if (duration <= 24 * 60 * 60 * 1000) { // 1 day or less
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (duration <= 7 * 24 * 60 * 60 * 1000) { // 1 week or less
      return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  } catch (error) {
    console.warn('⚠️ Failed to format axis time:', timestamp, error)
    return String(timestamp)
  }
}

/**
 * Format timestamp for tooltip display
 */
export function formatTooltipTime(timestamp) {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    console.warn('⚠️ Failed to format tooltip time:', timestamp, error)
    return String(timestamp)
  }
}

/**
 * Format axis values (handle large numbers)
 */
export function formatAxisValue(value) {
  if (typeof value !== 'number') return value

  if (Math.abs(value) >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (Math.abs(value) >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  } else if (Math.abs(value) < 1 && value !== 0) {
    return value.toFixed(4)
  } else {
    return value.toFixed(2)
  }
}

/**
 * Format window period for display
 */
export function formatWindowPeriod(windowInfo) {
  if (!windowInfo) return 'Unknown'

  const { windowPeriod, estimatedPoints, autoCalculated } = windowInfo

  if (windowPeriod === 'auto') {
    return `Auto (${estimatedPoints} points)`
  }

  const periodLabels = {
    '1sec': '1 second',
    '5sec': '5 seconds',
    '30sec': '30 seconds',
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 hour',
    '6h': '6 hours',
    '12h': '12 hours',
    '24h': '24 hours'
  }

  const label = periodLabels[windowPeriod] || windowPeriod
  return `${label} (${estimatedPoints} points)`
}

// ==================== CHART SYNCHRONIZATION ====================

/**
 * Synchronize zoom across multiple charts
 */
export function synchronizeChartZoom(sourceChart, targetCharts) {
  if (!sourceChart || !targetCharts) return

  const sourceScale = sourceChart.scales.x
  const { min, max } = sourceScale

  targetCharts.forEach(chart => {
    if (chart && chart !== sourceChart) {
      chart.zoomScale('x', { min, max }, 'none')
    }
  })
}

/**
 * Reset zoom on all charts
 */
export function resetAllChartsZoom(charts) {
  if (!charts) return

  charts.forEach(chart => {
    if (chart && typeof chart.resetZoom === 'function') {
      chart.resetZoom()
    }
  })
}

/**
 * Setup chart synchronization listeners
 */
export function setupChartSynchronization(charts) {
  // Listen for zoom events
  window.addEventListener('chartZoomed', (event) => {
    const { chartId, scale } = event.detail
    const sourceChart = charts.find(chart => chart.canvas.id === chartId)
    const targetCharts = charts.filter(chart => chart.canvas.id !== chartId)

    if (sourceChart) {
      synchronizeChartZoom(sourceChart, targetCharts)
    }
  })

  // Listen for pan events
  window.addEventListener('chartPanned', (event) => {
    const { chartId, scale } = event.detail
    const sourceChart = charts.find(chart => chart.canvas.id === chartId)
    const targetCharts = charts.filter(chart => chart.canvas.id !== chartId)

    if (sourceChart) {
      synchronizeChartZoom(sourceChart, targetCharts)
    }
  })
}

// ==================== CHART CONFIGURATION HELPERS ====================

/**
 * Create chart configuration for line chart
 */
export function createLineChartConfig(widgetConfig, chartData) {
  const config = {
    type: 'line',
    data: chartData,
    options: {
      ...defaultChartOptions,
      plugins: {
        ...defaultChartOptions.plugins,
        title: {
          ...defaultChartOptions.plugins.title,
          text: widgetConfig?.widget_label || 'Line Chart'
        }
      }
    }
  }

  // Apply custom styling
  if (widgetConfig?.styling_config) {
    applyCustomStyling(config, widgetConfig.styling_config)
  }

  return config
}

/**
 * Create chart configuration for bar chart
 */
export function createBarChartConfig(widgetConfig, chartData) {
  const config = {
    type: 'bar',
    data: chartData,
    options: {
      ...defaultChartOptions,
      plugins: {
        ...defaultChartOptions.plugins,
        title: {
          ...defaultChartOptions.plugins.title,
          text: widgetConfig?.widget_label || 'Bar Chart'
        }
      }
    }
  }

  // Remove zoom/pan for bar charts (usually not needed)
  delete config.options.plugins.zoom

  // Apply custom styling
  if (widgetConfig?.styling_config) {
    applyCustomStyling(config, widgetConfig.styling_config)
  }

  return config
}

/**
 * Apply custom styling configuration to chart
 */
function applyCustomStyling(chartConfig, stylingConfig) {
  // Show/hide legend
  if (stylingConfig.showLegend !== undefined) {
    chartConfig.options.plugins.legend.display = stylingConfig.showLegend
  }

  // Custom grid settings
  if (stylingConfig.showGrid !== undefined) {
    chartConfig.options.scales.x.grid.display = stylingConfig.showGrid
    chartConfig.options.scales.y.grid.display = stylingConfig.showGrid
  }

  // Custom animation settings
  if (stylingConfig.animationDuration !== undefined) {
    chartConfig.options.animation.duration = stylingConfig.animationDuration
  }

  // Custom point settings
  if (stylingConfig.pointRadius !== undefined) {
    chartConfig.options.elements.point.radius = stylingConfig.pointRadius
  }
}

// ==================== ERROR HANDLING ====================

/**
 * Create error state chart
 */
export function createErrorChart(errorMessage, widgetConfig) {
  return {
    type: 'line',
    data: {
      datasets: []
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: widgetConfig?.widget_label || 'Chart Error',
          color: '#f44336'
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'No Data Available'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: errorMessage
          }
        }
      }
    }
  }
}

/**
 * Create loading state chart
 */
export function createLoadingChart(widgetConfig) {
  return {
    type: 'line',
    data: {
      datasets: []
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: (widgetConfig?.widget_label || 'Chart') + ' - Loading...',
          color: '#666'
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Loading data...'
          }
        },
        y: {
          display: true
        }
      }
    }
  }
}

// ==================== PERFORMANCE OPTIMIZATION ====================

/**
 * Optimize chart for large datasets
 */
export function optimizeChartForLargeData(chartConfig, dataPointCount) {
  if (dataPointCount > 1000) {
    // Disable animations for large datasets
    chartConfig.options.animation = false

    // Reduce point radius
    chartConfig.options.elements.point.radius = 0
    chartConfig.options.elements.point.hoverRadius = 3

    // Optimize responsive behavior
    chartConfig.options.responsive = true
    chartConfig.options.maintainAspectRatio = false

    console.log(`📊 Chart optimized for ${dataPointCount} data points`)
  }

  return chartConfig
}

/**
 * Debounce chart updates
 */
export function debounceChartUpdate(updateFunction, delay = 300) {
  let timeoutId

  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => updateFunction.apply(this, args), delay)
  }
}

// ==================== CHART UTILITIES ====================

/**
 * Calculate chart dimensions based on container
 */
export function calculateChartDimensions(container) {
  if (!container) return { width: 400, height: 300 }

  const rect = container.getBoundingClientRect()
  return {
    width: rect.width || 400,
    height: rect.height || 300
  }
}

/**
 * Get chart instance by canvas ID
 */
export function getChartInstance(canvasId) {
  const canvas = document.getElementById(canvasId)
  if (!canvas) return null

  // Chart.js stores instance on canvas
  return Chart.getChart(canvas)
}

/**
 * Destroy chart instance safely
 */
export function destroyChart(chartInstance) {
  if (chartInstance && typeof chartInstance.destroy === 'function') {
    try {
      chartInstance.destroy()
      console.log('📊 Chart instance destroyed')
    } catch (error) {
      console.error('❌ Error destroying chart:', error)
    }
  }
}

// ==================== EXPORT UTILITIES ====================

/**
 * Export chart as image
 */
export function exportChartAsImage(chartInstance, filename = 'chart.png') {
  if (!chartInstance) return

  try {
    const url = chartInstance.toBase64Image()
    const link = document.createElement('a')
    link.download = filename
    link.href = url
    link.click()

    console.log('📊 Chart exported as image:', filename)
  } catch (error) {
    console.error('❌ Error exporting chart:', error)
  }
}

/**
 * Get chart data as CSV
 */
export function exportChartDataAsCSV(chartData, filename = 'chart-data.csv') {
  if (!chartData || !chartData.datasets) return

  try {
    let csv = 'Timestamp'

    // Headers
    chartData.datasets.forEach(dataset => {
      csv += `,${dataset.label}`
    })
    csv += '\n'

    // Data rows
    const maxLength = Math.max(...chartData.datasets.map(d => d.data.length))

    for (let i = 0; i < maxLength; i++) {
      const timestamp = chartData.datasets[0]?.data[i]?.x || ''
      csv += timestamp

      chartData.datasets.forEach(dataset => {
        const value = dataset.data[i]?.y || ''
        csv += `,${value}`
      })
      csv += '\n'
    }

    // Download
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.download = filename
    link.href = url
    link.click()
    window.URL.revokeObjectURL(url)

    console.log('📊 Chart data exported as CSV:', filename)
  } catch (error) {
    console.error('❌ Error exporting chart data:', error)
  }
}

// ==================== VALIDATION ====================

/**
 * Validate chart configuration
 */
export function validateChartConfig(config) {
  const errors = []

  if (!config) {
    errors.push('Chart configuration is required')
    return errors
  }

  if (!config.type) {
    errors.push('Chart type is required')
  }

  if (!config.data) {
    errors.push('Chart data is required')
  } else {
    if (!config.data.datasets) {
      errors.push('Chart datasets are required')
    }
  }

  if (!config.options) {
    errors.push('Chart options are required')
  }

  return errors
}

/**
 * Validate widget data format
 */
export function validateWidgetData(data) {
  const errors = []

  if (!data) {
    errors.push('Widget data is required')
    return errors
  }

  if (data.isEmpty) {
    return errors // Empty data is valid
  }

  if (!data.datasets || !Array.isArray(data.datasets)) {
    errors.push('Datasets array is required')
  }

  if (!data.labels && data.datasets && data.datasets.length > 0) {
    // Check if datasets have x,y format data
    const hasTimeData = data.datasets.every(dataset =>
      Array.isArray(dataset.data) &&
      dataset.data.every(point => point && typeof point.x !== 'undefined')
    )

    if (!hasTimeData) {
      errors.push('Either labels array or x,y data format is required')
    }
  }

  return errors
}

// ==================== DEBUG UTILITIES ====================

/**
 * Log chart information for debugging
 */
export function debugChart(chartInstance, label = 'Chart') {
  if (!chartInstance) {
    console.log(`🐛 ${label}: No chart instance`)
    return
  }

  console.group(`🐛 ${label} Debug Info`)
  console.log('Chart Type:', chartInstance.config.type)
  console.log('Canvas ID:', chartInstance.canvas.id)
  console.log('Dataset Count:', chartInstance.data.datasets.length)
  console.log('Data Points:', chartInstance.data.datasets.map(d => d.data.length))
  console.log('Scales:', Object.keys(chartInstance.scales))
  console.log('Plugins:', Object.keys(chartInstance.config.options.plugins || {}))
  console.groupEnd()
}

/**
 * Performance monitoring for chart operations
 */
export function monitorChartPerformance(operation, chartLabel = 'Chart') {
  const startTime = performance.now()

  return {
    end: () => {
      const endTime = performance.now()
      const duration = endTime - startTime
      console.log(`⏱️ ${chartLabel} ${operation}: ${duration.toFixed(2)}ms`)

      if (duration > 100) {
        console.warn(`⚠️ Slow chart operation detected: ${operation} took ${duration.toFixed(2)}ms`)
      }
    }
  }
}
