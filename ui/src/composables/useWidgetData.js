// src/composables/useWidgetData.js
// Advanced Widget Data Management Composable
// Handles API integration, caching, auto-refresh, and global time sync

import { ref, reactive, computed, watch, onBeforeUnmount, nextTick } from 'vue'
import  api  from 'src/services/Api.js'
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
 */
export function useWidgetData(widgetId, widgetConfig = {}, options = {}) {

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

  // Auto-refresh management
  const autoRefreshTimer = ref(null)
  const refreshCount = ref(0)

  // Cache status
  const cacheHit = ref(false)
  const cacheKey = ref(null)

  // ==================== GLOBAL TIME INTEGRATION ====================

  const globalTime = useGlobalTime()

  // ==================== COMPUTED PROPERTIES ====================

  /**
   * Current time range for API requests
   */
  const currentTimeRange = computed(() => ({
    start: globalTime.timeState.timeStart,
    end: globalTime.timeState.timeEnd,
    range_type: globalTime.timeState.rangeType,
    window_period: globalTime.timeState.windowPeriod
  }))

  /**
   * Check if data is stale and needs refresh
   */
  const isDataStale = computed(() => {
    if (!lastFetchTime.value) return true

    const age = Date.now() - lastFetchTime.value.getTime()
    return age > config.cacheTimeoutMs
  })

  /**
   * Check if background refresh is needed
   */
  const needsBackgroundRefresh = computed(() => {
    if (!lastFetchTime.value) return false

    const age = Date.now() - lastFetchTime.value.getTime()
    return age > config.backgroundRefreshThresholdMs && age < config.cacheTimeoutMs
  })

  /**
   * Data status information
   */
  const dataStatus = computed(() => ({
    hasData: hasData.value,
    isEmpty: isEmpty.value,
    isLoading: isLoading.value,
    isStale: isDataStale.value,
    error: error.value,
    lastFetch: lastFetchTime.value,
    age: dataAge.value,
    refreshCount: refreshCount.value,
    cacheHit: cacheHit.value
  }))

  /**
   * Performance metrics
   */
  const performanceMetrics = computed(() => ({
    globalHitRate: globalWidgetCache.hitCount / Math.max(1, globalWidgetCache.totalRequests),
    totalCachedWidgets: globalWidgetCache.data.size,
    errorRate: errorCount.value / Math.max(1, refreshCount.value),
    averageLoadTime: 0 // TODO: Track load times
  }))

  // ==================== CACHE MANAGEMENT ====================

  /**
   * Generate cache key for current state
   */
  function generateCacheKey() {
    const timeRange = currentTimeRange.value
    return `${widgetId}_${timeRange.start}_${timeRange.end}_${timeRange.window_period}`
  }

  /**
   * Get data from cache if available and valid
   */
  function getCachedData() {
    if (!config.enableCaching) return null

    const key = generateCacheKey()
    cacheKey.value = key

    const cached = globalWidgetCache.data.get(key)
    const timestamp = globalWidgetCache.timestamps.get(key)

    if (cached && timestamp) {
      const age = Date.now() - timestamp.getTime()

      if (age < config.cacheTimeoutMs) {
        console.log('💾 Cache hit for widget:', widgetId, 'age:', Math.round(age / 1000), 's')

        globalWidgetCache.hitCount++
        cacheHit.value = true

        return cached
      } else {
        // Clean expired cache
        globalWidgetCache.data.delete(key)
        globalWidgetCache.timestamps.delete(key)
      }
    }

    globalWidgetCache.missCount++
    cacheHit.value = false
    return null
  }

  /**
   * Store data in cache
   */
  function setCachedData(data) {
    if (!config.enableCaching) return

    const key = generateCacheKey()

    // Clean old cache if size limit exceeded
    if (globalWidgetCache.data.size >= globalWidgetCache.maxCacheSize) {
      cleanOldCache()
    }

    globalWidgetCache.data.set(key, data)
    globalWidgetCache.timestamps.set(key, new Date())
    globalWidgetCache.configs.set(widgetId, widgetConfig)

    console.log('💾 Cached data for widget:', widgetId, 'cache size:', globalWidgetCache.data.size)
  }

  /**
   * Clean old cache entries
   */
  function cleanOldCache() {
    const now = Date.now()
    const entriesToDelete = []

    // Find expired entries
    for (const [key, timestamp] of globalWidgetCache.timestamps.entries()) {
      const age = now - timestamp.getTime()
      if (age > globalWidgetCache.cacheTimeoutMs) {
        entriesToDelete.push(key)
      }
    }

    // Delete expired entries
    entriesToDelete.forEach(key => {
      globalWidgetCache.data.delete(key)
      globalWidgetCache.timestamps.delete(key)
    })

    // If still too large, delete oldest entries
    if (globalWidgetCache.data.size >= globalWidgetCache.maxCacheSize) {
      const sortedEntries = Array.from(globalWidgetCache.timestamps.entries())
        .sort(([,a], [,b]) => a.getTime() - b.getTime())

      const toDelete = sortedEntries.slice(0, 10) // Delete oldest 10 entries
      toDelete.forEach(([key]) => {
        globalWidgetCache.data.delete(key)
        globalWidgetCache.timestamps.delete(key)
      })
    }

    console.log('🧹 Cache cleaned, new size:', globalWidgetCache.data.size)
  }

  // ==================== API INTEGRATION ====================

  /**
   * Fetch widget data from backend API
   */
  async function fetchWidgetData(forceRefresh = false) {
    if (!widgetId || !currentTimeRange.value.start || !currentTimeRange.value.end) {
      console.warn('⚠️ Invalid widget ID or time range for data fetch')
      return
    }

    try {
      // Check for active request to prevent duplicates
      const requestKey = generateCacheKey()
      if (activeRequests.has(requestKey) && !forceRefresh) {
        console.log('⏳ Request already active for:', requestKey)
        return await activeRequests.get(requestKey)
      }

      // Check cache first (unless force refresh)
      if (!forceRefresh) {
        const cachedData = getCachedData()
        if (cachedData) {
          applyData(cachedData, true)
          return cachedData
        }
      }

      // Set loading states
      if (isInitialLoad.value) {
        isLoading.value = true
      } else {
        isBackgroundRefresh.value = true
      }

      error.value = null
      globalWidgetCache.totalRequests++

      console.log('📡 Fetching widget data:', widgetId, currentTimeRange.value)

      // Create API request promise
      const requestPromise = api.post(`/widgets/${widgetId}/data`, {
        time_start: currentTimeRange.value.start,
        time_end: currentTimeRange.value.end,
        time_range_type: currentTimeRange.value.range_type,
        window_period: currentTimeRange.value.window_period
      })

      // Store active request
      activeRequests.set(requestKey, requestPromise)

      // Execute request
      const response = await requestPromise
      const backendData = response.data

      console.log('✅ Widget data received:', {
        widgetId,
        isEmpty: backendData?.isEmpty,
        datasets: backendData?.datasets?.length || 0,
        totalPoints: backendData?.totalPoints || 0
      })

      // Transform data using our formatter
      const transformedData = transformWidgetDataToChart(backendData, widgetConfig)

      // Validate transformed data
      const validation = validateChartData(transformedData)
      if (!validation.valid) {
        console.warn('⚠️ Chart data validation failed:', validation.issues)
      }

      // Apply data to component state
      applyData({
        raw: backendData,
        chart: transformedData,
        validation
      })

      // Cache the data
      setCachedData({
        raw: backendData,
        chart: transformedData,
        validation
      })

      // Update success metrics
      refreshCount.value++
      errorCount.value = 0 // Reset error count on success

      return transformedData

    } catch (err) {
      console.error('❌ Widget data fetch failed:', err)

      handleFetchError(err)
      throw err

    } finally {
      // Clean up loading states
      isLoading.value = false
      isInitialLoad.value = false
      isBackgroundRefresh.value = false
      isRetrying.value = false

      // Remove active request
      activeRequests.delete(requestKey)
    }
  }

  /**
   * Apply fetched data to component state
   */
  function applyData(data, fromCache = false) {
    try {
      rawData.value = data.raw
      chartData.value = data.chart
      metadata.value = data.chart?.metadata || null

      hasData.value = !data.chart?.isEmpty
      isEmpty.value = data.chart?.isEmpty || false
      lastFetchTime.value = fromCache ? lastFetchTime.value : new Date()

      // Update data age
      updateDataAge()

      console.log(fromCache ? '💾 Applied cached data' : '✅ Applied fresh data', {
        hasData: hasData.value,
        datasets: chartData.value?.datasets?.length || 0
      })

    } catch (err) {
      console.error('❌ Failed to apply data:', err)
      handleFetchError(err)
    }
  }

  /**
   * Handle fetch errors with intelligent retry logic
   */
  function handleFetchError(err) {
    error.value = {
      message: err.message || 'Unknown error',
      code: err.response?.status || 'UNKNOWN',
      timestamp: new Date(),
      retryCount: errorCount.value
    }

    errorCount.value++
    lastErrorTime.value = new Date()

    // Store error in global cache for debugging
    globalWidgetCache.errors.set(widgetId, error.value)

    // Clear data on error
    hasData.value = false
    isEmpty.value = true
    chartData.value = null

    console.error('💥 Widget data error:', error.value)
  }

  // ==================== AUTO-REFRESH MANAGEMENT ====================

  /**
   * Start auto-refresh based on global time settings
   */
  function startAutoRefresh() {
    if (!config.enableAutoRefresh) return

    stopAutoRefresh() // Clear existing timer

    const refreshRate = globalTime.timeState.refreshRate
    const intervalMs = getRefreshIntervalMs(refreshRate)

    if (intervalMs > 0) {
      console.log('⏰ Starting auto-refresh for widget:', widgetId, 'interval:', intervalMs / 1000, 's')

      autoRefreshTimer.value = setInterval(async () => {
        try {
          console.log('🔄 Auto-refresh triggered for widget:', widgetId)
          await fetchWidgetData(true) // Force refresh
        } catch (err) {
          console.warn('⚠️ Auto-refresh failed for widget:', widgetId, err)
        }
      }, intervalMs)
    }
  }

  /**
   * Stop auto-refresh timer
   */
  function stopAutoRefresh() {
    if (autoRefreshTimer.value) {
      clearInterval(autoRefreshTimer.value)
      autoRefreshTimer.value = null
      console.log('⏹️ Auto-refresh stopped for widget:', widgetId)
    }
  }

  /**
   * Convert refresh rate to milliseconds
   */
  function getRefreshIntervalMs(refreshRate) {
    const intervals = {
      'manual': 0,
      '30s': 30 * 1000,
      '1m': 60 * 1000,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
      '30m': 30 * 60 * 1000,
      '1h': 60 * 60 * 1000
    }

    return intervals[refreshRate] || 0
  }

  // ==================== RETRY LOGIC ====================

  /**
   * Retry data fetch with exponential backoff
   */
  async function retryFetch() {
    if (errorCount.value >= config.maxRetries) {
      console.warn('⚠️ Max retries exceeded for widget:', widgetId)
      return
    }

    const delay = config.retryDelayMs * Math.pow(2, errorCount.value)

    console.log(`🔄 Retrying widget data fetch in ${delay}ms (attempt ${errorCount.value + 1}/${config.maxRetries})`)

    isRetrying.value = true

    setTimeout(async () => {
      try {
        await fetchWidgetData(true)
      } catch (err) {
        console.warn('⚠️ Retry failed for widget:', widgetId)
      }
    }, delay)
  }

  // ==================== UTILITY FUNCTIONS ====================

  /**
   * Update data age calculation
   */
  function updateDataAge() {
    if (lastFetchTime.value) {
      dataAge.value = Date.now() - lastFetchTime.value.getTime()
    }
  }

  /**
   * Force refresh data
   */
  async function refresh() {
    console.log('🔄 Manual refresh requested for widget:', widgetId)
    return await fetchWidgetData(true)
  }

  /**
   * Clear all cached data for this widget
   */
  function clearCache() {
    const keysToDelete = []

    for (const key of globalWidgetCache.data.keys()) {
      if (key.startsWith(widgetId)) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => {
      globalWidgetCache.data.delete(key)
      globalWidgetCache.timestamps.delete(key)
    })

    globalWidgetCache.errors.delete(widgetId)

    console.log('🧹 Cache cleared for widget:', widgetId)
  }

  /**
   * Initialize widget data management
   */
  async function initialize() {
    console.log('🚀 Initializing widget data management for:', widgetId)

    try {
      // Set up data age update timer
      const ageUpdateTimer = setInterval(() => {
        updateDataAge()
      }, 1000)

      // Clean up on unmount
      onBeforeUnmount(() => {
        clearInterval(ageUpdateTimer)
        stopAutoRefresh()
      })

      // Load initial data
      await fetchWidgetData()

      // Start auto-refresh if enabled
      startAutoRefresh()

      console.log('✅ Widget data management initialized for:', widgetId)

    } catch (err) {
      console.error('❌ Failed to initialize widget data management:', err)
    }
  }

  // ==================== WATCHERS ====================

  // Watch for global time changes
  watch(
    () => currentTimeRange.value,
    async (newTimeRange, oldTimeRange) => {
      // Only refresh if time range actually changed
      if (JSON.stringify(newTimeRange) !== JSON.stringify(oldTimeRange)) {
        console.log('🕒 Global time changed, refreshing widget:', widgetId)

        // Add small delay to batch multiple time changes
        await nextTick()
        await fetchWidgetData(true)
      }
    },
    { deep: true }
  )

  // Watch for refresh rate changes
  watch(
    () => globalTime.timeState.refreshRate,
    (newRate, oldRate) => {
      if (newRate !== oldRate) {
        console.log('⏰ Refresh rate changed, updating auto-refresh for widget:', widgetId)
        startAutoRefresh()
      }
    }
  )

  // ==================== CLEANUP ====================

  onBeforeUnmount(() => {
    stopAutoRefresh()
    console.log('🧹 Widget data management cleaned up for:', widgetId)
  })

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
