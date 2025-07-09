// src/composables/useWidgetData.js
// Advanced Widget Data Management Composable - FIXED VERSION
// Handles API integration, caching, auto-refresh, and global time sync
// Fixed: Lifecycle hooks, error handling, API integration

import { ref, reactive, computed, watch, onBeforeUnmount, nextTick, getCurrentInstance, readonly } from 'vue'
import { api } from 'boot/axios'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import { transformWidgetDataToChart, validateChartData } from 'src/utils/dataFormatter.js'

// ==================== GLOBAL CACHE MANAGEMENT ====================

// Global cache for widget data with intelligent cleanup
const globalWidgetCache = reactive({
  data: new Map(), // widgetId -> cached data
  timestamps: new Map(), // widgetId -> last fetch timestamp
  configs: new Map(), // widgetId -> widget configuration
  errors: new Map(), // widgetId -> error information

  // Cache management
  maxCacheSize: 50, // Maximum number of widgets to cache
  cacheTimeoutMs: 5 * 60 * 1000, // 5 minutes cache timeout

  // Performance tracking
  hitCount: 0,
  missCount: 0,
  totalRequests: 0
})

// Global active requests to prevent duplicate API calls
const activeRequests = new Map()

// ==================== CORE COMPOSABLE ====================

/**
 * Advanced Widget Data Management Composable
 * @param {string} widgetId - Widget identifier
 * @param {Object} widgetConfig - Widget configuration from wizard
 * @param {Object} options - Additional options
 * @param {Object} customTimeRange - Optional custom time range override
 */
export function useWidgetData(widgetId, widgetConfig = {}, options = {}, customTimeRange = null) {

  // Check if we're in a component context for lifecycle hooks
  const instance = getCurrentInstance()
  const canUseLifecycleHooks = !!instance

  // ==================== CONFIGURATION ====================

  const config = {
    enableCaching: true,
    enableAutoRefresh: true,
    maxRetries: 3,
    retryDelayMs: 1000,
    cacheTimeoutMs: 5 * 60 * 1000, // 5 minutes
    backgroundRefreshThresholdMs: 2 * 60 * 1000, // 2 minutes
    ...options
  }

  // ==================== REACTIVE STATE ====================

  // Data state
  const rawData = ref(null)
  const chartData = ref(null)
  const metadata = ref(null)

  // Loading states
  const isLoading = ref(false)
  const isInitialLoad = ref(true)
  const isBackgroundRefresh = ref(false)
  const isRetrying = ref(false)

  // Error handling
  const error = ref(null)
  const errorCount = ref(0)
  const lastErrorTime = ref(null)

  // Data status
  const hasData = ref(false)
  const isEmpty = ref(false)
  const lastFetchTime = ref(null)
  const dataAge = ref(0)
  const refreshCount = ref(0)

  // Auto-refresh management
  let autoRefreshTimer = null
  let dataAgeTimer = null
  const isAutoRefreshActive = ref(false)

  // Global time management with custom override
  const globalTime = useGlobalTime()
  const currentTimeRange = computed(() => {
    // Use custom time range if provided, otherwise use global time
    if (customTimeRange && customTimeRange.start && customTimeRange.end) {
      return customTimeRange
    }
    return globalTime.currentTimeRange
  })

  // ==================== COMPUTED PROPERTIES ====================

  const isDataStale = computed(() => {
    if (!lastFetchTime.value) return true
    return (Date.now() - lastFetchTime.value) > config.cacheTimeoutMs
  })

  const needsBackgroundRefresh = computed(() => {
    if (!lastFetchTime.value) return false
    return (Date.now() - lastFetchTime.value) > config.backgroundRefreshThresholdMs
  })

  const dataStatus = computed(() => ({
    isLoading: isLoading.value,
    isInitialLoad: isInitialLoad.value,
    isBackgroundRefresh: isBackgroundRefresh.value,
    isRetrying: isRetrying.value,
    hasData: hasData.value,
    isEmpty: isEmpty.value,
    isStale: isDataStale.value,
    needsRefresh: needsBackgroundRefresh.value,
    refreshCount: refreshCount.value,
    lastFetchTime: lastFetchTime.value,
    dataAge: dataAge.value,
    errorCount: errorCount.value
  }))

  const performanceMetrics = computed(() => {
    const cacheKey = widgetId
    return {
      cacheHit: globalWidgetCache.data.has(cacheKey),
      totalRequests: globalWidgetCache.totalRequests,
      hitRate: globalWidgetCache.hitCount / Math.max(1, globalWidgetCache.totalRequests),
      errorRate: errorCount.value / Math.max(1, refreshCount.value)
    }
  })

  // ==================== CACHE MANAGEMENT ====================

  function getCachedData() {
    const cacheKey = widgetId
    const cachedData = globalWidgetCache.data.get(cacheKey)
    const cacheTime = globalWidgetCache.timestamps.get(cacheKey)

    if (!cachedData || !cacheTime) {
      globalWidgetCache.missCount++
      return null
    }

    // Check if cache is still valid
    const isExpired = (Date.now() - cacheTime) > config.cacheTimeoutMs
    if (isExpired) {
      globalWidgetCache.data.delete(cacheKey)
      globalWidgetCache.timestamps.delete(cacheKey)
      globalWidgetCache.missCount++
      return null
    }

    globalWidgetCache.hitCount++
    return cachedData
  }

  function setCachedData(data) {
    const cacheKey = widgetId

    // Manage cache size
    if (globalWidgetCache.data.size >= globalWidgetCache.maxCacheSize) {
      // Remove oldest entries
      const oldestKey = Array.from(globalWidgetCache.timestamps.entries())
        .sort(([,a], [,b]) => a - b)[0]?.[0]

      if (oldestKey) {
        globalWidgetCache.data.delete(oldestKey)
        globalWidgetCache.timestamps.delete(oldestKey)
        globalWidgetCache.configs.delete(oldestKey)
      }
    }

    globalWidgetCache.data.set(cacheKey, data)
    globalWidgetCache.timestamps.set(cacheKey, Date.now())
    globalWidgetCache.configs.set(cacheKey, widgetConfig)
  }

  function clearCache() {
    const cacheKey = widgetId
    globalWidgetCache.data.delete(cacheKey)
    globalWidgetCache.timestamps.delete(cacheKey)
    globalWidgetCache.configs.delete(cacheKey)
    globalWidgetCache.errors.delete(cacheKey)
    console.log('🧹 Cache cleared for widget:', widgetId)
  }

  // ==================== API INTEGRATION ====================

  async function fetchWidgetData(forceRefresh = false) {
    if (!widgetId) {
      throw new Error('Widget ID is required')
    }

    const requestKey = `${widgetId}-${currentTimeRange.value?.start || ''}-${currentTimeRange.value?.end || ''}`

    // Prevent duplicate requests
    if (activeRequests.has(requestKey)) {
      console.log('⏳ Request already in progress for:', widgetId)
      return activeRequests.get(requestKey)
    }

    // Check cache first (unless force refresh)
    if (!forceRefresh && config.enableCaching) {
      const cachedData = getCachedData()
      if (cachedData) {
        console.log('💾 Using cached data for widget:', widgetId)
        updateStateFromData(cachedData)
        return cachedData
      }
    }

    globalWidgetCache.totalRequests++

    const fetchPromise = performDataFetch()
    activeRequests.set(requestKey, fetchPromise)

    try {
      const result = await fetchPromise
      return result
    } finally {
      activeRequests.delete(requestKey)
    }
  }

  async function performDataFetch() {
    const timeRange = currentTimeRange.value
    console.log('📡 Fetching data for widget:', widgetId, 'Time range:', {
      start: timeRange?.start,
      end: timeRange?.end,
      range_type: timeRange?.range_type
    })

    try {
      // Get and validate time range
      let validTimeRange = timeRange

      // If no time range available, create a default one
      if (!validTimeRange?.start || !validTimeRange?.end) {
        console.log('⚠️ No time range available, creating default range...')

        const now = new Date()
        const oneHourAgo = new Date(now - 60 * 60 * 1000)

        validTimeRange = {
          start: oneHourAgo.toISOString(),
          end: now.toISOString(),
          range_type: 'last_1h'
        }

        console.log('📅 Using default time range:', validTimeRange)
      }

      // Prepare request payload
      const requestData = {
        time_start: validTimeRange.start,
        time_end: validTimeRange.end,
        time_range_type: validTimeRange.range_type || 'custom'
      }

      console.log('📤 Sending request:', requestData)

      // Make API call
      const response = await api.post(`/widgets/${widgetId}/data`, requestData)

      if (!response || !response.data) {
        throw new Error('Empty response from server')
      }

      const apiData = response.data
      console.log('📥 Received data:', apiData)

      // Process the response
      updateStateFromData(apiData)

      // Cache the data
      if (config.enableCaching) {
        setCachedData(apiData)
      }

      // Clear error state on success
      error.value = null
      refreshCount.value++
      lastFetchTime.value = Date.now()

      return apiData

    } catch (err) {
      console.error('❌ Data fetch failed for widget:', widgetId, err)

      // Update error state
      error.value = err
      errorCount.value++
      lastErrorTime.value = Date.now()

      // Cache error to prevent repeated failed requests
      globalWidgetCache.errors.set(widgetId, {
        error: err.message,
        timestamp: Date.now()
      })

      throw err
    }
  }

  function updateStateFromData(apiData) {
    try {
      // Store raw data
      rawData.value = apiData

      // Check if data is empty
      if (apiData.isEmpty) {
        isEmpty.value = true
        hasData.value = false
        chartData.value = null
        metadata.value = apiData.metadata || null
        console.log('📊 Empty dataset received for widget:', widgetId)
        return
      }

      // Transform data for Chart.js
      const transformedData = transformWidgetDataToChart(apiData, widgetConfig)

      if (!transformedData || transformedData.isEmpty) {
        isEmpty.value = true
        hasData.value = false
        chartData.value = null
        console.log('⚠️ Data transformation resulted in empty dataset')
        return
      }

      // Validate transformed data
      const validation = validateChartData(transformedData)
      if (!validation.valid) {
        console.warn('⚠️ Chart data validation issues:', validation.issues)
        // Continue anyway - might still be usable
      }

      // Update state
      chartData.value = transformedData
      metadata.value = apiData.metadata || transformedData.metadata || null
      hasData.value = true
      isEmpty.value = false
      isInitialLoad.value = false

      console.log('✅ Data processed successfully for widget:', widgetId, {
        datasets: transformedData.datasets?.length || 0,
        totalPoints: apiData.totalPoints || 0
      })

    } catch (err) {
      console.error('❌ Failed to process data for widget:', widgetId, err)
      throw new Error(`Data processing failed: ${err.message}`)
    }
  }

  // ==================== AUTO-REFRESH MANAGEMENT ====================

  function startAutoRefresh() {
    if (!config.enableAutoRefresh) return

    stopAutoRefresh() // Clear any existing timer

    const refreshInterval = globalTime.timeState.refreshRate || 30000 // Default 30 seconds

    autoRefreshTimer = setInterval(async () => {
      if (!isLoading.value) {
        try {
          isBackgroundRefresh.value = true
          await fetchWidgetData(true)
        } catch (err) {
          console.warn('🔄 Background refresh failed:', err.message)
        } finally {
          isBackgroundRefresh.value = false
        }
      }
    }, refreshInterval)

    isAutoRefreshActive.value = true
    console.log('🔄 Auto-refresh started for widget:', widgetId, 'interval:', refreshInterval)
  }

  function stopAutoRefresh() {
    if (autoRefreshTimer) {
      clearInterval(autoRefreshTimer)
      autoRefreshTimer = null
    }
    isAutoRefreshActive.value = false
    console.log('⏸️ Auto-refresh stopped for widget:', widgetId)
  }

  function updateDataAge() {
    if (lastFetchTime.value) {
      dataAge.value = Date.now() - lastFetchTime.value
    }
  }

  // ==================== RETRY LOGIC ====================

  async function retryFetch() {
    if (isRetrying.value) return

    console.log('🔄 Retrying data fetch for widget:', widgetId)

    isRetrying.value = true

    for (let attempt = 1; attempt <= config.maxRetries; attempt++) {
      try {
        await fetchWidgetData(true)
        console.log('✅ Retry successful for widget:', widgetId)
        break
      } catch (err) {
        console.warn(`❌ Retry attempt ${attempt}/${config.maxRetries} failed:`, err.message)

        if (attempt < config.maxRetries) {
          const delay = config.retryDelayMs * Math.pow(2, attempt - 1) // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay))
        } else {
          console.error('❌ All retry attempts failed for widget:', widgetId)
          throw err
        }
      }
    }

    isRetrying.value = false
  }

  // ==================== PUBLIC METHODS ====================

  /**
   * Initialize the widget data management
   */
  async function initialize() {
    console.log('🚀 Initializing widget data management for:', widgetId)

    try {
      // Set up data age update timer
      dataAgeTimer = setInterval(() => {
        updateDataAge()
      }, 1000)

      // Load initial data
      isLoading.value = true
      await fetchWidgetData()

      // Start auto-refresh if enabled
      if (config.enableAutoRefresh) {
        startAutoRefresh()
      }

      console.log('✅ Widget data management initialized for:', widgetId)

    } catch (err) {
      console.error('❌ Failed to initialize widget data management:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Refresh data manually
   */
  async function refresh() {
    if (isLoading.value) return

    console.log('🔄 Manual refresh triggered for widget:', widgetId)

    try {
      isLoading.value = true
      await fetchWidgetData(true)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cleanup function
   */
  function cleanup() {
    stopAutoRefresh()

    if (dataAgeTimer) {
      clearInterval(dataAgeTimer)
      dataAgeTimer = null
    }

    console.log('🧹 Widget data management cleaned up for:', widgetId)
  }

  // ==================== WATCHERS ====================

  // Watch for global time changes
  watch(
    () => currentTimeRange.value,
    async (newTimeRange, oldTimeRange) => {
      // Only refresh if time range actually changed and we have a valid range
      if (newTimeRange && oldTimeRange &&
          (newTimeRange.start !== oldTimeRange.start ||
           newTimeRange.end !== oldTimeRange.end ||
           newTimeRange.range_type !== oldTimeRange.range_type)) {
        console.log('🕒 Global time changed, refreshing widget:', widgetId)

        try {
          isLoading.value = true
          // Add small delay to batch multiple time changes
          await nextTick()
          await fetchWidgetData(true)
        } catch (err) {
          console.warn('⚠️ Failed to refresh on time change:', err.message)
        } finally {
          isLoading.value = false
        }
      }
    },
    { deep: true }
  )

  // Watch for refresh rate changes
  watch(
    () => globalTime.timeState.refreshRate,
    (newRate, oldRate) => {
      if (newRate !== oldRate && config.enableAutoRefresh) {
        console.log('⏰ Refresh rate changed, updating auto-refresh for widget:', widgetId)
        startAutoRefresh()
      }
    }
  )

  // ==================== LIFECYCLE MANAGEMENT ====================

  // Only register lifecycle hooks if we're in a component context
  if (canUseLifecycleHooks) {
    onBeforeUnmount(() => {
      cleanup()
    })
  }

  // ==================== PUBLIC API ====================

  return {
    // Data state
    rawData: readonly(rawData),
    chartData: readonly(chartData),
    metadata: readonly(metadata),

    // Status
    isLoading: readonly(isLoading),
    isInitialLoad: readonly(isInitialLoad),
    isBackgroundRefresh: readonly(isBackgroundRefresh),
    isRetrying: readonly(isRetrying),

    // Error handling
    error: readonly(error),
    errorCount: readonly(errorCount),
    lastErrorTime: readonly(lastErrorTime),

    // Data status
    hasData: readonly(hasData),
    isEmpty: readonly(isEmpty),
    lastFetchTime: readonly(lastFetchTime),
    dataAge: readonly(dataAge),
    dataStatus,

    // Computed properties
    currentTimeRange,
    isDataStale,
    needsBackgroundRefresh,
    performanceMetrics,

    // Actions
    initialize,
    refresh,
    retryFetch,
    clearCache,
    startAutoRefresh,
    stopAutoRefresh,
    cleanup, // Add explicit cleanup method

    // Cache management
    getCachedData,
    setCachedData,

    // Utilities
    updateDataAge
  }
}

// ==================== GLOBAL UTILITIES ====================

/**
 * Get global cache statistics
 */
export function getGlobalCacheStats() {
  return {
    size: globalWidgetCache.data.size,
    hitRate: globalWidgetCache.hitCount / Math.max(1, globalWidgetCache.totalRequests),
    totalRequests: globalWidgetCache.totalRequests,
    hitCount: globalWidgetCache.hitCount,
    missCount: globalWidgetCache.missCount,
    errorCount: globalWidgetCache.errors.size
  }
}

/**
 * Clear all cached widget data
 */
export function clearAllWidgetCache() {
  globalWidgetCache.data.clear()
  globalWidgetCache.timestamps.clear()
  globalWidgetCache.configs.clear()
  globalWidgetCache.errors.clear()

  globalWidgetCache.hitCount = 0
  globalWidgetCache.missCount = 0
  globalWidgetCache.totalRequests = 0

  console.log('🧹 All widget cache cleared')
}

/**
 * Create multiple widget data composables for a page
 */
export function createPageWidgetComposables(widgets) {
  const composables = {}

  widgets.forEach(widget => {
    composables[widget.widget_id] = useWidgetData(
      widget.widget_id,
      widget,
      { enableAutoRefresh: true }
    )
  })

  return composables
}

// ==================== EXPORTS ====================

export default useWidgetData
