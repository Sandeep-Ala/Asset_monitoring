<template>
  <div class="q-pa-sm bg-grey-3">
    <div class="q-gutter-sm">
      <div class="text-subtitle1">{{ title || 'New Widget' }}</div>
      <q-btn dense flat icon="lock" @click="$emit('lock')" />
      <q-btn dense flat icon="delete" color="red" @click="$emit('delete')" />
    </div>

    <!-- Hide buttons after data is fetched -->
    <div class="q-mt-sm" v-if="!dataFetched">
      <q-btn-group>
        <q-btn label="Add Graph" @click="mode = 'graph'; dataFetched = false" />
        <q-btn label="Add Table" @click="mode = 'table'" />
        <q-btn label="Add Pie Chart" @click="mode = 'pie'" />
      </q-btn-group>
    </div>

    <!-- Show form only if graph mode and not fetched yet -->
    <div v-if="mode === 'graph' && !dataFetched" class="q-mt-md">
      <q-form @submit.prevent="fetchData">
        <q-input v-model="form.title" label="Widget Title" dense />
        <q-input v-model="form.subtitle" label="Sub-title" dense class="q-mt-sm" />
        <q-select
          v-model="form.container"
          :options="containers"
          label="Container Name"
          dense
          class="q-mt-sm"
        />
        <q-select
          v-model="form.equipment"
          :options="equipments"
          label="Equipment"
          dense
          class="q-mt-sm"
        />
        <div class="q-mt-sm">
          <div class="text-caption text-grey-7">Select Filters</div>

          <q-select
            v-for="(options, key) in filters"
            :key="key"
            v-model="selectedFilters[key]"
            :options="options"
            :label="key"
            dense
            multiple
            emit-value
            map-options
            class="q-mt-xs"
          />
        </div>
        <q-select
          v-model="form.metric"
          :options="metrics"
          label="Metric"
          dense
          class="q-mt-sm"
        />
        <q-btn label="Fetch" type="submit" color="primary" class="q-mt-md" />
      </q-form>
    </div>

    <!-- Show chart only after data is fetched -->
    <div v-if="chartData && dataFetched && mode === 'graph'" class="q-mt-md">
      <Chartrenderer :type="'line'" :data="chartData" :title="form.title" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useGlobalTime } from 'src/composables/globalTime'
import Chartrenderer from 'src/components/ChartRenderer.vue'

const props = defineProps({
  id: Number,
  title: String
})

const emit = defineEmits(['lock', 'delete'])

const mode = ref(null)
const dataFetched = ref(false)

const form = ref({
  title: '',
  subtitle: '',
  container: null,
  equipment: null,
  filter: null,
  metric: null
})
const selectedFilters = ref({
  n_rack: [],
  n_bank: []
})
const containers = Array.from({ length: 16 }, (_, i) => `BC-${i + 1}`)
const equipments = ['rbms', 'hvac', 'bsc', 'bmu', 'ups']
const filters = {
  n_rack: [1, 2, 3, 4],
  n_bank: [1, 2, 3, 4, 5, 6]
}
const metrics = ['soc', 'soh', 'n_soc', 'n_soh']

const chartData = ref(null)
const { globalTime } = useGlobalTime()

watch(globalTime, () => {
  if (mode.value === 'graph' && dataFetched.value) {
    fetchData()
  }
})

async function fetchData() {
  if (!form.value.metric || !form.value.container || !form.value.equipment) {
    console.warn('Incomplete form data')
    return
  }

  const payload = {
    year: new Date(globalTime.value.start).getFullYear(),
    month: null,
    equipment: form.value.equipment,
    day: null,
    dcu: parseInt(form.value.container.replace('BC-', '')),
    start_time: globalTime.value.start,
    end_time: globalTime.value.end,
    metrics: [form.value.metric],
    window_period: '1 hour',
    where_args: Object.entries(selectedFilters.value)
    .flatMap(([key, values]) => values.map(val => `${key}=${val}`))
  }

  try {
    const response = await axios.post('http://localhost:8000/query', payload)
    const data = response.data

    const timestamps = data.map(item => item.t_sampling_time)
    const values = data.map(item => item[form.value.metric])

    chartData.value = {
      labels: timestamps,
      series: [
        {
          name: form.value.metric,
          data: values
        }
      ]
    }

    dataFetched.value = true
    emit('update', {
      id: props.id,
      ...form.value,
      selectedFilters: selectedFilters.value
    })

  } catch (error) {
    console.error('Error fetching data:', error)
  }
}
</script>

<style scoped>
.q-btn-group {
  display: flex;
  gap: 8px;
}
</style>
