<!-- src/components/GlobalTimePicker.vue -->
<!-- Global Time Management Component for Widget System -->
<!-- Provides time range, window period, and refresh rate controls -->

<template>
  <div class="global-time-picker">
    <!-- Compact Trigger Button -->
    <div class="time-picker-trigger" v-if="!isExpanded">
      <q-btn
        flat
        dense
        icon="access_time"
        :label="compactTimeDisplay"
        @click="toggleExpanded"
        class="trigger-btn"
        :loading="isLoading"
      >
        <q-tooltip anchor="bottom middle" self="top middle" :offset="[0, 8]">
          <div class="text-body2">
            <div><strong>Time Range:</strong> {{ timeRangeDisplay }}</div>
            <div><strong>Window:</strong> {{ windowDisplay }}</div>
            <div><strong>Refresh:</strong> {{ refreshDisplay }}</div>
            <div class="text-caption q-mt-xs">Click to expand controls</div>
          </div>
        </q-tooltip>

        <!-- Auto-refresh indicator -->
        <q-badge
          v-if="isAutoRefreshActive"
          color="green"
          floating
          rounded
          class="refresh-indicator"
        >
          <q-icon name="refresh" size="10px" />
        </q-badge>
      </q-btn>
    </div>

    <!-- Expanded Control Panel -->
    <q-card v-if="isExpanded" class="time-picker-panel" flat bordered>
      <q-card-section class="q-pa-md">
        <!-- Header with close button -->
        <div class="row items-center q-mb-md">
          <div class="col">
            <div class="text-h6 text-primary">
              <q-icon name="access_time" class="q-mr-sm" />
              Time Controls
            </div>
          </div>
          <div class="col-auto">
            <q-btn
              flat
              dense
              round
              icon="close"
              @click="toggleExpanded"
              size="sm"
            />
          </div>
        </div>

        <!-- Time Range Selection -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="schedule" class="q-mr-xs" />
            Time Range
          </div>

          <q-select
            v-model="selectedTimeRange"
            :options="timeRangeOptions"
            option-label="label"
            option-value="value"
            outlined
            dense
            map-options
            emit-value
            @update:model-value="onTimeRangeChange"
            :loading="isLoadingPresets"
            class="q-mb-sm"
          >
            <template v-slot:prepend>
              <q-icon name="date_range" />
            </template>
          </q-select>

          <!-- Custom Date/Time Pickers -->
          <div v-if="selectedTimeRange === 'custom'" class="custom-time-inputs">
            <div class="row q-gutter-sm">
              <div class="col">
                <q-input
                  v-model="customStartTime"
                  type="datetime-local"
                  outlined
                  dense
                  label="Start Time"
                  @update:model-value="onCustomTimeChange"
                  :error="customTimeError"
                  :error-message="customTimeErrorMessage"
                >
                  <template v-slot:prepend>
                    <q-icon name="play_arrow" />
                  </template>
                </q-input>
              </div>
              <div class="col">
                <q-input
                  v-model="customEndTime"
                  type="datetime-local"
                  outlined
                  dense
                  label="End Time"
                  @update:model-value="onCustomTimeChange"
                  :error="customTimeError"
                  :error-message="customTimeErrorMessage"
                >
                  <template v-slot:prepend>
                    <q-icon name="stop" />
                  </template>
                </q-input>
              </div>
            </div>

            <div class="row q-mt-sm">
              <q-btn
                color="primary"
                label="Apply Custom Range"
                @click="applyCustomTimeRange"
                :disable="!isValidCustomRange"
                :loading="isApplyingCustomRange"
                size="sm"
                class="full-width"
              />
            </div>
          </div>
        </div>

        <!-- Window Period Selection -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="tune" class="q-mr-xs" />
            Window Period
            <q-icon
              name="help_outline"
              size="16px"
              class="q-ml-xs cursor-pointer"
              @click="showWindowPeriodHelp = true"
            />
          </div>

          <q-select
            v-model="selectedWindowPeriod"
            :options="windowPeriodOptions"
            option-label="label"
            option-value="value"
            outlined
            dense
            map-options
            emit-value
            @update:model-value="onWindowPeriodChange"
            :loading="isCalculatingWindow"
          >
            <template v-slot:prepend>
              <q-icon name="bar_chart" />
            </template>
          </q-select>

          <!-- Window Period Info Display -->
          <div v-if="windowInfo && !isCalculatingWindow" class="window-info q-mt-sm">
            <q-chip
              size="sm"
              :color="windowInfo.autoCalculated ? 'blue' : 'orange'"
              text-color="white"
              icon="info"
            >
              {{ formatWindowInfo() }}
            </q-chip>

            <q-chip
              v-if="windowInfo.estimatedPoints > windowInfo.maxPointsLimit"
              size="sm"
              color="red"
              text-color="white"
              icon="warning"
              class="q-ml-xs"
            >
              Too many points ({{ windowInfo.estimatedPoints }})
            </q-chip>
          </div>
        </div>

        <!-- Refresh Rate Selection -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="refresh" class="q-mr-xs" />
            Refresh Rate
          </div>

          <q-select
            v-model="selectedRefreshRate"
            :options="refreshRateOptions"
            option-label="label"
            option-value="value"
            outlined
            dense
            map-options
            emit-value
            @update:model-value="onRefreshRateChange"
          >
            <template v-slot:prepend>
              <q-icon name="update" />
            </template>
          </q-select>

          <!-- Auto-refresh status -->
          <div v-if="isAutoRefreshActive" class="auto-refresh-status q-mt-sm">
            <q-chip size="sm" color="green" text-color="white" icon="schedule">
              Auto-refresh active
            </q-chip>
            <q-chip
              size="sm"
              color="blue"
              text-color="white"
              icon="timer"
              class="q-ml-xs"
            >
              Next: {{ nextRefreshCountdown }}s
            </q-chip>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <div class="row q-gutter-sm">
            <div class="col">
              <q-btn
                color="primary"
                icon="refresh"
                label="Refresh Now"
                @click="triggerManualRefresh"
                :loading="isRefreshing"
                size="sm"
                class="full-width"
              />
            </div>
            <div class="col-auto">
              <q-btn
                flat
                color="grey"
                icon="settings_backup_restore"
                @click="resetToDefaults"
                size="sm"
              >
                <q-tooltip>Reset to defaults</q-tooltip>
              </q-btn>
            </div>
          </div>
        </div>

        <!-- Status Display -->
        <div class="status-display q-mt-md q-pt-md" style="border-top: 1px solid #e0e0e0">
          <div class="text-caption text-grey-7">
            <div class="row q-gutter-md">
              <div class="col">
                <div><strong>Duration:</strong> {{ timeRangeDisplay }}</div>
                <div><strong>Points:</strong> {{ windowInfo?.estimatedPoints || 'Calculating...' }}</div>
              </div>
              <div class="col">
                <div><strong>Last Update:</strong> {{ lastUpdateDisplay }}</div>
                <div><strong>Status:</strong>
                  <span :class="statusClass">{{ connectionStatus }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Window Period Help Dialog -->
    <q-dialog v-model="showWindowPeriodHelp">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Window Period Explanation</div>
        </q-card-section>
        <q-card-section>
          <div class="text-body2">
            <p><strong>Window Period</strong> determines how data points are grouped and averaged for display:</p>

            <ul class="q-pl-md">
              <li><strong>Auto:</strong> Automatically calculates optimal window to stay within {{ maxPointsLimit }} points</li>
              <li><strong>Manual periods:</strong> Fixed time intervals (1sec, 5min, 1hour, etc.)</li>
            </ul>

            <p class="q-mt-md">
              <strong>Example:</strong> With a 2-day time range and "Auto" window,
              the system calculates ~28.8 minute intervals to achieve exactly 100 data points.
            </p>

            <p class="text-caption text-grey-7 q-mt-md">
              Smaller windows = more detail but more data points.
              Larger windows = less detail but better performance.
            </p>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Got it" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import { useGlobalTimeInstance } from 'src/composables/useGlobalTime.js'
import { formatWindowPeriod } from 'src/utils/chartUtils.js'

// ==================== COMPOSABLES & DEPENDENCIES ====================

const $q = useQuasar()
const globalTime = useGlobalTimeInstance()

// ==================== COMPONENT STATE ====================

// UI State
const isExpanded = ref(false)
const showWindowPeriodHelp = ref(false)

// Loading States
const isLoading = ref(false)
const isLoadingPresets = ref(false)
const isCalculatingWindow = ref(false)
const isApplyingCustomRange = ref(false)
const isRefreshing = ref(false)

// Form State
const selectedTimeRange = ref('last_1h')
const selectedWindowPeriod = ref('auto')
const selectedRefreshRate = ref('manual')
const customStartTime = ref('')
const customEndTime = ref('')

// Validation State
const customTimeError = ref(false)
const customTimeErrorMessage = ref('')

// Auto-refresh tracking
const refreshCountdown = ref(0)
const refreshTimer = ref(null)

// Options from backend
const timeRangeOptions = ref([])
const windowPeriodOptions = ref([])
const refreshRateOptions = ref([])

// ==================== COMPUTED PROPERTIES ====================

/**
 * Compact display for trigger button
 */
const compactTimeDisplay = computed(() => {
  if (isLoading.value) return 'Loading...'

  const range = globalTime.timeRangeDisplay.value
  const window = windowInfo.value?.windowPeriod || 'auto'

  return `${range} • ${window}`
})

/**
 * Current time range display
 */
const timeRangeDisplay = computed(() => {
  return globalTime.timeRangeDisplay.value || 'Not set'
})

/**
 * Window period display
 */
const windowDisplay = computed(() => {
  const info = globalTime.timeState.windowInfo
  return info ? formatWindowPeriod(info) : 'Calculating...'
})

/**
 * Refresh rate display
 */
const refreshDisplay = computed(() => {
  const rate = globalTime.timeState.refreshRate
  const option = refreshRateOptions.value.find(opt => opt.value === rate)
  return option?.label || rate
})

/**
 * Window information from global state
 */
const windowInfo = computed(() => {
  return globalTime.timeState.windowInfo
})

/**
 * Check if auto-refresh is active
 */
const isAutoRefreshActive = computed(() => {
  return globalTime.timeState.autoRefreshEnabled &&
         globalTime.timeState.refreshRate !== 'manual'
})

/**
 * Next refresh countdown display
 */
const nextRefreshCountdown = computed(() => {
  return refreshCountdown.value
})

/**
 * Last update display
 */
const lastUpdateDisplay = computed(() => {
  const lastUpdate = globalTime.timeState.lastUpdated
  if (!lastUpdate) return 'Never'

  const date = new Date(lastUpdate)
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return `${diffSec}s ago`
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`
  return date.toLocaleTimeString()
})

/**
 * Connection status
 */
const connectionStatus = computed(() => {
  if (isLoading.value) return 'Connecting...'
  if (globalTime.timeState.presets) return 'Connected'
  return 'Offline'
})

/**
 * Status CSS class
 */
const statusClass = computed(() => {
  if (isLoading.value) return 'text-orange'
  if (globalTime.timeState.presets) return 'text-green'
  return 'text-red'
})

/**
 * Max points limit for window calculation
 */
const maxPointsLimit = computed(() => {
  return globalTime.timeState.windowInfo?.maxPointsLimit || 100
})

/**
 * Validate custom time range
 */
const isValidCustomRange = computed(() => {
  if (!customStartTime.value || !customEndTime.value) return false

  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)

  return start < end && start <= new Date() && end <= new Date()
})

// ==================== WATCHERS ====================

// Watch global time state changes
watch(
  () => globalTime.timeState.rangeType,
  (newRangeType) => {
    if (newRangeType !== selectedTimeRange.value) {
      selectedTimeRange.value = newRangeType
    }
  }
)

watch(
  () => globalTime.timeState.windowPeriod,
  (newWindowPeriod) => {
    if (newWindowPeriod !== selectedWindowPeriod.value) {
      selectedWindowPeriod.value = newWindowPeriod
    }
  }
)

watch(
  () => globalTime.timeState.refreshRate,
  (newRefreshRate) => {
    if (newRefreshRate !== selectedRefreshRate.value) {
      selectedRefreshRate.value = newRefreshRate
    }
  }
)

// Watch for window calculation loading
watch(
  () => globalTime.timeState.isLoading,
  (loading) => {
    if (loading) {
      isCalculatingWindow.value = true
    } else {
      setTimeout(() => {
        isCalculatingWindow.value = false
      }, 500) // Small delay for better UX
    }
  }
)

// ==================== METHODS ====================

/**
 * Toggle expanded/collapsed state
 */
function toggleExpanded() {
  isExpanded.value = !isExpanded.value

  if (isExpanded.value) {
    // Update local state when expanding
    syncFromGlobalState()
  }
}

/**
 * Initialize component with backend data
 */
async function initialize() {
  try {
    isLoading.value = true
    isLoadingPresets.value = true

    console.log('🕒 Initializing GlobalTimePicker...')

    // Initialize global time management
    await globalTime.initialize()

    // Load presets and populate options
    const presets = globalTime.timeState.presets

    if (presets) {
      timeRangeOptions.value = presets.presets || []
      refreshRateOptions.value = presets.refresh_rates || []
      windowPeriodOptions.value = presets.window_periods || []

      console.log('✅ Time picker options loaded:', {
        timeRanges: timeRangeOptions.value.length,
        windowPeriods: windowPeriodOptions.value.length,
        refreshRates: refreshRateOptions.value.length
      })
    }

    // Sync local state with global state
    syncFromGlobalState()

    // Start refresh countdown if auto-refresh is active
    if (isAutoRefreshActive.value) {
      startRefreshCountdown()
    }

  } catch (error) {
    console.error('❌ Failed to initialize GlobalTimePicker:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to load time controls',
      timeout: 3000
    })

  } finally {
    isLoading.value = false
    isLoadingPresets.value = false
  }
}

/**
 * Sync local component state with global time state
 */
function syncFromGlobalState() {
  selectedTimeRange.value = globalTime.timeState.rangeType || 'last_1h'
  selectedWindowPeriod.value = globalTime.timeState.windowPeriod || 'auto'
  selectedRefreshRate.value = globalTime.timeState.refreshRate || 'manual'

  // Sync custom time inputs if in custom mode
  if (selectedTimeRange.value === 'custom') {
    updateCustomTimeInputs()
  }
}

/**
 * Update custom time inputs from global state
 */
function updateCustomTimeInputs() {
  if (globalTime.timeState.timeStart && globalTime.timeState.timeEnd) {
    // Convert ISO strings to datetime-local format
    customStartTime.value = convertToLocalDateTime(globalTime.timeState.timeStart)
    customEndTime.value = convertToLocalDateTime(globalTime.timeState.timeEnd)
  }
}

/**
 * Convert ISO string to datetime-local input format
 */
function convertToLocalDateTime(isoString) {
  try {
    const date = new Date(isoString)
    // Format: YYYY-MM-DDTHH:mm
    return date.toISOString().slice(0, 16)
  } catch (error) {
    console.warn('⚠️ Failed to convert datetime:', isoString, error)
    return ''
  }
}

/**
 * Handle time range preset change
 */
async function onTimeRangeChange(newRange) {
  try {
    console.log('🕒 Time range changed to:', newRange)

    clearCustomTimeErrors()

    if (newRange === 'custom') {
      // Initialize custom inputs with current range
      updateCustomTimeInputs()
    } else {
      // Apply preset range
      isCalculatingWindow.value = true
      await globalTime.setTimeRange(newRange)

      $q.notify({
        type: 'positive',
        message: `Time range set to ${getTimeRangeLabel(newRange)}`,
        timeout: 2000
      })
    }

  } catch (error) {
    console.error('❌ Failed to change time range:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to update time range',
      timeout: 3000
    })
  }
}

/**
 * Handle custom time change (validation only)
 */
function onCustomTimeChange() {
  validateCustomTime()
}

/**
 * Apply custom time range
 */
async function applyCustomTimeRange() {
  if (!isValidCustomRange.value) {
    validateCustomTime()
    return
  }

  try {
    isApplyingCustomRange.value = true

    console.log('🕒 Applying custom time range:', {
      start: customStartTime.value,
      end: customEndTime.value
    })

    // Convert to ISO strings
    const startISO = new Date(customStartTime.value).toISOString()
    const endISO = new Date(customEndTime.value).toISOString()

    await globalTime.setTimeRange('custom', startISO, endISO)

    $q.notify({
      type: 'positive',
      message: 'Custom time range applied',
      timeout: 2000
    })

    clearCustomTimeErrors()

  } catch (error) {
    console.error('❌ Failed to apply custom time range:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to apply custom time range',
      timeout: 3000
    })
  } finally {
    isApplyingCustomRange.value = false
  }
}

/**
 * Validate custom time inputs
 */
function validateCustomTime() {
  if (!customStartTime.value || !customEndTime.value) {
    setCustomTimeError('Both start and end times are required')
    return false
  }

  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)
  const now = new Date()

  if (start >= end) {
    setCustomTimeError('Start time must be before end time')
    return false
  }

  if (start > now) {
    setCustomTimeError('Start time cannot be in the future')
    return false
  }

  if (end > now) {
    setCustomTimeError('End time cannot be in the future')
    return false
  }

  const diffDays = (end - start) / (1000 * 60 * 60 * 24)
  if (diffDays > 30) {
    setCustomTimeError('Time range cannot exceed 30 days')
    return false
  }

  clearCustomTimeErrors()
  return true
}

/**
 * Set custom time validation error
 */
function setCustomTimeError(message) {
  customTimeError.value = true
  customTimeErrorMessage.value = message
}

/**
 * Clear custom time validation errors
 */
function clearCustomTimeErrors() {
  customTimeError.value = false
  customTimeErrorMessage.value = ''
}

/**
 * Handle window period change
 */
async function onWindowPeriodChange(newPeriod) {
  try {
    console.log('⚙️ Window period changed to:', newPeriod)

    isCalculatingWindow.value = true
    await globalTime.setWindowPeriod(newPeriod)

    $q.notify({
      type: 'positive',
      message: `Window period set to ${getWindowPeriodLabel(newPeriod)}`,
      timeout: 2000
    })

  } catch (error) {
    console.error('❌ Failed to change window period:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to update window period',
      timeout: 3000
    })
  }
}

/**
 * Handle refresh rate change
 */
function onRefreshRateChange(newRate) {
  try {
    console.log('🔄 Refresh rate changed to:', newRate)

    globalTime.setRefreshRate(newRate)

    // Manage refresh countdown
    if (newRate === 'manual') {
      stopRefreshCountdown()
    } else {
      startRefreshCountdown()
    }

    $q.notify({
      type: 'positive',
      message: `Refresh rate set to ${getRefreshRateLabel(newRate)}`,
      timeout: 2000
    })

  } catch (error) {
    console.error('❌ Failed to change refresh rate:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to update refresh rate',
      timeout: 3000
    })
  }
}

/**
 * Trigger manual refresh
 */
function triggerManualRefresh() {
  try {
    isRefreshing.value = true

    console.log('🔄 Manual refresh triggered')
    globalTime.refresh()

    $q.notify({
      type: 'info',
      message: 'Refreshing all widgets...',
      timeout: 2000
    })

    // Reset refresh countdown
    if (isAutoRefreshActive.value) {
      resetRefreshCountdown()
    }

  } catch (error) {
    console.error('❌ Failed to trigger refresh:', error)
  } finally {
    setTimeout(() => {
      isRefreshing.value = false
    }, 1000)
  }
}

/**
 * Reset to default values
 */
async function resetToDefaults() {
  try {
    console.log('🔄 Resetting to defaults')

    // Reset to default values
    await globalTime.setTimeRange('last_1h')
    await globalTime.setWindowPeriod('auto')
    globalTime.setRefreshRate('manual')

    // Reset local state
    syncFromGlobalState()

    $q.notify({
      type: 'positive',
      message: 'Time controls reset to defaults',
      timeout: 2000
    })

  } catch (error) {
    console.error('❌ Failed to reset to defaults:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to reset controls',
      timeout: 3000
    })
  }
}

// ==================== AUTO-REFRESH COUNTDOWN ====================

/**
 * Start refresh countdown timer
 */
function startRefreshCountdown() {
  stopRefreshCountdown() // Clear existing timer

  const refreshMs = globalTime.refreshRateMs.value
  if (refreshMs <= 0) return

  refreshCountdown.value = Math.floor(refreshMs / 1000)

  refreshTimer.value = setInterval(() => {
    refreshCountdown.value--

    if (refreshCountdown.value <= 0) {
      resetRefreshCountdown()
    }
  }, 1000)
}

/**
 * Stop refresh countdown timer
 */
function stopRefreshCountdown() {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
  refreshCountdown.value = 0
}

/**
 * Reset refresh countdown to full duration
 */
function resetRefreshCountdown() {
  const refreshMs = globalTime.refreshRateMs.value
  if (refreshMs > 0) {
    refreshCountdown.value = Math.floor(refreshMs / 1000)
  }
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Get time range label by value
 */
function getTimeRangeLabel(value) {
  const option = timeRangeOptions.value.find(opt => opt.value === value)
  return option?.label || value
}

/**
 * Get window period label by value
 */
function getWindowPeriodLabel(value) {
  const option = windowPeriodOptions.value.find(opt => opt.value === value)
  return option?.label || value
}

/**
 * Get refresh rate label by value
 */
function getRefreshRateLabel(value) {
  const option = refreshRateOptions.value.find(opt => opt.value === value)
  return option?.label || value
}

/**
 * Format window information for display
 */
function formatWindowInfo() {
  const info = windowInfo.value
  if (!info) return 'Calculating...'

  const points = info.estimatedPoints || 0
  const auto = info.autoCalculated ? '(auto)' : ''

  return `${points} points ${auto}`.trim()
}

// ==================== LIFECYCLE ====================

onMounted(async () => {
  console.log('🚀 GlobalTimePicker mounted')
  await initialize()
})

onBeforeUnmount(() => {
  console.log('🧹 GlobalTimePicker unmounting')
  stopRefreshCountdown()
  globalTime.cleanup()
})

// ==================== EVENT LISTENERS ====================

// Listen for global time changes from other sources
window.addEventListener('globalTimeChanged', (event) => {
  console.log('🔄 Global time changed externally, syncing UI...')
  syncFromGlobalState()
})
</script>

<style scoped>
.global-time-picker {
  position: fixed;
  top: 80px;
  right: 16px;
  z-index: 3000;
  max-width: 400px;
}

.time-picker-trigger {
  position: relative;
}

.trigger-btn {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.trigger-btn:hover {
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.refresh-indicator {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.time-picker-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
  max-height: 90vh;
  overflow-y: auto;
}

.custom-time-inputs {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  margin-top: 8px;
}

.window-info {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.auto-refresh-status {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.action-buttons {
  margin-top: 16px;
}

.status-display {
  background: #fafafa;
  border-radius: 6px;
  padding: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
  .global-time-picker {
    position: fixed;
    top: 60px;
    right: 8px;
    left: 8px;
    max-width: none;
  }

  .time-picker-panel {
    max-height: 80vh;
  }

  .custom-time-inputs .row {
    flex-direction: column;
  }

  .custom-time-inputs .col {
    width: 100%;
    margin-bottom: 8px;
  }
}

/* Loading states */
.q-field--loading {
  opacity: 0.7;
}

/* Error states */
.q-field--error .q-field__control {
  border-color: #f44336;
}

/* Focus states */
.q-field--focused .q-field__control {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

/* Custom scrollbar for panel */
.time-picker-panel::-webkit-scrollbar {
  width: 6px;
}

.time-picker-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.time-picker-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.time-picker-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animation for panel show/hide */
.time-picker-panel {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Status indicators */
.text-green {
  color: #4caf50;
}

.text-orange {
  color: #ff9800;
}

.text-red {
  color: #f44336;
}

/* Chip hover effects */
.q-chip {
  transition: transform 0.2s ease;
}

.q-chip:hover {
  transform: scale(1.05);
}

/* Button hover effects */
.q-btn {
  transition: all 0.2s ease;
}

.q-btn:hover {
  transform: translateY(-1px);
}

/* Badge positioning */
.q-badge--floating {
  top: -4px;
  right: -4px;
}

/* Tooltip styling improvements */
:deep(.q-tooltip) {
  background: rgba(0, 0, 0, 0.9);
  border-radius: 6px;
  font-size: 13px;
  max-width: 300px;
}

/* Select dropdown improvements */
:deep(.q-select .q-field__control) {
  min-height: 40px;
}

:deep(.q-select .q-field__native) {
  padding: 8px 12px;
}

/* Input field improvements */
:deep(.q-input .q-field__control) {
  min-height: 40px;
}

:deep(.q-input .q-field__native) {
  padding: 8px 12px;
}

/* Card section padding adjustments */
:deep(.q-card__section) {
  padding: 16px;
}

/* Icon size consistency */
.q-icon {
  font-size: 18px;
}

/* Text color adjustments */
.text-subtitle2 {
  color: #424242;
  font-weight: 500;
}

.text-caption {
  color: #757575;
  font-size: 12px;
}

/* Error message styling */
.q-field__messages {
  color: #f44336;
  font-size: 12px;
  margin-top: 4px;
}

/* Success states */
.q-field--success .q-field__control {
  border-color: #4caf50;
}

/* Help icon styling */
.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  color: #1976d2;
}

/* Loading spinner improvements */
:deep(.q-spinner) {
  color: #1976d2;
}

/* Button loading state */
.q-btn--loading {
  pointer-events: none;
  opacity: 0.7;
}

/* Disabled button styling */
.q-btn--disable {
  opacity: 0.5;
  pointer-events: none;
}

/* Custom datetime input styling */
input[type="datetime-local"] {
  font-family: inherit;
  font-size: 14px;
}

/* Panel border enhancements */
.time-picker-panel {
  border: 2px solid transparent;
  background-clip: padding-box;
}

.time-picker-panel::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #e3f2fd, #bbdefb, #90caf9);
  border-radius: 14px;
  z-index: -1;
  opacity: 0.6;
}

/* Dark mode support (if enabled) */
@media (prefers-color-scheme: dark) {
  .trigger-btn {
    background: #424242;
    border-color: #616161;
    color: white;
  }

  .time-picker-panel {
    background: #424242;
    border-color: #616161;
    color: white;
  }

  .custom-time-inputs {
    background: #383838;
    border-color: #616161;
  }

  .status-display {
    background: #383838;
  }

  :deep(.q-field__control) {
    background: #383838;
    border-color: #616161;
    color: white;
  }

  :deep(.q-select__dropdown-icon) {
    color: white;
  }
}
</style>
