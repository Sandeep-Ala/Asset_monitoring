<!-- ui/src/components/SourceConnection.vue -->
<template>
  <div class="source-connection q-pa-lg">
    <!-- Connection Status Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h6">Connection Management</div>
        <div class="text-subtitle2 text-grey-6">
          Manage and monitor your data source connection
        </div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Test Connection"
          icon="wifi_find"
          color="primary"
          @click="testConnection"
          :loading="testing"
        />
        <q-btn
          label="Edit Configuration"
          icon="edit"
          color="secondary"
          outline
          @click="editMode = !editMode"
        />
      </div>
    </div>

    <!-- Connection Status Card -->
    <div class="q-mb-lg">
      <q-card flat bordered :class="connectionStatusClass">
        <q-card-section>
          <div class="row items-center">
            <q-icon
              :name="connectionStatusIcon"
              :color="connectionStatusColor"
              size="2rem"
              class="q-mr-md"
            />
            <div class="col">
              <div class="text-h6">{{ connectionStatusTitle }}</div>
              <div class="text-body2 text-grey-7">{{ connectionStatusMessage }}</div>
            </div>
            <div class="col-auto">
              <q-btn
                icon="refresh"
                flat
                round
                @click="refreshConnectionStatus"
                :loading="refreshing"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Connection Details -->
        <q-card-section v-if="lastConnectionTest" class="q-pt-none">
          <q-separator class="q-mb-md" />
          <div class="row q-gutter-md text-caption">
            <div>
              <strong>Last Test:</strong> {{ formatDateTime(lastConnectionTest.timestamp) }}
            </div>
            <div>
              <strong>Response Time:</strong> {{ lastConnectionTest.responseTime || 'N/A' }}
            </div>
            <div>
              <strong>Status:</strong> {{ lastConnectionTest.status || 'Unknown' }}
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Configuration Section -->
    <div class="row q-gutter-lg">
      <!-- Configuration Display/Edit -->
      <div class="col-12 col-lg-8">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="row items-center justify-between">
              <div class="text-h6">Connection Configuration</div>
              <q-toggle
                v-model="editMode"
                label="Edit Mode"
                color="primary"
              />
            </div>
          </q-card-section>

          <q-card-section>
            <!-- InfluxDB Configuration -->
            <div v-if="source.source_type === 'influxdb'">
              <InfluxDBConnectionConfig
                :config="connectionConfig"
                :edit-mode="editMode"
                @update="updateConfig"
                @test="testConnection"
                :testing="testing"
              />
            </div>

            <!-- Parquet Configuration -->
            <div v-else-if="source.source_type === 'parquet'">
              <ParquetConnectionConfig
                :config="connectionConfig"
                :edit-mode="editMode"
                @update="updateConfig"
                @test="testConnection"
                :testing="testing"
              />
            </div>

            <!-- Actions -->
            <div v-if="editMode" class="row q-gutter-sm q-mt-lg">
              <q-btn
                label="Save Changes"
                icon="save"
                color="positive"
                @click="saveConfiguration"
                :loading="saving"
                :disable="!hasConfigChanges"
              />
              <q-btn
                label="Reset"
                icon="refresh"
                color="warning"
                outline
                @click="resetConfiguration"
              />
              <q-btn
                label="Cancel"
                flat
                @click="cancelEdit"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Connection Monitoring -->
      <div class="col-12 col-lg-4">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">Connection Monitoring</div>
            <div class="text-caption">Real-time connection health</div>
          </q-card-section>

          <q-card-section>
            <!-- Health Metrics -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">Health Metrics</div>

              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="speed" color="blue" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Response Time</q-item-label>
                    <q-item-label caption>{{ healthMetrics.responseTime || 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="check_circle" color="green" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Uptime</q-item-label>
                    <q-item-label caption>{{ healthMetrics.uptime || 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="error" color="red" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Last Error</q-item-label>
                    <q-item-label caption>{{ healthMetrics.lastError || 'None' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <!-- Auto-monitoring Toggle -->
            <q-separator class="q-my-md" />

            <div class="text-subtitle2 q-mb-sm">Auto Monitoring</div>
            <q-toggle
              v-model="autoMonitoring"
              label="Enable automatic health checks"
              color="positive"
              @update:model-value="toggleAutoMonitoring"
            />
            <div class="text-caption text-grey-6 q-mt-xs">
              {{ autoMonitoring ? 'Checking every 5 minutes' : 'Manual checks only' }}
            </div>

            <!-- Manual Actions -->
            <q-separator class="q-my-md" />

            <div class="text-subtitle2 q-mb-sm">Manual Actions</div>
            <div class="column q-gutter-sm">
              <q-btn
                label="Ping Connection"
                icon="network_ping"
                color="blue"
                outline
                size="sm"
                @click="pingConnection"
                :loading="pinging"
              />
              <q-btn
                label="Check Permissions"
                icon="security"
                color="orange"
                outline
                size="sm"
                @click="checkPermissions"
                :loading="checkingPermissions"
              />
              <q-btn
                label="Clear Cache"
                icon="clear_all"
                color="grey"
                outline
                size="sm"
                @click="clearConnectionCache"
              />
            </div>
          </q-card-section>
        </q-card>

        <!-- Connection History -->
        <q-card flat bordered class="q-mt-md">
          <q-card-section class="bg-orange-1">
            <div class="text-h6">Connection History</div>
            <div class="text-caption">Recent connection tests</div>
          </q-card-section>

          <q-card-section>
            <q-list v-if="connectionHistory.length > 0" separator>
              <q-item
                v-for="(test, index) in connectionHistory.slice(0, 5)"
                :key="index"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="test.success ? 'check_circle' : 'error'"
                    :color="test.success ? 'positive' : 'negative'"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ test.success ? 'Success' : 'Failed' }}</q-item-label>
                  <q-item-label caption>{{ formatDateTime(test.timestamp) }}</q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip
                    :color="test.success ? 'positive' : 'negative'"
                    text-color="white"
                    size="sm"
                  >
                    {{ test.responseTime || 'N/A' }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-else class="text-center q-pa-md text-grey-6">
              <q-icon name="history" size="2rem" class="q-mb-sm" />
              <div>No connection history</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Advanced Settings -->
    <div class="q-mt-lg">
      <q-expansion-item
        icon="settings"
        label="Advanced Connection Settings"
        dense
      >
        <q-card flat bordered>
          <q-card-section>
            <div class="row q-gutter-md">
              <!-- Timeout Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.connectionTimeout"
                  label="Connection Timeout (seconds)"
                  type="number"
                  outlined
                  dense
                  :min="5"
                  :max="300"
                />
              </div>

              <!-- Retry Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.retryAttempts"
                  label="Retry Attempts"
                  type="number"
                  outlined
                  dense
                  :min="0"
                  :max="10"
                />
              </div>

              <!-- Pool Settings -->
              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="advancedSettings.maxConnections"
                  label="Max Connections"
                  type="number"
                  outlined
                  dense
                  :min="1"
                  :max="100"
                />
              </div>

              <!-- SSL Verification -->
              <div class="col-12">
                <q-toggle
                  v-model="advancedSettings.sslVerification"
                  label="SSL Certificate Verification"
                  color="primary"
                />
                <div class="text-caption text-grey-6">
                  Disable for self-signed certificates
                </div>
              </div>

              <!-- Keep Alive -->
              <div class="col-12">
                <q-toggle
                  v-model="advancedSettings.keepAlive"
                  label="Keep Connection Alive"
                  color="primary"
                />
                <div class="text-caption text-grey-6">
                  Maintain persistent connection
                </div>
              </div>
            </div>

            <div class="row q-gutter-sm q-mt-md">
              <q-btn
                label="Apply Settings"
                color="primary"
                @click="applyAdvancedSettings"
              />
              <q-btn
                label="Reset to Defaults"
                outline
                @click="resetAdvancedSettings"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'

// Import configuration components
import InfluxDBConnectionConfig from 'src/components/InfluxDBConfig.vue'
import ParquetConnectionConfig from 'src/components/ParquetConfig.vue'

// Props
const props = defineProps({
  source: Object
})

// Emits
const emit = defineEmits(['test-connection', 'update-config'])

// Reactive data
const $q = useQuasar()
const editMode = ref(false)
const testing = ref(false)
const saving = ref(false)
