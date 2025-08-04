// services/api.js
import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000', // Update this to match your backend URL
  timeout: 120000, // Increased to 2 minutes for large database schema discovery
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Data Source API endpoints
export const dataSourceAPI = {
  // Database Types
  getSupportedDbTypes() {
    return api.get('/datasources/db-types')
  },

  // Connection Management
  createConnection(connectionData) {
    return api.post('/datasources/connections', connectionData)
  },

  getAllConnections() {
    return api.get('/datasources/connections')
  },

  getConnectionById(connectionId) {
    return api.get(`/datasources/connections/${connectionId}`)
  },

  updateConnection(connectionId, updateData) {
    return api.put(`/datasources/connections/${connectionId}`, updateData)
  },

  deleteConnection(connectionId) {
    return api.delete(`/datasources/connections/${connectionId}`)
  },

  // Connection Configuration
  getConnectionConfigs(connectionId) {
    return api.get(`/datasources/connections/${connectionId}/configs`)
  },

  getConnectionConfigsDict(connectionId) {
    return api.get(`/datasources/connections/${connectionId}/configs/dict`)
  },

  saveConnectionConfigs(connectionId, configs) {
    return api.post(`/datasources/connections/${connectionId}/configs/batch`, configs)
  },

  // Connection Testing
  testConnection(testData) {
    return api.post('/datasources/connections/test', testData)
  },

  testConnectionOnly(dbType, config) {
    return api.post('/datasources/connections/test-only', config, {
      params: { db_type: dbType }
    })
  },

  // Schema Discovery
  getConnectionTables(connectionId) {
    return api.get(`/datasources/connections/${connectionId}/tables`)
  },

  getTableColumns(connectionId, tableName) {
    return api.get(`/datasources/connections/${connectionId}/tables/${tableName}/columns`)
  },

  getCompleteSchema(connectionId, quickMode = true) {
    return api.get(`/datasources/connections/${connectionId}/schema`, {
      params: { quick_mode: quickMode }
    })
  },

  getConnectionQuickInfo(connectionId) {
    return api.get(`/datasources/connections/${connectionId}/quick-info`)
  }
}

// Metadata API endpoints (existing APIs)
export const metaAPI = {
  // Master Models
  createMasterModel:async function (data) {
    try {
      const allModelsResponse = await  api.get('/models');
      const allModels = allModelsResponse.data;
      console.log(allModelsResponse)

      console.log(allModels)
      const existingModel = allModels.find(model =>
        // Adjust the condition as per how "equality" should be checked
        model.name === data.name // Example check
      );
      console.log(existingModel)

      if (existingModel) {
        console.log('model returning',existingModel)
        return existingModel;
      } else {
        const newModelResponse = await  api.post('/models', data);
        console.log('new model returning',newModelResponse)

        return newModelResponse.data;
      }
      } catch (error) {
        console.error('Error in createMasterModel:', error);
        throw error;
      }
    },

  getAllMasterModels() {
    return api.get('/models')
  },

  updateMasterModel(modelId, data) {
    return api.put(`/models/${modelId}`, data)
  },

  deleteMasterModel(modelId) {
    return api.delete(`/models/${modelId}`)
  },

  // Equipment
  createEquipment:async function (data) {
    try {
      const allEquResponse = await  api.get('/equipments');
      const allEqu = allEquResponse.data;
      console.log(allEquResponse)

      console.log(allEqu)
      const existingModel = allEqu.find(model =>
        // Adjust the condition as per how "equality" should be checked
        model.name === data.name // Example check
      );

      if (existingModel) {
        console.log('equ returning',existingModel)

        return existingModel;
      } else {
        const newModelResponse = await  api.post('/equipments', data);
        console.log('new equ returning',newModelResponse)

        return newModelResponse.data;
      }
      } catch (error) {
        console.error('Error in createMasterModel:', error);
        throw error;
      }
    },

  getAllEquipments() {
    return api.get('/equipments')
  },

  updateEquipment(equipmentId, data) {
    return api.put(`/equipments/${equipmentId}`, data)
  },

  deleteEquipment(equipmentId) {
    return api.delete(`/equipments/${equipmentId}`)
  },

  // Specifications
  createSpec(data) {
    return api.post('/specs', data)
  },

  getAllSpecs() {
    return api.get('/specs')
  },

  updateSpec(specId, data) {
    return api.put(`/specs/${specId}`, data)
  },

  deleteSpec(specId) {
    return api.delete(`/specs/${specId}`)
  },

  // Signals
  createSignal(data) {
    return api.post('/signals', data)
  },

  getAllSignals() {
    return api.get('/signals')
  },

  updateSignal(signalId, data) {
    return api.put(`/signals/${signalId}`, data)
  },

  deleteSignal(signalId) {
    return api.delete(`/signals/${signalId}`)
  },

  // Filters
  createFilter(data) {
    return api.post('/filters', data)
  },

  getAllFilters() {
    return api.get('/filters')
  },

  getFiltersByEquipmentId(equipmentId) {
    return api.get(`/filters/${equipmentId}`)
  },

  updateFilter(filterId, data) {
    return api.put(`/filters/${filterId}`, data)
  },

  deleteFilter(filterId) {
    return api.delete(`/filters/${filterId}`)
  },

  // Documents
  createDoc(data) {
    return api.post('/docs', data)
  },

  getAllDocs() {
    return api.get('/docs')
  },

  updateDoc(docId, data) {
    return api.put(`/docs/${docId}`, data)
  },

  deleteDoc(docId) {
    return api.delete(`/docs/${docId}`)
  }
}

// Pages API
export const pageAPI = {
  createPage(data) {
    return api.post('/pages/', data)
  },

  getAllPages() {
    return api.get('/pages/')
  },

  getPageById(pageId) {
    return api.get(`/pages/${pageId}`)
  },

  updatePage(pageId, data) {
    return api.put(`/pages/${pageId}`, data)
  },

  deletePage(pageId) {
    return api.delete(`/pages/${pageId}`)
  }
}

// Query API
export const widgetLayoutAPI = {
  /**
   * Save complete page layout with widgets and time settings
   * Formats data correctly for backend PageLayoutData model
   */
  async savePageLayout(pageId, widgets, gridConfig = null, timeSettings = null) {
    try {
      console.log('🔄 Saving page layout for page:', pageId)
      console.log('📊 Widgets to save:', widgets.length)

      // Format data according to PageLayoutData model
      const layoutData = {
        // ✅ Correct key: widgets_data (not widgets)
        widgets_data: widgets.map(widget => ({
          // Widget metadata
          widget_type: widget.widget_type || 'line_chart',
          widget_label: widget.widget_label || 'Untitled Widget',
          equipment_ids: widget.equipment_ids || [],
          signal_ids: widget.signal_ids || [],
          filter_selections: widget.filter_selections || {},
          styling_config: widget.styling_config || {},

          // Position data from GridStack
          position_data: {
            x: widget.x || 0,
            y: widget.y || 0,
            w: widget.w || 6,
            h: widget.h || 4
          }
        })),

        // ✅ Layout configuration
        layout_data: {
          grid_config: gridConfig || {
            columns: 12,
            cellHeight: 100,
            margin: 10
          },
          timestamp: new Date().toISOString(),
          version: "1.0"
        },

        // ✅ Time settings (optional)
        time_settings_data: timeSettings
      }

      console.log('📤 Sending layout data:', layoutData)

      const response = await api.put(`/widgets/pages/${pageId}/layout`, layoutData)

      console.log('✅ Layout saved successfully')
      return response.data

    } catch (error) {
      console.error('❌ Failed to save layout:', error)

      // Enhanced error handling
      if (error.response?.status === 422) {
        console.error('💡 Validation Error - Check data structure:', error.response.data)
      }

      throw error
    }
  },

  /**
   * Load complete page layout
   */
  async loadPageLayout(pageId) {
    try {
      console.log('📥 Loading page layout for page:', pageId)

      const response = await api.get(`/widgets/pages/${pageId}/layout`)

      console.log('✅ Layout loaded successfully')
      return response.data

    } catch (error) {
      if (error.response?.status === 404) {
        console.log('📝 No layout found for page:', pageId)
        return null
      }

      console.error('❌ Failed to load layout:', error)
      throw error
    }
  },

  /**
   * Convert GridStack layout to widget format
   * Helper function to transform GridStack data
   */
  convertGridStackToWidgets(gridStackNodes, widgetDataMap = {}) {
    return gridStackNodes.map(node => {
      const widgetId = node.el?.getAttribute('data-id') || node.id
      const widgetData = widgetDataMap[widgetId] || {}

      return {
        // Widget identity
        widget_id: widgetData.widget_id || widgetId,

        // GridStack position
        x: node.x,
        y: node.y,
        w: node.w,
        h: node.h,
        locked: node.locked || false,

        // Widget metadata
        widget_type: widgetData.widget_type || 'line_chart',
        widget_label: widgetData.widget_label || `Widget ${widgetId}`,
        equipment_ids: widgetData.equipment_ids || [],
        signal_ids: widgetData.signal_ids || [],
        filter_selections: widgetData.filter_selections || {},
        styling_config: widgetData.styling_config || {},

        // Timestamps
        created_at: widgetData.created_at,
        updated_at: widgetData.updated_at
      }
    })
  },

  /**
   * Convert backend widget format to GridStack format
   * Helper function for loading layouts
   */
  convertWidgetsToGridStack(widgets) {
    return widgets.map(widget => ({
      id: widget.widget_id,
      x: widget.position_data?.x || widget.x || 0,
      y: widget.position_data?.y || widget.y || 0,
      w: widget.position_data?.w || widget.w || 6,
      h: widget.position_data?.h || widget.h || 4,
      locked: widget.locked || false,
      content: widget
    }))
  }
}

// Enhanced Widget API
export const widgetAPI = {
  /**
   * Create widget via wizard
   */
  async createWidget(widgetData) {
    try {
      console.log('🔧 Creating widget:', widgetData)

      const response = await api.post('/widgets/', widgetData)

      console.log('✅ Widget created:', response.data)
      return response.data

    } catch (error) {
      console.error('❌ Failed to create widget:', error)
      throw error
    }
  },

  /**
   * Get widget data for chart display
   */
  async getWidgetData(widgetId, timeRange) {
    try {
      const response = await api.post(`/widgets/${widgetId}/data`, {
        time_start: timeRange.start,
        time_end: timeRange.end,
        time_range_type: timeRange.range_type || 'custom'
      })

      return response.data
    } catch (error) {
      console.error('❌ Failed to get widget data:', error)
      throw error
    }
  },

  /**
   * Get widgets for page
   */
  async getPageWidgets(pageId) {
    try {
      const response = await api.get(`/widgets/page/${pageId}`)
      return response.data
    } catch (error) {
      console.error('❌ Failed to get page widgets:', error)
      throw error
    }
  },

  /**
   * Update widget
   */
  async updateWidget(widgetId, updateData) {
    try {
      const response = await api.put(`/widgets/${widgetId}`, updateData)
      return response.data
    } catch (error) {
      console.error('❌ Failed to update widget:', error)
      throw error
    }
  },

  /**
   * Delete widget
   */
  async deleteWidget(widgetId) {
    try {
      await api.delete(`/widgets/${widgetId}`)
      console.log('✅ Widget deleted:', widgetId)
    } catch (error) {
      console.error('❌ Failed to delete widget:', error)
      throw error
    }
  }
}

// Export all APIs (add to your existing exports)


// Export default api instance for custom calls
export default api
