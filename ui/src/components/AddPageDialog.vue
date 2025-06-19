<template>
  <q-dialog v-model="show">
    <q-card>
      <q-card-section>
        <div class="text-h6">Create New Page</div>
        <q-input v-model="page_name" label="Page Name" />
        <q-input v-model="user_name" label="User Name" />
        <q-input v-model="page_route" label="Page Route" />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn label="Cancel" flat v-close-popup />
        <q-btn label="Create" color="primary" @click="createPage" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { usePageStore } from 'D:/Asset Monitoring System/ui/src/stores/userPageStore.js'
import { useQuasar } from 'quasar'

const show = ref(false)
const page_name = ref('')
const user_name = ref('')
const page_route = ref('')

const $q = useQuasar()
const pageStore = usePageStore()

const createPage = () => {
  const newPage = pageStore.addPage({
    page_name: page_name.value,
    user_name: user_name.value,
    page_route: page_route.value
  })
  $q.notify({ type: 'positive', message: `Page "${newPage.page_name}" created` })
  show.value = false
}

defineExpose({ show })
</script>
