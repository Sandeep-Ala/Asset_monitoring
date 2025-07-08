// src/composables/useGlobalTime.js
// Global Time Management Composable for Widget System
// Handles time ranges, window periods, refresh rates with backend integration

import { ref, reactive, computed, watch, nextTick, readonly } from 'vue'
import { api } from 'boot/axios'

// Global state - shared across all components
const globalTimeState = reactive({
  // Time Range
  timeStart: null,
  timeEnd: null,
  rangeType: 'last_1h', // 'custom', 'last_15m', 'last_1h', 'last_6h', 'last_24h'

  // Window Period
  windowPeriod: 'auto', // 'auto', '1sec', '5sec', '30sec', '1m', '5m', '15m', '30m', '1h', '6h', '12h', '24h'
  windowInfo: {
    windowPeriod: 'auto',
    windowSeconds: 3600,
    estimatedPoints: 100,
    maxPointsLimit: 100,
    autoCalculated: true
  },

  // Refresh Rate
  refreshRate: 'manual', // 'manual', '5m', '15m', '1h'

  // State Management
  isLoading: false,
  lastUpdated: null,
  presets: null,

  // Auto Refresh
  autoRefreshTimer: null,
  autoRefreshEnabled: false
})

// Backend preset data cache
const presetsCache = ref(null)

/**
 * Global Time Management Composable
 * Provides centralized time state management for all widgets
 */
export function useGlobalTime() {

  // ==================== COMPUTED PROPERTIES ====================

  /**
   * Current time range object for API calls
   */
  const currentTimeRange = computed(() => ({
    start: globalTimeState.timeStart,
    end: globalTimeState.timeEnd,
    range_type: globalTimeState.rangeType
  }))

  /**
   * Check if time range is valid
   */
  const isValidTimeRange = computed(() => {
    return globalTimeState.timeStart &&
           globalTimeState.timeEnd &&
           new Date(globalTimeState.timeStart) < new Date(globalTimeState.timeEnd)
  })

  /**
   * Format current time range for display
   */
  const timeRangeDisplay = computed(() => {
    if (!isValidTimeRange.value) return 'Invalid time range'

    const start = new Date(globalTimeState.timeStart)
    const end = new Date(globalTimeState.timeEnd)
    const duration = end - start

    // Format duration for display
    const hours = Math.floor(duration / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 0) {
      return `${days} day${days !== 1 ? 's' : ''}`
    } else if (hours > 0) {
      return `${hours} hour${hours !== 1 ? 's' : ''}`
    } else {
      const minutes = Math.floor(duration / (1000 * 60))
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`
    }
  })

  /**
   * Get refresh rate in milliseconds
   */
  const refreshRateMs = computed(() => {
    const rates = {
      'manual': 0,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
      '1h': 60 * 60 * 1000
    }
    return rates[globalTimeState.refreshRate] || 0
  })

  // ==================== API INTEGRATION ====================

  /**
   * Load time range presets and configuration from backend
   */
  async function loadPresets() {
    try {
      console.log('🕒 Loading time range presets from backend...')
      globalTimeState.isLoading = true

      const response = await api.get('/widgets/time-ranges/presets')
      presetsCache.value = response.data
      globalTimeState.presets = response.data

      console.log('✅ Time presets loaded:', response.data)

      // Initialize with first preset if no current range
      if (!globalTimeState.timeStart || !globalTimeState.timeEnd) {
        const defaultPreset = response.data.presets.find(p => p.value === 'last_1h') || response.data.presets[0]
        if (defaultPreset) {
          await setTimeRange(defaultPreset.value)
        }
      }

      return response.data
    } catch (error) {
      console.error('❌ Failed to load time presets:', error)

      // Fallback to default presets
      const fallbackPresets = createFallbackPresets()
      presetsCache.value = fallbackPresets
      globalTimeState.presets = fallbackPresets

      // Set default time range
      await setTimeRange('last_1h')

      return fallbackPresets
    } finally {
      globalTimeState.isLoading = false
    }
  }

  /**
   * Calculate optimal window period for current time range
   */
  async function calculateOptimalWindow() {
    if (!isValidTimeRange.value) {
      console.warn('⚠️ Cannot calculate window for invalid time range')
      return
    }

    try {
      console.log('⚙️ Calculating optimal window period...')

      const response = await api.post('/widgets/window-period/calculate', {
        time_start: globalTimeState.timeStart,
        time_end: globalTimeState.timeEnd,
        max_points: globalTimeState.windowInfo.maxPointsLimit
      })

      if (response.data.success) {
        globalTimeState.windowInfo = {
          windowPeriod: response.data.window_period,
          windowSeconds: response.data.window_seconds,
          estimatedPoints: response.data.estimated_points,
          maxPointsLimit: response.data.max_points_limit,
          autoCalculated: true
        }

        console.log('✅ Window period calculated:', globalTimeState.windowInfo)
      } else {
        console.error('❌ Window calculation failed:', response.data.error)
      }
    } catch (error) {
      console.error('❌ Failed to calculate window period:', error)

      // Fallback window calculation
      const fallbackWindow = calculateFallbackWindow()
      globalTimeState.windowInfo = fallbackWindow
    }
  }

  /**
   * Calculate time range from preset type
   */
  async function calculateTimeRange(rangeType, customStart = null, customEnd = null) {
    try {
      console.log('📅 Calculating time range for:', rangeType)

      // Build query parameters instead of request body
      const params = {
        range_type: rangeType
      }

      if (customStart) {
        params.custom_start = customStart
      }

      if (customEnd) {
        params.custom_end = customEnd
      }

      const response = await api.post('/widgets/time-ranges/calculate', {}, {
        params: params
      })

      return response.data
    } catch (error) {
      console.error('❌ Failed to calculate time range:', error)

      // Fallback time calculation
      return calculateFallbackTimeRange(rangeType, customStart, customEnd)
    }
  }

  // ==================== STATE MANAGEMENT ====================

  /**
   * Set time range by preset type or custom range
   */
  async function setTimeRange(rangeType, customStart = null, customEnd = null) {
    try {
      console.log('🕒 Setting time range:', rangeType, customStart, customEnd)

      globalTimeState.isLoading = true

      // Calculate time range
      const timeRange = await calculateTimeRange(rangeType, customStart, customEnd)

      // Update state
      globalTimeState.timeStart = timeRange.start
      globalTimeState.timeEnd = timeRange.end
      globalTimeState.rangeType = timeRange.range_type
      globalTimeState.lastUpdated = new Date().toISOString()

      // Auto-calculate window period if set to auto
      if (globalTimeState.windowPeriod === 'auto') {
        await calculateOptimalWindow()
      }

      // Save to localStorage
      saveToLocalStorage()

      console.log('✅ Time range set:', {
        start: globalTimeState.timeStart,
        end: globalTimeState.timeEnd,
        rangeType: globalTimeState.rangeType
      })

      // Emit change event for widgets
      emitTimeChange()

    } catch (error) {
      console.error('❌ Failed to set time range:', error)
    } finally {
      globalTimeState.isLoading = false
    }
  }

  /**
   * Set window period and recalculate if needed
   */
  async function setWindowPeriod(period) {
    console.log('⚙️ Setting window period:', period)

    globalTimeState.windowPeriod = period

    if (period === 'auto') {
      await calculateOptimalWindow()
    } else {
      // Use predefined window period
      const windowSeconds = getWindowSeconds(period)
      const estimatedPoints = calculateEstimatedPoints(windowSeconds)

      globalTimeState.windowInfo = {
        windowPeriod: period,
        windowSeconds: windowSeconds,
        estimatedPoints: estimatedPoints,
        maxPointsLimit: globalTimeState.windowInfo.maxPointsLimit,
        autoCalculated: false
      }
    }

    saveToLocalStorage()
    emitTimeChange()
  }

  /**
   * Set refresh rate and manage auto-refresh timer
   */
  function setRefreshRate(rate) {
    console.log('🔄 Setting refresh rate:', rate)

    globalTimeState.refreshRate = rate

    // Clear existing timer
    stopAutoRefresh()

    // Start new timer if not manual
    if (rate !== 'manual') {
      startAutoRefresh()
    }

    saveToLocalStorage()
  }

  /**
   * Manual refresh trigger
   */
  function refresh() {
    console.log('🔄 Manual refresh triggered')
    globalTimeState.lastUpdated = new Date().toISOString()
    emitTimeChange()
  }

  // ==================== AUTO REFRESH MANAGEMENT ====================

  /**
   * Start auto-refresh timer
   */
  function startAutoRefresh() {
    if (globalTimeState.autoRefreshTimer) {
      clearInterval(globalTimeState.autoRefreshTimer)
    }

    const intervalMs = refreshRateMs.value
    if (intervalMs > 0) {
      console.log('⏰ Starting auto-refresh every', intervalMs / 1000, 'seconds')

      globalTimeState.autoRefreshTimer = setInterval(() => {
        console.log('🔄 Auto-refresh triggered')
        refresh()
      }, intervalMs)

      globalTimeState.autoRefreshEnabled = true
    }
  }

  /**
   * Stop auto-refresh timer
   */
  function stopAutoRefresh() {
    if (globalTimeState.autoRefreshTimer) {
      console.log('⏹️ Stopping auto-refresh')
      clearInterval(globalTimeState.autoRefreshTimer)
      globalTimeState.autoRefreshTimer = null
      globalTimeState.autoRefreshEnabled = false
    }
  }

  // ==================== PERSISTENCE ====================

  /**
   * Save state to localStorage
   */
  function saveToLocalStorage() {
    try {
      const stateToSave = {
        timeStart: globalTimeState.timeStart,
        timeEnd: globalTimeState.timeEnd,
        rangeType: globalTimeState.rangeType,
        windowPeriod: globalTimeState.windowPeriod,
        refreshRate: globalTimeState.refreshRate,
        windowInfo: globalTimeState.windowInfo
      }

      localStorage.setItem('globalTimeState', JSON.stringify(stateToSave))
      console.log('💾 Time state saved to localStorage')
    } catch (error) {
      console.error('❌ Failed to save time state:', error)
    }
  }

  /**
   * Load state from localStorage
   */
  function loadFromLocalStorage() {
    try {
      const saved = localStorage.getItem('globalTimeState')
      if (saved) {
        const parsedState = JSON.parse(saved)

        // Restore state
        Object.assign(globalTimeState, parsedState)

        console.log('📂 Time state loaded from localStorage:', parsedState)
        return true
      }
    } catch (error) {
      console.error('❌ Failed to load time state:', error)
    }
    return false
  }

  // ==================== EVENT SYSTEM ====================

  /**
   * Emit time change event for widget synchronization
   */
  function emitTimeChange() {
    // Use Vue's nextTick to ensure DOM updates
    nextTick(() => {
      window.dispatchEvent(new CustomEvent('globalTimeChanged', {
        detail: {
          timeRange: currentTimeRange.value,
          windowPeriod: globalTimeState.windowPeriod,
          windowInfo: globalTimeState.windowInfo,
          lastUpdated: globalTimeState.lastUpdated
        }
      }))
    })
  }

  // ==================== UTILITY FUNCTIONS ====================

  /**
   * Get window period in seconds
   */
  function getWindowSeconds(period) {
    const windowOptions = {
      '1sec': 1,
      '5sec': 5,
      '30sec': 30,
      '1m': 60,
      '5m': 300,
      '15m': 900,
      '30m': 1800,
      '1h': 3600,
      '6h': 21600,
      '12h': 43200,
      '24h': 86400
    }
    return windowOptions[period] || 3600
  }

  /**
   * Calculate estimated points for window period
   */
  function calculateEstimatedPoints(windowSeconds) {
    if (!isValidTimeRange.value) return 100

    const totalSeconds = (new Date(globalTimeState.timeEnd) - new Date(globalTimeState.timeStart)) / 1000
    return Math.ceil(totalSeconds / windowSeconds)
  }

  /**
   * Fallback window calculation when backend fails
   */
  function calculateFallbackWindow() {
    if (!isValidTimeRange.value) {
      return {
        windowPeriod: '1h',
        windowSeconds: 3600,
        estimatedPoints: 100,
        maxPointsLimit: 100,
        autoCalculated: true
      }
    }

    const totalSeconds = (new Date(globalTimeState.timeEnd) - new Date(globalTimeState.timeStart)) / 1000
    const optimalWindow = Math.ceil(totalSeconds / 100) // Target 100 points

    // Find closest predefined window
    const windows = [1, 5, 30, 60, 300, 900, 1800, 3600, 21600, 43200, 86400]
    const closestWindow = windows.reduce((prev, curr) =>
      Math.abs(curr - optimalWindow) < Math.abs(prev - optimalWindow) ? curr : prev
    )

    const windowMap = {
      1: '1sec', 5: '5sec', 30: '30sec', 60: '1m', 300: '5m',
      900: '15m', 1800: '30m', 3600: '1h', 21600: '6h', 43200: '12h', 86400: '24h'
    }

    return {
      windowPeriod: windowMap[closestWindow] || '1h',
      windowSeconds: closestWindow,
      estimatedPoints: Math.ceil(totalSeconds / closestWindow),
      maxPointsLimit: 100,
      autoCalculated: true
    }
  }

  /**
   * Fallback time range calculation
   */
  function calculateFallbackTimeRange(rangeType, customStart = null, customEnd = null) {
    const now = new Date()

    if (rangeType === 'custom' && customStart && customEnd) {
      return {
        start: customStart,
        end: customEnd,
        range_type: 'custom'
      }
    }

    const ranges = {
      'last_15m': () => new Date(now - 15 * 60 * 1000),
      'last_1h': () => new Date(now - 60 * 60 * 1000),
      'last_6h': () => new Date(now - 6 * 60 * 60 * 1000),
      'last_24h': () => new Date(now - 24 * 60 * 60 * 1000)
    }

    const startTime = ranges[rangeType] ? ranges[rangeType]() : ranges['last_1h']()

    return {
      start: startTime.toISOString(),
      end: now.toISOString(),
      range_type: rangeType
    }
  }

  /**
   * Create fallback presets when backend is unavailable
   */
  function createFallbackPresets() {
    return {
      presets: [
        { label: "Last 15 minutes", value: "last_15m" },
        { label: "Last 1 hour", value: "last_1h" },
        { label: "Last 6 hours", value: "last_6h" },
        { label: "Last 24 hours", value: "last_24h" },
        { label: "Custom", value: "custom" }
      ],
      refresh_rates: [
        { label: "Manual", value: "manual" },
        { label: "Every 5 minutes", value: "5m" },
        { label: "Every 15 minutes", value: "15m" },
        { label: "Every 1 hour", value: "1h" }
      ],
      window_periods: [
        { label: "Auto (Smart calculation)", value: "auto" },
        { label: "1 second", value: "1sec" },
        { label: "5 seconds", value: "5sec" },
        { label: "30 seconds", value: "30sec" },
        { label: "1 minute", value: "1m" },
        { label: "5 minutes", value: "5m" },
        { label: "15 minutes", value: "15m" },
        { label: "30 minutes", value: "30m" },
        { label: "1 hour", value: "1h" },
        { label: "6 hours", value: "6h" },
        { label: "12 hours", value: "12h" },
        { label: "24 hours", value: "24h" }
      ],
      config: {
        max_points_per_widget: 100,
        default_window_period: "auto"
      }
    }
  }

  // ==================== INITIALIZATION ====================

  /**
   * Initialize global time management
   */
  async function initialize() {
    console.log('🚀 Initializing global time management...')

    // Load saved state
    const hasStoredState = loadFromLocalStorage()

    // Load presets from backend
    await loadPresets()

    // If no stored state, set default range
    if (!hasStoredState) {
      await setTimeRange('last_1h')
    } else {
      // Recalculate window if auto mode
      if (globalTimeState.windowPeriod === 'auto') {
        await calculateOptimalWindow()
      }
    }

    // Start auto-refresh if enabled
    if (globalTimeState.refreshRate !== 'manual') {
      startAutoRefresh()
    }

    console.log('✅ Global time management initialized')
  }

  // ==================== CLEANUP ====================

  /**
   * Cleanup function for component unmount
   */
  function cleanup() {
    stopAutoRefresh()
    console.log('🧹 Global time management cleaned up')
  }

  // ==================== WATCHERS ====================

  // Watch for refresh rate changes
  watch(
    () => globalTimeState.refreshRate,
    (newRate, oldRate) => {
      if (newRate !== oldRate) {
        setRefreshRate(newRate)
      }
    }
  )

  // ==================== PUBLIC API ====================

  return {
    // State (readonly)
    timeState: readonly(globalTimeState),
    currentTimeRange,
    isValidTimeRange,
    timeRangeDisplay,
    refreshRateMs,

    // Actions
    initialize,
    cleanup,
    loadPresets,
    setTimeRange,
    setWindowPeriod,
    setRefreshRate,
    refresh,
    calculateOptimalWindow,

    // Auto-refresh control
    startAutoRefresh,
    stopAutoRefresh,

    // Persistence
    saveToLocalStorage,
    loadFromLocalStorage,

    // Utilities
    getWindowSeconds,
    calculateEstimatedPoints
  }
}

// ==================== GLOBAL INSTANCE ====================

// Create global instance for app-wide access
let globalTimeInstance = null

/**
 * Get or create global time management instance
 */
export function useGlobalTimeInstance() {
  if (!globalTimeInstance) {
    globalTimeInstance = useGlobalTime()
  }
  return globalTimeInstance
}

/**
 * Initialize global time management (call once in main.js or App.vue)
 */
export async function initializeGlobalTime() {
  const instance = useGlobalTimeInstance()
  await instance.initialize()
  return instance
}

// Export readonly access to global state for debugging
export const timeState = readonly(globalTimeState)
