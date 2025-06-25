<!-- pages/DataSourcePage.vue -->
<template>
  <q-page class="q-pa-md">
    <div class="row q-gutter-md">
      <!-- Page Header -->
      <div class="col-12">
        <q-card flat bordered class="bg-blue-1">
          <q-card-section>
            <div class="text-h5 text-primary">
              <q-icon name="storage" class="q-mr-sm" />
              Data Source Management
            </div>
            <div class="text-subtitle2 text-grey-7">
              Manage database connections and discover schemas for metadata mapping
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Main Content -->
      <div class="col-12">
        <DataSourceManager
          @connection-created="onConnectionCreated"
          @connection-updated="onConnectionUpdated"
          @connection-deleted="onConnectionDeleted"
          @schema-discovered="onSchemaDiscovered"
        />
      </div>
    </div>

    <!-- Global Loading -->
    <q-loading :showing="globalLoading">
      <q-spinner-gears size="50px" color="primary" />
    </q-loading>

    <!-- Global Notifications -->
    <q-notification-group>
      <!-- Notifications will be handled by Quasar's notify plugin -->
    </q-notification-group>
  </q-page>
</template>

<script>
import DataSourceManager from 'src/components/DataSourceManager.vue'

export default {
  name: 'DataSourcePage',
  components: {
    DataSourceManager
  },
  data() {
    return {
      globalLoading: false
    }
  },
  methods: {
    onConnectionCreated(connection) {
      this.$q.notify({
        type: 'positive',
        message: `Connection "${connection.name}" created successfully`,
        position: 'top-right',
        timeout: 3000,
        actions: [
          {
            label: 'Dismiss',
            color: 'white',
            handler: () => { /* dismiss */ }
          }
        ]
      })
    },

    onConnectionUpdated(connection) {
      this.$q.notify({
        type: 'positive',
        message: `Connection "${connection.name}" updated successfully`,
        position: 'top-right',
        timeout: 3000
      })
    },

    onConnectionDeleted(connectionName) {
      this.$q.notify({
        type: 'negative',
        message: `Connection "${connectionName}" deleted`,
        position: 'top-right',
        timeout: 3000
      })
    },

    onSchemaDiscovered(schemaInfo) {
      this.$q.notify({
        type: 'info',
        message: `Schema discovered: ${schemaInfo.totalTables} tables, ${schemaInfo.totalColumns} columns`,
        position: 'top-right',
        timeout: 4000
      })
    },

    // Method to show global loading
    showGlobalLoading() {
      this.globalLoading = true
    },

    // Method to hide global loading
    hideGlobalLoading() {
      this.globalLoading = false
    },

    // Global error handler
    handleGlobalError(error) {
      console.error('Global Error:', error)
      this.$q.notify({
        type: 'negative',
        message: error.message || 'An unexpected error occurred',
        position: 'top-right',
        timeout: 5000,
        actions: [
          {
            label: 'Dismiss',
            color: 'white',
            handler: () => { /* dismiss */ }
          }
        ]
      })
    }
  },
  mounted() {
    // Page initialization
    console.log('📄 DataSource Page mounted')
  },
  beforeUnmount() {
    // Cleanup if needed
    console.log('📄 DataSource Page unmounting')
  }
}
</script>

<style scoped>
.q-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.text-h5 {
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .q-pa-md {
    padding: 8px;
  }

  .q-gutter-md > * {
    margin: 8px 0;
  }
}

/* Animation for smooth transitions */
.q-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.q-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}
</style>
