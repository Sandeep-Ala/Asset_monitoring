<!-- src/components/SchemaPreview.vue -->
<template>
  <div class="schema-preview">
    <div v-if="!schema.measurements.length" class="text-center q-pa-xl">
      <q-icon name="search" size="4rem" class="text-grey-4 q-mb-md" />
      <div class="text-h6 text-grey-6 q-mb-sm">No Schema Discovered</div>
      <div class="text-body2 text-grey-5">
        Click refresh to discover schema from your data source
      </div>
    </div>

    <div v-else>
      <!-- Schema Overview Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-4">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">{{ schema.measurements.length }}</div>
              <div class="text-subtitle2 text-grey-6">Measurements</div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">{{ totalTags }}</div>
              <div class="text-subtitle2 text-grey-6">Total Tags</div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">{{ totalFields }}</div>
              <div class="text-subtitle2 text-grey-6">Total Fields</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Measurements List -->
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Discovered Measurements</div>

          <q-list>
            <q-item
              v-for="measurement in schema.measurements"
              :key="measurement"
              clickable
              @click="viewMeasurement(measurement)"
            >
              <q-item-section avatar>
                <q-icon name="table_chart" color="primary" />
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ measurement }}</q-item-label>
                <q-item-label caption>
                  {{ getTagCount(measurement) }} tags, {{ getFieldCount(measurement) }} fields
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-btn
                  icon="visibility"
                  flat
                  round
                  size="sm"
                  @click.stop="viewMeasurement(measurement)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            label="Refresh"
            icon="refresh"
            color="primary"
            outline
            @click="$emit('refresh')"
            :loading="loading"
          />
        </q-card-actions>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  schema: {
    type: Object,
    default: () => ({
      measurements: [],
      tags: {},
      fields: {}
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh', 'view-measurement'])

// Computed properties
const totalTags = computed(() => {
  return Object.values(props.schema.tags || {}).reduce((total, tags) => {
    return total + (Array.isArray(tags) ? tags.length : 0)
  }, 0)
})

const totalFields = computed(() => {
  return Object.values(props.schema.fields || {}).reduce((total, fields) => {
    return total + (Array.isArray(fields) ? fields.length : 0)
  }, 0)
})

// Methods
const getTagCount = (measurement) => {
  const tags = props.schema.tags?.[measurement]
  return Array.isArray(tags) ? tags.length : 0
}

const getFieldCount = (measurement) => {
  const fields = props.schema.fields?.[measurement]
  return Array.isArray(fields) ? fields.length : 0
}

const viewMeasurement = (measurement) => {
  emit('view-measurement', measurement)
}
</script>
