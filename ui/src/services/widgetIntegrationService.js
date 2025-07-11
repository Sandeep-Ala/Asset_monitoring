// src/services/widgetIntegrationService.js
// Purpose: Validate and ensure proper data flow from backend to widgets
// Features: Data validation, error handling, performance monitoring

import { api } from 'src/boot/axios.js'
import WidgetAPIService from 'src/services/apiFixService.js'

/**
 * Widget Integration Service
 * Handles validation and debugging of widget data flow
 */
class WidgetIntegrationService {
  constructor() {
    this.debugMode = process.env.NODE_ENV === 'development'
    this.validationCache = new Map()
    this.performanceMetrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0
    }
  }

  /**
   * Validate widget configuration before rendering
   * @param {Object} widgetConfig - Widget configuration object
   * @returns {Object} Validation result
   */
  validateWidgetConfig(widgetConfig) {
    const errors = []
    const warnings = []

    // Required fields validation
    if (!widgetConfig.widget_id) {
      errors.push('Missing widget_id')
    }

    if (!widgetConfig.widget_type) {
      errors.push('Missing widget_type')
    }

    // Signal IDs validation
    if (!widgetConfig.signal_ids || !Array.isArray(widgetConfig.signal_ids)) {
      errors.push('signal_ids must be an array')
    } else if (widgetConfig.signal_ids.length === 0) {
      warnings.push('No signal_ids specified')
    }

    // Equipment IDs validation
    if (!widgetConfig.equipment_ids || !Array.isArray(widgetConfig.equipment_ids)) {
      errors.push('equipment_ids must be an array')
    } else if (widgetConfig.equipment_ids.length === 0) {
      warnings.push('No equipment_ids specified')
    }

    // Position data validation
    if (!widgetConfig.position_data) {
      warnings.push('Missing position_data - using defaults')
    } else {
      const pos = widgetConfig.position_data
      if (typeof pos.x !== 'number' || typeof pos.y !== 'number') {
        warnings.push('Invalid position coordinates')
      }
      if (typeof pos.w !== 'number' || typeof pos.h !== 'number') {
        warnings.push('Invalid widget dimensions')
      }
    }

    const result = {
      isValid: errors.length === 0,
      errors,
      warnings,
      config: widgetConfig
    }

    if (this.debugMode) {
      console.log('🔍 Widget config validation:', result)
    }

    return result
  }

  /**
   * Test widget data endpoint connectivity
   * @param {string} widgetId - Widget ID to test
   * @returns {Promise<Object>} Test result
   */
  async testWidgetDataEndpoint(widgetId) {
    try {
      console.log(`🧪 Testing widget data endpoint for: ${widgetId}`)

      // Use the new API service with correct format
      const timeRange = WidgetAPIService.createPresetTimeRange('last_1h')
      console.log('📅 Using time range:', timeRange)

      const result = await WidgetAPIService.testWidgetEndpoint(widgetId, timeRange)

      this.updatePerformanceMetrics(result.success, result.responseTime)

      if (this.debugMode) {
        console.log('✅ Widget data endpoint test complete:', result)
      }

      return {
        success: result.success,
        responseTime: result.responseTime,
        dataReceived: result.dataReceived,
        dataPoints: result.totalPoints,
        datasets: result.datasets,
        isEmpty: result.isEmpty,
        error: result.error,
        rawResponse: result.metadata
      }

    } catch (error) {
      console.error('❌ Widget data endpoint test failed:', error)

      this.updatePerformanceMetrics(false, 0)

      return {
        success: false,
        responseTime: 0,
        dataReceived: false,
        dataPoints: 0,
        datasets: 0,
        isEmpty: true,
        error: error.message,
        rawError: error
      }
    }
  }

  /**
   * Validate chart data structure
   * @param {Object} chartData - Chart data from useWidgetData composable
   * @returns {Object} Validation result
   */
  validateChartData(chartData) {
    const errors = []
    const warnings = []

    if (!chartData) {
      errors.push('Chart data is null or undefined')
      return { isValid: false, errors, warnings }
    }

    // Check for required Chart.js structure
    if (!chartData.labels || !Array.isArray(chartData.labels)) {
      errors.push('Missing or invalid labels array')
    }

    if (!chartData.datasets || !Array.isArray(chartData.datasets)) {
      errors.push('Missing or invalid datasets array')
    }

    // Validate datasets structure
    if (chartData.datasets) {
      chartData.datasets.forEach((dataset, index) => {
        if (!dataset.label) {
          warnings.push(`Dataset ${index} missing label`)
        }
        if (!dataset.data || !Array.isArray(dataset.data)) {
          errors.push(`Dataset ${index} has invalid data array`)
        }
        if (!dataset.borderColor && !dataset.backgroundColor) {
          warnings.push(`Dataset ${index} missing color configuration`)
        }
      })
    }

    // Check data consistency
    if (chartData.labels && chartData.datasets) {
      const labelsCount = chartData.labels.length
      chartData.datasets.forEach((dataset, index) => {
        if (dataset.data && dataset.data.length !== labelsCount) {
          warnings.push(`Dataset ${index} data length (${dataset.data.length}) doesn't match labels length (${labelsCount})`)
        }
      })
    }

    const result = {
      isValid: errors.length === 0,
      errors,
      warnings,
      structure: {
        labelsCount: chartData.labels?.length || 0,
        datasetsCount: chartData.datasets?.length || 0,
        totalDataPoints: chartData.datasets?.reduce((total, dataset) =>
          total + (dataset.data?.length || 0), 0) || 0,
        isEmpty: chartData.isEmpty || false
      }
    }

    if (this.debugMode) {
      console.log('📊 Chart data validation:', result)
    }

    return result
  }

  /**
   * Debug widget rendering issues
   * @param {string} widgetId - Widget ID
   * @param {Object} widgetConfig - Widget configuration
   * @param {Object} chartData - Chart data
   * @returns {Object} Debug report
   */
  debugWidgetRendering(widgetId, widgetConfig, chartData) {
    const report = {
      widgetId,
      timestamp: new Date().toISOString(),
      configValidation: this.validateWidgetConfig(widgetConfig),
      chartDataValidation: this.validateChartData(chartData),
      renderingChecks: {
        hasValidId: !!widgetId,
        hasConfig: !!widgetConfig,
        hasChartData: !!chartData,
        isLineChart: widgetConfig?.widget_type === 'line_chart',
        hasSignalIds: Array.isArray(widgetConfig?.signal_ids) && widgetConfig.signal_ids.length > 0,
        hasEquipmentIds: Array.isArray(widgetConfig?.equipment_ids) && widgetConfig.equipment_ids.length > 0
      },
      recommendations: []
    }

    // Generate recommendations based on issues found
    if (!report.renderingChecks.hasValidId) {
      report.recommendations.push('Ensure widget has a valid ID')
    }

    if (!report.renderingChecks.hasConfig) {
      report.recommendations.push('Provide complete widget configuration')
    }

    if (!report.renderingChecks.hasChartData) {
      report.recommendations.push('Verify data is being fetched from the API')
    }

    if (!report.renderingChecks.isLineChart) {
      report.recommendations.push('Only line_chart type is currently supported')
    }

    if (!report.renderingChecks.hasSignalIds) {
      report.recommendations.push('Configure signal_ids for data retrieval')
    }

    if (!report.renderingChecks.hasEquipmentIds) {
      report.recommendations.push('Configure equipment_ids for data filtering')
    }

    if (report.configValidation.errors.length > 0) {
      report.recommendations.push('Fix configuration errors: ' + report.configValidation.errors.join(', '))
    }

    if (report.chartDataValidation.errors.length > 0) {
      report.recommendations.push('Fix chart data errors: ' + report.chartDataValidation.errors.join(', '))
    }

    if (this.debugMode) {
      console.log('🔧 Widget rendering debug report:', report)
    }

    return report
  }

  /**
   * Update performance metrics
   * @param {boolean} success - Whether request was successful
   * @param {number} responseTime - Response time in milliseconds
   */
  updatePerformanceMetrics(success, responseTime) {
    this.performanceMetrics.totalRequests++

    if (success) {
      this.performanceMetrics.successfulRequests++
    } else {
      this.performanceMetrics.failedRequests++
    }

    // Update average response time (rolling average)
    const currentAvg = this.performanceMetrics.averageResponseTime
    const totalRequests = this.performanceMetrics.totalRequests
    this.performanceMetrics.averageResponseTime =
      ((currentAvg * (totalRequests - 1)) + responseTime) / totalRequests
  }

  /**
   * Get performance metrics
   * @returns {Object} Performance metrics
   */
  getPerformanceMetrics() {
    return {
      ...this.performanceMetrics,
      successRate: this.performanceMetrics.totalRequests > 0
        ? (this.performanceMetrics.successfulRequests / this.performanceMetrics.totalRequests) * 100
        : 0
    }
  }

  /**
   * Run comprehensive widget integration test
   * @param {string} widgetId - Widget ID to test
   * @param {Object} widgetConfig - Widget configuration
   * @returns {Promise<Object>} Complete test results
   */
  async runIntegrationTest(widgetId, widgetConfig) {
    console.log(`🧪 Running comprehensive integration test for widget: ${widgetId}`)

    const testResults = {
      widgetId,
      timestamp: new Date().toISOString(),
      configValidation: null,
      endpointTest: null,
      dataValidation: null,
      overallSuccess: false,
      summary: []
    }

    try {
      // Step 1: Validate configuration
      testResults.configValidation = this.validateWidgetConfig(widgetConfig)

      if (testResults.configValidation.isValid) {
        testResults.summary.push('✅ Widget configuration is valid')
      } else {
        testResults.summary.push('❌ Widget configuration has errors')
      }

      // Step 2: Test endpoint
      testResults.endpointTest = await this.testWidgetDataEndpoint(widgetId)

      if (testResults.endpointTest.success) {
        testResults.summary.push('✅ Widget data endpoint is working')
      } else {
        testResults.summary.push('❌ Widget data endpoint failed')
      }

      // Step 3: Validate received data (if endpoint test was successful)
      if (testResults.endpointTest.success && testResults.endpointTest.rawResponse) {
        testResults.dataValidation = this.validateChartData(testResults.endpointTest.rawResponse)

        if (testResults.dataValidation.isValid) {
          testResults.summary.push('✅ Chart data structure is valid')
        } else {
          testResults.summary.push('❌ Chart data structure has issues')
        }
      }

      // Determine overall success
      testResults.overallSuccess =
        testResults.configValidation.isValid &&
        testResults.endpointTest.success &&
        (testResults.dataValidation?.isValid || !testResults.dataValidation)

      if (testResults.overallSuccess) {
        testResults.summary.unshift('🎉 All integration tests passed!')
      } else {
        testResults.summary.unshift('⚠️ Integration tests found issues')
      }

    } catch (error) {
      testResults.summary.push('❌ Integration test failed with error: ' + error.message)
      console.error('🚫 Integration test error:', error)
    }

    console.log('📋 Integration test complete:', testResults)
    return testResults
  }

  /**
   * Monitor widget performance in real-time
   * @param {string} widgetId - Widget ID to monitor
   * @param {Function} callback - Callback function for updates
   * @returns {Function} Stop monitoring function
   */
  startPerformanceMonitoring(widgetId, callback) {
    const monitoringData = {
      widgetId,
      startTime: Date.now(),
      renderCount: 0,
      errorCount: 0,
      lastUpdate: null,
      averageRenderTime: 0
    }

    const interval = setInterval(() => {
      const currentTime = Date.now()
      const uptime = currentTime - monitoringData.startTime

      const report = {
        ...monitoringData,
        uptime,
        uptimeFormatted: this.formatDuration(uptime)
      }

      callback(report)
    }, 1000) // Update every second

    // Return stop function
    return () => {
      clearInterval(interval)
      console.log(`📊 Performance monitoring stopped for widget: ${widgetId}`)
    }
  }

  /**
   * Format duration in milliseconds to human readable format
   * @param {number} ms - Duration in milliseconds
   * @returns {string} Formatted duration
   */
  formatDuration(ms) {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`
    } else {
      return `${seconds}s`
    }
  }

  /**
   * Clear validation cache
   */
  clearCache() {
    this.validationCache.clear()
    console.log('🧹 Validation cache cleared')
  }

  /**
   * Reset performance metrics
   */
  resetMetrics() {
    this.performanceMetrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0
    }
    console.log('📊 Performance metrics reset')
  }

  /**
   * Export debug report as JSON
   * @param {Object} debugData - Debug data to export
   * @returns {string} JSON string
   */
  exportDebugReport(debugData) {
    const report = {
      timestamp: new Date().toISOString(),
      performanceMetrics: this.getPerformanceMetrics(),
      debugData,
      environment: {
        userAgent: navigator.userAgent,
        url: window.location.href,
        nodeEnv: process.env.NODE_ENV
      }
    }

    return JSON.stringify(report, null, 2)
  }
}

// Create singleton instance
export const widgetIntegrationService = new WidgetIntegrationService()

// Export for debugging in browser console
if (typeof window !== 'undefined') {
  window.widgetIntegrationService = widgetIntegrationService
}

export default widgetIntegrationService
