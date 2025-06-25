<!-- components/ConnectionList.vue -->
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
              @click="$emit('test', props.row)"
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
              @click="$emit('discover-schema', props.row)"
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
              @click="$emit('edit', props.row)"
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
      <q-card style="min-width: 400px">
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
        error: 'red'
      }
      return colors[status] || 'grey'
    },

    getStatusIcon(status) {
      const icons = {
        active: 'check_circle',
        inactive: 'radio_button_unchecked',
        error: 'error'
      }
      return icons[status] || 'help'
    },

    canTest(connection) {
      return connection.status !== 'active' // Only allow testing if not already active
    },

    formatDate(dateString) {
      return date.formatDate(dateString, 'MMM DD, YYYY')
    },

    formatTime(dateString) {
      return date.formatDate(dateString, 'HH:mm:ss')
    },

    formatDateTime(dateString) {
      return date.formatDate(dateString, 'MMM DD, YYYY HH:mm:ss')
    },

    confirmDelete(connection) {
      this.$q.dialog({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete connection "${connection.name}"? This action cannot be undone.`,
        cancel: true,
        persistent: true,
        color: 'negative'
      }).onOk(() => {
        this.$emit('delete', connection)
      })
    },

    viewDetails(connection) {
      this.selectedConnection = connection
      this.showDetailsDialog = true
    },

    duplicateConnection(connection) {
      this.$q.notify({
        type: 'info',
        message: 'Duplicate functionality will be implemented in the next phase',
        position: 'top-right'
      })
    },

    exportConnection(connection) {
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
}

:deep(.q-table tbody tr:hover) {
  background: #f0f8ff;
}

/* Action buttons styling */
.q-btn {
  transition: all 0.2s ease;
}

.q-btn:hover {
  transform: scale(1.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  :deep(.q-table th),
  :deep(.q-table td) {
    padding: 8px 4px;
  }

  .q-btn {
    min-width: 32px;
    padding: 6px;
  }
}

/* Empty state styling */
.text-center {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
