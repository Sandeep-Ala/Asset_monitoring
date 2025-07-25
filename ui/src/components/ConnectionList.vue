<!-- components/ConnectionList.vue - Fixed Event Bindings & Table Display -->
<template>
  <div class="connection-list">
    <!-- Loading State -->
    <div v-if="loading" class="q-pa-md text-center">
      <q-spinner-dots size="40px" color="primary" />
      <div class="q-mt-sm">Loading connections...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!connections.length" class="q-pa-xl text-center">
      <q-icon name="storage" size="64px" color="grey-4" />
      <div class="text-h6 text-grey-6 q-mt-md">No connections found</div>
      <div class="text-body2 text-grey-7">Create your first database connection to get started</div>
    </div>

    <!-- Connections Table -->
    <q-table
      v-else
      :rows="connections"
      :columns="columns"
      row-key="id"
      flat
      :pagination="{ rowsPerPage: 10 }"
      :loading="loading"
      no-data-label="No connections available"
      loading-label="Loading connections..."
    >
      <!-- Connection Name -->
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <div class="row items-center q-gutter-sm">
            <q-icon :name="getDbTypeIcon(props.row.db_type)" :color="getDbTypeColor(props.row.db_type)" />
            <div>
              <div class="text-weight-medium">{{ props.value }}</div>
              <div class="text-caption text-grey-7" v-if="props.row.description">
                {{ props.row.description }}
              </div>
            </div>
          </div>
        </q-td>
      </template>

      <!-- Database Type -->
      <template v-slot:body-cell-db_type="props">
        <q-td :props="props">
          <q-chip
            :color="getDbTypeColor(props.value)"
            text-color="white"
            size="sm"
          >
            {{ props.value.toUpperCase() }}
          </q-chip>
        </q-td>
      </template>

      <!-- Status -->
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-chip
            :color="getStatusColor(props.value)"
            text-color="white"
            size="sm"
            :icon="getStatusIcon(props.value)"
          >
            {{ props.value.toUpperCase() }}
          </q-chip>
        </q-td>
      </template>

      <!-- Created Date -->
      <template v-slot:body-cell-created_at="props">
        <q-td :props="props">
          <div class="text-body2">{{ formatDate(props.value) }}</div>
          <div class="text-caption text-grey-6">{{ formatTime(props.value) }}</div>
        </q-td>
      </template>

      <!-- Actions -->
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-xs">
            <!-- Test Connection -->
            <q-btn
              round
              flat
              size="sm"
              icon="wifi_protected_setup"
              color="info"
              @click="handleTestConnection(props.row)"
              :disable="!canTest(props.row)"
            >
              <q-tooltip>Test Connection</q-tooltip>
            </q-btn>

            <!-- Discover Schema -->
            <q-btn
              round
              flat
              size="sm"
              icon="schema"
              color="purple"
              @click="handleDiscoverSchema(props.row)"
              :disable="props.row.status !== 'active'"
            >
              <q-tooltip>Discover Schema</q-tooltip>
            </q-btn>

            <!-- Edit -->
            <q-btn
              round
              flat
              size="sm"
              icon="edit"
              color="primary"
              @click="handleEditConnection(props.row)"
            >
              <q-tooltip>Edit Connection</q-tooltip>
            </q-btn>

            <!-- Delete -->
            <q-btn
              round
              flat
              size="sm"
              icon="delete"
              color="negative"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>Delete Connection</q-tooltip>
            </q-btn>

            <!-- More Actions Menu -->
            <q-btn round flat size="sm" icon="more_vert">
              <q-menu>
                <q-list style="min-width: 150px">
                  <q-item clickable v-close-popup @click="viewDetails(props.row)">
                    <q-item-section avatar>
                      <q-icon name="info" />
                    </q-item-section>
                    <q-item-section>View Details</q-item-section>
                  </q-item>

                  <q-item
                    clickable
                    v-close-popup
                    @click="duplicateConnection(props.row)"
                  >
                    <q-item-section avatar>
                      <q-icon name="content_copy" />
                    </q-item-section>
                    <q-item-section>Duplicate</q-item-section>
                  </q-item>

                  <q-separator />

                  <q-item
                    clickable
                    v-close-popup
                    @click="exportConnection(props.row)"
                    :disable="props.row.status !== 'active'"
                  >
                    <q-item-section avatar>
                      <q-icon name="download" />
                    </q-item-section>
                    <q-item-section>Export Config</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
          </div>
        </q-td>
      </template>
    </q-table>

    <!-- Connection Details Dialog -->
    <q-dialog v-model="showDetailsDialog" persistent>
      <q-card style="min-width: 400px; max-width: 600px;">
        <q-card-section>
          <div class="text-h6">Connection Details</div>
        </q-card-section>

        <q-card-section v-if="selectedConnection">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="label" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Name</q-item-label>
                <q-item-label caption>{{ selectedConnection.name }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="storage" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Database Type</q-item-label>
                <q-item-label caption>{{ selectedConnection.db_type }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="info" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Status</q-item-label>
                <q-item-label caption>{{ selectedConnection.status }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="selectedConnection.description">
              <q-item-section avatar>
                <q-icon name="description" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Description</q-item-label>
                <q-item-label caption>{{ selectedConnection.description }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="schedule" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Created</q-item-label>
                <q-item-label caption>{{ formatDateTime(selectedConnection.created_at) }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="update" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Last Updated</q-item-label>
                <q-item-label caption>{{ formatDateTime(selectedConnection.updated_at) }}</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Connection ID for debugging -->
            <q-item v-if="$q.dev">
              <q-item-section avatar>
                <q-icon name="fingerprint" />
              </q-item-section>
              <q-item-section>
                <q-item-label>ID (Dev Only)</q-item-label>
                <q-item-label caption>{{ selectedConnection.id }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { date } from 'quasar'

export default {
  name: 'ConnectionList',
  props: {
    connections: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  // 🔧 FIXED: Updated emit events to match DataSourceManager expectations
  emits: ['edit', 'delete', 'test', 'discover-schema'],
  data() {
    return {
      showDetailsDialog: false,
      selectedConnection: null,
      columns: [
        {
          name: 'name',
          label: 'Connection',
          field: 'name',
          align: 'left',
          sortable: true,
          style: 'width: 25%'
        },
        {
          name: 'db_type',
          label: 'Type',
          field: 'db_type',
          align: 'center',
          sortable: true,
          style: 'width: 15%'
        },
        {
          name: 'status',
          label: 'Status',
          field: 'status',
          align: 'center',
          sortable: true,
          style: 'width: 15%'
        },
        {
          name: 'created_at',
          label: 'Created',
          field: 'created_at',
          align: 'center',
          sortable: true,
          style: 'width: 20%'
        },
        {
          name: 'actions',
          label: 'Actions',
          align: 'center',
          style: 'width: 25%'
        }
      ]
    }
  },
  methods: {
    // 🔧 FIXED: Event handlers with proper emission
    handleEditConnection(connection) {
      console.log('📝 Edit connection clicked:', connection.name)
      this.$emit('edit', connection)
    },

    handleTestConnection(connection) {
      console.log('🧪 Test connection clicked:', connection.name)
      this.$emit('test', connection)
    },

    handleDiscoverSchema(connection) {
      console.log('🔍 Discover schema clicked:', connection.name)
      this.$emit('discover-schema', connection)
    },

    confirmDelete(connection) {
      console.log('🗑️ Delete connection clicked:', connection.name)

      this.$q.dialog({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete connection "${connection.name}"? This action cannot be undone.`,
        cancel: true,
        persistent: true,
        color: 'negative'
      }).onOk(() => {
        console.log('🗑️ Deletion confirmed for:', connection.name)
        this.$emit('delete', connection)
      })
    },

    // Helper methods
    getDbTypeIcon(dbType) {
      const icons = {
        sqlite3: 'storage',
        influxdb: 'timeline',
        parquet: 'folder'
      }
      return icons[dbType] || 'database'
    },

    getDbTypeColor(dbType) {
      const colors = {
        sqlite3: 'blue',
        influxdb: 'orange',
        parquet: 'green'
      }
      return colors[dbType] || 'grey'
    },

    getStatusColor(status) {
      const colors = {
        active: 'green',
        inactive: 'grey',
        error: 'red',
        testing: 'orange',
        unknown: 'grey-5'
      }
      return colors[status] || 'grey'
    },

    getStatusIcon(status) {
      const icons = {
        active: 'check_circle',
        inactive: 'radio_button_unchecked',
        error: 'error',
        testing: 'sync',
        unknown: 'help'
      }
      return icons[status] || 'help'
    },

    canTest(connection) {
      // Allow testing for all connections except those currently being tested
      return connection.status !== 'testing'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return date.formatDate(dateString, 'MMM DD, YYYY')
    },

    formatTime(dateString) {
      if (!dateString) return ''
      return date.formatDate(dateString, 'HH:mm:ss')
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      return date.formatDate(dateString, 'MMM DD, YYYY HH:mm:ss')
    },

    viewDetails(connection) {
      console.log('ℹ️ View details clicked:', connection.name)
      this.selectedConnection = connection
      this.showDetailsDialog = true
    },

    duplicateConnection(connection) {
      console.log('📋 Duplicate connection clicked:', connection.name)
      this.$q.notify({
        type: 'info',
        message: 'Duplicate functionality will be implemented in the next phase',
        position: 'top-right'
      })
    },

    exportConnection(connection) {
      console.log('📤 Export connection clicked:', connection.name)
      this.$q.notify({
        type: 'info',
        message: 'Export functionality will be implemented in the next phase',
        position: 'top-right'
      })
    }
  }
}
</script>

<style scoped>
.connection-list {
  background: transparent;
}

/* Custom table styling */
:deep(.q-table) {
  background: transparent;
}

:deep(.q-table thead th) {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
}

:deep(.q-table tbody tr) {
  transition: background-color 0.2s ease;
}

:deep(.q-table tbody tr:hover) {
  background: #f0f8ff;
}

:deep(.q-table tbody tr:nth-child(even)) {
  background: #fafafa;
}

:deep(.q-table tbody tr:nth-child(even):hover) {
  background: #f0f8ff;
}

/* Action buttons styling */
.q-btn {
  transition: all 0.2s ease;
}

.q-btn:hover {
  transform: scale(1.1);
}

/* Chip styling */
.q-chip {
  font-weight: 600;
}

/* Empty state styling */
.text-center {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* Loading state styling */
.q-spinner-dots {
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  :deep(.q-table th),
  :deep(.q-table td) {
    padding: 8px 4px;
    font-size: 0.875rem;
  }

  .q-btn {
    min-width: 32px;
    padding: 6px;
  }

  .row.q-gutter-xs {
    gap: 2px;
  }

  /* Hide some columns on mobile */
  :deep(.q-table th:nth-child(4)),
  :deep(.q-table td:nth-child(4)) {
    display: none;
  }
}

@media (max-width: 480px) {
  /* Hide more columns on very small screens */
  :deep(.q-table th:nth-child(3)),
  :deep(.q-table td:nth-child(3)) {
    display: none;
  }
}

/* Dialog styling */
.q-dialog .q-card {
  border-radius: 8px;
}

/* Status and type chip animations */
.q-chip {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Table row hover effects */
:deep(.q-table tbody tr) {
  cursor: pointer;
}

/* Action button container */
.row.q-gutter-xs {
  justify-content: center;
  flex-wrap: nowrap;
}

/* Tooltip styling */
.q-tooltip {
  font-size: 0.75rem;
  padding: 4px 8px;
}
</style>
