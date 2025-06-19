<template>
  <div class="q-pa-sm bg-grey-3">
    <div class="q-gutter-sm">
      <div class="text-subtitle1">{{ title || 'New Widget' }}</div>
      <q-btn dense flat icon="lock" @click="$emit('lock')" />
      <q-btn dense flat icon="delete" color="red" @click="$emit('delete')" />
    </div>

    <div class="q-mt-sm">
      <q-btn-group>
        <q-btn label="Add Graph" @click="mode = 'graph'" />
        <q-btn label="Add Table" @click="mode = 'table'" />
        <q-btn label="Add Pie Chart" @click="mode = 'pie'" />
      </q-btn-group>
    </div>

    <div v-if="mode === 'graph'" class="q-mt-md">
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
        <q-select
          v-model="form.filter"
          :options="filters"
          label="Filter"
          dense
          class="q-mt-sm"
        />
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

    <div v-if="chartOptions" class="q-mt-md">
      <vue-echarts :option="chartOptions" style="height: 300px;" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useGlobalTime } from 'src/composables/globalTime'
import VueECharts from 'vue-echarts'

const props = defineProps({
  id: Number
})

const emit = defineEmits(['lock', 'delete'])

const mode = ref(null)
const form = ref({
  title: '',
  subtitle: '',
  container: null,
  equipment: null,
  filter: null,
  metric: null
})

const containers = Array.from({ length: 16 }, (_, i) => `BC-${i + 1}`)
const equipments = ['bms.bmu', 'hvac', 'bsc', 'bmu', 'ups']
const filters = ['n_rack', 'n_bank']
const metrics = ['soc', 'soh', 'n_soc', 'n_soh']

const chartOptions = ref(null)

const { globalTime } = useGlobalTime()

watch(globalTime, () => {
  if (chartOptions.value) {
    fetchData()
  }
})

async function fetchData() {
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
    where_args: [`${form.value.filter}=1`]
  }

  try {
    const response = await axios.post('http://localhost:8000/query', payload)
    const data = response.data

    chartOptions.value = {
      title: {
        text: form.value.title,
        subtext: form.value.subtitle
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.timestamps
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: form.value.metric,
          type: 'line',
          data: data.values
        }
      ]
    }
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
