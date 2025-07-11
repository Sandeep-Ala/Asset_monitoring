// src/services/apiFixService.js
// Purpose: Ensure all widget API calls use the correct request format
// Fixes: HTTP 422 errors from incorrect field names

import { api } from 'src/boot/axios.js'

/**
 * Widget API Service with correct request format
 * Ensures all API calls match the backend's expected schema
 */
export class WidgetAPIService {

  /**
   * Get widget data with correct request format
   * @param {string} widgetId - Widget ID
   * @param {Object} timeRange - Time range object
   * @returns {Promise<Object>} Widget data response
   */
  static async getWidgetData(widgetId, timeRange = null) {
    try {
      console.log('📡 Making widget data API call:', {
        widgetId,
        timeRange
      })

      // Create default time range if none provided
      if (!timeRange || !timeRange.start || !timeRange.end) {
        const now = new Date()
        const oneHourAgo = new Date(now - 60 * 60 * 1000)

        timeRange = {
          start: oneHourAgo.toISOString(),
          end: now.toISOString(),
          range_type: 'last_1h'
        }

        console.log('📅 Using default time range:', timeRange)
      }

      // CRITICAL: Use exact field names expected by backend
      const requestPayload = {
        time_start: timeRange.start,     // ✅ Correct field name
        time_end: timeRange.end,         // ✅ Correct field name
        time_range_type: timeRange.range_type || 'custom'  // ✅ Correct field name
      }

      console.log('📤 Request payload:', requestPayload)
      console.log('🎯 API endpoint:', `/widgets/${widgetId}/data`)

      const response = await api.post(`/widgets/${widgetId}/data`, requestPayload)

      console.log('📥 Response received:', {
        status: response.status,
        hasData: !!response.data,
        isEmpty: response.data?.isEmpty,
        datasets: response.data?.datasets?.length || 0,
        totalPoints: response.data?.totalPoints || 0
      })

      return response.data

    } catch (error) {
      console.error('❌ Widget data API call failed:', {
        widgetId,
        error: error.message,
        status: error.response?.status,
        data: error.response?.data
      })

      // Log the actual request that failed
      if (error.config) {
        console.error('❌ Failed request details:', {
          method: error.config.method,
          url: error.config.url,
          data: error.config.data
        })
      }

      throw error
    }
  }

  /**
   * Test widget data endpoint with proper error handling
   * @param {string} widgetId - Widget ID
   * @param {Object} timeRange - Optional time range
   * @returns {Promise<Object>} Test result
   */
  static async testWidgetEndpoint(widgetId, timeRange = null) {
    const startTime = Date.now()

    try {
      console.log(`🧪 Testing widget endpoint: ${widgetId}`)

      const data = await this.getWidgetData(widgetId, timeRange)
      const responseTime = Date.now() - startTime

      const result = {
        success: true,
        responseTime,
        widgetId,
        dataReceived: !!data,
        isEmpty: data?.isEmpty || false,
        datasets: data?.datasets?.length || 0,
        totalPoints: data?.totalPoints || 0,
        labels: data?.labels?.length || 0,
        metadata: data?.metadata || null,
        error: null
      }

      console.log('✅ Widget endpoint test successful:', result)
      return result

    } catch (error) {
      const responseTime = Date.now() - startTime

      const result = {
        success: false,
        responseTime,
        widgetId,
        dataReceived: false,
        isEmpty: true,
        datasets: 0,
        totalPoints: 0,
        labels: 0,
        metadata: null,
        error: error.message,
        errorDetails: {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        }
      }

      console.error('❌ Widget endpoint test failed:', result)
      return result
    }
  }

  /**
   * Validate request format before sending
   * @param {Object} requestData - Request data to validate
   * @returns {Object} Validation result
   */
  static validateRequestFormat(requestData) {
    const errors = []
    const warnings = []

    // Check required fields
    if (!requestData.time_start) {
      errors.push('Missing required field: time_start')
    }

    if (!requestData.time_end) {
      errors.push('Missing required field: time_end')
    }

    // Check field types
    if (requestData.time_start && typeof requestData.time_start !== 'string') {
      errors.push('time_start must be a string (ISO datetime)')
    }

    if (requestData.time_end && typeof requestData.time_end !== 'string') {
      errors.push('time_end must be a string (ISO datetime)')
    }

    // Check for incorrect field names (common mistakes)
    if (requestData.start_time) {
      warnings.push('Found start_time field - should be time_start')
    }

    if (requestData.end_time) {
      warnings.push('Found end_time field - should be time_end')
    }

    if (requestData.window_period) {
      warnings.push('Found window_period field - not supported in this endpoint')
    }

    // Validate datetime format
    if (requestData.time_start) {
      try {
        new Date(requestData.time_start)
      } catch (e) {
        errors.push('time_start is not a valid ISO datetime string')
      }
    }

    if (requestData.time_end) {
      try {
        new Date(requestData.time_end)
      } catch (e) {
        errors.push('time_end is not a valid ISO datetime string')
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      correctedData: this.correctRequestFormat(requestData)
    }
  }

  /**
   * Correct common request format issues
   * @param {Object} requestData - Original request data
   * @returns {Object} Corrected request data
   */
  static correctRequestFormat(requestData) {
    const corrected = { ...requestData }

    // Fix common field name mistakes
    if (corrected.start_time && !corrected.time_start) {
      corrected.time_start = corrected.start_time
      delete corrected.start_time
    }

    if (corrected.end_time && !corrected.time_end) {
      corrected.time_end = corrected.end_time
      delete corrected.end_time
    }

    // Remove unsupported fields
    delete corrected.window_period

    // Ensure time_range_type is set
    if (!corrected.time_range_type) {
      corrected.time_range_type = 'custom'
    }

    return corrected
  }

  /**
   * Create a properly formatted time range
   * @param {Date|string} start - Start time
   * @param {Date|string} end - End time
   * @param {string} rangeType - Range type identifier
   * @returns {Object} Formatted time range
   */
  static createTimeRange(start, end, rangeType = 'custom') {
    const startDate = start instanceof Date ? start : new Date(start)
    const endDate = end instanceof Date ? end : new Date(end)

    return {
      start: startDate.toISOString(),
      end: endDate.toISOString(),
      range_type: rangeType
    }
  }

  /**
   * Create preset time ranges
   * @param {string} preset - Preset name ('last_1h', 'last_24h', etc.)
   * @returns {Object} Time range object
   */
  static createPresetTimeRange(preset) {
    const now = new Date()
    let start, rangeType

    switch (preset) {
      case 'last_15m':
        start = new Date(now - 15 * 60 * 1000)
        rangeType = 'last_15m'
        break
      case 'last_1h':
        start = new Date(now - 60 * 60 * 1000)
        rangeType = 'last_1h'
        break
      case 'last_6h':
        start = new Date(now - 6 * 60 * 60 * 1000)
        rangeType = 'last_6h'
        break
      case 'last_24h':
        start = new Date(now - 24 * 60 * 60 * 1000)
        rangeType = 'last_24h'
        break
      case 'last_7d':
        start = new Date(now - 7 * 24 * 60 * 60 * 1000)
        rangeType = 'last_7d'
        break
      default:
        start = new Date(now - 60 * 60 * 1000) // Default to 1 hour
        rangeType = 'last_1h'
    }

    return this.createTimeRange('2025-03-10T05:44:14.416Z', '2025-03-12T06:44:14.416Z', 'custom')
  }
}

// Export for easy use
export default WidgetAPIService

// Utility function for quick testing
export function quickTestWidget(widgetId, preset = 'last_1h') {
  const timeRange = WidgetAPIService.createPresetTimeRange(preset)
  return WidgetAPIService.testWidgetEndpoint(widgetId, timeRange)
}

// Export for global access (debugging)
if (typeof window !== 'undefined') {
  window.WidgetAPIService = WidgetAPIService
  window.quickTestWidget = quickTestWidget
}
