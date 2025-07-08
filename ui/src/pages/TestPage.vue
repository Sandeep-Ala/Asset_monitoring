<!-- src/pages/TestPage.vue -->
<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">🧪 Phase 6.3.1 & 6.3.2 Testing</div>

    <q-tabs v-model="tab" class="text-grey" active-color="primary" indicator-color="primary">
      <q-tab name="time" label="Global Time Test" />
      <q-tab name="chart" label="Chart Utils Test" />
      <q-tab name="picker" label="Time Picker Test" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="time">
        <TestTimeComposable />
      </q-tab-panel>

      <q-tab-panel name="chart">
        <TestChartUtils />
      </q-tab-panel>

      <q-tab-panel name="picker">
        <GlobalTimePicker />
        <div class="q-mt-md q-pa-md bg-blue-1">
          <div class="text-subtitle1">Instructions:</div>
          <ul>
            <li>Click the time picker trigger button in the top-right corner</li>
            <li>Test different time ranges and window periods</li>
            <li>Enable auto-refresh and watch the countdown</li>
            <li>Try custom date ranges</li>
          </ul>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import TestTimeComposable from 'src/components/TestTimeComposable.vue'
import TestChartUtils from 'src/components/TestChartUtils.vue'
import GlobalTimePicker from 'src/components/GlobalTimePicker.vue'

const tab = ref('time')
</script>
