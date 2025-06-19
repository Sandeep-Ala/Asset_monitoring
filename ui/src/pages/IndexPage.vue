<template>
  <q-page padding>
    <div class="row q-gutter-md items-center">
      <q-btn icon="add" label="Add Widget" @click="addWidget" color="primary" />
      <q-btn icon="save" label="Save Layout" @click="saveLayout" color="positive" />
    </div>


    <div ref="gridContainer" class="grid-stack q-mt-md"></div>

  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { GridStack } from 'gridstack'
import { createApp,h } from 'vue'

import { Quasar } from 'quasar'
import 'gridstack/dist/gridstack.min.css'
import axios from 'axios'
import box from 'src/components/WidgetBox.vue'
const grid = ref(null)
const gridContainer = ref(null)
const widgets = ref([])
const pageId = 123  // Hardcoded for now; you can make this dynamic later
const widgetDataMap = ref({})

onMounted(() => {
  grid.value = GridStack.init({
    cellHeight: 100,
    float: true,
    resizable: { handles: 'all' }
  }, gridContainer.value)
})

const addWidget = () => {
  const id = Date.now()

  // Create the widget wrapper
  const wrapper = document.createElement('div')
  wrapper.className = 'grid-stack-item'
  wrapper.setAttribute('gs-x', '0')
  wrapper.setAttribute('gs-y', '0')
  wrapper.setAttribute('gs-w', '4')
  wrapper.setAttribute('gs-h', '2')
  wrapper.setAttribute('data-id', id)

  // Create content container
  const content = document.createElement('div')
  content.className = 'grid-stack-item-content'
  wrapper.appendChild(content)

  // Append to container directly (bypassing addWidget)
  gridContainer.value.appendChild(wrapper)

  // Tell GridStack to initialize this DOM element as a widget
  grid.value.makeWidget(wrapper)

  // Create app and provide Quasar context
  const widgetApp = createApp({
    render() {
      return h(box, {
        id,
        onLock: () => lockWidget(id),
        onDelete: () => removeWidget(id),
        onUpdate: (data) => {
        widgetDataMap.value[id] = data
      }
      })
    }
  })

  widgetApp.use(Quasar) // IMPORTANT: inject Quasar so <q-btn> works
  widgetApp.mount(content)

  // Track widget
  widgets.value.push({ id, locked: false })
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
  const layout = grid.value.engine.nodes.map(node => {
  const id = node.el.getAttribute('data-id')
  return {
    id,
    x: node.x,
    y: node.y,
    w: node.w,
    h: node.h,
    locked: node.locked || false,
    attributes: widgetDataMap.value[id] || {}
  }
})


  try {
    await axios.post(`http://localhost:8000/save-layout?page_id=${pageId}`, { layout })
    alert('Layout saved successfully!')
  } catch (error) {
    console.error('Failed to save layout:', error)
    alert('Error saving layout')
  }
}

</script>
