<!-- src/components/WidgetWizard.vue -->
<!-- Multi-step Widget Creation Wizard -->
<!-- Guides users through equipment → signals → filters → styling → widget creation -->

<template>
  <q-dialog
    v-model="isOpen"
    persistent
    maximized
    transition-show="slide-up"
    transition-hide="slide-down"
  >
    <q-card class="widget-wizard-card">
      <!-- Header -->
      <q-card-section class="row items-center q-pa-md bg-primary text-white">
        <div class="col">
          <div class="text-h5">
            <q-icon name="auto_awesome" class="q-mr-sm" />
            Widget Creation Wizard
          </div>
          <div class="text-subtitle2 opacity-80">
            Step {{ currentStep }} of {{ totalSteps }}: {{ stepTitles[currentStep - 1] }}
          </div>
        </div>
        <div class="col-auto">
          <q-btn flat round dense icon="close" @click="handleClose" />
        </div>
      </q-card-section>

      <!-- Progress Indicator -->
      <q-card-section class="q-pa-none">
        <q-linear-progress
          :value="stepProgress"
          color="primary"
          size="4px"
          class="progress-bar"
        />

        <div class="step-indicator q-pa-md">
          <div class="row items-center justify-center q-gutter-sm">
            <div
              v-for="(title, index) in stepTitles"
              :key="index"
              class="step-item"
              :class="{
                'step-completed': index + 1 < currentStep,
                'step-active': index + 1 === currentStep,
                'step-upcoming': index + 1 > currentStep
              }"
            >
              <div class="step-circle">
                <q-icon
                  v-if="index + 1 < currentStep"
                  name="check"
                  size="16px"
                />
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="step-label">{{ title }}</div>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Main Content Area -->
      <q-card-section class="wizard-content row no-wrap" style="height: calc(100vh - 240px);">

        <!-- Left Panel - Step Content -->
        <div class="col-8 q-pr-md">
          <q-scroll-area style="height: 100%;">

            <!-- Step 1: Widget Type Selection -->
            <div v-if="currentStep === 1" class="step-content">
              <div class="text-h6 q-mb-md">📊 Choose Widget Type</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Select the type of visualization you want to create for your data.
              </div>

              <div class="row q-gutter-md">
                <div
                  v-for="type in widgetTypes"
                  :key="type.value"
                  class="col-12 col-sm-6 col-md-3"
                >
                  <q-card
                    flat
                    bordered
                    class="widget-type-card cursor-pointer"
                    :class="{ 'selected': wizardData.widgetType === type.value }"
                    @click="selectWidgetType(type.value)"
                  >
                    <q-card-section class="text-center q-pa-lg">
                      <q-icon :name="type.icon" size="48px" :color="wizardData.widgetType === type.value ? 'primary' : 'grey-6'" />
                      <div class="text-h6 q-mt-md">{{ type.label }}</div>
                      <div class="text-caption text-grey-7 q-mt-sm">{{ type.description }}</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>

              <!-- Advanced Options -->
              <div class="q-mt-xl">
                <q-expansion-item icon="tune" label="Advanced Options" class="bg-grey-1">
                  <div class="q-pa-md">
                    <q-toggle
                      v-model="wizardData.advanced.enableZoom"
                      label="Enable zoom/pan functionality"
                      color="primary"
                    />
                    <q-toggle
                      v-model="wizardData.advanced.enableAnimation"
                      label="Enable chart animations"
                      color="primary"
                      class="q-ml-md"
                    />
                    <q-toggle
                      v-model="wizardData.advanced.showDataPoints"
                      label="Show individual data points"
                      color="primary"
                      class="q-ml-md"
                    />
                  </div>
                </q-expansion-item>
              </div>
            </div>

            <!-- Step 2: Equipment Selection -->
            <div v-if="currentStep === 2" class="step-content">
              <div class="text-h6 q-mb-md">🏭 Select Equipment</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Choose one or more equipment sources for your widget data.
              </div>

              <div class="row q-gutter-md">
                <!-- Equipment Search -->
                <div class="col-12">
                  <q-input
                    v-model="equipmentSearch"
                    outlined
                    placeholder="Search equipment..."
                    clearable
                    debounce="300"
                  >
                    <template v-slot:prepend>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </div>

                <!-- Equipment List -->
                <div class="col-12">
                  <div v-if="loadingEquipment" class="text-center q-pa-lg">
                    <q-spinner-dots size="40px" color="primary" />
                    <div class="q-mt-sm">Loading equipment...</div>
                  </div>

                  <div v-else-if="filteredEquipment.length === 0" class="text-center q-pa-lg">
                    <q-icon name="search_off" size="48px" color="grey-4" />
                    <div class="text-h6 text-grey-6 q-mt-md">No equipment found</div>
                    <div class="text-body2 text-grey-7">Try adjusting your search terms</div>
                  </div>

                  <div v-else class="equipment-grid">
                    <q-card
                      v-for="equipment in filteredEquipment"
                      :key="equipment.id"
                      flat
                      bordered
                      class="equipment-card cursor-pointer"
                      :class="{ 'selected': wizardData.selectedEquipment.includes(equipment.id) }"
                      @click="toggleEquipment(equipment.id)"
                    >
                      <q-card-section class="q-pa-md">
                        <div class="row items-center">
                          <div class="col">
                            <div class="text-subtitle1">{{ equipment.name }}</div>
                            <div class="text-caption text-grey-7">{{ equipment.location || 'No location' }}</div>
                          </div>
                          <div class="col-auto">
                            <q-checkbox
                              :model-value="wizardData.selectedEquipment.includes(equipment.id)"
                              @update:model-value="toggleEquipment(equipment.id)"
                              color="primary"
                            />
                          </div>
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>

                <!-- Selection Summary -->
                <div v-if="wizardData.selectedEquipment.length > 0" class="col-12">
                  <q-banner class="bg-blue-1 text-blue-8">
                    <template v-slot:avatar>
                      <q-icon name="info" />
                    </template>
                    {{ wizardData.selectedEquipment.length }} equipment selected.
                    This will determine which signals are available in the next step.
                  </q-banner>
                </div>
              </div>
            </div>

            <!-- Step 3: Signal Selection -->
            <div v-if="currentStep === 3" class="step-content">
              <div class="text-h6 q-mb-md">📡 Select Signals</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Choose the data signals you want to display in your widget.
              </div>

              <div class="row q-gutter-md">
                <!-- Signal Search -->
                <div class="col-12">
                  <q-input
                    v-model="signalSearch"
                    outlined
                    placeholder="Search signals..."
                    clearable
                    debounce="300"
                  >
                    <template v-slot:prepend>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </div>

                <!-- Signals by Equipment -->
                <div class="col-12">
                  <div v-if="loadingSignals" class="text-center q-pa-lg">
                    <q-spinner-dots size="40px" color="primary" />
                    <div class="q-mt-sm">Loading signals...</div>
                  </div>

                  <div v-else>
                    <q-expansion-item
                      v-for="equipmentSignals in groupedSignals"
                      :key="equipmentSignals.equipmentId"
                      :label="equipmentSignals.equipmentName"
                      :caption="`${equipmentSignals.signals.length} signals available`"
                      icon="timeline"
                      default-opened
                      class="q-mb-sm"
                    >
                      <div class="q-pa-md">
                        <div class="row q-gutter-sm">
                          <div
                            v-for="signal in equipmentSignals.filteredSignals"
                            :key="signal.id"
                            class="col-12 col-sm-6 col-md-4"
                          >
                            <q-card
                              flat
                              bordered
                              class="signal-card cursor-pointer"
                              :class="{ 'selected': wizardData.selectedSignals.includes(signal.id) }"
                              @click="toggleSignal(signal.id)"
                            >
                              <q-card-section class="q-pa-sm">
                                <div class="row items-center">
                                  <div class="col">
                                    <div class="text-body2">{{ signal.key }}</div>
                                    <div class="text-caption text-grey-7">{{ signal.desc || signal.value }}</div>
                                    <div v-if="signal.unit" class="text-caption text-blue-7">Unit: {{ signal.unit }}</div>
                                  </div>
                                  <div class="col-auto">
                                    <q-checkbox
                                      :model-value="wizardData.selectedSignals.includes(signal.id)"
                                      @update:model-value="toggleSignal(signal.id)"
                                      color="primary"
                                      size="sm"
                                    />
                                  </div>
                                </div>
                              </q-card-section>
                            </q-card>
                          </div>
                        </div>
                      </div>
                    </q-expansion-item>
                  </div>
                </div>

                <!-- Selection Summary -->
                <div v-if="wizardData.selectedSignals.length > 0" class="col-12">
                  <q-banner class="bg-green-1 text-green-8">
                    <template v-slot:avatar>
                      <q-icon name="check_circle" />
                    </template>
                    {{ wizardData.selectedSignals.length }} signal{{ wizardData.selectedSignals.length !== 1 ? 's' : '' }} selected.
                    These will be the data series in your {{ wizardData.widgetType.replace('_', ' ') }}.
                  </q-banner>
                </div>
              </div>
            </div>

            <!-- Step 4: Filter Selection (Optional) -->
            <div v-if="currentStep === 4" class="step-content">
              <div class="text-h6 q-mb-md">🔧 Configure Filters</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Optionally apply filters to your data. This step can be skipped if no filtering is needed.
              </div>

              <div class="row q-gutter-md">
                <!-- Skip Option -->
                <div class="col-12">
                  <q-card flat bordered class="bg-blue-1">
                    <q-card-section class="q-pa-md">
                      <q-checkbox
                        v-model="wizardData.skipFilters"
                        label="Skip filters - show all data"
                        color="primary"
                        class="text-body1"
                      />
                      <div class="text-caption text-grey-7 q-mt-xs">
                        Check this to display all available data without any filtering
                      </div>
                    </q-card-section>
                  </q-card>
                </div>

                <!-- Filter Configuration -->
                <div v-if="!wizardData.skipFilters" class="col-12">
                  <div v-if="loadingFilters" class="text-center q-pa-lg">
                    <q-spinner-dots size="40px" color="primary" />
                    <div class="q-mt-sm">Loading available filters...</div>
                  </div>

                  <div v-else>
                    <div
                      v-for="equipmentFilter in groupedFilters"
                      :key="equipmentFilter.equipmentId"
                      class="q-mb-md"
                    >
                      <q-expansion-item
                        :label="equipmentFilter.equipmentName"
                        :caption="`${equipmentFilter.filters.length} filters available`"
                        icon="filter_list"
                        class="bg-grey-1"
                      >
                        <div class="q-pa-md">
                          <div class="row q-gutter-md">
                            <div
                              v-for="filter in equipmentFilter.filters"
                              :key="filter.id"
                              class="col-12 col-sm-6"
                            >
                              <q-card flat bordered>
                                <q-card-section class="q-pa-md">
                                  <div class="text-subtitle2">{{ filter.filter_key }}</div>
                                  <q-input
                                    v-model="wizardData.filterSelections[`${equipmentFilter.equipmentId}_${filter.filter_key}`]"
                                    :label="`${filter.filter_key} value`"
                                    :placeholder="filter.filter_value || 'Enter value'"
                                    outlined
                                    dense
                                    class="q-mt-sm"
                                  />
                                </q-card-section>
                              </q-card>
                            </div>
                          </div>
                        </div>
                      </q-expansion-item>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 5: Widget Styling -->
            <div v-if="currentStep === 5" class="step-content">
              <div class="text-h6 q-mb-md">🎨 Customize Appearance</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Configure colors, styles, and visual options for your widget.
              </div>

              <div class="row q-gutter-md">
                <!-- Color Configuration -->
                <div class="col-12">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-subtitle1 q-mb-md">
                        <q-icon name="palette" class="q-mr-sm" />
                        Signal Colors
                      </div>

                      <div class="row q-gutter-sm">
                        <div
                          v-for="(signalId, index) in wizardData.selectedSignals"
                          :key="signalId"
                          class="col-12 col-sm-6 col-md-4"
                        >
                          <div class="signal-color-config">
                            <div class="text-body2 q-mb-xs">{{ getSignalName(signalId) }}</div>
                            <div class="row items-center q-gutter-sm">
                              <div class="col">
                                <q-input
                                  v-model="wizardData.styling.colors[index]"
                                  type="color"
                                  outlined
                                  dense
                                  style="max-width: 80px;"
                                />
                              </div>
                              <div class="col">
                                <q-select
                                  v-model="wizardData.styling.lineStyles[index]"
                                  :options="lineStyleOptions"
                                  option-label="label"
                                  option-value="value"
                                  outlined
                                  dense
                                  map-options
                                  emit-value
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>

                <!-- Chart Options -->
                <div class="col-12">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-subtitle1 q-mb-md">
                        <q-icon name="tune" class="q-mr-sm" />
                        Chart Options
                      </div>

                      <div class="row q-gutter-md">
                        <div class="col-12 col-sm-6">
                          <q-toggle
                            v-model="wizardData.styling.showLegend"
                            label="Show legend"
                            color="primary"
                          />
                          <q-toggle
                            v-model="wizardData.styling.showGrid"
                            label="Show grid lines"
                            color="primary"
                            class="q-mt-sm"
                          />
                          <q-toggle
                            v-model="wizardData.styling.enableAnimation"
                            label="Enable animations"
                            color="primary"
                            class="q-mt-sm"
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            v-model.number="wizardData.styling.pointRadius"
                            type="number"
                            label="Point radius"
                            outlined
                            dense
                            min="0"
                            max="10"
                            class="q-mb-sm"
                          />
                          <q-input
                            v-model.number="wizardData.styling.animationDuration"
                            type="number"
                            label="Animation duration (ms)"
                            outlined
                            dense
                            min="0"
                            max="3000"
                          />
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Step 6: Widget Configuration -->
            <div v-if="currentStep === 6" class="step-content">
              <div class="text-h6 q-mb-md">⚙️ Widget Settings</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Configure the final widget settings and positioning.
              </div>

              <div class="row q-gutter-md">
                <!-- Basic Settings -->
                <div class="col-12 col-md-6">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-subtitle1 q-mb-md">Basic Settings</div>

                      <q-input
                        v-model="wizardData.widgetLabel"
                        label="Widget Title *"
                        outlined
                        :rules="[val => !!val || 'Title is required']"
                        class="q-mb-md"
                      />

                      <q-input
                        v-model="wizardData.description"
                        label="Description (optional)"
                        type="textarea"
                        outlined
                        rows="2"
                      />
                    </q-card-section>
                  </q-card>
                </div>

                <!-- Position Settings -->
                <div class="col-12 col-md-6">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-subtitle1 q-mb-md">Position & Size</div>

                      <div class="row q-gutter-sm">
                        <div class="col-6">
                          <q-input
                            v-model.number="wizardData.position.w"
                            type="number"
                            label="Width"
                            outlined
                            dense
                            min="2"
                            max="12"
                          />
                        </div>
                        <div class="col-6">
                          <q-input
                            v-model.number="wizardData.position.h"
                            type="number"
                            label="Height"
                            outlined
                            dense
                            min="2"
                            max="10"
                          />
                        </div>
                      </div>

                      <div class="text-caption text-grey-7 q-mt-sm">
                        Position (X, Y) will be automatically determined when the widget is added to the dashboard.
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Step 7: Preview & Create -->
            <div v-if="currentStep === 7" class="step-content">
              <div class="text-h6 q-mb-md">👀 Preview & Create</div>
              <div class="text-body2 text-grey-7 q-mb-lg">
                Review your widget configuration and create the widget.
              </div>

              <!-- Configuration Summary -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle1 q-mb-md">Configuration Summary</div>

                  <div class="row q-gutter-md text-body2">
                    <div class="col-12 col-sm-6">
                      <div><strong>Type:</strong> {{ getWidgetTypeLabel(wizardData.widgetType) }}</div>
                      <div><strong>Title:</strong> {{ wizardData.widgetLabel }}</div>
                      <div><strong>Equipment:</strong> {{ wizardData.selectedEquipment.length }} selected</div>
                      <div><strong>Signals:</strong> {{ wizardData.selectedSignals.length }} selected</div>
                    </div>
                    <div class="col-12 col-sm-6">
                      <div><strong>Filters:</strong> {{ wizardData.skipFilters ? 'None' : Object.keys(wizardData.filterSelections).length }}</div>
                      <div><strong>Size:</strong> {{ wizardData.position.w }}x{{ wizardData.position.h }}</div>
                      <div><strong>Legend:</strong> {{ wizardData.styling.showLegend ? 'Enabled' : 'Disabled' }}</div>
                      <div><strong>Animation:</strong> {{ wizardData.styling.enableAnimation ? 'Enabled' : 'Disabled' }}</div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Create Widget Action -->
              <div class="text-center">
                <q-btn
                  color="primary"
                  size="lg"
                  icon="add_circle"
                  label="Create Widget"
                  @click="createWidget"
                  :loading="creatingWidget"
                  :disable="!canCreateWidget"
                />

                <div v-if="!canCreateWidget" class="text-caption text-red q-mt-sm">
                  Please ensure all required fields are filled
                </div>
              </div>
            </div>

          </q-scroll-area>
        </div>

        <!-- Right Panel - Live Preview -->
        <div class="col-4 bg-grey-1">
          <div class="preview-panel q-pa-md">
            <div class="text-subtitle1 q-mb-md">
              <q-icon name="visibility" class="q-mr-sm" />
              Live Preview
            </div>

            <!-- Preview Content -->
            <div class="preview-content">
              <div v-if="currentStep < 3" class="preview-placeholder">
                <q-icon name="widgets" size="64px" color="grey-4" />
                <div class="text-grey-6 q-mt-md">Preview will appear after selecting equipment and signals</div>
              </div>

              <div v-else-if="!wizardData.selectedSignals.length" class="preview-placeholder">
                <q-icon name="timeline" size="64px" color="grey-4" />
                <div class="text-grey-6 q-mt-md">Select signals to see preview</div>
              </div>

              <!-- Actual Preview (when data is available) -->
              <div v-else class="preview-widget">
                <div class="preview-title">{{ wizardData.widgetLabel || 'Untitled Widget' }}</div>

                <!-- Mock chart preview -->
                <div class="mock-chart" :class="`chart-${wizardData.widgetType}`">
                  <div v-if="wizardData.widgetType === 'line_chart'" class="line-chart-preview">
                    <svg viewBox="0 0 300 200" class="chart-svg">
                      <!-- Mock data lines -->
                      <path
                        v-for="(signalId, index) in wizardData.selectedSignals.slice(0, 3)"
                        :key="signalId"
                        :d="generateMockPath(index)"
                        :stroke="wizardData.styling.colors[index] || getDefaultColor(index)"
                        :stroke-width="2"
                        :stroke-dasharray="getStrokeDashArray(wizardData.styling.lineStyles[index])"
                        fill="none"
                      />
                      <!-- Mock grid -->
                      <g v-if="wizardData.styling.showGrid" class="grid" stroke="#e0e0e0" stroke-width="1">
                        <line x1="50" y1="20" x2="50" y2="180" />
                        <line x1="50" y1="180" x2="280" y2="180" />
                        <line x1="50" y1="140" x2="280" y2="140" opacity="0.5" />
                        <line x1="50" y1="100" x2="280" y2="100" opacity="0.5" />
                        <line x1="50" y1="60" x2="280" y2="60" opacity="0.5" />
                      </g>
                    </svg>
                  </div>

                  <div v-else-if="wizardData.widgetType === 'bar_chart'" class="bar-chart-preview">
                    <div class="bars">
                      <div
                        v-for="(signalId, index) in wizardData.selectedSignals.slice(0, 5)"
                        :key="signalId"
                        class="bar"
                        :style="{
                          backgroundColor: wizardData.styling.colors[index] || getDefaultColor(index),
                          height: `${Math.random() * 80 + 20}%`
                        }"
                      />
                    </div>
                  </div>

                  <div v-else class="generic-chart-preview">
                    <q-icon :name="getWidgetTypeIcon(wizardData.widgetType)" size="48px" color="primary" />
                    <div class="q-mt-sm">{{ getWidgetTypeLabel(wizardData.widgetType) }} Preview</div>
                  </div>
                </div>

                <!-- Mock legend -->
                <div v-if="wizardData.styling.showLegend && wizardData.selectedSignals.length" class="preview-legend">
                  <div
                    v-for="(signalId, index) in wizardData.selectedSignals.slice(0, 3)"
                    :key="signalId"
                    class="legend-item"
                  >
                    <div
                      class="legend-color"
                      :style="{ backgroundColor: wizardData.styling.colors[index] || getDefaultColor(index) }"
                    />
                    <span class="legend-label">{{ getSignalName(signalId) }}</span>
                  </div>
                  <div v-if="wizardData.selectedSignals.length > 3" class="legend-more">
                    +{{ wizardData.selectedSignals.length - 3 }} more...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-separator />

      <!-- Footer Navigation -->
      <q-card-actions class="row items-center q-pa-md bg-grey-1">
        <div class="col">
          <q-btn
            flat
            label="Cancel"
            @click="handleClose"
            color="grey-8"
          />
        </div>

        <div class="col-auto">
          <div class="row q-gutter-sm">
            <q-btn
              v-if="currentStep > 1"
              flat
              label="Previous"
              icon="arrow_back"
              @click="previousStep"
              color="grey-8"
            />

            <q-btn
              v-if="currentStep < totalSteps"
              unelevated
              :label="getNextButtonLabel()"
              icon-right="arrow_forward"
              @click="nextStep"
              color="primary"
              :disable="!canProceedToNext"
            />
          </div>
        </div>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import { signalColorPalette } from 'src/utils/chartUtils.js'

// ==================== PROPS & EMITS ====================

const props = defineProps({
  pageId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['widget-created', 'close'])

// ==================== COMPONENT STATE ====================

const $q = useQuasar()

// Dialog state
const isOpen = ref(false)
const currentStep = ref(1)
const totalSteps = 7

// Loading states
const loadingEquipment = ref(false)
const loadingSignals = ref(false)
const loadingFilters = ref(false)
const creatingWidget = ref(false)

// Search filters
const equipmentSearch = ref('')
const signalSearch = ref('')

// Data from backend
const availableEquipment = ref([])
const availableSignals = ref([])
const availableFilters = ref([])

// Wizard data model
const wizardData = reactive({
  // Step 1: Widget Type
  widgetType: '',
  advanced: {
    enableZoom: true,
    enableAnimation: true,
    showDataPoints: true
  },

  // Step 2: Equipment
  selectedEquipment: [],

  // Step 3: Signals
  selectedSignals: [],

  // Step 4: Filters
  skipFilters: true,
  filterSelections: {},

  // Step 5: Styling
  styling: {
    colors: [],
    lineStyles: [],
    showLegend: true,
    showGrid: true,
    enableAnimation: true,
    pointRadius: 3,
    animationDuration: 750
  },

  // Step 6: Configuration
  widgetLabel: '',
  description: '',
  position: {
    x: 0,
    y: 0,
    w: 6,
    h: 4
  }
})

// ==================== CONSTANTS ====================

const stepTitles = [
  'Widget Type',
  'Equipment',
  'Signals',
  'Filters',
  'Styling',
  'Settings',
  'Create'
]

const widgetTypes = [
  {
    value: 'line_chart',
    label: 'Line Chart',
    icon: 'timeline',
    description: 'Show trends over time'
  },
  {
    value: 'bar_chart',
    label: 'Bar Chart',
    icon: 'bar_chart',
    description: 'Compare values'
  },
  {
    value: 'pie_chart',
    label: 'Pie Chart',
    icon: 'pie_chart',
    description: 'Show proportions'
  },
  {
    value: 'table',
    label: 'Data Table',
    icon: 'table_rows',
    description: 'Display raw data'
  }
]

const lineStyleOptions = [
  { label: 'Solid', value: 'solid' },
  { label: 'Dashed', value: 'dashed' },
  { label: 'Dotted', value: 'dotted' },
  { label: 'Dash-Dot', value: 'dashdot' }
]

// ==================== COMPUTED PROPERTIES ====================

const stepProgress = computed(() => {
  return (currentStep.value - 1) / (totalSteps - 1)
})

const filteredEquipment = computed(() => {
  if (!equipmentSearch.value) return availableEquipment.value

  const search = equipmentSearch.value.toLowerCase()
  return availableEquipment.value.filter(eq =>
    eq.name.toLowerCase().includes(search) ||
    (eq.location && eq.location.toLowerCase().includes(search))
  )
})

const groupedSignals = computed(() => {
  const groups = []

  wizardData.selectedEquipment.forEach(equipmentId => {
    const equipment = availableEquipment.value.find(eq => eq.id === equipmentId)
    const equipmentSignals = availableSignals.value.filter(signal =>
      signal.equipment_id === equipmentId
    )

    if (equipment && equipmentSignals.length > 0) {
      const filteredSignals = signalSearch.value
        ? equipmentSignals.filter(signal =>
            signal.key.toLowerCase().includes(signalSearch.value.toLowerCase()) ||
            (signal.desc && signal.desc.toLowerCase().includes(signalSearch.value.toLowerCase()))
          )
        : equipmentSignals

      groups.push({
        equipmentId,
        equipmentName: equipment.name,
        signals: equipmentSignals,
        filteredSignals
      })
    }
  })

  return groups
})

const groupedFilters = computed(() => {
  const groups = []

  wizardData.selectedEquipment.forEach(equipmentId => {
    const equipment = availableEquipment.value.find(eq => eq.id === equipmentId)
    const equipmentFilters = availableFilters.value.filter(filter =>
      filter.equipment_id === equipmentId
    )

    if (equipment && equipmentFilters.length > 0) {
      groups.push({
        equipmentId,
        equipmentName: equipment.name,
        filters: equipmentFilters
      })
    }
  })

  return groups
})

const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!wizardData.widgetType
    case 2:
      return wizardData.selectedEquipment.length > 0
    case 3:
      return wizardData.selectedSignals.length > 0
    case 4:
      return true // Filters are optional
    case 5:
      return true // Styling has defaults
    case 6:
      return !!wizardData.widgetLabel.trim()
    default:
      return false
  }
})

const canCreateWidget = computed(() => {
  return wizardData.widgetType &&
         wizardData.selectedEquipment.length > 0 &&
         wizardData.selectedSignals.length > 0 &&
         wizardData.widgetLabel.trim()
})

// ==================== METHODS ====================

/**
 * Open the wizard
 */
function open() {
  isOpen.value = true
  resetWizard()
  loadInitialData()
}

/**
 * Close the wizard
 */
function close() {
  isOpen.value = false
  emit('close')
}

/**
 * Handle close with confirmation if needed
 */
function handleClose() {
  if (currentStep.value > 1) {
    $q.dialog({
      title: 'Close Widget Wizard?',
      message: 'Your progress will be lost. Are you sure you want to close?',
      cancel: true,
      persistent: true
    }).onOk(() => {
      close()
    })
  } else {
    close()
  }
}

/**
 * Reset wizard to initial state
 */
function resetWizard() {
  currentStep.value = 1

  // Reset wizard data
  Object.assign(wizardData, {
    widgetType: '',
    advanced: {
      enableZoom: true,
      enableAnimation: true,
      showDataPoints: true
    },
    selectedEquipment: [],
    selectedSignals: [],
    skipFilters: true,
    filterSelections: {},
    styling: {
      colors: [],
      lineStyles: [],
      showLegend: true,
      showGrid: true,
      enableAnimation: true,
      pointRadius: 3,
      animationDuration: 750
    },
    widgetLabel: '',
    description: '',
    position: {
      x: 0,
      y: 0,
      w: 6,
      h: 4
    }
  })

  // Reset search
  equipmentSearch.value = ''
  signalSearch.value = ''
}

/**
 * Load initial data from backend
 */
async function loadInitialData() {
  await loadEquipment()
}

/**
 * Move to next step
 */
function nextStep() {
  if (!canProceedToNext.value) return

  if (currentStep.value < totalSteps) {
    currentStep.value++
    handleStepChange()
  }
}

/**
 * Move to previous step
 */
function previousStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

/**
 * Handle step changes and load required data
 */
async function handleStepChange() {
  switch (currentStep.value) {
    case 3:
      // Load signals when reaching step 3
      if (wizardData.selectedEquipment.length > 0) {
        await loadSignals()
      }
      break
    case 4:
      // Load filters when reaching step 4
      if (wizardData.selectedEquipment.length > 0) {
        await loadFilters()
      }
      break
    case 5:
      // Initialize styling when reaching step 5
      initializeStyling()
      break
  }
}

/**
 * Get next button label
 */
function getNextButtonLabel() {
  if (currentStep.value === totalSteps - 1) return 'Review'
  if (currentStep.value === 4 && wizardData.skipFilters) return 'Skip Filters'
  return 'Next'
}

// ==================== STEP 1: WIDGET TYPE ====================

function selectWidgetType(type) {
  wizardData.widgetType = type
  console.log('🎯 Widget type selected:', type)
}

function getWidgetTypeLabel(type) {
  const widgetType = widgetTypes.find(wt => wt.value === type)
  return widgetType ? widgetType.label : type
}

function getWidgetTypeIcon(type) {
  const widgetType = widgetTypes.find(wt => wt.value === type)
  return widgetType ? widgetType.icon : 'widgets'
}

// ==================== STEP 2: EQUIPMENT ====================

async function loadEquipment() {
  loadingEquipment.value = true
  try {
    console.log('🏭 Loading equipment...')
    const response = await api.get('/widgets/metadata/equipments')
    availableEquipment.value = response.data.equipments || []
    console.log('✅ Equipment loaded:', availableEquipment.value.length)
  } catch (error) {
    console.error('❌ Failed to load equipment:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load equipment: ' + error.message
    })
  } finally {
    loadingEquipment.value = false
  }
}

function toggleEquipment(equipmentId) {
  const index = wizardData.selectedEquipment.indexOf(equipmentId)
  if (index > -1) {
    wizardData.selectedEquipment.splice(index, 1)
  } else {
    wizardData.selectedEquipment.push(equipmentId)
  }

  console.log('🏭 Equipment selection updated:', wizardData.selectedEquipment)

  // Clear signals when equipment changes
  wizardData.selectedSignals = []
}

// ==================== STEP 3: SIGNALS ====================

async function loadSignals() {
  loadingSignals.value = true
  availableSignals.value = []

  try {
    console.log('📡 Loading signals for equipment:', wizardData.selectedEquipment)

    for (const equipmentId of wizardData.selectedEquipment) {
      const response = await api.get(`/widgets/metadata/equipment/${equipmentId}/signals`)
      const equipmentSignals = response.data.signals.map(signal => ({
        ...signal,
        equipment_id: equipmentId
      }))
      availableSignals.value.push(...equipmentSignals)
    }

    console.log('✅ Signals loaded:', availableSignals.value.length)
  } catch (error) {
    console.error('❌ Failed to load signals:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load signals: ' + error.message
    })
  } finally {
    loadingSignals.value = false
  }
}

function toggleSignal(signalId) {
  const index = wizardData.selectedSignals.indexOf(signalId)
  if (index > -1) {
    wizardData.selectedSignals.splice(index, 1)
  } else {
    wizardData.selectedSignals.push(signalId)
  }

  console.log('📡 Signal selection updated:', wizardData.selectedSignals)
}

function getSignalName(signalId) {
  const signal = availableSignals.value.find(s => s.id === signalId)
  return signal ? signal.key : `Signal ${signalId}`
}

// ==================== STEP 4: FILTERS ====================

async function loadFilters() {
  loadingFilters.value = true
  availableFilters.value = []

  try {
    console.log('🔧 Loading filters for equipment:', wizardData.selectedEquipment)

    for (const equipmentId of wizardData.selectedEquipment) {
      const response = await api.get(`/widgets/metadata/equipment/${equipmentId}/signals`)
      const equipmentFilters = response.data.filters.map(filter => ({
        ...filter,
        equipment_id: equipmentId
      }))
      availableFilters.value.push(...equipmentFilters)
    }

    console.log('✅ Filters loaded:', availableFilters.value.length)
  } catch (error) {
    console.error('❌ Failed to load filters:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load filters: ' + error.message
    })
  } finally {
    loadingFilters.value = false
  }
}

// ==================== STEP 5: STYLING ====================

function initializeStyling() {
  // Initialize colors for selected signals
  wizardData.styling.colors = wizardData.selectedSignals.map((_, index) =>
    signalColorPalette[index % signalColorPalette.length]
  )

  // Initialize line styles
  wizardData.styling.lineStyles = wizardData.selectedSignals.map(() => 'solid')

  console.log('🎨 Styling initialized:', wizardData.styling)
}

function getDefaultColor(index) {
  return signalColorPalette[index % signalColorPalette.length]
}

// ==================== STEP 7: PREVIEW & CREATE ====================

async function createWidget() {
  creatingWidget.value = true

  try {
    console.log('🚀 Creating widget...', wizardData)

    // Prepare widget data for API
    const widgetData = {
      page_id: props.pageId,
      widget_type: wizardData.widgetType,
      widget_label: wizardData.widgetLabel,
      equipment_ids: wizardData.selectedEquipment,
      signal_ids: wizardData.selectedSignals,
      filter_selections: wizardData.skipFilters ? {} : wizardData.filterSelections,
      position_data: wizardData.position,
      styling_config: wizardData.styling
    }

    const response = await api.post('/widgets/', widgetData)

    console.log('✅ Widget created successfully:', response.data)

    $q.notify({
      type: 'positive',
      message: `Widget "${wizardData.widgetLabel}" created successfully!`,
      timeout: 3000
    })

    // Emit widget created event
    emit('widget-created', response.data)

    // Close wizard
    close()

  } catch (error) {
    console.error('❌ Failed to create widget:', error)

    $q.notify({
      type: 'negative',
      message: 'Failed to create widget: ' + (error.response?.data?.detail || error.message),
      timeout: 5000
    })
  } finally {
    creatingWidget.value = false
  }
}

// ==================== PREVIEW HELPERS ====================

function generateMockPath(index) {
  // Generate a simple sine wave for preview
  const points = []
  const amplitude = 40 + (index * 20)
  const frequency = 0.02 + (index * 0.01)
  const offset = 100 + (index * 10)

  for (let x = 50; x <= 280; x += 5) {
    const y = offset + Math.sin((x - 50) * frequency) * amplitude
    points.push(`${x},${Math.max(20, Math.min(180, y))}`)
  }

  return `M${points.join(' L')}`
}

function getStrokeDashArray(style) {
  const styles = {
    'solid': '',
    'dashed': '5,5',
    'dotted': '2,2',
    'dashdot': '10,5,2,5'
  }
  return styles[style] || ''
}

// ==================== WATCHERS ====================

// Watch for equipment changes to reload signals
watch(
  () => wizardData.selectedEquipment,
  (newEquipment) => {
    if (currentStep.value >= 3 && newEquipment.length > 0) {
      loadSignals()
    }
    if (currentStep.value >= 4 && newEquipment.length > 0) {
      loadFilters()
    }
  },
  { deep: true }
)

// Watch for signals changes to update styling
watch(
  () => wizardData.selectedSignals,
  () => {
    if (currentStep.value >= 5) {
      initializeStyling()
    }
  },
  { deep: true }
)

// ==================== LIFECYCLE ====================

onMounted(() => {
  console.log('🧙‍♂️ Widget Wizard mounted')
})

// ==================== EXPOSE PUBLIC METHODS ====================

defineExpose({
  open,
  close
})
</script>

<style scoped>
.widget-wizard-card {
  max-width: 100vw;
  max-height: 100vh;
}

.progress-bar {
  transition: all 0.3s ease;
}

.step-indicator {
  background: white;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.step-item.step-active {
  opacity: 1;
}

.step-item.step-completed {
  opacity: 0.8;
  color: #4caf50;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.step-item.step-active .step-circle {
  background: #2196f3;
  color: white;
}

.step-item.step-completed .step-circle {
  background: #4caf50;
  color: white;
}

.step-label {
  font-size: 12px;
  text-align: center;
  font-weight: 500;
}

.wizard-content {
  overflow: hidden;
}

.step-content {
  padding: 24px;
  max-width: 100%;
}

.widget-type-card {
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.widget-type-card:hover {
  border-color: #e3f2fd;
  transform: translateY(-2px);
}

.widget-type-card.selected {
  border-color: #2196f3;
  background: #e3f2fd;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.equipment-card,
.signal-card {
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.equipment-card:hover,
.signal-card:hover {
  border-color: #e3f2fd;
  transform: translateY(-1px);
}

.equipment-card.selected,
.signal-card.selected {
  border-color: #2196f3;
  background: #e3f2fd;
}

.signal-color-config {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.preview-panel {
  height: 100%;
  border-left: 1px solid #e0e0e0;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
  color: #757575;
}

.preview-widget {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.preview-title {
  font-weight: bold;
  margin-bottom: 16px;
  text-align: center;
}

.mock-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.bars {
  display: flex;
  align-items: end;
  height: 150px;
  gap: 8px;
  padding: 20px;
}

.bar {
  flex: 1;
  min-height: 20px;
  border-radius: 2px;
}

.generic-chart-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #757575;
}

.preview-legend {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-more {
  font-size: 12px;
  color: #757575;
  font-style: italic;
}

/* Responsive design */
@media (max-width: 768px) {
  .wizard-content {
    flex-direction: column;
  }

  .wizard-content .col-8,
  .wizard-content .col-4 {
    width: 100%;
  }

  .equipment-grid {
    grid-template-columns: 1fr;
  }

  .step-item {
    min-width: 60px;
  }

  .step-circle {
    width: 28px;
    height: 28px;
  }

  .step-label {
    font-size: 10px;
  }
}

/* Animation for step transitions */
.step-content {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Loading states */
.q-spinner-dots {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
