// src/composables/useWidgetData.js - FIXED VERSION
// Critical fixes for time synchronization and manual refresh
// FIXED: currentTimeRange computation, manual refresh function, proper global time watching

import { ref, reactive, computed, watch, onBeforeUnmount, nextTick, getCurrentInstance, readonly } from 'vue'
import { api } from 'boot/axios'
import { useGlobalTime } from 'src/composables/useGlobalTime.js'
import { transformWidgetDataToChart, validateChartData } from 'src/utils/dataFormatter.js'

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

  // ==================== CONFIGURATION ====================

  const config = {
    enableCaching: true,
    enableAutoRefresh: true,
    maxRetries: 3,
    retryDelayMs: 1000,
    cacheTimeoutMs: 5 * 60 * 1000,
    backgroundRefreshThresholdMs: 2 * 60 * 1000,
    ...options
  }

  // ==================== REACTIVE STATE ====================

  const rawData = ref(null)
  const chartData = ref(null)
  const metadata = ref(null)

  const isLoading = ref(false)
  const isInitialLoad = ref(true)
  const isBackgroundRefresh = ref(false)
  const isRetrying = ref(false)

  const error = ref(null)
  const errorCount = ref(0)
  const lastErrorTime = ref(null)

  const hasData = ref(false)
  const isEmpty = ref(false)
  const lastFetchTime = ref(null)
  const dataAge = ref(0)
  const refreshCount = ref(0)

  let autoRefreshTimer = null
  let dataAgeTimer = null
  const isAutoRefreshActive = ref(false)

  // ==================== CRITICAL FIX: GLOBAL TIME INTEGRATION ====================

  const globalTime = useGlobalTime()

  // FIXED: Proper currentTimeRange computation
  const currentTimeRange = computed(() => {
    // CRITICAL: Always use global time unless customTimeRange has BOTH start and end
    if (customTimeRange &&
        customTimeRange.start &&
        customTimeRange.end &&
        customTimeRange.start !== '' &&
        customTimeRange.end !== '') {
      console.log('🔧 Using custom time range:', customTimeRange)
      return customTimeRange
    }

    // Use global time by default
    const globalRange = globalTime.currentTimeRange.value
    console.log('🌍 Using global time range:', globalRange)
    return globalRange
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
      hitRate: globalWidgetCache.totalRequests > 0
        ? (globalWidgetCache.hitCount / globalWidgetCache.totalRequests) * 100
        : 0,
      cacheSize: globalWidgetCache.data.size
    }
  })

  // ==================== CACHE MANAGEMENT ====================

  function getCachedData() {
    const cacheKey = widgetId
    const cached = globalWidgetCache.data.get(cacheKey)
    const timestamp = globalWidgetCache.timestamps.get(cacheKey)

    if (!cached || !timestamp) {
      globalWidgetCache.missCount++
      return null
    }

    const isExpired = (Date.now() - timestamp) > config.cacheTimeoutMs
    if (isExpired) {
      globalWidgetCache.data.delete(cacheKey)
      globalWidgetCache.timestamps.delete(cacheKey)
      globalWidgetCache.configs.delete(cacheKey)
      globalWidgetCache.missCount++
      return null
    }

    globalWidgetCache.hitCount++
    return cached
  }

  function setCachedData(data) {
    const cacheKey = widgetId

    if (globalWidgetCache.data.size >= globalWidgetCache.maxCacheSize) {
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

  // ==================== API INTEGRATION - FIXED ====================

  async function fetchWidgetData(forceRefresh = false) {
    if (!widgetId) {
      throw new Error('Widget ID is required')
    }

    // CRITICAL FIX: Get current time range properly
    const timeRange = currentTimeRange.value
    console.log('🔍 Current time range for API call:', timeRange)

    const requestKey = `${widgetId}-${timeRange?.start || ''}-${timeRange?.end || ''}`

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
    // CRITICAL FIX: Always get fresh time range
    const timeRange = currentTimeRange.value

    console.log('📡 Fetching data for widget:', widgetId, 'Time range:', {
      start: timeRange?.start,
      end: timeRange?.end,
      range_type: timeRange?.range_type,
      source: timeRange === globalTime.currentTimeRange.value ? 'GLOBAL' : 'CUSTOM'
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

      // CRITICAL FIX: Ensure we're sending the right time range
      const requestData = {
        time_start: validTimeRange.start,
        time_end: validTimeRange.end,
        time_range_type: validTimeRange.range_type || 'custom'
      }

      console.log('📤 Sending request with time range:', requestData)

      // Make API call
      const response = await api.post(`/widgets/${widgetId}/data`, requestData)

      if (!response || !response.data) {
        throw new Error('Empty response from server')
      }

      const apiData = response.data
      console.log('📥 Received data:', {
        isEmpty: apiData.isEmpty,
        datasets: apiData.datasets?.length || 0,
        totalPoints: apiData.totalPoints || 0
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
      const transformedData = transformWidgetDataToChart(apiData)
      if (!validateChartData(transformedData)) {
        throw new Error('Invalid chart data format after transformation')
      }

      // Update state
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
      console.error('❌ Failed to process widget data:', widgetId, err)
      error.value = new Error(`Data processing failed: ${err.message}`)
      hasData.value = false
      isEmpty.value = true
    }
  }

  // ==================== PUBLIC API - FIXED ====================

  async function initialize() {
    console.log('🚀 Initializing widget data management for:', widgetId)

    try {
      isLoading.value = true
      await fetchWidgetData(false)
    } catch (err) {
      console.error('❌ Failed to initialize widget data:', err)
      throw err
    } finally {
      isLoading.value = false
      isInitialLoad.value = false
    }
  }

  // CRITICAL FIX: Proper manual refresh function
  async function refresh() {
    console.log('🔄 Manual refresh triggered for widget:', widgetId)
    console.log('🔍 Current time range for refresh:', currentTimeRange.value)

    try {
      isLoading.value = true
      // CRITICAL: Force refresh and clear cache
      clearCache()
      await fetchWidgetData(true)
      console.log('✅ Manual refresh completed for widget:', widgetId)
    } catch (err) {
      console.error('❌ Manual refresh failed for widget:', widgetId, err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function retryFetch() {
    console.log('🔄 Retry fetch triggered for widget:', widgetId)

    isRetrying.value = true

    try {
      await fetchWidgetData(true)
    } finally {
      isRetrying.value = false
    }
  }

  function startAutoRefresh() {
    if (autoRefreshTimer || !config.enableAutoRefresh) return

    const refreshMs = globalTime.refreshRateMs.value
    if (refreshMs <= 0) return

    autoRefreshTimer = setInterval(async () => {
      if (!isLoading.value) {
        console.log('⏰ Auto-refresh triggered for widget:', widgetId)
        isBackgroundRefresh.value = true
        try {
          await fetchWidgetData(true)
        } finally {
          isBackgroundRefresh.value = false
        }
      }
    }, refreshMs)

    isAutoRefreshActive.value = true
    console.log('▶️ Auto-refresh started for widget:', widgetId, 'interval:', refreshMs + 'ms')
  }

  function stopAutoRefresh() {
    if (autoRefreshTimer) {
      clearInterval(autoRefreshTimer)
      autoRefreshTimer = null
      isAutoRefreshActive.value = false
      console.log('⏸️ Auto-refresh stopped for widget:', widgetId)
    }
  }

  function cleanup() {
    stopAutoRefresh()

    if (dataAgeTimer) {
      clearInterval(dataAgeTimer)
      dataAgeTimer = null
    }

    console.log('🧹 Widget data management cleaned up for:', widgetId)
  }

  // ==================== WATCHERS - ENHANCED ====================

  // CRITICAL FIX: Watch for global time changes properly
  watch(
    () => globalTime.currentTimeRange.value,
    async (newTimeRange, oldTimeRange) => {
      // Only refresh if:
      // 1. We're using global time (not custom override)
      // 2. Time range actually changed
      // 3. We have valid ranges

      const usingGlobalTime = !customTimeRange || !customTimeRange.start || !customTimeRange.end

      if (usingGlobalTime && newTimeRange && oldTimeRange) {
        const timeChanged =
          newTimeRange.start !== oldTimeRange.start ||
          newTimeRange.end !== oldTimeRange.end ||
          newTimeRange.range_type !== oldTimeRange.range_type

        if (timeChanged) {
          console.log('🕒 Global time changed, refreshing widget:', widgetId)
          console.log('📅 Old time:', oldTimeRange)
          console.log('📅 New time:', newTimeRange)

          try {
            isLoading.value = true
            // Clear cache to ensure fresh data
            clearCache()
            await fetchWidgetData(true)
          } catch (err) {
            console.warn('⚠️ Failed to refresh on time change:', err.message)
          } finally {
            isLoading.value = false
          }
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
    currentTimeRange: readonly(currentTimeRange),
    isDataStale,
    needsBackgroundRefresh,
    performanceMetrics,

    // Actions
    initialize,
    refresh, // FIXED: This is the correct manual refresh function
    retryFetch,
    clearCache,
    startAutoRefresh,
    stopAutoRefresh,
    cleanup
  }
}
