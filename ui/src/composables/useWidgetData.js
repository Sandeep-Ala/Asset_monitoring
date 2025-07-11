// src/composables/useWidgetData.js - FIXED VERSION
// Critical fixes for API request format and time synchronization
// FIXES: HTTP 422 errors, correct field names, reliable data fetching

import { ref, reactive, computed, watch, onBeforeUnmount, nextTick, getCurrentInstance, readonly } from 'vue'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import { transformWidgetDataToChart, validateChartData } from 'src/utils/dataFormatter.js'
import WidgetAPIService from 'src/services/apiFixService.js'

// ==================== GLOBAL CACHE MANAGEMENT ====================

const globalWidgetCache = reactive({
  data: new Map(),
  timestamps: new Map(),
  configs: new Map(),
  errors: new Map(),
  maxCacheSize: 50,
  cacheTimeoutMs: 5 * 60 * 1000, // 5 minutes
  hitCount: 0,
  missCount: 0,
  totalRequests: 0
})

const activeRequests = new Map()

// ==================== CORE COMPOSABLE ====================

export function useWidgetData(widgetId, widgetConfig = {}, options = {}, customTimeRange = null) {

  const instance = getCurrentInstance()
  const canUseLifecycleHooks = !!instance
  const globalTime = useGlobalTime()

  // ==================== CONFIGURATION ====================

  const config = reactive({
    enableCaching: options.enableCaching !== false,
    autoRefresh: options.autoRefresh !== false,
    retryAttempts: options.retryAttempts || 3,
    retryDelay: options.retryDelay || 1000,
    debugMode: options.debugMode || false
  })

  // ==================== REACTIVE STATE ====================

  const isLoading = ref(false)
  const isRefreshing = ref(false)
  const isBackgroundRefresh = ref(false)
  const hasData = ref(false)
  const isEmpty = ref(false)
  const error = ref(null)

  // Data state
  const rawData = ref(null)
  const chartData = ref(null)
  const metadata = ref(null)

  // Performance tracking
  const refreshCount = ref(0)
  const errorCount = ref(0)
  const lastFetchTime = ref(null)
  const lastErrorTime = ref(null)

  // ==================== COMPUTED PROPERTIES ====================

  const currentTimeRange = computed(() => {
    if (customTimeRange) {
      console.log('🕒 Using custom time range:', customTimeRange)
      return customTimeRange
    }

    const globalTimeRange = globalTime.currentTimeRange.value
    console.log('🕒 Using global time range:', globalTimeRange)
    return globalTimeRange
  })

  const dataStatus = computed(() => ({
    isLoading: isLoading.value,
    isRefreshing: isRefreshing.value,
    hasData: hasData.value,
    isEmpty: isEmpty.value,
    hasError: !!error.value,
    refreshCount: refreshCount.value,
    errorCount: errorCount.value,
    lastFetchTime: lastFetchTime.value,
    lastErrorTime: lastErrorTime.value
  }))

  const cacheKey = computed(() => {
    const timeRange = currentTimeRange.value
    return `${widgetId}-${timeRange?.start || ''}-${timeRange?.end || ''}`
  })

  // ==================== CACHE MANAGEMENT ====================

  function getCachedData() {
    const key = cacheKey.value
    const cachedData = globalWidgetCache.data.get(key)
    const cachedTime = globalWidgetCache.timestamps.get(key)

    if (cachedData && cachedTime) {
      const age = Date.now() - cachedTime
      if (age < globalWidgetCache.cacheTimeoutMs) {
        globalWidgetCache.hitCount++
        console.log('💾 Cache hit for widget:', widgetId, `(${Math.round(age/1000)}s old)`)
        return cachedData
      } else {
        // Expired cache
        globalWidgetCache.data.delete(key)
        globalWidgetCache.timestamps.delete(key)
        console.log('⏰ Cache expired for widget:', widgetId)
      }
    }

    globalWidgetCache.missCount++
    return null
  }

  function setCachedData(data) {
    if (!config.enableCaching) return

    const key = cacheKey.value

    // Manage cache size
    if (globalWidgetCache.data.size >= globalWidgetCache.maxCacheSize) {
      const oldestKey = Array.from(globalWidgetCache.timestamps.entries())
        .sort(([,a], [,b]) => a - b)[0]?.[0]

      if (oldestKey) {
        globalWidgetCache.data.delete(oldestKey)
        globalWidgetCache.timestamps.delete(oldestKey)
        globalWidgetCache.configs.delete(oldestKey)
      }
    }

    globalWidgetCache.data.set(key, data)
    globalWidgetCache.timestamps.set(key, Date.now())
    globalWidgetCache.configs.set(key, widgetConfig)
    console.log('💾 Data cached for widget:', widgetId)
  }

  function clearCache() {
    const key = cacheKey.value
    globalWidgetCache.data.delete(key)
    globalWidgetCache.timestamps.delete(key)
    globalWidgetCache.configs.delete(key)
    globalWidgetCache.errors.delete(key)
    console.log('🧹 Cache cleared for widget:', widgetId)
  }

  // ==================== API INTEGRATION - FIXED ====================

  async function fetchWidgetData(forceRefresh = false) {
    if (!widgetId) {
      throw new Error('Widget ID is required')
    }

    const timeRange = currentTimeRange.value
    console.log('🔍 Fetching data for widget:', widgetId, 'Time range:', timeRange)

    if (!timeRange?.start || !timeRange?.end) {
      throw new Error('Valid time range is required')
    }

    const requestKey = `${widgetId}-${timeRange.start}-${timeRange.end}`

    // Prevent duplicate requests
    if (activeRequests.has(requestKey)) {
      console.log('⏳ Request already in progress for:', widgetId)
      return activeRequests.get(requestKey)
    }

    // Check cache first (unless force refresh)
    if (!forceRefresh && config.enableCaching) {
      const cachedData = getCachedData()
      if (cachedData) {
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

    console.log('📡 Making API call for widget:', widgetId, {
      timeRange: {
        start: timeRange?.start,
        end: timeRange?.end,
        range_type: timeRange?.range_type
      }
    })

    try {
      // Use the new API service with correct format
      const apiData = await WidgetAPIService.getWidgetData(widgetId, timeRange)

      console.log('📥 API response received:', {
        isEmpty: apiData?.isEmpty,
        datasets: apiData?.datasets?.length || 0,
        totalPoints: apiData?.totalPoints || 0,
        labels: apiData?.labels?.length || 0
      })

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

      // Process chart data
      const transformedData = transformWidgetDataToChart(apiData, widgetConfig)
      const validation = validateChartData(transformedData)

      if (!validation || !validation.isValid) {
        console.warn('⚠️ Chart data validation failed:', validation?.errors || 'Unknown validation error')
        console.warn('📊 Transformed data that failed validation:', transformedData)

        // Don't throw error, just log warnings and continue with the data
        // The chart component can handle some validation issues
        if (validation?.errors?.length > 0) {
          console.warn('🔍 Validation errors:', validation.errors)
        }
        if (validation?.warnings?.length > 0) {
          console.warn('⚠️ Validation warnings:', validation.warnings)
        }
      }

      // Update state with transformed data regardless of minor validation issues
      chartData.value = transformedData
      metadata.value = apiData.metadata || null
      hasData.value = true
      isEmpty.value = false

      console.log('📊 Chart data updated for widget:', widgetId, {
        datasets: transformedData.datasets?.length || 0,
        totalPoints: transformedData.datasets?.reduce((total, dataset) =>
          total + (dataset.data?.length || 0), 0) || 0
      })

    } catch (err) {
      console.error('❌ Failed to update state from data:', err)
      error.value = err
      hasData.value = false
      chartData.value = null
    }
  }

  // ==================== PUBLIC METHODS ====================

  async function initialize() {
    if (isLoading.value) {
      console.log('⏳ Widget already initializing:', widgetId)
      return
    }

    console.log('🚀 Initializing widget data for:', widgetId)

    isLoading.value = true

    try {
      await fetchWidgetData()
      console.log('✅ Widget initialized successfully:', widgetId)
    } catch (err) {
      console.error('❌ Widget initialization failed:', widgetId, err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function refresh(force = false) {
    if (isRefreshing.value) {
      console.log('⏳ Widget already refreshing:', widgetId)
      return
    }

    console.log('🔄 Refreshing widget data:', widgetId)

    isRefreshing.value = true

    try {
      await fetchWidgetData(force)
      console.log('✅ Widget refreshed successfully:', widgetId)
    } catch (err) {
      console.error('❌ Widget refresh failed:', widgetId, err)
      throw err
    } finally {
      isRefreshing.value = false
    }
  }

  async function retryFetch() {
    if (!error.value) {
      console.log('⚠️ No error state to retry from')
      return
    }

    console.log('🔄 Retrying failed request for widget:', widgetId)

    // Clear error state
    error.value = null

    // Attempt refresh
    await refresh(true)
  }

  function reset() {
    console.log('🔄 Resetting widget data state:', widgetId)

    isLoading.value = false
    isRefreshing.value = false
    hasData.value = false
    isEmpty.value = false
    error.value = null
    rawData.value = null
    chartData.value = null
    metadata.value = null
    refreshCount.value = 0
    errorCount.value = 0
    lastFetchTime.value = null
    lastErrorTime.value = null

    clearCache()
  }

  // ==================== WATCHERS ====================

  // Watch for global time changes
  if (canUseLifecycleHooks && !customTimeRange) {
    watch(
      () => globalTime.currentTimeRange.value,
      async (newTimeRange, oldTimeRange) => {
        if (!newTimeRange || !oldTimeRange) return

        const timeChanged = newTimeRange.start !== oldTimeRange.start ||
                           newTimeRange.end !== oldTimeRange.end

        if (timeChanged && hasData.value) {
          console.log('⏰ Global time changed, refreshing widget:', widgetId)

          isBackgroundRefresh.value = true

          try {
            await fetchWidgetData(true)
          } catch (err) {
            console.error('❌ Background refresh failed:', err)
          } finally {
            isBackgroundRefresh.value = false
          }
        }
      },
      { deep: true }
    )
  }

  // Watch for widget config changes
  watch(
    () => widgetConfig,
    (newConfig) => {
      if (newConfig && hasData.value) {
        console.log('🔧 Widget config changed, refreshing:', widgetId)
        refresh(true)
      }
    },
    { deep: true }
  )

  // ==================== LIFECYCLE ====================

  if (canUseLifecycleHooks) {
    onBeforeUnmount(() => {
      console.log('🔄 Cleaning up widget data composable:', widgetId)

      // Clear any active requests
      const timeRange = currentTimeRange.value
      const requestKey = `${widgetId}-${timeRange?.start || ''}-${timeRange?.end || ''}`
      activeRequests.delete(requestKey)

      // Note: We don't clear the cache on unmount as it might be shared
    })
  }

  // ==================== RETURN PUBLIC API ====================

  return {
    // State (readonly)
    isLoading: readonly(isLoading),
    isRefreshing: readonly(isRefreshing),
    isBackgroundRefresh: readonly(isBackgroundRefresh),
    hasData: readonly(hasData),
    isEmpty: readonly(isEmpty),
    error: readonly(error),

    // Data (readonly)
    rawData: readonly(rawData),
    chartData: readonly(chartData),
    metadata: readonly(metadata),

    // Status (readonly)
    dataStatus: readonly(dataStatus),
    currentTimeRange: readonly(currentTimeRange),

    // Methods
    initialize,
    refresh,
    retryFetch,
    reset,
    clearCache,

    // Configuration
    config
  }
}

// ==================== GLOBAL UTILITIES ====================

export function getGlobalCacheStats() {
  const totalRequests = globalWidgetCache.hitCount + globalWidgetCache.missCount

  return {
    cacheSize: globalWidgetCache.data.size,
    maxSize: globalWidgetCache.maxCacheSize,
    hitCount: globalWidgetCache.hitCount,
    missCount: globalWidgetCache.missCount,
    hitRate: totalRequests > 0 ? globalWidgetCache.hitCount / totalRequests : 0,
    totalRequests: globalWidgetCache.totalRequests,
    memoryUsage: `${globalWidgetCache.data.size}/${globalWidgetCache.maxCacheSize}`
  }
}

export function clearAllWidgetCache() {
  globalWidgetCache.data.clear()
  globalWidgetCache.timestamps.clear()
  globalWidgetCache.configs.clear()
  globalWidgetCache.errors.clear()

  console.log('🧹 All widget cache cleared')

  return {
    cleared: true,
    timestamp: new Date().toISOString()
  }
}

export function debugWidgetCache() {
  const stats = getGlobalCacheStats()
  const cacheEntries = Array.from(globalWidgetCache.data.keys())

  console.log('🔍 Widget Cache Debug Info:')
  console.log('📊 Stats:', stats)
  console.log('🗝️ Cache Keys:', cacheEntries)

  return {
    stats,
    cacheEntries,
    rawCache: {
      data: globalWidgetCache.data,
      timestamps: globalWidgetCache.timestamps,
      configs: globalWidgetCache.configs,
      errors: globalWidgetCache.errors
    }
  }
}

// Export default for convenience
export default useWidgetData

// Global access for debugging
if (typeof window !== 'undefined') {
  window.useWidgetData = useWidgetData
  window.getGlobalCacheStats = getGlobalCacheStats
  window.clearAllWidgetCache = clearAllWidgetCache
  window.debugWidgetCache = debugWidgetCache
}
