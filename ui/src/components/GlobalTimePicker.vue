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

        <!-- Enhanced Time Range Selection -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">
            <q-icon name="schedule" class="q-mr-xs" />
            Select Time Range
          </div>

          <!-- Quick Preset Buttons -->
          <div class="quick-presets q-mb-md">
            <div class="text-caption text-grey-7 q-mb-xs">Quick selection:</div>
            <q-btn-group flat class="full-width">
              <q-btn
                flat
                label="1h"
                @click="setQuickRange('last_1h')"
                size="sm"
                :color="selectedTimeRange === 'last_1h' ? 'primary' : 'grey-7'"
                class="col"
              />
              <q-btn
                flat
                label="6h"
                @click="setQuickRange('last_6h')"
                size="sm"
                :color="selectedTimeRange === 'last_6h' ? 'primary' : 'grey-7'"
                class="col"
              />
              <q-btn
                flat
                label="24h"
                @click="setQuickRange('last_24h')"
                size="sm"
                :color="selectedTimeRange === 'last_24h' ? 'primary' : 'grey-7'"
                class="col"
              />
              <q-btn
                flat
                label="7d"
                @click="setQuickRange('last_7d')"
                size="sm"
                :color="selectedTimeRange === 'last_7d' ? 'primary' : 'grey-7'"
                class="col"
              />
            </q-btn-group>
          </div>

          <!-- Primary Custom Date/Time Inputs -->
          <div class="custom-datetime-primary">
            <div class="text-caption text-grey-7 q-mb-xs">Or select custom range:</div>
            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model="customFromTime"
                  type="datetime-local"
                  outlined
                  label="From Date & Time"
                  @update:model-value="onCustomTimeChange"
                  :error="customTimeError"
                  :error-message="customTimeErrorMessage"
                  class="datetime-input"
                >
                  <template v-slot:prepend>
                    <q-icon name="event" color="primary" />
                  </template>
                  <template v-slot:append>
                    <q-icon name="schedule" class="cursor-pointer text-grey-6" @click="setFromToNow(-1)">
                      <q-tooltip>Set to 1 hour ago</q-tooltip>
                    </q-icon>
                  </template>
                </q-input>
              </div>
              <div class="col">
                <q-input
                  v-model="customToTime"
                  type="datetime-local"
                  outlined
                  label="To Date & Time"
                  @update:model-value="onCustomTimeChange"
                  :error="customTimeError"
                  :error-message="customTimeErrorMessage"
                  class="datetime-input"
                >
                  <template v-slot:prepend>
                    <q-icon name="event" color="primary" />
                  </template>
                  <template v-slot:append>
                    <q-icon name="schedule" class="cursor-pointer text-grey-6" @click="setFromToNow(0)">
                      <q-tooltip>Set to now</q-tooltip>
                    </q-icon>
                  </template>
                </q-input>
              </div>
            </div>

            <!-- Duration Display and Quick Adjustments -->
            <div class="datetime-controls q-mt-md">
              <div class="row items-center q-gutter-sm">
                <div class="col">
                  <!-- Duration Display -->
                  <div v-if="isValidCustomRange" class="duration-display">
                    <q-chip
                      icon="schedule"
                      color="blue"
                      text-color="white"
                      size="sm"
                    >
                      Duration: {{ formatCustomDuration() }}
                    </q-chip>
                    <q-chip
                      v-if="estimatedCustomPoints > 0"
                      icon="scatter_plot"
                      :color="estimatedCustomPoints > maxPointsLimit ? 'red' : 'green'"
                      text-color="white"
                      size="sm"
                      class="q-ml-xs"
                    >
                      ~{{ estimatedCustomPoints }} points
                    </q-chip>
                  </div>
                  <div v-else-if="customFromTime || customToTime" class="duration-display">
                    <q-chip icon="warning" color="orange" text-color="white" size="sm">
                      {{ customTimeError ? customTimeErrorMessage : 'Select both dates' }}
                    </q-chip>
                  </div>
                </div>

                <div class="col-auto">
                  <!-- Quick Time Adjustments -->
                  <q-btn-group flat>
                    <q-btn
                      flat
                      icon="remove"
                      @click="adjustTimeRange(-1)"
                      size="sm"
                      color="grey-7"
                    >
                      <q-tooltip>Extend start time by 1 hour</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      icon="add"
                      @click="adjustTimeRange(1)"
                      size="sm"
                      color="grey-7"
                    >
                      <q-tooltip>Extend end time by 1 hour</q-tooltip>
                    </q-btn>
                  </q-btn-group>
                </div>
              </div>
            </div>

            <!-- Apply Custom Range Button -->
            <div class="q-mt-md">
              <q-btn
                color="primary"
                label="Apply Custom Time Range"
                icon="check"
                @click="applyCustomTimeRange"
                :disable="!isValidCustomRange"
                :loading="isApplyingCustomRange"
                class="full-width"
                unelevated
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
const customFromTime = ref('')
const customToTime = ref('')

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
  if (!customFromTime.value || !customToTime.value) return false

  const start = new Date(customFromTime.value)
  const end = new Date(customToTime.value)

  return start < end && start <= new Date() && end <= new Date()
})

/**
 * Estimated points for custom range
 */
const estimatedCustomPoints = computed(() => {
  if (!isValidCustomRange.value) return 0

  const start = new Date(customFromTime.value)
  const end = new Date(customToTime.value)
  const durationMs = end - start
  const durationSeconds = durationMs / 1000

  // Use current window period or default to 1 minute for estimation
  const windowSeconds = windowInfo.value?.windowSeconds || 60

  return Math.ceil(durationSeconds / windowSeconds)
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

  // Sync custom time inputs from global state
  updateCustomTimeInputs()
}

/**
 * Update custom time inputs from global state
 */
function updateCustomTimeInputs() {
  if (globalTime.timeState.timeStart && globalTime.timeState.timeEnd) {
    // Convert ISO strings to datetime-local format
    customFromTime.value = convertToLocalDateTime(globalTime.timeState.timeStart)
    customToTime.value = convertToLocalDateTime(globalTime.timeState.timeEnd)
  } else {
    // Set reasonable defaults
    const now = new Date()
    const oneHourAgo = new Date(now - 60 * 60 * 1000)
    customFromTime.value = convertToLocalDateTime(oneHourAgo.toISOString())
    customToTime.value = convertToLocalDateTime(now.toISOString())
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
 * Set quick range preset
 */
async function setQuickRange(rangeType) {
  try {
    console.log('⚡ Quick range selected:', rangeType)

    selectedTimeRange.value = rangeType
    clearCustomTimeErrors()

    // Apply preset range
    isCalculatingWindow.value = true
    await globalTime.setTimeRange(rangeType)

    // Update custom inputs to reflect the new range
    updateCustomTimeInputs()

    $q.notify({
      type: 'positive',
      message: `Time range set to ${getTimeRangeLabel(rangeType)}`,
      timeout: 2000
    })

  } catch (error) {
    console.error('❌ Failed to set quick range:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to update time range',
      timeout: 3000
    })
  }
}

/**
 * Handle time range preset change (legacy dropdown support)
 */
async function onTimeRangeChange(newRange) {
  await setQuickRange(newRange)
}

/**
 * Handle custom time change (validation only)
 */
function onCustomTimeChange() {
  validateCustomTime()
  selectedTimeRange.value = 'custom'
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
      from: customFromTime.value,
      to: customToTime.value
    })

    // Convert to ISO strings
    const startISO = new Date(customFromTime.value).toISOString()
    const endISO = new Date(customToTime.value).toISOString()

    await globalTime.setTimeRange('custom', startISO, endISO)
    selectedTimeRange.value = 'custom'

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
  if (!customFromTime.value || !customToTime.value) {
    setCustomTimeError('Both start and end times are required')
    return false
  }

  const start = new Date(customFromTime.value)
  const end = new Date(customToTime.value)
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
 * Format custom duration for display
 */
function formatCustomDuration() {
  if (!isValidCustomRange.value) return 'Invalid range'

  const start = new Date(customFromTime.value)
  const end = new Date(customToTime.value)
  const diffMs = end - start

  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

/**
 * Set From/To time relative to now
 */
function setFromToNow(hoursOffset) {
  const now = new Date()
  const targetTime = new Date(now.getTime() + (hoursOffset * 60 * 60 * 1000))

  if (hoursOffset <= 0) {
    // Setting "From" time
    customFromTime.value = convertToLocalDateTime(targetTime.toISOString())
  } else {
    // Setting "To" time
    customToTime.value = convertToLocalDateTime(targetTime.toISOString())
  }

  onCustomTimeChange()
}

/**
 * Adjust time range by extending start or end
 */
function adjustTimeRange(direction) {
  if (!customFromTime.value || !customToTime.value) {
    // Initialize with reasonable defaults
    const now = new Date()
    const oneHourAgo = new Date(now - 60 * 60 * 1000)
    customFromTime.value = convertToLocalDateTime(oneHourAgo.toISOString())
    customToTime.value = convertToLocalDateTime(now.toISOString())
    return
  }

  if (direction < 0) {
    // Extend start time backwards (make range longer)
    const currentStart = new Date(customFromTime.value)
    const newStart = new Date(currentStart.getTime() - (60 * 60 * 1000)) // 1 hour back
    customFromTime.value = convertToLocalDateTime(newStart.toISOString())
  } else {
    // Extend end time forwards (make range longer)
    const currentEnd = new Date(customToTime.value)
    const now = new Date()
    const newEnd = new Date(Math.min(currentEnd.getTime() + (60 * 60 * 1000), now.getTime())) // 1 hour forward, but not past now
    customToTime.value = convertToLocalDateTime(newEnd.toISOString())
  }

  onCustomTimeChange()
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
  color: #424242;
}

.custom-time-inputs {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  margin-top: 8px;
}

/* Enhanced Custom DateTime Styles */
.quick-presets {
  margin-bottom: 16px;
}

.quick-presets .q-btn-group {
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  background: white;
}

.quick-presets .q-btn {
  flex: 1;
  border-radius: 0;
  transition: all 0.2s ease;
  color: #666;
  background: white;
  border: 1px solid #e0e0e0;
}

.quick-presets .q-btn:hover {
  background: rgba(33, 150, 243, 0.1);
  color: #2196f3;
}

.quick-presets .q-btn--active {
  background: #2196f3;
  color: white;
}

.custom-datetime-primary {
  background: white;
  border: 2px solid #e3f2fd;
  border-radius: 12px;
  padding: 16px;
  margin-top: 8px;
}

.datetime-input {
  margin-bottom: 8px;
}

.datetime-input .q-field__control {
  border-radius: 8px;
  min-height: 48px;
  background: white;
  border: 1px solid #e0e0e0;
}

.datetime-input .q-field__native {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
}

.datetime-input .q-field__label {
  color: #666;
}

.datetime-controls {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.duration-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.duration-display .q-chip {
  font-weight: 500;
}

/* Time adjustment buttons */
.time-adjustments .q-btn {
  min-width: 36px;
  min-height: 36px;
  background: white;
  border: 1px solid #e0e0e0;
  color: #666;
}

.time-adjustments .q-btn:hover {
  background: #f5f5f5;
  color: #2196f3;
}

/* Input focus enhancements */
.datetime-input .q-field--focused .q-field__control {
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

/* Error state enhancements */
.datetime-input .q-field--error .q-field__control {
  border-color: #f44336;
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2);
}

/* Success state for valid ranges */
.datetime-input.valid-range .q-field__control {
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

/* Quick preset active state */
.quick-presets .q-btn[aria-pressed="true"] {
  background: #2196f3;
  color: white;
}

/* Datetime input icons */
.datetime-input .q-icon {
  transition: color 0.2s ease;
  color: #666;
}

.datetime-input:hover .q-icon {
  color: #2196f3;
}

/* Apply button enhancements */
.custom-datetime-primary .q-btn {
  height: 44px;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: #2196f3;
  color: white;
}

.custom-datetime-primary .q-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
  background: #1976d2;
}

.custom-datetime-primary .q-btn:disabled {
  transform: none;
  box-shadow: none;
  background: #e0e0e0;
  color: #999;
}

/* Status display with white theme */
.status-display {
  background: #fafafa;
  border-radius: 6px;
  padding: 8px;
  color: #666;
}

/* Action buttons white theme */
.action-buttons .q-btn {
  background: white;
  border: 1px solid #e0e0e0;
  color: #666;
}

.action-buttons .q-btn:hover {
  background: #f5f5f5;
  color: #2196f3;
}

.action-buttons .q-btn--primary {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.action-buttons .q-btn--primary:hover {
  background: #1976d2;
  border-color: #1976d2;
}

/* Window info chips white theme */
.window-info .q-chip {
  background: white;
  border: 1px solid #e0e0e0;
  color: #666;
}

.auto-refresh-status .q-chip {
  background: white;
  border: 1px solid #e0e0e0;
  color: #666;
}

/* Ensure all text is visible on white background */
.time-picker-panel .text-subtitle2 {
  color: #424242;
}

.time-picker-panel .text-caption {
  color: #666;
}

.time-picker-panel .text-grey-7 {
  color: #666;
}

/* Responsive enhancements */
@media (max-width: 640px) {
  .custom-datetime-primary {
    padding: 12px;
  }

  .datetime-input .q-field__control {
    min-height: 44px;
  }

  .quick-presets .q-btn {
    font-size: 12px;
    padding: 8px 4px;
  }

  .duration-display {
    flex-direction: column;
    align-items: flex-start;
  }
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


</style>
