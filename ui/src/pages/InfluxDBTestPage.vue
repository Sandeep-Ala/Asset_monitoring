<!-- pages/InfluxDBTestPage.vue - Debug Backend API -->
<template>
  <q-page class="q-pa-md">
    <div class="row q-gutter-md">
      <!-- Page Header -->
      <div class="col-12">
        <q-card flat bordered class="bg-orange-1">
          <q-card-section>
            <div class="text-h5 text-orange-8">
              <q-icon name="bug_report" class="q-mr-sm" />
              InfluxDB Backend API Test
            </div>
            <div class="text-subtitle2 text-orange-7">
              Debug tool to test InfluxDB schema discovery API calls
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Connection Test -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">1. Test InfluxDB Connection</div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-6">
                <q-input v-model="testConfig.url" label="InfluxDB URL" outlined />
              </div>
              <div class="col-6">
                <q-input v-model="testConfig.token" label="API Token" type="password" outlined />
              </div>
              <div class="col-6">
                <q-input v-model="testConfig.org" label="Organization" outlined />
              </div>
              <div class="col-6">
                <q-input v-model="testConfig.bucket" label="Bucket" outlined />
              </div>
            </div>
            <div class="row q-mt-md">
              <q-btn
                color="primary"
                label="Test Connection"
                icon="link"
                @click="testConnection"
                :loading="testing"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Connection Result -->
      <div v-if="connectionResult" class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Connection Test Result</div>
          </q-card-section>
          <q-card-section>
            <div class="row">
              <div class="col-12">
                <q-badge :color="connectionResult.success ? 'positive' : 'negative'" class="q-mb-md">
                  {{ connectionResult.success ? 'SUCCESS' : 'FAILED' }}
                </q-badge>
                <div class="text-body1">{{ connectionResult.message }}</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Schema Discovery Test -->
      <div v-if="connectionResult?.success" class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">2. Test Schema Discovery</div>
          </q-card-section>
          <q-card-section>
            <q-btn
              color="secondary"
              label="Discover Schema"
              icon="search"
              @click="discoverSchema"
              :loading="discovering"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- Schema Result -->
      <div v-if="schemaResult" class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Schema Discovery Result</div>
          </q-card-section>
          <q-card-section>
            <div class="row q-gutter-md">
              <div class="col-12">
                <q-badge :color="schemaResult.success ? 'positive' : 'negative'" class="q-mb-md">
                  {{ schemaResult.success ? 'SUCCESS' : 'FAILED' }}
                </q-badge>
                <div class="text-body1 q-mb-md">{{ schemaResult.message }}</div>
              </div>

              <!-- Database Info -->
              <div v-if="schemaResult.success && schemaResult.data?.database_info" class="col-12">
                <q-card flat bordered class="bg-blue-1">
                  <q-card-section>
                    <div class="text-subtitle1">Database Info</div>
                    <pre class="text-caption">{{ JSON.stringify(schemaResult.data.database_info, null, 2) }}</pre>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Measurements -->
              <div v-if="schemaResult.success && schemaResult.data?.measurements" class="col-12">
                <q-card flat bordered class="bg-green-1">
                  <q-card-section>
                    <div class="text-subtitle1">
                      Measurements Found ({{ schemaResult.data.measurements.length }})
                    </div>
                    <div class="q-mt-md">
                      <q-expansion-item
                        v-for="measurement in schemaResult.data.measurements"
                        :key="measurement.name"
                        :label="measurement.name"
                        :caption="`${measurement.field_count || 0} fields, ${measurement.tag_count || 0} tags`"
                        icon="timeline"
                      >
                        <div class="q-pa-md">
                          <pre class="text-caption">{{ JSON.stringify(measurement, null, 2) }}</pre>

                          <!-- Test Field Discovery -->
                          <q-btn
                            size="sm"
                            color="accent"
                            label="Get Fields"
                            icon="list"
                            @click="getFields(measurement.name)"
                            :loading="loadingFields[measurement.name]"
                            class="q-mt-md"
                          />
                        </div>
                      </q-expansion-item>
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Raw Response -->
              <div v-if="schemaResult" class="col-12">
                <q-card flat bordered class="bg-grey-1">
                  <q-card-section>
                    <div class="text-subtitle1">Raw API Response</div>
                    <pre class="text-caption">{{ JSON.stringify(schemaResult, null, 2) }}</pre>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Field Discovery Results -->
      <div v-if="Object.keys(fieldResults).length > 0" class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Field Discovery Results</div>
          </q-card-section>
          <q-card-section>
            <div v-for="(result, measurementName) in fieldResults" :key="measurementName" class="q-mb-md">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1">{{ measurementName }}</div>
                  <q-badge :color="result.success ? 'positive' : 'negative'" class="q-mb-md">
                    {{ result.success ? 'SUCCESS' : 'FAILED' }}
                  </q-badge>
                  <div class="text-body2 q-mb-md">{{ result.message }}</div>

                  <div v-if="result.success && result.data">
                    <div class="text-subtitle2 q-mb-sm">Fields & Tags ({{ result.data.length }})</div>
                    <div class="row q-gutter-xs">
                      <q-chip
                        v-for="field in result.data"
                        :key="field.name"
                        :color="field.category === 'field' ? 'green' : field.category === 'tag' ? 'blue' : 'grey'"
                        text-color="white"
                        size="sm"
                      >
                        <q-icon
                          :name="field.category === 'field' ? 'functions' : field.category === 'tag' ? 'local_offer' : 'schedule'"
                          size="xs"
                          class="q-mr-xs"
                        />
                        {{ field.name }} ({{ field.category }})
                      </q-chip>
                    </div>
                  </div>

                  <div class="q-mt-md">
                    <q-expansion-item label="Raw Response" icon="code">
                      <div class="q-pa-md">
                        <pre class="text-caption">{{ JSON.stringify(result, null, 2) }}</pre>
                      </div>
                    </q-expansion-item>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- API Endpoints -->
      <div class="col-12">
        <q-card flat bordered class="bg-purple-1">
          <q-card-section>
            <div class="text-h6">Backend API Endpoints Being Tested</div>
            <div class="text-body2 q-mt-md">
              <strong>Connection Test:</strong> POST /datasources/connections/test<br>
              <strong>Schema Discovery:</strong> GET /datasources/connections/{id}/schema<br>
              <strong>Field Discovery:</strong> GET /datasources/connections/{id}/tables/{measurement}/columns
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { dataSourceAPI } from 'src/services/Api'

export default {
  name: 'InfluxDBTestPage',
  setup() {
    // Test configuration
    const testConfig = ref({
      url: 'http://localhost:8086',
      token: '',
      org: 'primary',
      bucket: 'asset_monitoring'
    })

    // Loading states
    const testing = ref(false)
    const discovering = ref(false)
    const loadingFields = ref({})

    // Results
    const connectionResult = ref(null)
    const schemaResult = ref(null)
    const fieldResults = ref({})
    const connectionId = ref(null)

    // Methods
    const testConnection = async () => {
      testing.value = true
      connectionResult.value = null

      try {
        console.log('🔍 Testing InfluxDB connection with config:', testConfig.value)

        // First create a temporary connection
        const createResponse = await dataSourceAPI.createConnection({
          name: 'Test InfluxDB Connection',
          db_type: 'influxdb',
          description: 'Temporary test connection'
        })

        if (!createResponse.data.id) {
          throw new Error('Failed to create test connection')
        }

        connectionId.value = createResponse.data.id
        console.log('✅ Test connection created:', connectionId.value)

        // Test the connection
        const testResponse = await dataSourceAPI.testConnection({
          connection_id: connectionId.value,
          config: testConfig.value
        })

        connectionResult.value = testResponse.data
        console.log('📊 Connection test result:', connectionResult.value)

      } catch (error) {
        console.error('❌ Connection test failed:', error)
        connectionResult.value = {
          success: false,
          message: error.response?.data?.detail || error.message
        }
      } finally {
        testing.value = false
      }
    }

    const discoverSchema = async () => {
      if (!connectionId.value) {
        return
      }

      discovering.value = true
      schemaResult.value = null

      try {
        console.log('🔍 Discovering schema for connection:', connectionId.value)

        const response = await dataSourceAPI.getCompleteSchema(connectionId.value, true)
        schemaResult.value = response.data
        console.log('📊 Schema discovery result:', schemaResult.value)

      } catch (error) {
        console.error('❌ Schema discovery failed:', error)
        schemaResult.value = {
          success: false,
          message: error.response?.data?.detail || error.message,
          data: null
        }
      } finally {
        discovering.value = false
      }
    }

    const getFields = async (measurementName) => {
      if (!connectionId.value) {
        return
      }

      loadingFields.value[measurementName] = true

      try {
        console.log('🔍 Getting fields for measurement:', measurementName)

        const response = await dataSourceAPI.getTableColumns(connectionId.value, measurementName)
        fieldResults.value[measurementName] = response.data
        console.log('📊 Field discovery result for', measurementName, ':', response.data)

      } catch (error) {
        console.error('❌ Field discovery failed for', measurementName, ':', error)
        fieldResults.value[measurementName] = {
          success: false,
          message: error.response?.data?.detail || error.message,
          data: null
        }
      } finally {
        loadingFields.value[measurementName] = false
      }
    }

    return {
      // Reactive data
      testConfig,
      testing,
      discovering,
      loadingFields,
      connectionResult,
      schemaResult,
      fieldResults,
      connectionId,

      // Methods
      testConnection,
      discoverSchema,
      getFields
    }
  }
}
</script>

<style scoped>
pre {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
}

.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 8px;
}
</style>
