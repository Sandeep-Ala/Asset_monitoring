<!-- ui/src/components/SchemaQuality.vue -->
<!-- Schema quality assessment component - Enhanced version -->

<template>
  <div class="schema-quality">
    <!-- Quality Assessment Header -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-gradient-primary text-white">
            <div class="row items-center justify-between">
              <div>
                <div class="text-h6 q-mb-xs">
                  <q-icon name="verified" class="q-mr-sm" />
                  Schema Quality Assessment
                </div>
                <div class="text-body2 opacity-80">
                  Comprehensive data quality analysis and monitoring
                </div>
              </div>
              <div class="text-center">
                <q-circular-progress
                  :value="overallQualityScore"
                  size="80px"
                  :thickness="0.12"
                  color="white"
                  track-color="rgba(255,255,255,0.3)"
                  show-value
                  font-size="18px"
                  class="text-white"
                />
                <div class="text-caption q-mt-xs">Overall Score</div>
              </div>
            </div>
          </q-card-section>

          <!-- Quick Controls -->
          <q-card-section class="q-pt-md">
            <div class="row q-gutter-md items-end">
              <div class="col-12 col-md-3">
                <q-select
                  v-model="assessmentScope"
                  :options="scopeOptions"
                  label="Assessment Scope"
                  outlined
                  dense
                  @update:model-value="onScopeChange"
                />
              </div>

              <div class="col-12 col-md-4">
                <q-select
                  v-model="selectedDimensions"
                  :options="dimensionOptions"
                  label="Quality Dimensions"
                  multiple
                  use-chips
                  outlined
                  dense
                  @update:model-value="onDimensionsChange"
                />
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="severityFilter"
                  :options="severityFilterOptions"
                  label="Issue Severity"
                  outlined
                  dense
                  @update:model-value="onSeverityChange"
                />
              </div>

              <div class="col-12 col-md-2">
                <q-btn
                  label="Run Assessment"
                  icon="play_arrow"
                  color="primary"
                  class="full-width"
                  @click="runQualityAssessment"
                  :loading="isAssessing"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Quality Dimensions Dashboard -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">
              <q-icon name="dashboard" class="q-mr-sm" />
              Quality Dimensions
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="!hasAssessmentData" class="text-center q-pa-xl">
              <q-icon name="assessment" size="4rem" class="text-grey-4 q-mb-md" />
              <div class="text-h6 text-grey-6">No Assessment Data</div>
              <div class="text-body2 text-grey-5 q-mb-lg">
                Run a quality assessment to see detailed quality metrics
              </div>
              <q-btn
                label="Start Assessment"
                icon="play_arrow"
                color="primary"
                size="lg"
                @click="runQualityAssessment"
                :loading="isAssessing"
              />
            </div>

            <div v-else class="row q-gutter-md">
              <div
                v-for="dimension in qualityDimensions"
                :key="dimension.id"
                class="col-12 col-sm-6 col-md-4 col-lg-3"
              >
                <q-card
                  flat
                  :class="getDimensionCardClass(dimension.score)"
                  @click="showDimensionDetails(dimension)"
                  style="cursor: pointer"
                >
                  <q-card-section class="text-center q-pb-sm">
                    <q-icon :name="dimension.icon" size="2rem" :color="getDimensionColor(dimension.score)" />
                    <div class="text-h6 q-mt-sm">{{ dimension.name }}</div>
                  </q-card-section>

                  <q-card-section class="text-center q-pt-none">
                    <q-circular-progress
                      :value="dimension.score"
                      size="60px"
                      :thickness="0.15"
                      :color="getDimensionColor(dimension.score)"
                      track-color="grey-3"
                      show-value
                      font-size="14px"
                    />
                    <div class="text-caption q-mt-sm text-grey-6">
                      {{ dimension.description }}
                    </div>
                  </q-card-section>

                  <q-card-section class="q-pt-none">
                    <div class="row items-center justify-between">
                      <q-chip
                        :color="getDimensionColor(dimension.score)"
                        text-color="white"
                        size="sm"
                      >
                        {{ getScoreGrade(dimension.score) }}
                      </q-chip>
                      <div class="text-caption text-grey-6">
                        {{ dimension.issueCount }} issues
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Issues Management -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-orange-1">
            <div class="row items-center justify-between">
              <div class="text-h6">
                <q-icon name="warning" class="q-mr-sm" />
                Quality Issues ({{ filteredIssues.length }})
              </div>
              <div class="q-gutter-sm">
                <q-btn
                  label="Fix All Critical"
                  icon="build"
                  color="negative"
                  size="sm"
                  outline
                  @click="fixCriticalIssues"
                  :loading="isBulkFixing"
                  :disable="!hasCriticalIssues"
                />
                <q-btn
                  label="Export Report"
                  icon="download"
                  color="primary"
                  size="sm"
                  outline
                  @click="exportQualityReport"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <div v-if="filteredIssues.length === 0" class="text-center q-pa-xl">
              <q-icon name="check_circle" size="3rem" color="positive" class="q-mb-md" />
              <div class="text-h6 text-positive">No Quality Issues Found</div>
              <div class="text-body2 text-grey-6">
                {{ severityFilter === 'all' ? 'Your schema meets all quality standards' : 'No issues match the current filter' }}
              </div>
            </div>

            <q-table
              v-else
              :rows="filteredIssues"
              :columns="issueColumns"
              row-key="id"
              flat
              :pagination="issuesPagination"
              :loading="isAssessing"
              @row-click="viewIssueDetails"
            >
              <template #top>
                <div class="row full-width items-center q-gutter-md">
                  <q-input
                    v-model="issueSearchQuery"
                    placeholder="Search issues..."
                    dense
                    clearable
                    class="col-grow"
                  >
                    <template #prepend>
                      <q-icon name="search" />
                    </template>
                  </q-input>

                  <q-btn-toggle
                    v-model="issueViewMode"
                    :options="viewModeOptions"
                    size="sm"
                    color="primary"
                    outline
                  />
                </div>
              </template>

              <template #body-cell-severity="props">
                <q-td :props="props">
                  <q-chip
                    :color="getSeverityColor(props.value)"
                    text-color="white"
                    size="sm"
                    :icon="getSeverityIcon(props.value)"
                  >
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>

              <template #body-cell-category="props">
                <q-td :props="props">
                  <q-chip
                    :color="getCategoryColor(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>

              <template #body-cell-status="props">
                <q-td :props="props">
                  <q-badge
                    :color="getStatusColor(props.value)"
                    :label="props.value"
                  />
                </q-td>
              </template>

              <template #body-cell-actions="props">
                <q-td :props="props">
                  <div class="q-gutter-xs">
                    <q-btn
                      icon="visibility"
                      flat
                      round
                      size="sm"
                      @click.stop="viewIssueDetails(props.row)"
                    >
                      <q-tooltip>View Details</q-tooltip>
                    </q-btn>

                    <q-btn
                      v-if="props.row.canAutoFix"
                      icon="auto_fix_high"
                      flat
                      round
                      size="sm"
                      color="primary"
                      @click.stop="autoFixIssue(props.row)"
                      :loading="fixingIssues.includes(props.row.id)"
                    >
                      <q-tooltip>Auto Fix</q-tooltip>
                    </q-btn>

                    <q-btn
                      icon="build"
                      flat
                      round
                      size="sm"
                      color="secondary"
                      @click.stop="manualFixIssue(props.row)"
                      :loading="fixingIssues.includes(props.row.id)"
                    >
                      <q-tooltip>Manual Fix</q-tooltip>
                    </q-btn>

                    <q-btn
                      icon="schedule"
                      flat
                      round
                      size="sm"
                      color="warning"
                      @click.stop="scheduleIssue(props.row)"
                    >
                      <q-tooltip>Schedule Fix</q-tooltip>
                    </q-btn>

                    <q-btn
                      icon="visibility_off"
                      flat
                      round
                      size="sm"
                      color="grey"
                      @click.stop="ignoreIssue(props.row)"
                    >
                      <q-tooltip>Ignore</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Quality Analytics -->
    <div class="row q-gutter-md q-mb-lg">
      <!-- Quality Trends -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">
              <q-icon name="trending_up" class="q-mr-sm" />
              Quality Trends
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="qualityTrends.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="timeline" size="2rem" class="q-mb-sm" />
              <div>No trend data available</div>
              <div class="text-caption">Run multiple assessments to see trends</div>
            </div>

            <div v-else>
              <div v-for="trend in qualityTrends" :key="trend.dimension" class="q-mb-lg">
                <div class="row items-center q-gutter-sm q-mb-sm">
                  <q-icon :name="getDimensionIcon(trend.dimension)" color="primary" />
                  <div class="text-subtitle2">{{ trend.dimension }}</div>
                  <q-space />
                  <q-chip
                    :color="getTrendColor(trend.direction)"
                    text-color="white"
                    size="sm"
                    :icon="getTrendIcon(trend.direction)"
                  >
                    {{ trend.change }}%
                  </q-chip>
                </div>

                <q-linear-progress
                  :value="trend.currentScore / 100"
                  :color="getDimensionColor(trend.currentScore)"
                  size="12px"
                  class="q-mb-xs"
                />

                <div class="text-caption text-grey-6">
                  {{ trend.description }}
                </div>

                <div class="row q-gutter-xs q-mt-sm">
                  <q-chip
                    v-for="period in trend.periods"
                    :key="period.label"
                    size="xs"
                    outline
                    :color="getDimensionColor(period.score)"
                  >
                    {{ period.label }}: {{ period.score }}%
                  </q-chip>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Recommendations Engine -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-purple-1">
            <div class="row items-center justify-between">
              <div class="text-h6">
                <q-icon name="lightbulb" class="q-mr-sm" />
                Smart Recommendations
              </div>
              <q-btn
                icon="refresh"
                flat
                round
                size="sm"
                @click="refreshRecommendations"
                :loading="isGeneratingRecommendations"
              />
            </div>
          </q-card-section>
          <q-card-section>
            <div v-if="smartRecommendations.length === 0" class="text-center q-pa-md text-grey-6">
              <q-icon name="psychology" size="2rem" class="q-mb-sm" />
              <div>No recommendations available</div>
              <div class="text-caption">AI-powered suggestions will appear here</div>
            </div>

            <q-list v-else>
              <q-item
                v-for="recommendation in smartRecommendations"
                :key="recommendation.id"
                clickable
                @click="viewRecommendationDetails(recommendation)"
              >
                <q-item-section avatar>
                  <q-avatar
                    :color="getRecommendationColor(recommendation.priority)"
                    text-color="white"
                    :icon="getRecommendationIcon(recommendation.type)"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ recommendation.title }}</q-item-label>
                  <q-item-label caption>{{ recommendation.description }}</q-item-label>
                  <q-item-label caption class="q-mt-xs">
                    <q-chip size="xs" :color="getImpactColor(recommendation.impact)" text-color="white">
                      {{ recommendation.impact }} Impact
                    </q-chip>
                    <q-chip size="xs" color="grey-6" text-color="white" class="q-ml-xs">
                      {{ recommendation.effort }} Effort
                    </q-chip>
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="column q-gutter-xs">
                    <q-btn
                      label="Apply"
                      size="sm"
                      :color="getRecommendationColor(recommendation.priority)"
                      @click.stop="applyRecommendation(recommendation)"
                      :loading="applyingRecommendations.includes(recommendation.id)"
                    />
                    <div class="text-caption text-center">
                      {{ recommendation.confidence }}% confidence
                    </div>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Detailed Quality Metrics -->
    <div class="row q-gutter-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section class="bg-teal-1">
            <div class="row items-center justify-between">
              <div class="text-h6">
                <q-icon name="analytics" class="q-mr-sm" />
                Detailed Quality Metrics by Measurement
              </div>
              <q-btn-toggle
                v-model="metricsViewMode"
                :options="metricsViewOptions"
                size="sm"
                color="primary"
                outline
              />
            </div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <q-table
              :rows="detailedMetrics"
              :columns="metricsColumns"
              row-key="measurement"
              flat
              :pagination="metricsPagination"
              :visible-columns="visibleMetricsColumns"
            >
              <template #body-cell-measurement="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-avatar size="sm" color="primary" text-color="white">
                      <q-icon name="table_chart" />
                    </q-avatar>
                    <div>
                      <div class="text-body2">{{ props.value }}</div>
                      <div class="text-caption text-grey-6">
                        {{ getMeasurementInfo(props.row).fieldCount }} fields
                      </div>
                    </div>
                  </div>
                </q-td>
              </template>

              <template #body-cell-completeness="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-circular-progress
                      :value="props.value"
                      size="30px"
                      :thickness="0.15"
                      :color="getDimensionColor(props.value)"
                      track-color="grey-3"
                      show-value
                      font-size="10px"
                    />
                    <div class="text-caption">{{ props.value }}%</div>
                  </div>
                </q-td>
              </template>

              <template #body-cell-accuracy="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-circular-progress
                      :value="props.value"
                      size="30px"
                      :thickness="0.15"
                      :color="getDimensionColor(props.value)"
                      track-color="grey-3"
                      show-value
                      font-size="10px"
                    />
                    <div class="text-caption">{{ props.value }}%</div>
                  </div>
                </q-td>
              </template>

              <template #body-cell-consistency="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-circular-progress
                      :value="props.value"
                      size="30px"
                      :thickness="0.15"
                      :color="getDimensionColor(props.value)"
                      track-color="grey-3"
                      show-value
                      font-size="10px"
                    />
                    <div class="text-caption">{{ props.value }}%</div>
                  </div>
                </q-td>
              </template>

              <template #body-cell-validity="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-sm">
                    <q-circular-progress
                      :value="props.value"
                      size="30px"
                      :thickness="0.15"
                      :color="getDimensionColor(props.value)"
                      track-color="grey-3"
                      show-value
                      font-size="10px"
                    />
                    <div class="text-caption">{{ props.value }}%</div>
                  </div>
                </q-td>
              </template>

              <template #body-cell-overallScore="props">
                <q-td :props="props">
                  <q-chip
                    :color="getDimensionColor(props.value)"
                    text-color="white"
                    size="sm"
                  >
                    {{ props.value }}% - {{ getScoreGrade(props.value) }}
                  </q-chip>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Issue Details Dialog -->
    <q-dialog v-model="showIssueDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Issue Details</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showIssueDialog = false" />
        </q-card-section>

        <q-card-section class="scroll" v-if="selectedIssue">
          <div class="row q-gutter-md">
            <!-- Issue Overview -->
            <div class="col-12 col-md-6">
              <q-card flat bordered>
                <q-card-section class="bg-blue-1">
                  <div class="text-subtitle1">Issue Overview</div>
                </q-card-section>
                <q-card-section>
                  <q-list dense>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Title</q-item-label>
                        <q-item-label>{{ selectedIssue.title }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Description</q-item-label>
                        <q-item-label>{{ selectedIssue.description }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Severity</q-item-label>
                        <q-item-label>
                          <q-chip
                            :color="getSeverityColor(selectedIssue.severity)"
                            text-color="white"
                            :icon="getSeverityIcon(selectedIssue.severity)"
                          >
                            {{ selectedIssue.severity }}
                          </q-chip>
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Category</q-item-label>
                        <q-item-label>{{ selectedIssue.category }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Affected Measurement</q-item-label>
                        <q-item-label>{{ selectedIssue.measurement }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Impact</q-item-label>
                        <q-item-label>{{ selectedIssue.impact }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Resolution Guide -->
            <div class="col-12 col-md-6">
              <q-card flat bordered>
                <q-card-section class="bg-green-1">
                  <div class="text-subtitle1">Resolution Guide</div>
                </q-card-section>
                <q-card-section>
                  <q-stepper
                    v-model="resolutionStep"
                    vertical
                    color="primary"
                    animated
                  >
                    <q-step
                      v-for="(step, index) in selectedIssue.resolutionSteps"
                      :key="index"
                      :name="index + 1"
                      :title="`Step ${index + 1}`"
                      :icon="index === 0 ? 'play_arrow' : index + 1 <= resolutionStep ? 'check' : 'schedule'"
                      :done="index + 1 < resolutionStep"
                    >
                      <div>{{ step }}</div>

                      <q-stepper-navigation>
                        <q-btn
                          v-if="index < selectedIssue.resolutionSteps.length - 1"
                          @click="resolutionStep = index + 2"
                          color="primary"
                          label="Next"
                        />
                        <q-btn
                          v-if="index > 0"
                          flat
                          color="primary"
                          @click="resolutionStep = index"
                          label="Back"
                          class="q-ml-sm"
                        />
                      </q-stepper-navigation>
                    </q-step>
                  </q-stepper>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showIssueDialog = false" />
          <q-btn
            v-if="selectedIssue?.canAutoFix"
            label="Auto Fix"
            color="primary"
            @click="autoFixSelectedIssue"
            :loading="fixingIssues.includes(selectedIssue?.id)"
          />
          <q-btn
            label="Manual Fix"
            color="secondary"
            @click="manualFixSelectedIssue"
            :loading="fixingIssues.includes(selectedIssue?.id)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dimension Details Dialog -->
    <q-dialog v-model="showDimensionDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ selectedDimension?.name }} Quality Details</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showDimensionDialog = false" />
        </q-card-section>

        <q-card-section class="scroll" v-if="selectedDimension">
          <!-- Dimension details content would go here -->
          <div class="text-center q-pa-xl">
            <q-icon :name="selectedDimension.icon" size="4rem" class="text-grey-4 q-mb-md" />
            <div class="text-h5 text-grey-6">{{ selectedDimension.name }} Analysis</div>
            <div class="text-body1 text-grey-5">
              Detailed {{ selectedDimension.name.toLowerCase() }} quality analysis and recommendations
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  schema: {
    type: Object,
    default: null
  },
  qualityMetrics: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['run-quality-check', 'fix-quality-issue'])

// Reactive data
const $q = useQuasar()
const assessmentScope = ref('all')
const selectedDimensions = ref(['completeness', 'accuracy', 'consistency', 'validity'])
const severityFilter = ref('all')
const assessing = ref(false)
const refreshing = ref(false)
const showIssueDialog = ref(false)
const selectedIssue = ref(null)
const fixingIssues = ref([])

const overallScore = ref(85)
const qualityIssues = ref([])
const qualityDimensions = ref([])
const qualityTrends = ref([])
const qualityRecommendations = ref([])
const detailedMetrics = ref([])

// Computed properties
const scopeOptions = [
  { label: 'All Measurements', value: 'all' },
  { label: 'Current Selection', value: 'selected' },
  { label: 'Critical Only', value: 'critical' },
  { label: 'Recent Changes', value: 'recent' }
]

const dimensionOptions = [
  { label: 'Completeness', value: 'completeness' },
  { label: 'Accuracy', value: 'accuracy' },
  { label: 'Consistency', value: 'consistency' },
  { label: 'Validity', value: 'validity' },
  { label: 'Uniqueness', value: 'uniqueness' },
  { label: 'Timeliness', value: 'timeliness' }
]

const severityOptions = [
  { label: 'All Issues', value: 'all' },
  { label: 'Critical Only', value: 'critical' },
  { label: 'High & Critical', value: 'high_critical' },
  { label: 'Medium & Above', value: 'medium_above' }
]

const filteredIssues = computed(() => {
  if (severityFilter.value === 'all') return qualityIssues.value

  const severityMap = {
    critical: ['Critical'],
    high_critical: ['Critical', 'High'],
    medium_above: ['Critical', 'High', 'Medium']
  }

  const allowedSeverities = severityMap[severityFilter.value] || []
  return qualityIssues.value.filter(issue => allowedSeverities.includes(issue.severity))
})

const issueColumns = [
  {
    name: 'severity',
    label: 'Severity',
    field: 'severity',
    align: 'center',
    sortable: true
  },
  {
    name: 'category',
    label: 'Category',
    field: 'category',
    align: 'center',
    sortable: true
  },
  {
    name: 'title',
    label: 'Issue',
    field: 'title',
    align: 'left',
    sortable: true
  },
  {
    name: 'measurement',
    label: 'Measurement',
    field: 'measurement',
    align: 'left',
    sortable: true
  },
  {
    name: 'impact',
    label: 'Impact',
    field: 'impact',
    align: 'left',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Actions',
    field: 'actions',
    align: 'center'
  }
]

const metricsColumns = [
  {
    name: 'measurement',
    label: 'Measurement',
    field: 'measurement',
    align: 'left',
    sortable: true
  },
  {
    name: 'completeness',
    label: 'Completeness',
    field: 'completeness',
    align: 'center',
    sortable: true
  },
  {
    name: 'accuracy',
    label: 'Accuracy',
    field: 'accuracy',
    align: 'center',
    sortable: true
  },
  {
    name: 'consistency',
    label: 'Consistency',
    field: 'consistency',
    align: 'center',
    sortable: true
  },
  {
    name: 'validity',
    label: 'Validity',
    field: 'validity',
    align: 'center',
    sortable: true
  }
]

// Methods
const getScoreColor = (score) => {
  if (score >= 90) return 'positive'
  if (score >= 70) return 'warning'
  return 'negative'
}

const getScoreGrade = (score) => {
  if (score >= 90) return 'Excellent'
  if (score >= 80) return 'Good'
  if (score >= 70) return 'Fair'
  if (score >= 60) return 'Poor'
  return 'Critical'
}

const getSeverityColor = (severity) => {
  const colors = {
    Critical: 'negative',
    High: 'red',
    Medium: 'warning',
    Low: 'info'
  }
  return colors[severity] || 'grey'
}

const getSeverityIcon = (severity) => {
  const icons = {
    Critical: 'error',
    High: 'warning',
    Medium: 'info',
    Low: 'help'
  }
  return icons[severity] || 'help'
}

const getCategoryColor = (category) => {
  const colors = {
    'Data Completeness': 'blue',
    'Data Accuracy': 'green',
    'Data Consistency': 'orange',
    'Data Validity': 'purple',
    'Schema Structure': 'teal'
  }
  return colors[category] || 'grey'
}

const getTrendColor = (direction) => {
  const colors = {
    improving: 'positive',
    declining: 'negative',
    stable: 'info'
  }
  return colors[direction] || 'grey'
}

const getTrendIcon = (direction) => {
  const icons = {
    improving: 'trending_up',
    declining: 'trending_down',
    stable: 'trending_flat'
  }
  return icons[direction] || 'help'
}

const getRecommendationIcon = (type) => {
  const icons = {
    validation: 'verified',
    cleanup: 'cleaning_services',
    structure: 'account_tree',
    performance: 'speed'
  }
  return icons[type] || 'lightbulb'
}

const getRecommendationColor = (priority) => {
  const colors = {
    High: 'negative',
    Medium: 'warning',
    Low: 'info'
  }
  return colors[priority] || 'grey'
}

const updateAssessment = () => {
  // Trigger assessment update when parameters change
  if (qualityDimensions.value.length > 0) {
    runQualityCheck()
  }
}

const filterIssues = () => {
  // Filtering is handled by computed property
}

const runQualityCheck = async () => {
  assessing.value = true

  try {
    // Simulate quality assessment
    await new Promise(resolve => setTimeout(resolve, 4000))

    // Generate quality dimensions
    qualityDimensions.value = selectedDimensions.value.map(dimension => {
      const scores = {
        completeness: 92,
        accuracy: 88,
        consistency: 85,
        validity: 78,
        uniqueness: 95,
        timeliness: 82
      }

      const descriptions = {
        completeness: 'Data presence',
        accuracy: 'Data correctness',
        consistency: 'Data uniformity',
        validity: 'Data conformity',
        uniqueness: 'Data distinctness',
        timeliness: 'Data freshness'
      }

      return {
        name: dimension.charAt(0).toUpperCase() + dimension.slice(1),
        score: scores[dimension] || Math.floor(Math.random() * 30 + 70),
        description: descriptions[dimension] || 'Data quality metric'
      }
    })

    // Calculate overall score
    const avgScore = qualityDimensions.value.reduce((sum, dim) => sum + dim.score, 0) / qualityDimensions.value.length
    overallScore.value = Math.round(avgScore)

    // Generate quality issues
    qualityIssues.value = [
      {
        id: 1,
        severity: 'High',
        category: 'Data Completeness',
        title: 'Missing timestamp values',
        measurement: 'battery_voltage',
        impact: 'Prevents time-series analysis',
        description: 'Some records lack proper timestamp information',
        resolutionSteps: [
          'Identify records with missing timestamps',
          'Implement timestamp validation rules',
          'Backfill missing timestamps where possible'
        ]
      },
      {
        id: 2,
        severity: 'Medium',
        category: 'Data Validity',
        title: 'Out-of-range voltage values',
        measurement: 'cell_voltage',
        impact: 'May indicate sensor malfunction',
        description: 'Voltage readings exceed expected operational range',
        resolutionSteps: [
          'Review sensor calibration',
          'Set up range validation rules',
          'Flag outlier values for review'
        ]
      },
      {
        id: 3,
        severity: 'Low',
        category: 'Data Consistency',
        title: 'Inconsistent field naming',
        measurement: 'temperature',
        impact: 'Complicates data integration',
        description: 'Temperature fields use different naming conventions',
        resolutionSteps: [
          'Standardize field naming convention',
          'Create mapping documentation',
          'Implement naming validation'
        ]
      }
    ]

    // Generate quality trends
    qualityTrends.value = [
      {
        dimension: 'Completeness',
        currentScore: 92,
        direction: 'improving',
        change: '+3.2',
        description: 'Steady improvement over the last month'
      },
      {
        dimension: 'Accuracy',
        currentScore: 88,
        direction: 'stable',
        change: '+0.5',
        description: 'Maintaining consistent accuracy levels'
      },
      {
        dimension: 'Consistency',
        currentScore: 85,
        direction: 'declining',
        change: '-1.8',
        description: 'Slight decline due to new data sources'
      }
    ]

    // Generate recommendations
    qualityRecommendations.value = [
      {
        id: 1,
        type: 'validation',
        priority: 'High',
        title: 'Implement Data Validation Rules',
        description: 'Add validation rules for critical fields to prevent quality issues'
      },
      {
        id: 2,
        type: 'cleanup',
        priority: 'Medium',
        title: 'Clean Historical Data',
        description: 'Review and clean existing data to improve overall quality scores'
      },
      {
        id: 3,
        type: 'structure',
        priority: 'Low',
        title: 'Standardize Schema',
        description: 'Align field names and types across all measurements'
      }
    ]

    // Generate detailed metrics
    const measurements = props.schema?.measurements || ['battery_voltage', 'cell_voltage', 'temperature']
    detailedMetrics.value = measurements.map(measurement => ({
      measurement,
      completeness: Math.floor(Math.random() * 20 + 80),
      accuracy: Math.floor(Math.random() * 25 + 75),
      consistency: Math.floor(Math.random() * 30 + 70),
      validity: Math.floor(Math.random() * 35 + 65)
    }))

    emit('run-quality-check', {
      scope: assessmentScope.value,
      dimensions: selectedDimensions.value,
      overallScore: overallScore.value,
      issues: qualityIssues.value.length
    })

    $q.notify({
      type: 'positive',
      message: 'Quality assessment completed',
      caption: `Overall score: ${overallScore.value}% - ${qualityIssues.value.length} issues found`
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Quality assessment failed',
      caption: error.message
    })
  } finally {
    assessing.value = false
  }
}

const refreshAssessment = async () => {
  refreshing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    await runQualityCheck()
  } finally {
    refreshing.value = false
  }
}

const viewIssueDetails = (issue) => {
  selectedIssue.value = issue
  showIssueDialog.value = true
}

const fixIssue = async (issue) => {
  fixingIssues.value.push(issue.id)

  try {
    // Simulate fixing issue
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Remove from issues list
    const index = qualityIssues.value.findIndex(i => i.id === issue.id)
    if (index !== -1) {
      qualityIssues.value.splice(index, 1)
    }

    emit('fix-quality-issue', issue)

    $q.notify({
      type: 'positive',
      message: `Fixed: ${issue.title}`,
      caption: 'Quality issue resolved successfully'
    })

  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to fix issue',
      caption: error.message
    })
  } finally {
    fixingIssues.value = fixingIssues.value.filter(id => id !== issue.id)
  }
}

const fixSelectedIssue = () => {
  if (selectedIssue.value) {
    fixIssue(selectedIssue.value)
    showIssueDialog.value = false
  }
}

const ignoreIssue = (issue) => {
  $q.dialog({
    title: 'Ignore Issue',
    message: `Are you sure you want to ignore "${issue.title}"?`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    const index = qualityIssues.value.findIndex(i => i.id === issue.id)
    if (index !== -1) {
      qualityIssues.value.splice(index, 1)
    }

    $q.notify({
      type: 'info',
      message: 'Issue ignored'
    })
  })
}

const applyRecommendation = (recommendation) => {
  $q.notify({
    type: 'info',
    message: `Applying: ${recommendation.title}`,
    caption: 'Implementation details would be shown here'
  })
}

// Lifecycle
onMounted(() => {
  // Auto-run quality check if schema is available
  if (props.schema) {
    runQualityCheck()
  }
})
</script>

<style scoped>
.schema-quality {
  width: 100%;
}

.text-h6 {
  font-weight: 600;
}

.q-chip {
  font-size: 11px;
}

.q-linear-progress {
  border-radius: 4px;
}
</style>
