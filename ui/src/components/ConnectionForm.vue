<!-- components/ConnectionForm.vue - Fixed Form Submission & API Integration -->
<template>
  <q-form @submit="handleSubmit" @reset="resetForm" class="q-gutter-md">
    <!-- Connection Basic Info -->
    <q-input
      v-model="form.name"
      label="Connection Name *"
      outlined
      :rules="[val => !!val || 'Name is required']"
      lazy-rules
      :disable="saveLoading"
    />

    <q-input
      v-model="form.description"
      label="Description"
      outlined
      type="textarea"
      rows="2"
      :disable="saveLoading"
    />

    <!-- Database Type Selection -->
    <q-select
      v-model="form.db_type"
      :options="dbTypeOptions"
      option-label="label"
      option-value="value"
      label="Database Type *"
      outlined
      map-options
      emit-value
      :rules="[val => !!val || 'Database type is required']"
      @update:model-value="onDbTypeChange"
      :disable="saveLoading"
    >
      <template v-slot:option="scope">
        <q-item v-bind="scope.itemProps">
          <q-item-section avatar>
            <q-icon :name="getDbTypeIcon(scope.opt.value)" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ scope.opt.label }}</q-item-label>
            <q-item-label caption>{{ scope.opt.description }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>

    <!-- Dynamic Configuration Fields -->
    <div v-if="form.db_type && selectedDbType" class="q-mt-md">
      <q-separator class="q-mb-md" />
      <div class="text-subtitle2 text-primary q-mb-md">
        <q-icon :name="getDbTypeIcon(form.db_type)" class="q-mr-sm" />
        {{ selectedDbType.name }} Configuration
      </div>

      <!-- Dynamic fields based on database type -->
      <div v-for="field in selectedDbType.fields" :key="field.key" class="q-mb-md">
        <q-input
          v-if="field.type === 'text'"
          v-model="form.config[field.key]"
          :label="field.label + (field.required ? ' *' : '')"
          :placeholder="field.placeholder"
          outlined
          :rules="field.required ? [val => !!val || `${field.label} is required`] : []"
          lazy-rules
          :disable="saveLoading"
        />

        <q-input
          v-else-if="field.type === 'password'"
          v-model="form.config[field.key]"
          :label="field.label + (field.required ? ' *' : '')"
          :placeholder="field.placeholder"
          type="password"
          outlined
          :rules="field.required ? [val => !!val || `${field.label} is required`] : []"
          lazy-rules
          :disable="saveLoading"
        />

        <q-input
          v-else-if="field.type === 'number'"
          v-model.number="form.config[field.key]"
          :label="field.label + (field.required ? ' *' : '')"
          :placeholder="field.placeholder"
          type="number"
          outlined
          :rules="field.required ? [val => !!val || `${field.label} is required`] : []"
          lazy-rules
          :disable="saveLoading"
        />
      </div>
    </div>

    <!-- Test Connection -->
    <div v-if="form.db_type && hasValidConfig" class="q-mt-md">
      <q-btn
        @click="testConnection"
        color="info"
        icon="wifi_protected_setup"
        label="Test Connection"
        :loading="testLoading"
        :disable="!canTest || saveLoading"
        class="full-width"
      />

      <!-- Test Result -->
      <div v-if="testResult" class="q-mt-sm">
        <q-banner
          :class="testResult.success ? 'bg-green-1 text-green-8' : 'bg-red-1 text-red-8'"
          dense
        >
          <template v-slot:avatar>
            <q-icon :name="testResult.success ? 'check_circle' : 'error'" />
          </template>
          {{ testResult.message }}
        </q-banner>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="row q-gutter-sm q-mt-md">
      <q-btn
        type="submit"
        color="primary"
        icon="save"
        :label="editMode ? 'Update Connection' : 'Create Connection'"
        :loading="saveLoading"
        :disable="!canSave"
        class="col"
      />

      <!-- Show why save is disabled for better UX -->
      <div v-if="!editMode && !testResult?.success && form.name && form.db_type" class="col-12">
        <q-banner class="bg-orange-1 text-orange-8" dense>
          <template v-slot:avatar>
            <q-icon name="warning" />
          </template>
          Please test the connection successfully before creating
        </q-banner>
      </div>

      <!-- Edit Mode Cancel Button -->
      <q-btn
        v-if="editMode"
        type="button"
        color="grey"
        icon="cancel"
        label="Cancel"
        @click="handleCancel"
        :disable="saveLoading"
        class="col"
      />

      <!-- Reset Button -->
      <q-btn
        type="reset"
        color="grey"
        icon="refresh"
        label="Reset"
        :disable="saveLoading"
        class="col"
      />
    </div>

    <!-- Debug Information (Remove in production) -->
    <div v-if="$q.dev" class="q-mt-md">
      <q-expansion-item
        icon="bug_report"
        label="Debug Info (Dev Only)"
        dense
      >
        <q-card>
          <q-card-section class="text-caption">
            <div><strong>Edit Mode:</strong> {{ editMode }}</div>
            <div><strong>Has Valid Config:</strong> {{ hasValidConfig }}</div>
            <div><strong>Can Test:</strong> {{ canTest }}</div>
            <div><strong>Can Save:</strong> {{ canSave }}</div>
            <div><strong>Test Result:</strong> {{ testResult?.success || 'Not tested' }}</div>
            <div><strong>Form Data:</strong></div>
            <pre>{{ JSON.stringify(form, null, 2) }}</pre>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </div>
  </q-form>
</template>

<script>
import { dataSourceAPI } from 'src/services/Api'

export default {
  name: 'ConnectionForm',
  props: {
    editMode: {
      type: Boolean,
      default: false
    },
    connectionData: {
      type: Object,
      default: null
    }
  },
  emits: ['save', 'cancel', 'test'],
  data() {
    return {
      form: {
        name: '',
        description: '',
        db_type: '',
        config: {}
      },
      dbTypes: {},
      testResult: null,
      testLoading: false,
      saveLoading: false,
      dbTypesLoading: false
    }
  },
  computed: {
    dbTypeOptions() {
      return Object.entries(this.dbTypes).map(([key, value]) => ({
        label: value.name,
        value: key,
        description: `Configure ${value.name} connection`
      }))
    },

    selectedDbType() {
      return this.dbTypes[this.form.db_type] || null
    },

    hasValidConfig() {
      if (!this.selectedDbType) return false

      const requiredFields = this.selectedDbType.fields.filter(f => f.required)
      return requiredFields.every(field => {
        const value = this.form.config[field.key]
        return value !== null && value !== undefined && value !== ''
      })
    },

    canTest() {
      return this.hasValidConfig && !this.testLoading && !this.saveLoading
    },

    canSave() {
      const basicValidation = this.form.name && this.form.db_type && !this.saveLoading

      if (this.editMode) {
        // In edit mode, allow save without re-testing if connection was previously active
        return basicValidation && this.hasValidConfig
      } else {
        // In create mode, require successful test
        return basicValidation && this.testResult && this.testResult.success
      }
    }
  },
  async mounted() {
    console.log('🔧 ConnectionForm mounted, editMode:', this.editMode)
    await this.loadDbTypes()
    if (this.editMode && this.connectionData) {
      await this.loadConnectionData()
    }
  },
  watch: {
    connectionData: {
      handler() {
        if (this.editMode && this.connectionData) {
          console.log('🔧 ConnectionData changed, reloading...')
          this.loadConnectionData()
        }
      },
      deep: true
    }
  },
  methods: {
    async loadDbTypes() {
      this.dbTypesLoading = true
      try {
        console.log('🔧 Loading database types...')
        const response = await dataSourceAPI.getSupportedDbTypes()
        this.dbTypes = response.data
        console.log('✅ Database types loaded:', this.dbTypes)
      } catch (error) {
        console.error('❌ Failed to load database types:', error)
        this.$q.notify({
          type: 'negative',
          message: 'Failed to load database types: ' + error.message
        })
      } finally {
        this.dbTypesLoading = false
      }
    },

    async loadConnectionData() {
      if (!this.connectionData) return

      console.log('🔧 Loading connection data for edit:', this.connectionData)

      // Load basic connection info
      this.form.name = this.connectionData.name
      this.form.description = this.connectionData.description || ''
      this.form.db_type = this.connectionData.db_type

      // Load connection configuration
      try {
        const response = await dataSourceAPI.getConnectionConfigsDict(this.connectionData.id)
        this.form.config = response.data || {}
        console.log('✅ Connection config loaded:', this.form.config)
      } catch (error) {
        console.error('❌ Failed to load connection config:', error)
        this.form.config = {}
      }

      // Clear test result when loading existing connection
      this.testResult = null
    },

    onDbTypeChange() {
      console.log('🔧 Database type changed to:', this.form.db_type)

      // Reset config when database type changes
      this.form.config = {}
      this.testResult = null

      // Initialize config with default values
      if (this.selectedDbType) {
        this.selectedDbType.fields.forEach(field => {
          if (field.type === 'number') {
            this.form.config[field.key] = null
          } else {
            this.form.config[field.key] = ''
          }
        })
        console.log('🔧 Initialized config for', this.selectedDbType.name, ':', this.form.config)
      }
    },

    async testConnection() {
      console.log('🧪 Testing connection...')
      this.testLoading = true
      this.testResult = null

      try {
        const response = await dataSourceAPI.testConnectionOnly(this.form.db_type, this.form.config)
        this.testResult = response.data

        console.log('🧪 Test result:', this.testResult)

        // Emit test event to parent
        this.$emit('test', {
          success: response.data.success,
          message: response.data.message
        })

        // Show notification
        this.$q.notify({
          type: this.testResult.success ? 'positive' : 'negative',
          message: this.testResult.message,
          position: 'top-right',
          timeout: 3000
        })

      } catch (error) {
        console.error('❌ Connection test failed:', error)

        this.testResult = {
          success: false,
          message: 'Connection test failed: ' + (error.response?.data?.detail || error.message)
        }

        this.$q.notify({
          type: 'negative',
          message: this.testResult.message,
          position: 'top-right',
          timeout: 5000
        })
      } finally {
        this.testLoading = false
      }
    },

    // 🔧 FIXED: Proper form submission handling
    async handleSubmit() {
      console.log('💾 Form submitted for', this.editMode ? 'update' : 'create')
      this.saveLoading = true

      try {
        // Prepare connection data
        const connectionData = {
          name: this.form.name.trim(),
          description: this.form.description?.trim() || '',
          db_type: this.form.db_type
        }

        // Prepare config data (only include non-empty values)
        const configData = {}
        Object.keys(this.form.config).forEach(key => {
          const value = this.form.config[key]
          if (value !== '' && value !== null && value !== undefined) {
            configData[key] = value
          }
        })

        // Combine connection and config data
        const completeData = {
          ...connectionData,
          config: configData
        }

        console.log('💾 Emitting save event with data:', completeData)

        // Emit save event to parent (DataSourceManager will handle the API calls)
        this.$emit('save', completeData)

        // Don't show success message here - let parent handle it after API call

      } catch (error) {
        console.error('❌ Error preparing form data:', error)

        this.$q.notify({
          type: 'negative',
          message: 'Error preparing data: ' + error.message,
          position: 'top-right'
        })

        this.saveLoading = false
      }
      // Note: saveLoading will be reset by parent after API call completes
    },

    handleCancel() {
      console.log('❌ Form cancelled')
      this.$emit('cancel')
    },

    resetForm() {
      console.log('🔄 Resetting form')

      this.form = {
        name: '',
        description: '',
        db_type: '',
        config: {}
      }
      this.testResult = null
      this.saveLoading = false

      // If in edit mode and we have connection data, reload it
      if (this.editMode && this.connectionData) {
        this.loadConnectionData()
      }
    },

    // Public method that parent can call to reset loading state
    resetLoadingState() {
      this.saveLoading = false
    },

    getDbTypeIcon(dbType) {
      const icons = {
        sqlite3: 'storage',
        influxdb: 'timeline',
        parquet: 'folder'
      }
      return icons[dbType] || 'database'
    }
  }
}
</script>

<style scoped>
.q-form {
  max-width: 100%;
}

.q-banner {
  border-radius: 4px;
}

/* Responsive form adjustments */
@media (max-width: 600px) {
  .row.q-gutter-sm .col {
    width: 100%;
    margin-bottom: 8px;
  }
}

/* Loading state styling */
.q-btn:disabled {
  opacity: 0.6;
}

/* Test result animation */
.q-banner {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Form field styling */
.q-input:disabled {
  opacity: 0.7;
}

.q-select:disabled {
  opacity: 0.7;
}

/* Debug section styling */
.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>
