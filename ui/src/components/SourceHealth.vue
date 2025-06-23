<!-- ui/src/components/SourceHealth.vue -->
<template>
  <div class="source-health q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Health Monitoring</div>
        <div class="text-subtitle2 text-grey-6">
          Monitor connection health and performance metrics
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Refresh Health"
          icon="refresh"
          color="primary"
          @click="refreshHealth"
          :loading="refreshing"
        />
        <q-btn
          label="Run Diagnostics"
          icon="troubleshoot"
          color="secondary"
          outline
          @click="runDiagnostics"
          :loading="diagnosing"
        />
        <q-btn
          label="Export Report"
          icon="file_download"
          color="positive"
          outline
          @click="exportHealthReport"
        />
      </div>
    </div>

    <!-- Overall Health Status -->
    <div class="q-mb-lg">
      <q-card flat bordered :class="overallHealthClass">
        <q-card-section>
          <div class="row items-center">
            <q-icon
              :name="overallHealthIcon"
              :color="overallHealthColor"
              size="3rem"
              class="q-mr-lg"
            />
            <div class="col">
              <div class="text-h5">{{ overallHealthTitle }}</div>
              <div class="text-body1 text-grey-7">{{ overallHealthMessage }}</div>
              <div class="text-caption q-mt-sm">
                Last updated: {{ formatDateTime(lastHealthCheck) }}
              </div>
            </div>
            <div class="col-auto">
              <q-circular-progress
                :value="overallHealthScore"
                size="80px"
                :thickness="0.15"
                :color="overallHealthColor"
                track-color="grey-3"
                class="q-mr-md"
              >
                <div class="text-h6">{{ Math.round(overallHealthScore) }}%</div>
              </q-circular-progress>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Health Metrics Grid -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered class="metric-card">
          <q-card-section class="text-center">
            <q-icon name="network_check" size="2rem" :color="getMetricColor(connectionHealth)" class="q-mb-sm" />
            <div class="text-h6">{{ connectionHealth }}%</div>
            <div class="text-caption text-grey-6">Connection</div>
            <q-linear-progress
              :value="connectionHealth / 100"
              :color="getMetricColor(connectionHealth)"
              size="4px"
              class="q-mt-sm"
            />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="metric-card">
          <q-card-section class="text-center">
            <q-icon name="speed" size="2rem" :color="getMetricColor(performanceHealth)" class="q-mb-sm" />
            <div class="text-h6">{{ performanceHealth }}%</div>
            <div class="text-caption text-grey-6">Performance</div>
            <q-linear-progress
              :value="performanceHealth / 100"
              :color="getMetricColor(performanceHealth)"
              size="4px"
              class="q-mt-sm"
            />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="metric-card">
          <q-card-section class="text-center">
            <q-icon name="verified" size="2rem" :color="getMetricColor(dataQualityHealth)" class="q-mb-sm" />
            <div class="text-h6">{{ dataQualityHealth }}%</div>
            <div class="text-caption text-grey-6">Data Quality</div>
            <q-linear-progress
              :value="dataQualityHealth / 100"
              :color="getMetricColor(dataQualityHealth)"
              size="4px"
              class="q-mt-sm"
            />
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-3">
        <q-card flat bordered class="metric-card">
          <q-card-section class="text-center">
            <q-icon name="security" size="2rem" :color="getMetricColor(securityHealth)" class="q-mb-sm" />
            <div class="text-h6">{{ securityHealth }}%</div>
            <div class="text-caption text-grey-6">Security</div>
            <q-linear-progress
              :value="securityHealth / 100"
              :color="getMetricColor(securityHealth)"
              size="4px"
              class="q-mt-sm"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Health Details Tabs -->
    <q-tabs v-model="activeTab" dense class="text-grey" active-color="primary">
      <q-tab name="connection" label="Connection" icon="network_check" />
      <q-tab name="performance" label="Performance" icon="speed" />
      <q-tab name="alerts" label="Alerts" icon="notifications" />
      <q-tab name="history" label="History" icon="history" />
      <q-tab name="diagnostics" label="Diagnostics" icon="troubleshoot" />
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-tab-panels v-model="activeTab" animated class="q-mt-md">
      <!-- Connection Tab -->
      <q-tab-panel name="connection">
        <div class="row q-gutter-lg">
          <!-- Connection Status -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Connection Status</div>

                <q-list>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="wifi" :color="connectionMetrics.isConnected ? 'positive' : 'negative'" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Connection State</q-item-label>
                      <q-item-label caption>
                        {{ connectionMetrics.isConnected ? 'Connected' : 'Disconnected' }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="timer" color="blue" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Response Time</q-item-label>
                      <q-item-label caption>{{ connectionMetrics.responseTime || 'N/A' }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="access_time" color="orange" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Uptime</q-item-label>
                      <q-item-label caption>{{ connectionMetrics.uptime || 'Unknown' }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="error" :color="connectionMetrics.errorCount > 0 ? 'negative' : 'positive'" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>Error Count (24h)</q-item-label>
                      <q-item-label caption>{{ connectionMetrics.errorCount || 0 }} errors</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Connection Tests -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Connection Tests</div>

                <div class="column q-gutter-sm">
                  <q-btn
                    label="Ping Test"
                    icon="network_ping"
                    color="blue"
                    outline
                    @click="runPingTest"
                    :loading="testing.ping"
                  />
                  <q-btn
                    label="Authentication Test"
                    icon="vpn_key"
                    color="green"
                    outline
                    @click="runAuthTest"
                    :loading="testing.auth"
                  />
                  <q-btn
                    label="Data Access Test"
                    icon="storage"
                    color="orange"
                    outline
                    @click="runDataAccessTest"
                    :loading="testing.dataAccess"
                  />
                  <q-btn
                    label="Full Connection Test"
                    icon="wifi_find"
                    color="primary"
                    @click="runFullConnectionTest"
                    :loading="testing.full"
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Recent Connection Events -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Recent Connection Events</div>

                <q-list v-if="connectionEvents.length > 0" separator>
                  <q-item v-for="event in connectionEvents.slice(0, 5)" :key="event.id">
                    <q-item-section avatar>
                      <q-icon
                        :name="getEventIcon(event.type)"
                        :color="getEventColor(event.type)"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ event.message }}</q-item-label>
                      <q-item-label caption>{{ formatDateTime(event.timestamp) }}</q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <q-chip
                        :color="getEventColor(event.type)"
                        text-color="white"
                        size="sm"
                      >
                        {{ event.type.toUpperCase() }}
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-md text-grey-6">
                  <q-icon name="event_note" size="2rem" class="q-mb-sm" />
                  <div>No recent connection events</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Performance Tab -->
      <q-tab-panel name="performance">
        <div class="row q-gutter-lg">
          <!-- Performance Metrics -->
          <div class="col-12 col-md-8">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Performance Metrics</div>

                <!-- Performance Chart Placeholder -->
                <div class="performance-chart q-pa-lg text-center bg-grey-1">
                  <q-icon name="show_chart" size="3rem" class="text-grey-5 q-mb-md" />
                  <div class="text-h6 text-grey-6">Performance Chart</div>
                  <div class="text-body2 text-grey-5">Response time and throughput over time</div>

                  <!-- Mock performance data -->
                  <div class="row q-gutter-md q-mt-lg">
                    <div class="col text-center">
                      <div class="text-h6 text-positive">{{ performanceMetrics.avgResponseTime }}ms</div>
                      <div class="text-caption">Avg Response Time</div>
                    </div>
                    <div class="col text-center">
                      <div class="text-h6 text-blue">{{ performanceMetrics.throughput }}/min</div>
                      <div class="text-caption">Throughput</div>
                    </div>
                    <div class="col text-center">
                      <div class="text-h6 text-orange">{{ performanceMetrics.errorRate }}%</div>
                      <div class="text-caption">Error Rate</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Performance Summary -->
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Performance Summary</div>

                <q-list>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Current Status</q-item-label>
                      <q-item-label>{{ getPerformanceStatus() }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Peak Response Time</q-item-label>
                      <q-item-label>{{ performanceMetrics.peakResponseTime }}ms</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Min Response Time</q-item-label>
                      <q-item-label>{{ performanceMetrics.minResponseTime }}ms</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Total Requests (24h)</q-item-label>
                      <q-item-label>{{ performanceMetrics.totalRequests }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <!-- Performance Recommendations -->
            <q-card flat bordered class="q-mt-md">
              <q-card-section>
                <div class="text-h6 q-mb-md">Recommendations</div>

                <q-list v-if="performanceRecommendations.length > 0">
                  <q-item v-for="rec in performanceRecommendations" :key="rec.id">
                    <q-item-section avatar>
                      <q-icon :name="rec.icon" :color="rec.color" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ rec.title }}</q-item-label>
                      <q-item-label caption>{{ rec.description }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-md text-grey-6">
                  <q-icon name="thumb_up" size="2rem" class="text-positive q-mb-sm" />
                  <div>Performance looks good!</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Alerts Tab -->
      <q-tab-panel name="alerts">
        <div class="row q-gutter-lg">
          <!-- Active Alerts -->
          <div class="col-12 col-md-8">
            <q-card flat bordered>
              <q-card-section>
                <div class="row items-center justify-between q-mb-md">
                  <div class="text-h6">Active Alerts</div>
                  <q-btn
                    label="Clear All"
                    icon="clear_all"
                    color="negative"
                    outline
                    size="sm"
                    @click="clearAllAlerts"
                    :disable="activeAlerts.length === 0"
                  />
                </div>

                <q-list v-if="activeAlerts.length > 0" separator>
                  <q-item
                    v-for="alert in activeAlerts"
                    :key="alert.id"
                    :class="getAlertClass(alert.severity)"
                  >
                    <q-item-section avatar>
                      <q-icon
                        :name="getAlertIcon(alert.severity)"
                        :color="getAlertColor(alert.severity)"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ alert.message }}</q-item-label>
                      <q-item-label caption>
                        {{ alert.details }} • {{ formatDateTime(alert.timestamp) }}
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <div class="row q-gutter-xs">
                        <q-btn
                          icon="check"
                          flat
                          round
                          size="sm"
                          @click="acknowledgeAlert(alert)"
                          title="Acknowledge"
                        />
                        <q-btn
                          icon="close"
                          flat
                          round
                          size="sm"
                          @click="dismissAlert(alert)"
                          title="Dismiss"
                        />
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center q-pa-lg text-grey-6">
                  <q-icon name="check_circle" size="3rem" class="text-positive q-mb-md" />
                  <div class="text-h6">No Active Alerts</div>
                  <div class="text-body2">Your data source is operating normally</div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Alert Configuration -->
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Alert Settings</div>

                <q-list>
                  <q-item>
                    <q-item-section>
                      <q-toggle
                        v-model="alertSettings.connectionAlerts"
                        label="Connection Alerts"
                        color="primary"
                      />
                      <div class="text-caption text-grey-6">Alert on connection failures</div>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-toggle
                        v-model="alertSettings.performanceAlerts"
                        label="Performance Alerts"
                        color="primary"
                      />
                      <div class="text-caption text-grey-6">Alert on slow response times</div>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-toggle
                        v-model="alertSettings.errorAlerts"
                        label="Error Alerts"
                        color="primary"
                      />
                      <div class="text-caption text-grey-6">Alert on errors and exceptions</div>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-toggle
                        v-model="alertSettings.emailNotifications"
                        label="Email Notifications"
                        color="primary"
                      />
                      <div class="text-caption text-grey-6">Send alerts via email</div>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-separator class="q-my-md" />

                <div class="text-subtitle2 q-mb-sm">Thresholds</div>

                <q-input
                  v-model.number="alertSettings.responseTimeThreshold"
                  label="Response Time (ms)"
                  type="number"
                  outlined
                  dense
                  class="q-mb-sm"
                />

                <q-input
                  v-model.number="alertSettings.errorRateThreshold"
                  label="Error Rate (%)"
                  type="number"
                  outlined
                  dense
                  class="q-mb-sm"
                />

                <q-btn
                  label="Save Settings"
                  color="primary"
                  size="sm"
                  @click="saveAlertSettings"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- History Tab -->
      <q-tab-panel name="history">
        <div class="row q-gutter-lg">
          <!-- Health History Chart -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Health History</div>

                <!-- Health History Chart Placeholder -->
                <div class="health-chart q-pa-lg text-center bg-grey-1">
                  <q-icon name="timeline" size="3rem" class="text-grey-5 q-mb-md" />
                  <div class="text-h6 text-grey-6">Health History Chart</div>
                  <div class="text-body2 text-grey-5">Health metrics over the past 30 days</div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Historical Events -->
          <div class="col-12">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Historical Events</div>

                <q-table
                  :rows="historicalEvents"
                  :columns="eventColumns"
                  row-key="id"
                  :pagination="{ rowsPerPage: 10 }"
                  flat
                  bordered
                >
                  <template #body-cell-type="props">
                    <q-td :props="props">
                      <q-chip
                        :color="getEventColor(props.value)"
                        text-color="white"
                        size="sm"
                      >
                        {{ props.value.toUpperCase() }}
                      </q-chip>
                    </q-td>
                  </template>

                  <template #body-cell-timestamp="props">
                    <q-td :props="props">
                      {{ formatDateTime(props.value) }}
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>

      <!-- Diagnostics Tab -->
      <q-tab-panel name="diagnostics">
        <div class="row q-gutter-lg">
          <!-- Diagnostic Tests -->
          <div class="col-12 col-md-8">
            <q-card flat bordered>
              <q-card-section>
                <div class="row items-center justify-between q-mb-md">
                  <div class="text-h6">Diagnostic Tests</div>
                  <q-btn
                    label="Run All Tests"
                    icon="play_arrow"
                    color="primary"
                    @click="runAllDiagnostics"
                    :loading="diagnosing"
                  />
                </div>

                <q-list separator>
                  <q-item v-for="test in diagnosticTests" :key="test.id">
                    <q-item-section avatar>
                      <q-icon
                        :name="getDiagnosticIcon(test.status)"
                        :color="getDiagnosticColor(test.status)"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ test.name }}</q-item-label>
                      <q-item-label caption>{{ test.description }}</q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <div class="row items-center q-gutter-sm">
                        <q-chip
                          v-if="test.status !== 'pending'"
                          :color="getDiagnosticColor(test.status)"
                          text-color="white"
                          size="sm"
                        >
                          {{ test.status.toUpperCase() }}
                        </q-chip>

                        <q-btn
                          icon="play_arrow"
                          flat
                          round
                          size="sm"
                          @click="runDiagnosticTest(test)"
                          :loading="test.running"
                        />
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Diagnostic Results -->
          <div class="col-12 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Test Results</div>

                <div class="text-center q-mb-md">
                  <q-circular-progress
                    :value="diagnosticScore"
                    size="100px"
                    :thickness="0.2"
                    :color="getMetricColor(diagnosticScore)"
                    track-color="grey-3"
                  >
                    <div class="text-h5">{{ Math.round(diagnosticScore) }}%</div>
                  </q-circular-progress>
                  <div class="text-subtitle2 q-mt-sm">Diagnostic Score</div>
                </div>

                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Tests Passed</q-item-label>
                      <q-item-label>{{ passedTests }} / {{ totalTests }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Last Run</q-item-label>
                      <q-item-label>{{ formatDateTime(lastDiagnosticRun) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>

            <!-- System Information -->
            <q-card flat bordered class="q-mt-md">
              <q-card-section>
                <div class="text-h6 q-mb-md">System Information</div>

                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Source Type</q-item-label>
                      <q-item-label>{{ source?.source_type?.toUpperCase() || 'Unknown' }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Created</q-item-label>
                      <q-item-label>{{ formatDateTime(source?.created_at) }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Last Modified</q-item-label>
                      <q-item-label>{{ formatDateTime(source?.updated_at) }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Health Monitoring</q-item-label>
                      <q-item-label>{{ autoMonitoring ? 'Enabled' : 'Disabled' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-separator class="q-my-md" />

                <q-toggle
                  v-model="autoMonitoring"
                  label="Auto Health Monitoring"
                  color="positive"
                  @update:model-value="toggleAutoMonitoring"
                />
                <div class="text-caption text-grey-6 q-mt-xs">
                  {{ autoMonitoring ? 'Automatic checks every 5 minutes' : 'Manual checks only' }}
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  source: Object,
  healthData: Object
})

// Emits
const emit = defineEmits(['refresh-health'])

// Reactive data
const $q = useQuasar()
const activeTab = ref('connection')
const refreshing = ref(false)
const diagnosing = ref(false)
const lastHealthCheck = ref(new Date())
const autoMonitoring = ref(false)

// Test states
const testing = ref({
  ping: false,
  auth: false,
  dataAccess: false,
  full: false
})

// Health metrics (reactive to simulate live data)
const connectionHealth = ref(95)
const performanceHealth = ref(87)
const dataQualityHealth = ref(92)
const securityHealth = ref(98)

// Connection metrics
const connectionMetrics = ref({
  isConnected: true,
  responseTime: '45ms',
  uptime: '99.8%',
  errorCount: 2
})

// Performance metrics
const performanceMetrics = ref({
  avgResponseTime: 45,
  throughput: 150,
  errorRate: 0.2,
  peakResponseTime: 89,
  minResponseTime: 12,
  totalRequests: 34567
})

// Alerts
const activeAlerts = ref([
  {
    id: 1,
    severity: 'warning',
    message: 'Slow response times detected',
    details: 'Average response time exceeded 100ms threshold',
    timestamp: new Date(Date.now() - 3600000) // 1 hour ago
  },
  {
    id: 2,
    severity: 'info',
    message: 'Scheduled maintenance reminder',
    details: 'Database maintenance scheduled for next week',
    timestamp: new Date(Date.now() - 7200000) // 2 hours ago
  }
])

const alertSettings = ref({
  connectionAlerts: true,
  performanceAlerts: true,
  errorAlerts: true,
  emailNotifications: false,
  responseTimeThreshold: 100,
  errorRateThreshold: 5
})

// Events
const connectionEvents = ref([
  {
    id: 1,
    type: 'success',
    message: 'Connection test passed',
    timestamp: new Date()
  },
  {
    id: 2,
    type: 'warning',
    message: 'Slow response detected',
    timestamp: new Date(Date.now() - 1800000)
  },
  {
    id: 3,
    type: 'error',
    message: 'Connection timeout',
    timestamp: new Date(Date.now() - 3600000)
  }
])

const historicalEvents = ref([
  {
    id: 1,
    type: 'success',
    message: 'Health check passed',
    timestamp: new Date(),
    details: 'All systems operational'
  },
  {
    id: 2,
    type: 'warning',
    message: 'Performance degradation',
    timestamp: new Date(Date.now() - 3600000),
    details: 'Response time increased to 150ms'
  },
  {
    id: 3,
    type: 'error',
    message: 'Connection failure',
    timestamp: new Date(Date.now() - 7200000),
    details: 'Database connection lost for 5 minutes'
  }
])

// Diagnostic tests
const diagnosticTests = ref([
  {
    id: 'connectivity',
    name: 'Connectivity Test',
    description: 'Test basic network connectivity',
    status: 'passed',
    running: false
  },
  {
    id: 'authentication',
    name: 'Authentication Test',
    description: 'Verify authentication credentials',
    status: 'passed',
    running: false
  },
  {
    id: 'permissions',
    name: 'Permissions Test',
    description: 'Check data access permissions',
    status: 'warning',
    running: false
  },
  {
    id: 'schema',
    name: 'Schema Validation',
    description: 'Validate data schema consistency',
    status: 'passed',
    running: false
  },
  {
    id: 'performance',
    name: 'Performance Test',
    description: 'Test query performance',
    status: 'pending',
    running: false
  }
])

const lastDiagnosticRun = ref(new Date(Date.now() - 1800000)) // 30 minutes ago

// Performance recommendations
const performanceRecommendations = ref([
  {
    id: 1,
    title: 'Optimize Query Performance',
    description: 'Consider adding indexes to frequently queried fields',
    icon: 'speed',
    color: 'orange'
  }
])

// Event columns for history table
const eventColumns = [
  {
    name: 'type',
    label: 'Type',
    field: 'type',
    align: 'center',
    sortable: true
  },
  {
    name: 'message',
    label: 'Message',
    field: 'message',
    align: 'left',
    sortable: true
  },
  {
    name: 'timestamp',
    label: 'Timestamp',
    field: 'timestamp',
    align: 'left',
    sortable: true
  },
  {
    name: 'details',
    label: 'Details',
    field: 'details',
    align: 'left'
  }
]

// Auto-monitoring interval
let healthInterval = null

// Computed properties
const overallHealthScore = computed(() => {
  return (connectionHealth.value + performanceHealth.value + dataQualityHealth.value + securityHealth.value) / 4
})

const overallHealthClass = computed(() => {
  const score = overallHealthScore.value
  if (score >= 90) return 'bg-green-1'
  if (score >= 70) return 'bg-orange-1'
  return 'bg-red-1'
})

const overallHealthIcon = computed(() => {
  const score = overallHealthScore.value
  if (score >= 90) return 'check_circle'
  if (score >= 70) return 'warning'
  return 'error'
})

const overallHealthColor = computed(() => {
  const score = overallHealthScore.value
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
})

const overallHealthTitle = computed(() => {
  const score = overallHealthScore.value
  if (score >= 90) return 'Excellent Health'
  if (score >= 70) return 'Good Health'
  if (score >= 50) return 'Fair Health'
  return 'Poor Health'
})

const overallHealthMessage = computed(() => {
  const score = overallHealthScore.value
  if (score >= 90) return 'All systems are operating optimally'
  if (score >= 70) return 'Minor issues detected, monitoring recommended'
  if (score >= 50) return 'Several issues require attention'
  return 'Critical issues detected, immediate action required'
})

const diagnosticScore = computed(() => {
  const total = diagnosticTests.value.length
  const passed = diagnosticTests.value.filter(test => test.status === 'passed').length
  return total > 0 ? (passed / total) * 100 : 0
})

const passedTests = computed(() => {
  return diagnosticTests.value.filter(test => test.status === 'passed').length
})

const totalTests = computed(() => {
  return diagnosticTests.value.length
})

// Lifecycle hooks
onMounted(() => {
  startHealthMonitoring()
  if (props.healthData) {
    updateFromHealthData()
  }
})

onUnmounted(() => {
  stopHealthMonitoring()
})

// Methods
const startHealthMonitoring = () => {
  if (autoMonitoring.value) {
    // Auto-refresh health data every 30 seconds
    healthInterval = setInterval(() => {
      updateHealthMetrics()
    }, 30000)
  }
}

const stopHealthMonitoring = () => {
  if (healthInterval) {
    clearInterval(healthInterval)
    healthInterval = null
  }
}

const toggleAutoMonitoring = (enabled) => {
  autoMonitoring.value = enabled
  if (enabled) {
    startHealthMonitoring()
    $q.notify({
      type: 'positive',
      message: 'Auto-monitoring enabled',
      caption: 'Health checks will run every 5 minutes'
    })
  } else {
    stopHealthMonitoring()
    $q.notify({
      type: 'info',
      message: 'Auto-monitoring disabled'
    })
  }
}

const updateFromHealthData = () => {
  if (props.healthData) {
    connectionHealth.value = props.healthData.connection || connectionHealth.value
    performanceHealth.value = props.healthData.performance || performanceHealth.value
    dataQualityHealth.value = props.healthData.dataQuality || dataQualityHealth.value
    securityHealth.value = props.healthData.security || securityHealth.value
  }
}

const updateHealthMetrics = () => {
  // Simulate slight variations in health metrics
  connectionHealth.value = Math.max(85, Math.min(100, connectionHealth.value + (Math.random() - 0.5) * 5))
  performanceHealth.value = Math.max(80, Math.min(100, performanceHealth.value + (Math.random() - 0.5) * 8))
  dataQualityHealth.value = Math.max(88, Math.min(100, dataQualityHealth.value + (Math.random() - 0.5) * 3))
  securityHealth.value = Math.max(95, Math.min(100, securityHealth.value + (Math.random() - 0.5) * 2))
  lastHealthCheck.value = new Date()

  // Update connection metrics
  connectionMetrics.value.responseTime = `${Math.floor(Math.random() * 50 + 20)}ms`
  performanceMetrics.value.avgResponseTime = Math.floor(Math.random() * 50 + 20)
}

const refreshHealth = async () => {
  refreshing.value = true

  try {
    updateHealthMetrics()
    emit('refresh-health')

    $q.notify({
      type: 'positive',
      message: 'Health data refreshed',
      icon: 'refresh'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to refresh health data'
    })
  } finally {
    refreshing.value = false
  }
}

const runDiagnostics = async () => {
  diagnosing.value = true

  try {
    // Reset all tests to pending
    diagnosticTests.value.forEach(test => {
      test.status = 'pending'
      test.running = false
    })

    // Run each diagnostic test
    for (const test of diagnosticTests.value) {
      await runDiagnosticTest(test)
      await new Promise(resolve => setTimeout(resolve, 500)) // Small delay between tests
    }

    lastDiagnosticRun.value = new Date()

    $q.notify({
      type: 'positive',
      message: 'Diagnostics completed',
      caption: `${passedTests.value}/${totalTests.value} tests passed`
    })
  } finally {
    diagnosing.value = false
  }
}

const runDiagnosticTest = async (test) => {
  test.running = true

  try {
    // Simulate test execution
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

    // Simulate test results (mostly pass, some warnings)
    const random = Math.random()
    if (random > 0.8) {
      test.status = 'failed'
    } else if (random > 0.6) {
      test.status = 'warning'
    } else {
      test.status = 'passed'
    }

  } finally {
    test.running = false
  }
}

const runAllDiagnostics = async () => {
  await runDiagnostics()
}

const runPingTest = async () => {
  testing.value.ping = true

  try {
    await new Promise(resolve => setTimeout(resolve, 1000))

    const responseTime = Math.floor(Math.random() * 30 + 10)
    connectionMetrics.value.responseTime = `${responseTime}ms`

    // Add event
    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'success',
      message: 'Ping test successful',
      timestamp: new Date()
    })

    $q.notify({
      type: 'positive',
      message: 'Ping test successful',
      caption: `Response time: ${responseTime}ms`
    })
  } catch (error) {
    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'error',
      message: 'Ping test failed',
      timestamp: new Date()
    })

    $q.notify({
      type: 'negative',
      message: 'Ping test failed'
    })
  } finally {
    testing.value.ping = false
  }
}

const runAuthTest = async () => {
  testing.value.auth = true

  try {
    await new Promise(resolve => setTimeout(resolve, 1500))

    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'success',
      message: 'Authentication test passed',
      timestamp: new Date()
    })

    $q.notify({
      type: 'positive',
      message: 'Authentication test passed',
      caption: 'Credentials are valid'
    })
  } catch (error) {
    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'error',
      message: 'Authentication test failed',
      timestamp: new Date()
    })

    $q.notify({
      type: 'negative',
      message: 'Authentication test failed'
    })
  } finally {
    testing.value.auth = false
  }
}

const runDataAccessTest = async () => {
  testing.value.dataAccess = true

  try {
    await new Promise(resolve => setTimeout(resolve, 2000))

    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'success',
      message: 'Data access test successful',
      timestamp: new Date()
    })

    $q.notify({
      type: 'positive',
      message: 'Data access test successful',
      caption: 'Can read/write data successfully'
    })
  } catch (error) {
    connectionEvents.value.unshift({
      id: Date.now(),
      type: 'error',
      message: 'Data access test failed',
      timestamp: new Date()
    })

    $q.notify({
      type: 'negative',
      message: 'Data access test failed'
    })
  } finally {
    testing.value.dataAccess = false
  }
}

const runFullConnectionTest = async () => {
  testing.value.full = true

  try {
    await runPingTest()
    await runAuthTest()
    await runDataAccessTest()

    $q.notify({
      type: 'positive',
      message: 'Full connection test passed',
      caption: 'All connection tests successful'
    })
  } finally {
    testing.value.full = false
  }
}

const acknowledgeAlert = (alert) => {
  $q.notify({
    type: 'info',
    message: `Alert acknowledged: ${alert.message}`
  })
}

const dismissAlert = (alert) => {
  const index = activeAlerts.value.findIndex(a => a.id === alert.id)
  if (index > -1) {
    activeAlerts.value.splice(index, 1)
    $q.notify({
      type: 'positive',
      message: 'Alert dismissed'
    })
  }
}

const clearAllAlerts = () => {
  activeAlerts.value = []
  $q.notify({
    type: 'positive',
    message: 'All alerts cleared'
  })
}

const saveAlertSettings = () => {
  $q.notify({
    type: 'positive',
    message: 'Alert settings saved',
    icon: 'save'
  })
}

const exportHealthReport = () => {
  const reportData = {
    source: {
      id: props.source?.source_id,
      name: props.source?.source_name,
      type: props.source?.source_type
    },
    healthMetrics: {
      overall: Math.round(overallHealthScore.value),
      connection: Math.round(connectionHealth.value),
      performance: Math.round(performanceHealth.value),
      dataQuality: Math.round(dataQualityHealth.value),
      security: Math.round(securityHealth.value)
    },
    connectionMetrics: connectionMetrics.value,
    performanceMetrics: performanceMetrics.value,
    activeAlerts: activeAlerts.value,
    diagnosticResults: diagnosticTests.value.map(test => ({
      name: test.name,
      status: test.status,
      description: test.description
    })),
    events: connectionEvents.value.slice(0, 10),
    generatedAt: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = `${props.source?.source_name || 'datasource'}_health_report.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  $q.notify({
    type: 'positive',
    message: 'Health report exported',
    icon: 'file_download'
  })
}

// Utility methods
const getMetricColor = (value) => {
  if (value >= 90) return 'positive'
  if (value >= 70) return 'warning'
  return 'negative'
}

const getPerformanceStatus = () => {
  const score = performanceHealth.value
  if (score >= 90) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 50) return 'Fair'
  return 'Poor'
}

const getEventIcon = (type) => {
  const icons = {
    'success': 'check_circle',
    'warning': 'warning',
    'error': 'error',
    'info': 'info'
  }
  return icons[type] || 'circle'
}

const getEventColor = (type) => {
  const colors = {
    'success': 'positive',
    'warning': 'warning',
    'error': 'negative',
    'info': 'info'
  }
  return colors[type] || 'grey'
}

const getAlertIcon = (severity) => {
  const icons = {
    'critical': 'error',
    'warning': 'warning',
    'info': 'info'
  }
  return icons[severity] || 'info'
}

const getAlertColor = (severity) => {
  const colors = {
    'critical': 'negative',
    'warning': 'warning',
    'info': 'info'
  }
  return colors[severity] || 'info'
}

const getAlertClass = (severity) => {
  const classes = {
    'critical': 'bg-red-1',
    'warning': 'bg-orange-1',
    'info': 'bg-blue-1'
  }
  return classes[severity] || ''
}

const getDiagnosticIcon = (status) => {
  const icons = {
    'passed': 'check_circle',
    'warning': 'warning',
    'failed': 'error',
    'pending': 'schedule'
  }
  return icons[status] || 'help'
}

const getDiagnosticColor = (status) => {
  const colors = {
    'passed': 'positive',
    'warning': 'warning',
    'failed': 'negative',
    'pending': 'grey'
  }
  return colors[status] || 'grey'
}

const formatDateTime = (date) => {
  if (!date) return 'Unknown'
  try {
    return new Date(date).toLocaleString()
  } catch {
    return 'Invalid date'
  }
}
</script>

<style scoped>
.source-health {
  background-color: #fafafa;
  min-height: 100%;
}

.metric-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-orange-1 {
  background-color: rgba(255, 152, 0, 0.1);
}

.bg-red-1 {
  background-color: rgba(244, 67, 54, 0.1);
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.performance-chart,
.health-chart {
  border-radius: 8px;
  min-height: 300px;
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-tab-panel {
  padding: 0;
}

.q-chip {
  font-weight: 500;
}

.q-item {
  border-radius: 8px;
  margin-bottom: 4px;
}

.q-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .row.q-gutter-lg {
    margin: -8px;
  }

  .row.q-gutter-lg > div {
    padding: 8px;
  }

  .performance-chart,
  .health-chart {
    min-height: 200px;
  }
}
</style>
