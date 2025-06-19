<template>
  <q-layout class="appScrollBar" view="hHh Lpr lff">
    <!-- HEADER -->
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-img class="q-ma-xs" contain width="150px" height="50px" src="~/assets/tmeic_logo_white.svg" />
        <q-space />
        <q-toolbar-title shrink class="text-center absolute-center">
          <span>{{ route.meta.title }}</span>
        </q-toolbar-title>
        <q-space />

        <q-btn
          class="q-pr-sm"
          icon-right="fas fa-sign-out-alt"
          flat
          dense
          :label="Username"
          color="white"
          @click="showlogout = !showlogout"
        >
          <q-tooltip>Logout</q-tooltip>
        </q-btn>

        <div>
          <div class="text-white text-subtitle2 q-px-s">
            <q-icon class="q-px-sm" name="today" style="font-size: 1.5em" />
            {{ currentdate }}
          </div>
          <div class="text-white text-subtitle2 q-px-s">
            <q-icon class="q-px-sm" name="access_time" style="font-size: 1.5em" />
            {{ currenttime }}
          </div>
        </div>
      </q-toolbar>

      <!-- Logout Popup -->
      <q-dialog v-model="showlogout" persistent>
        <q-card>
          <q-card-section>
            <div class="text-subtitle1 text-bolder text-center">Are you sure you want to logout?</div>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn class="q-ml-sm" flat label="Cancel" v-close-popup />
            <q-btn class="q-ml-sm" flat label="Logout" color="red" @click="logout" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-header>

    <!-- DRAWER -->
    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-list>
        <q-item clickable v-ripple @click="openDialog">
          <q-item-section avatar>
            <q-icon name="add" />
          </q-item-section>
          <q-item-section>Add Page</q-item-section>
        </q-item>

        <q-item v-for="page in pageStore.pages" :key="page.page_id" :to="page.page_route" clickable>
          <q-item-section>{{ page.page_name }}</q-item-section>
          <q-item-section side>
            <q-btn dense flat icon="edit" @click.stop="openRenameDialog(page)" />
            <q-btn dense flat icon="delete" color="red" @click.stop="deletePage(page.page_id)" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- DIALOGS -->
    <add-page-dialog ref="addDialog" />

    <q-dialog v-model="renameDialog.show">
      <q-card>
        <q-card-section>
          <q-input v-model="renameDialog.newName" label="New Page Name" />
          <q-input v-model="renameDialog.newRoute" label="New Page Route" class="q-mt-md" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn label="Cancel" flat v-close-popup />
          <q-btn label="Save" color="primary" @click="renamePage" />
        </q-card-actions>
      </q-card>
    </q-dialog>


    <!-- PAGE -->
    <q-page-container>
      <router-view :key="$route.fullPath" />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { usePageStore } from 'src/stores/userPageStore'
import AddPageDialog from 'src/components/AddPageDialog.vue'

// STATE
const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const Username = localStorage.getItem('username')
const leftDrawerOpen = ref(true)
const showlogout = ref(false)
const currentdate = ref('')
const currenttime = ref('')
const addDialog = ref()
const pageStore = usePageStore()

// RENAME DIALOG STATE
const renameDialog = ref({
  show: false,
  pageId: null,
  newName: ''
})

// INIT
onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 1000)
  pageStore.fetchPages()
})

// ACTIONS
function openDialog() {
  addDialog.value.show = true
}

function openRenameDialog(page) {
  renameDialog.value = {
    show: true,
    pageId: page.page_id,
    newName: page.page_name,
    newRoute: page.page_route
  }
}

async function renamePage() {
  await pageStore.updatePage(renameDialog.value.pageId, {
    page_name: renameDialog.value.newName,
    page_route: renameDialog.value.newRoute
  })
  renameDialog.value.show = false
}


const deletePage = (page_id) => {
  $q.dialog({
    title: 'Confirm',
    message: 'Are you sure you want to delete this page?',
    cancel: true,
    persistent: true
  }).onOk(() => {
    pageStore.removePage(page_id)
  })
}

function logout() {
  localStorage.clear()
  $q.notify({
    message: 'Logged out Successfully',
    type: 'positive',
    position: 'top'
  })
  router.push('/login')
}

function updateDateTime() {
  const datetime = new Date().toLocaleString('sv-SE').split(' ')
  currentdate.value = datetime[0]
  currenttime.value = datetime[1]
}
</script>

<style lang="sass">
.my-sticky-table
  height: 119px
  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    background-color: $blue-8
    color: $grey-1
  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0
  &.q-table--loading thead tr:last-child th
    top: 48px
  tbody
    scroll-margin-top: 48px

.my-sticky-no-table
  height: 119px
  .q-table__top,
  thead tr:first-child th
    background-color: $blue-8
    color: $grey-1
  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0
  &.q-table--loading thead tr:last-child th
    top: 48px
  tbody
    scroll-margin-top: 48px
</style>
