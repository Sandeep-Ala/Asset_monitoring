<!-- ui/src/components/MeasurementOverview.vue -->
<template>
  <div class="measurement-overview q-pa-lg">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h5">{{ measurement }}</div>
        <div class="text-subtitle1 text-grey-6">Measurement Schema Overview</div>
      </div>

      <div class="row q-gutter-sm">
        <q-btn
          label="Discover Tags"
          icon="label"
          color="blue"
          outline
          @click="$emit('discover-tags')"
          :disable="tags.length > 0"
        />
        <q-btn
          label="Discover Fields"
          icon="insights"
          color="green"
          outline
          @click="$emit('discover-fields')"
          :disable="fields.length > 0"
        />
        <q-btn
          label="Get Sample"
          icon="preview"
          color="orange"
          outline
          @click="$emit('get-sample')"
          :disable="sampleData.length > 0"
        />
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div class="col-12 col-md-4">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="label" size="2rem" color="blue" class="q-mb-sm" />
            <div class="text-h6">{{ tags.length }}</div>
            <div class="text-caption text-grey-6">Tag Columns</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="insights" size="2rem" color="green" class="q-mb-sm" />
            <div class="text-h6">{{ fields.length }}</div>
            <div class="text-caption text-grey-6">Field Columns</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card flat bordered class="stat-card">
          <q-card-section class="text-center">
            <q-icon name="preview" size="2rem" color="orange" class="q-mb-sm" />
            <div class="text-h6">{{ sampleData.length }}</div>
            <div class="text-caption text-grey-6">Sample Records</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Schema Structure -->
    <div class="row q-gutter-lg">
      <!-- Tags Overview -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-blue-1">
            <div class="text-h6">Tag Columns</div>
            <div class="text-caption">Used for filtering and grouping data</div>
          </q-card-section>

          <q-card-section v-if="tags.length === 0" class="text-center q-pa-lg">
            <q-icon name="label" size="3rem" class="text-grey-4 q-mb-md" />
            <div class="text-h6 text-grey-6">No Tags Discovered</div>
            <div class="text-body2 text-grey-5 q-mb-lg">
              Discover tag columns to see filtering options
            </div>
            <q-btn
              label="Discover Tags"
              color="blue"
              @click="$emit('discover-tags')"
            />
          </q-card-section>

          <q-list v-else separator>
            <q-item v-for="tag in tags.slice(0, 5)" :key="tag">
              <q-item-section avatar>
                <q-avatar color="blue" text-color="white" size="sm">
                  <q-icon name="label" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ tag }}</q-item-label>
                <q-item-label caption>Tag column for filtering</q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-chip color="blue" text-color="white" size="sm">TAG</q-chip>
              </q-item-section>
            </q-item>

            <q-item v-if="tags.length > 5">
              <q-item-section class="text-center">
                <q-btn
                  :label="`View all ${tags.length} tags`"
                  flat
                  color="blue"
                  @click="showAllTags = true"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <!-- Fields Overview -->
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="bg-green-1">
            <div class="text-h6">Field Columns</div>
            <div class="text-caption">Contain measurement values and data</div>
          </q-card-section>

          <q-card-section v-if="fields.length === 0" class="text-center q-pa-lg">
            <q-icon name="insights" size="3rem" class="text-grey-4 q-mb-md" />
            <div class="text-h6 text-grey-6">No Fields Discovered</div>
            <div class="text-body2 text-grey-5 q-mb-lg">
              Discover field columns to see available measurements
            </div>
            <q-btn
              label="Discover Fields"
              color="green"
              @click="$emit('discover-fields')"
            />
          </q-card-section>

          <q-list v-else separator>
            <q-item v-for="field in fields.slice(0, 5)" :key="field.name || field">
              <q-item-section avatar>
                <q-avatar color="green" text-color="white" size="sm">
                  <q-icon name="insights" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ field.name || field }}</q-item-label>
                <q-item-label caption>
                  {{ field.type || 'Unknown type' }} •
                  {{ field.description || 'Measurement field' }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-chip color="green" text-color="white" size="sm">FIELD</q-chip>
              </q-item-section>
            </q-item>

            <q-item v-if="fields.length > 5">
              <q-item-section class="text-center">
                <q-btn
                  :label="`View all ${fields.length} fields`"
                  flat
                  color="green"
                  @click="showAllFields = true"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <!-- Sample Data Preview -->
    <div v-if="sampleData.length > 0" class="q-mt-lg">
      <q-card flat bordered>
        <q-card-section class="bg-orange-1">
          <div class="row items-center justify-between">
            <div>
              <div class="text-h6">Sample Data</div>
              <div class="text-caption">Preview of actual data from this measurement</div>
            </div>
            <q-btn
              label="View Full Sample"
              icon="open_in_full"
              color="orange"
              outline
              size="sm"
              @click="showFullSample = true"
            />
          </div>
        </q-card-section>

        <q-card-section>
          <SampleDataTable
            :data="sampleData.slice(0, 3)"
            :compact="true"
          />

          <div v-if="sampleData.length > 3" class="text-center q-mt-md">
            <q-btn
              :label="`View all ${sampleData.length} records`"
              flat
              color="orange"
              @click="showFullSample = true"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Data Quality Insights -->
    <div v-if="tags.length > 0 || fields.length > 0" class="q-mt-lg">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Data Quality Insights</div>

          <div class="row q-gutter-md">
            <!-- Completeness -->
            <div class="col-12 col-md-4">
              <q-card flat bordered class="bg-blue-1">
                <q-card-section class="text-center">
                  <q-circular-progress
                    :value="dataCompleteness"
                    size="60px"
                    :thickness="0.2"
                    color="blue"
                    track-color="grey-3"
                    class="q-mb-sm"
                  >
                    {{ Math.round(dataCompleteness) }}%
                  </q-circular-progress>
                  <div class="text-subtitle2">Data Completeness</div>
                  <div class="text-caption text-grey-6">Schema coverage</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Mapping Potential -->
            <div class="col-12 col-md-4">
              <q-card flat bordered class="bg-green-1">
                <q-card-section class="text-center">
                  <q-circular-progress
                    :value="mappingPotential"
                    size="60px"
                    :thickness="0.2"
                    color="green"
                    track-color="grey-3"
                    class="q-mb-sm"
                  >
                    {{ Math.round(mappingPotential) }}%
                  </q-circular-progress>
                  <div class="text-subtitle2">Mapping Potential</div>
                  <div class="text-caption text-grey-6">Auto-map readiness</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Data Richness -->
            <div class="col-12 col-md-4">
              <q-card flat bordered class="bg-orange-1">
                <q-card-section class="text-center">
                  <q-circular-progress
                    :value="dataRichness"
                    size="60px"
                    :thickness="0.2"
                    color="orange"
                    track-color="grey-3"
                    class="q-mb-sm"
                  >
                    {{ Math.round(dataRichness) }}%
                  </q-circular-progress>
                  <div class="text-subtitle2">Data Richness</div>
                  <div class="text-caption text-grey-6">Information density</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations.length > 0" class="q-mt-lg">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Recommendations</div>

          <q-list>
            <q-item
              v-for="(recommendation, index) in recommendations"
              :key="index"
              class="recommendation-item"
            >
              <q-item-section avatar>
                <q-icon
                  :name="recommendation.icon"
                  :color="recommendation.color"
                  size="md"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-subtitle2">{{ recommendation.title }}</q-item-label>
                <q-item-label caption>{{ recommendation.description }}</q-item-label>
              </q-item-section>

              <q-item-section side v-if="recommendation.action">
                <q-btn
                  :label="recommendation.action.label"
                  :icon="recommendation.action.icon"
                  :color="recommendation.color"
                  outline
                  size="sm"
                  @click="handleRecommendationAction(recommendation)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <!-- All Tags Dialog -->
    <q-dialog v-model="showAllTags">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">All Tag Columns</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="tagSearchQuery"
            placeholder="Search tags..."
            outlined
            dense
            clearable
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-list class="q-mt-md" separator>
            <q-item v-for="tag in filteredTags" :key="tag">
              <q-item-section avatar>
                <q-icon name="label" color="blue" />
              </q-item-section>
              <q-item-section>{{ tag }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showAllTags = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- All Fields Dialog -->
    <q-dialog v-model="showAllFields">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">All Field Columns</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="fieldSearchQuery"
            placeholder="Search fields..."
            outlined
            dense
            clearable
          >
            <template #prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <q-list class="q-mt-md" separator>
            <q-item v-for="field in filteredFields" :key="field.name || field">
              <q-item-section avatar>
                <q-icon name="insights" color="green" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ field.name || field }}</q-item-label>
                <q-item-label caption>{{ field.type || 'Unknown type' }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Close" flat @click="showAllFields = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Full Sample Dialog -->
    <q-dialog v-model="showFullSample" maximized>
      <q-card>
        <q-card-section class="bg-orange text-white">
          <div class="row items-center">
            <div class="col">
              <div class="text-h6">Sample Data - {{ measurement }}</div>
              <div class="text-subtitle2">{{ sampleData.length }} records</div>
            </div>
            <div class="col-auto">
              <q-btn icon="close" flat round @click="showFullSample = false" />
            </div>
          </div>
        </q-card-section>

        <q-card-section>
          <SampleDataTable
            :data="sampleData"
            :compact="false"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Import sub-components
import SampleDataTable from 'src/components/SampleDataTable.vue'

// Props
const props = defineProps({
  measurement: String,
  tags: Array,
  fields: Array,
  sampleData: Array
})

// Emits
const emit = defineEmits(['discover-tags', 'discover-fields', 'get-sample'])

// Reactive data
const showAllTags = ref(false)
const showAllFields = ref(false)
const showFullSample = ref(false)
const tagSearchQuery = ref('')
const fieldSearchQuery = ref('')

// Computed properties
const dataCompleteness = computed(() => {
  const hasBasicData = props.tags.length > 0 && props.fields.length > 0
  const hasSampleData = props.sampleData.length > 0

  if (hasBasicData && hasSampleData) return 100
  if (hasBasicData) return 75
  if (props.tags.length > 0 || props.fields.length > 0) return 50
  return 25
})

const mappingPotential = computed(() => {
  const tagScore = Math.min(props.tags.length * 10, 50)
  const fieldScore = Math.min(props.fields.length * 5, 50)
  return tagScore + fieldScore
})

const dataRichness = computed(() => {
  const columnCount = props.tags.length + props.fields.length
  const sampleScore = props.sampleData.length > 0 ? 30 : 0
  const columnScore = Math.min(columnCount * 5, 70)
  return sampleScore + columnScore
})

const recommendations = computed(() => {
  const recs = []

  if (props.tags.length === 0) {
    recs.push({
      title: 'Discover Tag Columns',
      description: 'Find tag columns for better data filtering and organization',
      icon: 'label',
      color: 'blue',
      action: {
        label: 'Discover',
        icon: 'search'
      },
      type: 'discover-tags'
    })
  }

  if (props.fields.length === 0) {
    recs.push({
      title: 'Discover Field Columns',
      description: 'Find measurement fields to understand available data',
      icon: 'insights',
      color: 'green',
      action: {
        label: 'Discover',
        icon: 'search'
      },
      type: 'discover-fields'
    })
  }

  if (props.sampleData.length === 0 && props.fields.length > 0) {
    recs.push({
      title: 'Get Sample Data',
      description: 'Preview actual data to understand structure and quality',
      icon: 'preview',
      color: 'orange',
      action: {
        label: 'Get Sample',
        icon: 'preview'
      },
      type: 'get-sample'
    })
  }

  if (props.tags.length > 0 && props.fields.length > 0) {
    recs.push({
      title: 'Create Equipment Mapping',
      description: 'Connect this measurement to equipment for monitoring',
      icon: 'link',
      color: 'positive',
      action: {
        label: 'Create Mapping',
        icon: 'add'
      },
      type: 'create-mapping'
    })
  }

  return recs
})

const filteredTags = computed(() => {
  if (!tagSearchQuery.value) return props.tags

  const query = tagSearchQuery.value.toLowerCase()
  return props.tags.filter(tag => tag.toLowerCase().includes(query))
})

const filteredFields = computed(() => {
  if (!fieldSearchQuery.value) return props.fields

  const query = fieldSearchQuery.value.toLowerCase()
  return props.fields.filter(field => {
    const name = field.name || field
    return name.toLowerCase().includes(query)
  })
})

// Methods
const handleRecommendationAction = (recommendation) => {
  switch (recommendation.type) {
    case 'discover-tags':
      emit('discover-tags')
      break
    case 'discover-fields':
      emit('discover-fields')
      break
    case 'get-sample':
      emit('get-sample')
      break
    case 'create-mapping':
      // This would typically emit an event to parent
      console.log('Create mapping action')
      break
  }
}
</script>

<style scoped>
.measurement-overview {
  background-color: #fafafa;
  min-height: 100%;
}

.stat-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.bg-blue-1 {
  background-color: rgba(25, 118, 210, 0.1);
}

.bg-green-1 {
  background-color: rgba(76, 175, 80, 0.1);
}

.bg-orange-1 {
  background-color: rgba(255, 152, 0, 0.1);
}

.recommendation-item {
  border-radius: 8px;
  margin-bottom: 8px;
  background-color: rgba(0, 0, 0, 0.02);
}

.recommendation-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.q-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.q-chip {
  font-weight: 500;
}

/* Custom scrollbar for dialogs */
.q-list {
  max-height: 400px;
  overflow-y: auto;
}

.q-list::-webkit-scrollbar {
  width: 6px;
}

.q-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.q-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.q-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
