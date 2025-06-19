<template>
  <div ref="chartContainer" class="chart" :style="{ height: '400px', width: '100%' }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  data: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    default: ''
  }
})

const chartContainer = ref(null)
let chartInstance = null

const renderChart = () => {
  if (!chartInstance || !props.data) return

  let option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: props.data.labels || []
    },
    yAxis: {
      type: 'value'
    },
    series: []
  }

  if (props.type === 'line' || props.type === 'bar') {
    option.series = props.data.series.map(series => ({
      name: series.name,
      type: props.type,
      data: series.data,
      smooth: true
    }))
  } else if (props.type === 'pie') {
    option = {
      title: {
        text: props.title,
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          name: props.title,
          type: 'pie',
          radius: '50%',
          data: props.data.series[0].data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  chartInstance = echarts.init(chartContainer.value)
  renderChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})

watch(() => props.data, () => {
  if (chartInstance) {
    renderChart()
  }
}, { deep: true })

watch(() => props.type, () => {
  if (chartInstance) {
    renderChart()
  }
})
</script>

<style scoped>
.chart {
  width: 100%;
}
</style>
