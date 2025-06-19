<template>
  <div class="q-pa-md">
    <h5>This is your dynamic page: {{ route.params.pageRoute }}</h5>
  </div>
  <q-page padding>
    <div class="row q-gutter-md items-center">
      <q-btn icon="add" label="Add Widget" @click="addWidget" color="primary" />
      <q-btn icon="save" label="Save Layout" @click="saveLayout" color="positive" />
    </div>

    <div ref="gridContainer" class="grid-stack q-mt-md"></div>
  </q-page>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()

import { onMounted, ref } from 'vue'
import { GridStack } from 'gridstack'
import 'gridstack/dist/gridstack.min.css'
import axios from 'axios'

const grid = ref(null)
const gridContainer = ref(null)
const widgets = ref([])
const pageId = 123  // Hardcoded for now; you can make this dynamic later

onMounted(() => {
  grid.value = GridStack.init({
    cellHeight: 100,
    float: true,
    resizable: { handles: 'all' }
  }, gridContainer.value)
})

const addWidget = () => {
  const id = Date.now()
  const el = document.createElement('div')
  el.className = 'grid-stack-item'
  el.setAttribute('gs-x', '0')
  el.setAttribute('gs-y', '0')
  el.setAttribute('gs-w', '4')
  el.setAttribute('gs-h', '2')
  el.setAttribute('data-id', id)

  el.innerHTML = `
    <div class="grid-stack-item-content q-pa-sm bg-grey-3">
      <div class="q-gutter-sm">
        <div class="text-subtitle1">Widget ${widgets.value.length + 1}</div>
        <button class="q-btn q-btn--dense q-btn--flat material-icons" data-action="lock">lock</button>
        <button class="q-btn q-btn--dense q-btn--flat material-icons text-red" data-action="delete">delete</button>
      </div>
    </div>
  `

  grid.value.addWidget(el)
  widgets.value.push({ id, locked: false })

  el.querySelector('[data-action="delete"]').addEventListener('click', () => removeWidget(id))
  el.querySelector('[data-action="lock"]').addEventListener('click', () => lockWidget(id))
}

const removeWidget = (id) => {
  const el = gridContainer.value.querySelector(`[data-id="${id}"]`)
  if (el) {
    grid.value.removeWidget(el)
    widgets.value = widgets.value.filter(w => w.id !== id)
  }
}

const lockWidget = (id) => {
  const el = gridContainer.value.querySelector(`[data-id="${id}"]`)
  const item = widgets.value.find(w => w.id === id)
  if (el && item) {
    item.locked = !item.locked
    grid.value.update(el, { locked: item.locked, noResize: item.locked })
  }
}

const saveLayout = async () => {
  const layout = grid.value.engine.nodes.map(node => ({
    id: node.el.getAttribute('data-id'),
    x: node.x,
    y: node.y,
    w: node.w,
    h: node.h,
    locked: node.locked || false
  }))

  try {
    await axios.post(`http://localhost:8000/save-layout?page_id=${pageId}`, { layout })
    alert('Layout saved successfully!')
  } catch (error) {
    console.error('Failed to save layout:', error)
    alert('Error saving layout')
  }
}

</script>
