<!--
  File: src/pages/WidgetIntegrationTestPage.vue - COMPLETE ENHANCED VERSION
  Purpose: Complete testing interface for widget integration validation
  Features: Selectable time ranges, real chart display, comprehensive testing
-->

<template>
  <q-page class="integration-test-page q-pa-md">
    <div class="page-header q-mb-lg">
      <h4 class="q-ma-none">Enhanced Widget Integration Test Suite</h4>
      <p class="text-grey-7 q-mt-sm">
        Test and validate widget integration with selectable time ranges and real chart display
      </p>
    </div>

    <!-- Quick Status Banner -->
    <q-banner v-if="lastTestResult" :class="statusBannerClass" class="q-mb-md">
      <template v-slot:avatar>
        <q-icon :name="statusIcon" :color="statusColor" />
      </template>
      <div class="banner-content">
        <div class="banner-title">{{ statusTitle }}</div>
        <div class="banner-subtitle">{{ statusSubtitle }}</div>
      </div>
      <template v-slot:action>
        <q-btn flat icon="close" @click="lastTestResult = null" />
      </template>
    </q-banner>

    <!-- Test Configuration -->
    <q-card class="test-config-card q-mb-md">
      <q-card-section>
        <div class="row items-center">
          <div class="col">
            <div class="text-h6">Enhanced Test Configuration</div>
            <div class="text-caption text-grey-7">Configure widget for comprehensive integration testing</div>
          </div>
          <div class="col-auto">
            <q-btn-group>
              <q-btn
                icon="flash_on"
                label="Quick Test"
                color="primary"
                @click="runQuickTest"
                :loading="runningQuickTest"
                :disable="!testWidgetId"
              />
              <q-btn
                icon="build"
                label="Full Integration"
                color="secondary"
                @click="runCompleteIntegrationTest"
                :loading="runningTest"
                :disable="!testWidgetId"
              />
            </q-btn-group>
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-gutter-md">
          <!-- Widget Selection -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="testWidgetId"
              :options="predefinedWidgets"
              option-value="widget_id"
              option-label="widget_label"
              label="Select Test Widget"
              outlined
              emit-value
              map-options
              clearable
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.widget_label }}</q-item-label>
                    <q-item-label caption>{{ scope.opt.widget_id }}</q-item-label>
                    <q-item-label caption>
                      {{ scope.opt.equipment_ids?.length || 0 }} equipment •
                      {{ scope.opt.signal_ids?.length || 0 }} signals
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
          </div>

          <!-- Enhanced Time Range Selection -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="timePreset"
              :options="timePresetOptions"
              label="Time Range"
              outlined
              emit-value
              map-options
              @update:model-value="onTimeRangeChanged"
            >
              <template v-slot:append>
                <q-btn
                  icon="date_range"
                  flat
                  dense
                  @click="showCustomTimeDialog = true"
                >
                  <q-tooltip>Custom Time Range</q-tooltip>
                </q-btn>
              </template>
            </q-select>
          </div>

          <!-- Test Mode -->
          <div class="col-12 col-md-4">
            <q-select
              v-model="testMode"
              :options="testModeOptions"
              label="Test Mode"
              outlined
              emit-value
              map-options
            />
          </div>
        </div>

        <!-- Current Time Range Display -->
        <div v-if="currentTimeRange" class="time-range-display q-mt-md">
          <q-chip outline color="primary" icon="schedule">
            {{ formatTimeRangeDisplay() }}
          </q-chip>
        </div>

        <!-- Advanced Options -->
        <q-expansion-item
          label="Advanced Test Options"
          class="q-mt-md"
          header-class="text-grey-7"
        >
          <div class="q-pa-md bg-grey-1">
            <div class="row q-gutter-md">
              <div class="col">
                <q-toggle v-model="testOptions.validateConfig" label="Validate Configuration" />
              </div>
              <div class="col">
                <q-toggle v-model="testOptions.testEndpoint" label="Test Data Endpoint" />
              </div>
              <div class="col">
                <q-toggle v-model="testOptions.validateChartData" label="Validate Chart Data" />
              </div>
              <div class="col">
                <q-toggle v-model="testOptions.performanceTest" label="Performance Test" />
              </div>
              <div class="col">
                <q-toggle v-model="testOptions.testAPIFormat" label="Test API Format Fix" />
              </div>
            </div>
          </div>
        </q-expansion-item>
      </q-card-section>
    </q-card>

    <!-- Custom Time Range Dialog -->
    <q-dialog v-model="showCustomTimeDialog">
      <q-card style="min-width: 400px;">
        <q-card-section>
          <div class="text-h6">Custom Time Range</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="row q-gutter-md">
            <div class="col-12">
              <q-input
                v-model="customStartTime"
                label="Start Time"
                type="datetime-local"
                outlined
                dense
              />
            </div>
            <div class="col-12">
              <q-input
                v-model="customEndTime"
                label="End Time"
                type="datetime-local"
                outlined
                dense
              />
            </div>
          </div>

          <!-- Quick Custom Presets -->
          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Quick Custom Ranges:</div>
            <div class="row q-gutter-sm">
              <q-btn size="sm" outline @click="setCustomRange('2h')" label="Last 2 Hours" />
              <q-btn size="sm" outline @click="setCustomRange('12h')" label="Last 12 Hours" />
              <q-btn size="sm" outline @click="setCustomRange('3d')" label="Last 3 Days" />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="showCustomTimeDialog = false" />
          <q-btn
            flat
            label="Apply"
            color="primary"
            @click="applyCustomTimeRange"
            :disable="!customStartTime || !customEndTime"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Test Results Grid -->
    <div class="row q-gutter-md">
      <!-- Live Widget Test -->
      <div class="col-12 col-lg-8">
        <q-card class="widget-test-card">
          <q-card-section>
            <div class="row items-center justify-between">
              <div>
                <div class="text-h6">Live Widget Test</div>
                <div class="text-caption text-grey-7">Real widget rendering with actual data</div>
              </div>
              <div class="widget-status-indicators">
                <q-chip
                  :color="widgetStatus.color"
                  :icon="widgetStatus.icon"
                  text-color="white"
                  class="q-mr-sm"
                >
                  {{ widgetStatus.label }}
                </q-chip>
                <q-chip
                  v-if="apiFormatStatus"
                  :color="apiFormatStatus.color"
                  :icon="apiFormatStatus.icon"
                  text-color="white"
                  outline
                >
                  {{ apiFormatStatus.label }}
                </q-chip>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section style="height: 500px;">
            <!-- Actual Widget Under Test - FIXED -->
            <div v-if="selectedWidgetConfig && testWidgetId" class="widget-test-container">
              <div class="widget-time-info q-mb-sm">
                <q-chip outline color="info" size="sm" icon="schedule">
                  {{ formatTimeRangeDisplay() }}
                </q-chip>
                <q-chip outline color="grey" size="sm" class="q-ml-sm" icon="widgets">
                  {{ selectedWidgetConfig.widget_label }}
                </q-chip>
                <q-btn
                  icon="refresh"
                  size="sm"
                  flat
                  round
                  @click="forceWidgetRefresh"
                  class="q-ml-sm"
                >
                  <q-tooltip>Refresh Widget</q-tooltip>
                </q-btn>
              </div>

              <WidgetBox
                :key="widgetRenderKey"
                :widget-data="enhancedWidgetConfig"
                :widget-config="enhancedWidgetConfig"
                content-height="400px"
                :auto-refresh-enabled="true"
                :show-debug-info="showDebugInfo"
                :show-status-bar="true"
                @chart-ready="onWidgetChartReady"
                @chart-error="onWidgetChartError"
                @chart-updated="onWidgetChartUpdated"
                @widget-refresh="onWidgetRefresh"
              />
            </div>

            <!-- No Widget Selected -->
            <div v-else class="no-widget-selected">
              <q-icon name="widgets" size="64px" color="grey-4" />
              <div class="text-h6 text-grey-6 q-mt-md">No Widget Selected</div>
              <div class="text-body2 text-grey-7">Select a widget above to start testing</div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Enhanced Test Results Panel -->
      <div class="col-12 col-lg-4">
        <q-card class="test-results-card">
          <q-card-section>
            <div class="text-h6">Test Results</div>
            <div class="text-caption text-grey-7">Real-time validation results</div>
          </q-card-section>

          <q-separator />

          <q-card-section class="test-results-content">
            <!-- Overall Status -->
            <div class="test-status-section q-mb-md">
              <q-linear-progress
                :value="testProgress"
                color="primary"
                class="q-mb-sm"
              />
              <div class="text-caption text-center">
                {{ Math.round(testProgress * 100) }}% Complete
              </div>
            </div>

            <!-- Test Steps -->
            <div class="test-steps">
              <div
                v-for="(step, index) in testSteps"
                :key="index"
                class="test-step q-mb-sm"
                :class="step.status"
              >
                <q-icon
                  :name="step.icon"
                  :color="step.color"
                  class="q-mr-sm"
                />
                <span class="step-label">{{ step.label }}</span>
                <div v-if="step.details" class="step-details text-caption text-grey-7">
                  {{ step.details }}
                </div>
                <div v-if="step.timing" class="step-timing text-caption text-grey-7">
                  {{ step.timing }}
                </div>
              </div>
            </div>

            <!-- Enhanced Performance Metrics -->
            <div v-if="performanceMetrics" class="performance-section q-mt-md">
              <div class="text-subtitle2 q-mb-sm">Performance Metrics</div>
              <div class="metrics-grid">
                <div class="metric-item">
                  <div class="metric-label">Response Time</div>
                  <div class="metric-value">{{ performanceMetrics.averageResponseTime }}ms</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Success Rate</div>
                  <div class="metric-value">{{ performanceMetrics.successRate.toFixed(1) }}%</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Total Requests</div>
                  <div class="metric-value">{{ performanceMetrics.totalRequests }}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Cache Hits</div>
                  <div class="metric-value">{{ cacheStats?.hitRate ? (cacheStats.hitRate * 100).toFixed(1) + '%' : 'N/A' }}</div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="quick-actions q-mt-md">
              <q-btn
                icon="refresh"
                label="Refresh Widget"
                size="sm"
                outline
                @click="refreshTestWidget"
                :disable="!testWidgetId"
                class="full-width q-mb-sm"
              />
              <q-btn
                icon="clear_all"
                label="Clear Cache"
                size="sm"
                outline
                @click="clearTestCache"
                class="full-width"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Enhanced Detailed Results Tabs -->
    <q-card class="detailed-results-card q-mt-md">
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="config" label="Configuration" icon="settings" />
        <q-tab name="endpoint" label="API Endpoint" icon="api" />
        <q-tab name="chartData" label="Chart Data" icon="insert_chart" />
        <q-tab name="apiFormat" label="API Format" icon="code" />
        <q-tab name="debug" label="Debug Log" icon="bug_report" />
        <q-tab name="export" label="Export" icon="download" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated>
        <!-- Configuration Tab -->
        <q-tab-panel name="config">
          <div v-if="testResults?.configValidation">
            <div class="validation-header q-mb-md">
              <q-chip
                :color="testResults.configValidation.isValid ? 'positive' : 'negative'"
                :icon="testResults.configValidation.isValid ? 'check_circle' : 'error'"
                text-color="white"
              >
                {{ testResults.configValidation.isValid ? 'Valid Configuration' : 'Configuration Errors' }}
              </q-chip>
            </div>

            <!-- Errors -->
            <div v-if="testResults.configValidation.errors.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-negative q-mb-sm">Errors:</div>
              <q-list dense>
                <q-item v-for="error in testResults.configValidation.errors" :key="error">
                  <q-item-section avatar>
                    <q-icon name="error" color="negative" />
                  </q-item-section>
                  <q-item-section>{{ error }}</q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Warnings -->
            <div v-if="testResults.configValidation.warnings.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-warning q-mb-sm">Warnings:</div>
              <q-list dense>
                <q-item v-for="warning in testResults.configValidation.warnings" :key="warning">
                  <q-item-section avatar>
                    <q-icon name="warning" color="warning" />
                  </q-item-section>
                  <q-item-section>{{ warning }}</q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Configuration Details -->
            <q-expansion-item label="Raw Configuration" class="config-details">
              <pre class="config-json">{{ JSON.stringify(selectedWidgetConfig, null, 2) }}</pre>
            </q-expansion-item>
          </div>
          <div v-else class="no-data">
            <q-icon name="settings" size="48px" color="grey-4" />
            <div class="text-grey-6 q-mt-sm">No configuration validation data</div>
          </div>
        </q-tab-panel>

        <!-- API Endpoint Tab -->
        <q-tab-panel name="endpoint">
          <div v-if="testResults?.endpointTest">
            <div class="endpoint-header q-mb-md">
              <q-chip
                :color="testResults.endpointTest.success ? 'positive' : 'negative'"
                :icon="testResults.endpointTest.success ? 'check_circle' : 'error'"
                text-color="white"
              >
                {{ testResults.endpointTest.success ? 'Endpoint Working' : 'Endpoint Failed' }}
              </q-chip>

              <q-chip outline color="info" class="q-ml-sm">
                {{ testResults.endpointTest.responseTime }}ms
              </q-chip>

              <q-chip
                v-if="testResults.endpointTest.success"
                outline
                color="positive"
                class="q-ml-sm"
              >
                HTTP 200 OK
              </q-chip>
            </div>

            <div class="endpoint-details">
              <div class="row q-gutter-md">
                <div class="col">
                  <q-list dense>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="data_usage" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Data Points</q-item-label>
                        <q-item-label caption>{{ testResults.endpointTest.dataPoints }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="layers" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Datasets</q-item-label>
                        <q-item-label caption>{{ testResults.endpointTest.datasets }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section avatar>
                        <q-icon name="schedule" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>Time Range</q-item-label>
                        <q-item-label caption>{{ timePreset.replace('_', ' ').toUpperCase() }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
              </div>

              <q-expansion-item label="Raw API Response" class="api-response">
                <pre class="response-json">{{ JSON.stringify(testResults.endpointTest.rawResponse, null, 2) }}</pre>
              </q-expansion-item>
            </div>
          </div>
          <div v-else class="no-data">
            <q-icon name="api" size="48px" color="grey-4" />
            <div class="text-grey-6 q-mt-sm">No endpoint test data</div>
          </div>
        </q-tab-panel>

        <!-- Chart Data Tab -->
        <q-tab-panel name="chartData">
          <div v-if="testResults?.dataValidation">
            <div class="chart-data-header q-mb-md">
              <q-chip
                :color="testResults.dataValidation.isValid ? 'positive' : 'negative'"
                :icon="testResults.dataValidation.isValid ? 'check_circle' : 'error'"
                text-color="white"
              >
                {{ testResults.dataValidation.isValid ? 'Valid Chart Data' : 'Chart Data Issues' }}
              </q-chip>
            </div>

            <!-- Data Structure Info -->
            <div class="structure-info q-mb-md">
              <div class="row q-gutter-md">
                <div class="col-auto">
                  <q-circular-progress
                    :value="Math.min(testResults.dataValidation.structure.labelsCount, 1000)"
                    :max="1000"
                    show-value
                    size="60px"
                    color="primary"
                  />
                  <div class="text-center text-caption q-mt-xs">Labels</div>
                </div>
                <div class="col-auto">
                  <q-circular-progress
                    :value="testResults.dataValidation.structure.datasetsCount"
                    :max="10"
                    show-value
                    size="60px"
                    color="secondary"
                  />
                  <div class="text-center text-caption q-mt-xs">Datasets</div>
                </div>
                <div class="col-auto">
                  <q-circular-progress
                    :value="Math.min(testResults.dataValidation.structure.totalDataPoints, 1000)"
                    :max="1000"
                    show-value
                    size="60px"
                    color="accent"
                  />
                  <div class="text-center text-caption q-mt-xs">Total Points</div>
                </div>
              </div>
            </div>

            <!-- Validation Issues -->
            <div v-if="testResults.dataValidation.errors.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-negative q-mb-sm">Data Errors:</div>
              <q-list dense bordered>
                <q-item v-for="error in testResults.dataValidation.errors" :key="error">
                  <q-item-section avatar>
                    <q-icon name="error" color="negative" />
                  </q-item-section>
                  <q-item-section>{{ error }}</q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
          <div v-else class="no-data">
            <q-icon name="insert_chart" size="48px" color="grey-4" />
            <div class="text-grey-6 q-mt-sm">No chart data validation</div>
          </div>
        </q-tab-panel>

        <!-- API Format Tab -->
        <q-tab-panel name="apiFormat">
          <div v-if="apiFormatValidation">
            <div class="api-format-header q-mb-md">
              <q-chip
                :color="apiFormatValidation.isValid ? 'positive' : 'negative'"
                :icon="apiFormatValidation.isValid ? 'check_circle' : 'error'"
                text-color="white"
              >
                {{ apiFormatValidation.isValid ? 'Correct API Format' : 'API Format Issues' }}
              </q-chip>
            </div>

            <!-- Current Request Format -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">Current Request Format:</div>
              <pre class="api-format-code">{{ currentRequestFormat }}</pre>
            </div>

            <!-- Validation Results -->
            <div v-if="apiFormatValidation.errors.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-negative q-mb-sm">Format Errors:</div>
              <q-list dense>
                <q-item v-for="error in apiFormatValidation.errors" :key="error">
                  <q-item-section avatar>
                    <q-icon name="error" color="negative" />
                  </q-item-section>
                  <q-item-section>{{ error }}</q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="apiFormatValidation.warnings.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-warning q-mb-sm">Format Warnings:</div>
              <q-list dense>
                <q-item v-for="warning in apiFormatValidation.warnings" :key="warning">
                  <q-item-section avatar>
                    <q-icon name="warning" color="warning" />
                  </q-item-section>
                  <q-item-section>{{ warning }}</q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Corrected Format -->
            <div v-if="apiFormatValidation.correctedData" class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">Corrected Format:</div>
              <pre class="api-format-code">{{ JSON.stringify(apiFormatValidation.correctedData, null, 2) }}</pre>
            </div>

            <!-- Format Guidelines -->
            <q-expansion-item label="API Format Guidelines" class="q-mt-md">
              <div class="format-guidelines q-pa-md">
                <div class="text-subtitle2 q-mb-sm">Required Fields:</div>
                <ul>
                  <li><code>time_start</code> (string): ISO datetime string</li>
                  <li><code>time_end</code> (string): ISO datetime string</li>
                  <li><code>time_range_type</code> (string): Range type identifier</li>
                </ul>

                <div class="text-subtitle2 q-mb-sm q-mt-md">Common Mistakes:</div>
                <ul>
                  <li><code>start_time</code> → should be <code>time_start</code></li>
                  <li><code>end_time</code> → should be <code>time_end</code></li>
                  <li><code>window_period</code> → not supported in this endpoint</li>
                </ul>
              </div>
            </q-expansion-item>
          </div>
          <div v-else class="no-data">
            <q-icon name="code" size="48px" color="grey-4" />
            <div class="text-grey-6 q-mt-sm">No API format validation</div>
          </div>
        </q-tab-panel>

        <!-- Debug Log Tab -->
        <q-tab-panel name="debug">
          <div class="debug-log">
            <div class="debug-controls q-mb-md">
              <q-btn
                icon="clear_all"
                label="Clear Log"
                size="sm"
                @click="clearDebugLog"
                outline
              />
              <q-toggle
                v-model="autoScrollLog"
                label="Auto-scroll"
                class="q-ml-md"
              />
              <q-toggle
                v-model="showDebugInfo"
                label="Show Debug in Widget"
                class="q-ml-md"
              />
            </div>

            <q-scroll-area style="height: 300px;" class="debug-log-area">
              <div
                v-for="(entry, index) in debugLog"
                :key="index"
                class="debug-entry"
                :class="entry.type"
              >
                <span class="debug-time">{{ entry.time }}</span>
                <span class="debug-message">{{ entry.message }}</span>
              </div>
            </q-scroll-area>
          </div>
        </q-tab-panel>

        <!-- Export Tab -->
        <q-tab-panel name="export">
          <div class="export-options">
            <div class="text-h6 q-mb-md">Export Test Results</div>

            <div class="row q-gutter-md">
              <div class="col-12 col-sm-6">
                <q-btn
                  icon="download"
                  label="Export JSON Report"
                  color="primary"
                  @click="exportJsonReport"
                  :disable="!testResults"
                  block
                />
              </div>
              <div class="col-12 col-sm-6">
                <q-btn
                  icon="content_copy"
                  label="Copy to Clipboard"
                  color="secondary"
                  @click="copyToClipboard"
                  :disable="!testResults"
                  block
                />
              </div>
            </div>

            <q-separator class="q-my-md" />

            <div class="export-preview">
              <div class="text-subtitle2 q-mb-sm">Preview:</div>
              <q-scroll-area style="height: 200px;" class="export-preview-area">
                <pre class="export-json">{{ exportPreview }}</pre>
              </q-scroll-area>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import { format } from 'date-fns'

// Import Components
import WidgetBox from 'src/components/WidgetBox.vue'

// Import Services
import widgetIntegrationService from 'src/services/widgetIntegrationService.js'
import WidgetAPIService from 'src/services/apiFixService.js'
import { getGlobalCacheStats, clearAllWidgetCache } from 'src/composables/useWidgetData.js'

// ==================== SETUP ====================

const $q = useQuasar()

// ==================== REACTIVE STATE ====================

// Test Configuration
const testWidgetId = ref('')
const timePreset = ref('last_1h')
const testMode = ref('full-integration')
const runningTest = ref(false)
const runningQuickTest = ref(false)
const showDebugInfo = ref(false)

// Time Range State
const showCustomTimeDialog = ref(false)
const customStartTime = ref('')
const customEndTime = ref('')
const currentTimeRange = ref(null)
const widgetRenderKey = ref(0)

// Enhanced time preset options
const timePresetOptions = [
  { label: 'Last 15 minutes', value: 'last_15m' },
  { label: 'Last 1 hour', value: 'last_1h' },
  { label: 'Last 2 hours', value: 'last_2h' },
  { label: 'Last 6 hours', value: 'last_6h' },
  { label: 'Last 12 hours', value: 'last_12h' },
  { label: 'Last 24 hours', value: 'last_24h' },
  { label: 'Last 3 days', value: 'last_3d' },
  { label: 'Last 7 days', value: 'last_7d' },
  { label: 'Custom Range', value: 'custom' }
]

const testModeOptions = [
  { label: 'Full Integration Test', value: 'full-integration' },
  { label: 'Configuration Only', value: 'config-only' },
  { label: 'Endpoint Only', value: 'endpoint-only' },
  { label: 'Chart Data Only', value: 'chart-data-only' },
  { label: 'API Format Only', value: 'api-format-only' }
]

const testOptions = ref({
  validateConfig: true,
  testEndpoint: true,
  validateChartData: true,
  performanceTest: true,
  testAPIFormat: true
})

// Predefined Test Widgets
const predefinedWidgets = ref([
  {
    widget_id: '92587d13-d13f-4051-bee7-28e5f00c8f62',
    widget_label: 'SOC BMS (Previously Problematic)',
    widget_type: 'line_chart',
    equipment_ids: [1],
    signal_ids: [1],
    filter_selections: {'1_n_bank': '1', '1_dcu': '1'},
    position_data: { x: 0, y: 0, w: 6, h: 4 }
  },
  {
    widget_id: '2d6ba3a5-1d2c-4c6d-bc39-5d2a1411b532',
    widget_label: 'SOC BMS-1 (Working Widget)',
    widget_type: 'line_chart',
    equipment_ids: [1],
    signal_ids: [1],
    filter_selections: {'1_n_bank': '1', '1_dcu': '1'},
    position_data: { x: 0, y: 0, w: 6, h: 4 }
  },
  {
    widget_id: 'test-widget-' + Date.now(),
    widget_label: 'Test Widget (Dynamic)',
    widget_type: 'line_chart',
    equipment_ids: [1],
    signal_ids: [1],
    filter_selections: {'1_n_bank': '1', '1_dcu': '1'},
    position_data: { x: 0, y: 0, w: 6, h: 4 }
  }
])

// Test Results
const testResults = ref(null)
const lastTestResult = ref(null)
const testSteps = ref([])
const testProgress = ref(0)
const performanceMetrics = ref(null)
const cacheStats = ref(null)
const apiFormatValidation = ref(null)

// Widget Status
const widgetStatus = ref({
  label: 'Not Started',
  color: 'grey',
  icon: 'help'
})

const apiFormatStatus = ref(null)

// UI State
const activeTab = ref('config')
const debugLog = ref([])
const autoScrollLog = ref(true)

// ==================== COMPUTED ====================

const selectedWidgetConfig = computed(() => {
  return predefinedWidgets.value.find(w => w.widget_id === testWidgetId.value)
})

const enhancedWidgetConfig = computed(() => {
  if (!selectedWidgetConfig.value) return null

  return {
    ...selectedWidgetConfig.value,
    // Ensure position data exists
    position_data: {
      x: 0,
      y: 0,
      w: 6,
      h: 4,
      ...selectedWidgetConfig.value.position_data
    },
    // Add time range context
    _testTimeRange: currentTimeRange.value,
    _renderKey: widgetRenderKey.value
  }
})

const exportPreview = computed(() => {
  if (!testResults.value) return 'No test results available'

  return widgetIntegrationService.exportDebugReport(testResults.value)
})

const statusBannerClass = computed(() => {
  if (!lastTestResult.value) return ''

  return lastTestResult.value.success ? 'bg-green-1 text-green-8' : 'bg-red-1 text-red-8'
})

const statusTitle = computed(() => {
  if (!lastTestResult.value) return ''

  return lastTestResult.value.success ? '✅ All Tests Passed!' : '❌ Tests Failed'
})

const statusSubtitle = computed(() => {
  if (!lastTestResult.value) return ''

  const result = lastTestResult.value
  if (result.success) {
    return `API working, ${result.dataPoints || 0} data points received in ${result.responseTime || 0}ms`
  } else {
    return `Error: ${result.error || 'Unknown error'}`
  }
})

const statusIcon = computed(() => {
  if (!lastTestResult.value) return 'help'
  return lastTestResult.value.success ? 'check_circle' : 'error'
})

const statusColor = computed(() => {
  if (!lastTestResult.value) return 'grey'
  return lastTestResult.value.success ? 'positive' : 'negative'
})

const currentRequestFormat = computed(() => {
  if (!currentTimeRange.value) return 'No time range selected'

  return JSON.stringify({
    time_start: currentTimeRange.value.start,
    time_end: currentTimeRange.value.end,
    time_range_type: currentTimeRange.value.range_type
  }, null, 2)
})

// ==================== TIME RANGE METHODS ====================

function onTimeRangeChanged(newPreset) {
  addDebugEntry('info', `Time range changed to: ${newPreset}`)

  if (newPreset === 'custom') {
    showCustomTimeDialog.value = true
    return
  }

  // Create time range from preset
  currentTimeRange.value = WidgetAPIService.createPresetTimeRange(newPreset)

  // Force widget re-render with new time range
  forceWidgetRefresh()

  addDebugEntry('info', `Applied time range: ${currentTimeRange.value.start} to ${currentTimeRange.value.end}`)
}

function setCustomRange(preset) {
  const now = new Date()
  let start

  switch (preset) {
    case '2h':
      start = new Date(now - 2 * 60 * 60 * 1000)
      break
    case '12h':
      start = new Date(now - 12 * 60 * 60 * 1000)
      break
    case '3d':
      start = new Date(now - 3 * 24 * 60 * 60 * 1000)
      break
    default:
      start = new Date(now - 60 * 60 * 1000)
  }

  customStartTime.value = formatDateTimeLocal(start)
  customEndTime.value = formatDateTimeLocal(now)
}

function applyCustomTimeRange() {
  if (!customStartTime.value || !customEndTime.value) {
    $q.notify({
      type: 'negative',
      message: 'Please select both start and end times',
      timeout: 3000
    })
    return
  }

  const start = new Date(customStartTime.value)
  const end = new Date(customEndTime.value)

  if (start >= end) {
    $q.notify({
      type: 'negative',
      message: 'Start time must be before end time',
      timeout: 3000
    })
    return
  }

  currentTimeRange.value = {
    start: start.toISOString(),
    end: end.toISOString(),
    range_type: 'custom'
  }

  timePreset.value = 'custom'
  showCustomTimeDialog.value = false

  // Force widget re-render
  forceWidgetRefresh()

  addDebugEntry('success', `Applied custom time range: ${start.toLocaleString()} to ${end.toLocaleString()}`)

  $q.notify({
    type: 'positive',
    message: 'Custom time range applied',
    timeout: 2000
  })
}

function formatDateTimeLocal(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}`
}

function formatTimeRangeDisplay() {
  if (!currentTimeRange.value) return 'No time range selected'

  const start = new Date(currentTimeRange.value.start)
  const end = new Date(currentTimeRange.value.end)

  return `${start.toLocaleString()} → ${end.toLocaleString()}`
}

function forceWidgetRefresh() {
  // Increment render key to force widget re-mount
  widgetRenderKey.value++

  addDebugEntry('info', 'Forcing widget refresh with new time range')
}

// ==================== TEST METHODS ====================

async function runQuickTest() {
  if (!testWidgetId.value) {
    $q.notify({
      type: 'negative',
      message: 'Please select a widget to test',
      timeout: 3000
    })
    return
  }

  runningQuickTest.value = true
  addDebugEntry('info', 'Starting quick API test...')

  try {
    // Ensure we have a time range
    if (!currentTimeRange.value) {
      currentTimeRange.value = WidgetAPIService.createPresetTimeRange(timePreset.value)
    }

    // Test API format first
    const requestData = {
      time_start: currentTimeRange.value.start,
      time_end: currentTimeRange.value.end,
      time_range_type: currentTimeRange.value.range_type
    }

    // Validate API format
    apiFormatValidation.value = WidgetAPIService.validateRequestFormat(requestData)

    if (apiFormatValidation.value.isValid) {
      apiFormatStatus.value = {
        label: 'Format OK',
        color: 'positive',
        icon: 'check_circle'
      }
      addDebugEntry('success', 'API format validation passed')
    } else {
      apiFormatStatus.value = {
        label: 'Format Issues',
        color: 'negative',
        icon: 'error'
      }
      addDebugEntry('error', 'API format validation failed')
      apiFormatValidation.value.errors.forEach(error => {
        addDebugEntry('error', error)
      })
    }

    // Test the actual API endpoint
    addDebugEntry('info', `Testing API endpoint for widget: ${testWidgetId.value}`)
    const result = await WidgetAPIService.testWidgetEndpoint(testWidgetId.value, currentTimeRange.value)

    lastTestResult.value = result

    if (result.success) {
      widgetStatus.value = {
        label: 'API Working',
        color: 'positive',
        icon: 'check_circle'
      }

      addDebugEntry('success', `Quick test passed! ${result.totalPoints} data points received`)

      $q.notify({
        type: 'positive',
        message: '✅ Quick test successful!',
        caption: `${result.totalPoints} data points in ${result.responseTime}ms`,
        timeout: 3000
      })
    } else {
      widgetStatus.value = {
        label: 'API Failed',
        color: 'negative',
        icon: 'error'
      }

      addDebugEntry('error', `Quick test failed: ${result.error}`)

      $q.notify({
        type: 'negative',
        message: '❌ Quick test failed',
        caption: result.error,
        timeout: 5000
      })
    }

  } catch (error) {
    console.error('❌ Quick test failed:', error)
    addDebugEntry('error', `Quick test error: ${error.message}`)

    widgetStatus.value = {
      label: 'Test Failed',
      color: 'negative',
      icon: 'error'
    }

    $q.notify({
      type: 'negative',
      message: 'Quick test error',
      caption: error.message,
      timeout: 5000
    })
  } finally {
    runningQuickTest.value = false
  }
}

async function runCompleteIntegrationTest() {
  if (!testWidgetId.value) {
    $q.notify({
      type: 'negative',
      message: 'Please select a widget to test',
      timeout: 3000
    })
    return
  }

  runningTest.value = true
  testProgress.value = 0
  testSteps.value = []

  addDebugEntry('info', 'Starting complete integration test...')

  try {
    updateTestStep('Initializing test...', 'pending', 'hourglass_empty', 'grey')
    testProgress.value = 0.1

    // Ensure we have a time range
    if (!currentTimeRange.value) {
      currentTimeRange.value = WidgetAPIService.createPresetTimeRange(timePreset.value)
    }

    // Get widget configuration
    const widgetConfig = selectedWidgetConfig.value
    if (!widgetConfig) {
      throw new Error('Widget configuration not found')
    }

    updateTestStep('Configuration loaded', 'success', 'check_circle', 'positive')
    testProgress.value = 0.2

    // Test API format if enabled
    if (testOptions.value.testAPIFormat) {
      updateTestStep('Testing API format...', 'pending', 'hourglass_empty', 'grey')
      const requestData = {
        time_start: currentTimeRange.value.start,
        time_end: currentTimeRange.value.end,
        time_range_type: currentTimeRange.value.range_type
      }

      apiFormatValidation.value = WidgetAPIService.validateRequestFormat(requestData)

      if (apiFormatValidation.value.isValid) {
        updateTestStep('API format validation passed', 'success', 'check_circle', 'positive')
        apiFormatStatus.value = { label: 'Format OK', color: 'positive', icon: 'check_circle' }
      } else {
        updateTestStep('API format has issues', 'warning', 'warning', 'warning')
        apiFormatStatus.value = { label: 'Format Issues', color: 'warning', icon: 'warning' }
      }
      testProgress.value = 0.3
    }

    // Run the comprehensive integration test
    addDebugEntry('info', `Testing widget: ${widgetConfig.widget_id}`)

    const results = await widgetIntegrationService.runIntegrationTest(
      testWidgetId.value,
      widgetConfig
    )

    testResults.value = results
    testProgress.value = 0.8

    // Update performance metrics and cache stats
    performanceMetrics.value = widgetIntegrationService.getPerformanceMetrics()
    cacheStats.value = getGlobalCacheStats()

    testProgress.value = 1.0

    // Update final status
    if (results.overallSuccess) {
      widgetStatus.value = {
        label: 'All Tests Passed',
        color: 'positive',
        icon: 'check_circle'
      }
      lastTestResult.value = { success: true, dataPoints: results.endpointTest?.dataPoints || 0, responseTime: results.endpointTest?.responseTime || 0 }
      updateTestStep('Integration test completed successfully', 'success', 'check_circle', 'positive')
      addDebugEntry('success', 'All integration tests passed!')

      $q.notify({
        type: 'positive',
        message: '🎉 All tests passed!',
        caption: 'Widget integration is working perfectly',
        timeout: 3000
      })
    } else {
      widgetStatus.value = {
        label: 'Issues Found',
        color: 'negative',
        icon: 'error'
      }
      lastTestResult.value = { success: false, error: 'Integration test found issues' }
      updateTestStep('Integration test found issues', 'error', 'error', 'negative')
      addDebugEntry('error', 'Integration test found issues')

      $q.notify({
        type: 'warning',
        message: '⚠️ Tests found issues',
        caption: 'Check the detailed results for more information',
        timeout: 5000
      })
    }

  } catch (error) {
    console.error('❌ Integration test failed:', error)

    widgetStatus.value = {
      label: 'Test Failed',
      color: 'negative',
      icon: 'error'
    }

    lastTestResult.value = { success: false, error: error.message }
    updateTestStep(`Test failed: ${error.message}`, 'error', 'error', 'negative')
    addDebugEntry('error', `Test failed: ${error.message}`)

    $q.notify({
      type: 'negative',
      message: 'Integration test failed',
      caption: error.message,
      timeout: 5000
    })
  } finally {
    runningTest.value = false
  }
}

// ==================== UTILITY METHODS ====================

function updateTestStep(label, status, icon, color, details = null) {
  const step = {
    label,
    status,
    icon,
    color,
    details,
    timing: format(new Date(), 'HH:mm:ss'),
    timestamp: new Date().toISOString()
  }

  testSteps.value.push(step)
}

function addDebugEntry(type, message) {
  const entry = {
    type,
    message,
    time: format(new Date(), 'HH:mm:ss.SSS')
  }

  debugLog.value.push(entry)

  if (autoScrollLog.value) {
    nextTick(() => {
      const debugArea = document.querySelector('.debug-log-area .q-scrollarea__content')
      if (debugArea) {
        debugArea.scrollTop = debugArea.scrollHeight
      }
    })
  }
}

function clearDebugLog() {
  debugLog.value = []
  addDebugEntry('info', 'Debug log cleared')
}

async function refreshTestWidget() {
  if (!testWidgetId.value) return

  addDebugEntry('info', 'Refreshing test widget...')

  // Trigger a refresh by updating the widget key or emitting an event
  widgetStatus.value = {
    label: 'Refreshing...',
    color: 'info',
    icon: 'refresh'
  }

  // Clear cache and re-run quick test
  clearTestCache()
  await runQuickTest()
}

function clearTestCache() {
  clearAllWidgetCache()
  cacheStats.value = getGlobalCacheStats()
  addDebugEntry('info', 'Widget cache cleared')

  $q.notify({
    type: 'info',
    message: 'Cache cleared',
    timeout: 2000
  })
}

// ==================== WIDGET EVENT HANDLERS ====================

function onWidgetChartReady(widgetId, chartData) {
  addDebugEntry('success', `Widget chart ready: ${widgetId}`)
  if (chartData?.metadata?.totalPoints) {
    addDebugEntry('info', `Chart data: ${chartData.metadata.totalPoints} points`)
  }

  widgetStatus.value = {
    label: 'Chart Ready',
    color: 'positive',
    icon: 'check_circle'
  }
}

function onWidgetChartError(widgetId, error) {
  addDebugEntry('error', `Widget chart error: ${widgetId} - ${error}`)
  widgetStatus.value = {
    label: 'Chart Error',
    color: 'negative',
    icon: 'error'
  }
}

function onWidgetChartUpdated(widgetId, chartData) {
  addDebugEntry('info', `Widget chart updated: ${widgetId}`)
  if (chartData?.metadata?.totalPoints) {
    addDebugEntry('info', `Updated data: ${chartData.metadata.totalPoints} points`)
  }
}

function onWidgetRefresh(widgetId) {
  addDebugEntry('info', `Widget refresh requested: ${widgetId}`)
}

// ==================== EXPORT FUNCTIONS ====================

function exportJsonReport() {
  if (!testResults.value) {
    $q.notify({
      type: 'warning',
      message: 'No test results to export',
      timeout: 2000
    })
    return
  }

  const reportData = widgetIntegrationService.exportDebugReport({
    ...testResults.value,
    apiFormatValidation: apiFormatValidation.value,
    cacheStats: cacheStats.value,
    debugLog: debugLog.value
  })

  const blob = new Blob([reportData], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = `enhanced-widget-test-${testWidgetId.value}-${Date.now()}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Enhanced test report exported successfully',
    timeout: 2000
  })
}

async function copyToClipboard() {
  if (!testResults.value) {
    $q.notify({
      type: 'warning',
      message: 'No test results to copy',
      timeout: 2000
    })
    return
  }

  try {
    const reportData = widgetIntegrationService.exportDebugReport({
      ...testResults.value,
      apiFormatValidation: apiFormatValidation.value,
      cacheStats: cacheStats.value,
      debugLog: debugLog.value
    })

    await navigator.clipboard.writeText(reportData)

    $q.notify({
      type: 'positive',
      message: 'Test results copied to clipboard',
      timeout: 2000
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy to clipboard',
      timeout: 2000
    })
  }
}

// ==================== LIFECYCLE ====================

onMounted(() => {
  addDebugEntry('info', 'Enhanced Widget Integration Test Suite initialized')

  // Set default widget for testing
  if (predefinedWidgets.value.length > 0) {
    testWidgetId.value = predefinedWidgets.value[0].widget_id
  }

  // Initialize default time range
  currentTimeRange.value = WidgetAPIService.createPresetTimeRange(timePreset.value)
  addDebugEntry('info', `Default time range initialized: ${timePreset.value}`)

  // Update cache stats
  cacheStats.value = getGlobalCacheStats()
})

// ==================== WATCHERS ====================

watch(testWidgetId, (newWidgetId) => {
  if (newWidgetId) {
    const widget = predefinedWidgets.value.find(w => w.widget_id === newWidgetId)
    if (widget) {
      addDebugEntry('info', `Selected widget: ${widget.widget_label}`)
      widgetStatus.value = {
        label: 'Widget Selected',
        color: 'info',
        icon: 'widgets'
      }

      // Reset status indicators
      apiFormatStatus.value = null
      lastTestResult.value = null

      // Force widget refresh with current time range
      forceWidgetRefresh()
    }
  }
})

watch(timePreset, (newPreset) => {
  addDebugEntry('info', `Time range preset changed to: ${newPreset}`)
})
</script>

<style scoped>
.integration-test-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header h4 {
  color: #1976d2;
  font-weight: 600;
}

.test-config-card,
.widget-test-card,
.test-results-card,
.detailed-results-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.banner-content {
  flex: 1;
}

.banner-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.banner-subtitle {
  margin-top: 4px;
  opacity: 0.8;
}

.time-range-display {
  padding: 8px 0;
}

.widget-test-container {
  height: 100%;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.widget-time-info {
  display: flex;
  align-items: center;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.no-widget-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.widget-status-indicators {
  display: flex;
  align-items: center;
}

.test-results-content {
  padding: 16px;
}

.test-steps {
  max-height: 200px;
  overflow-y: auto;
}

.test-step {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.test-step.success {
  background: #f3f9f3;
}

.test-step.error {
  background: #fef5f5;
}

.test-step.pending {
  background: #f8f8f8;
}

.test-step.warning {
  background: #fff8e1;
}

.step-label {
  flex: 1;
  margin-left: 8px;
}

.step-details,
.step-timing {
  margin-left: 32px;
  margin-top: 4px;
  font-size: 0.75rem;
}

.performance-section {
  border-top: 1px solid #e0e0e0;
  padding-top: 16px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-item {
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.metric-label {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1976d2;
}

.quick-actions .q-btn {
  justify-content: flex-start;
}

.validation-header,
.endpoint-header,
.chart-data-header,
.api-format-header {
  display: flex;
  align-items: center;
}

.config-json,
.response-json,
.export-json,
.api-format-code {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  margin: 0;
}

.structure-info {
  text-align: center;
}

.format-guidelines {
  background: #f9f9f9;
  border-radius: 4px;
}

.format-guidelines ul {
  margin: 8px 0;
  padding-left: 20px;
}

.format-guidelines code {
  background: #e0e0e0;
  padding: 2px 4px;
  border-radius: 2px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.85rem;
}

.debug-log {
  font-family: 'Roboto Mono', monospace;
}

.debug-controls {
  display: flex;
  align-items: center;
}

.debug-log-area {
  background: #f8f8f8;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
}

.debug-entry {
  display: flex;
  margin-bottom: 4px;
  font-size: 0.8rem;
}

.debug-entry.success {
  color: #4caf50;
}

.debug-entry.error {
  color: #f44336;
}

.debug-entry.warning {
  color: #ff9800;
}

.debug-entry.info {
  color: #2196f3;
}

.debug-time {
  width: 80px;
  color: #666;
  font-weight: 500;
}

.debug-message {
  flex: 1;
  margin-left: 8px;
}

.export-options {
  padding: 16px;
}

.export-preview-area {
  background: #f8f8f8;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .config-json,
  .response-json,
  .export-json,
  .api-format-code {
    font-size: 0.7rem;
  }

  .widget-time-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* Animation */
.test-step {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Custom time dialog */
.q-dialog .q-card {
  max-width: 90vw;
}

/* Widget test container enhancements */
.widget-test-container:hover {
  border-color: #1976d2;
  background: #f8f9fa;
}

/* Status indicators */
.widget-status-indicators .q-chip {
  font-weight: 500;
}

/* Time range display */
.time-range-display .q-chip {
  font-size: 0.9rem;
  padding: 8px 12px;
}
</style>
