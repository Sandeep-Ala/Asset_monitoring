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
  createMasterModel(data) {
    return api.post('/models', data)
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
  createEquipment(data) {
    return api.post('/equipments', data)
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
export const queryAPI = {
  queryData(filters) {
    return api.post('/query', filters)
  },

  saveLayout(layoutData, pageId) {
    return api.post('/save-layout', layoutData, {
      params: { page_id: pageId }
    })
  }
}

// Export default api instance for custom calls
export default api
