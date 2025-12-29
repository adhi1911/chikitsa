<template>
  <div class="export-records-admin">
    <!-- Export Button -->
    <button 
      @click="showModal = true"
      class="btn btn-outline-primary btn-sm d-inline-flex align-items-center gap-1"
      :disabled="loading"
      :title="'Export records for ' + patientName"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <span>Export</span>
    </button>


    <Teleport to="body">
      <div v-if="showModal" class="modal-backdrop fade show"></div>
      <div 
        v-if="showModal" 
        class="modal fade show d-block" 
        tabindex="-1"
        @click.self="closeModal"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">

            <div class="modal-header">
              <h5 class="modal-title">Export Patient Records</h5>
              <button 
                type="button" 
                class="btn-close" 
                @click="closeModal"
                aria-label="Close"
              ></button>
            </div>


            <div class="modal-body">
              <div class="alert alert-info py-2 mb-3">
                <small>
                  <strong>Patient:</strong> {{ patientName }}<br>
                  <strong>ID:</strong> {{ patientId }}
                </small>
              </div>

              <p class="text-muted mb-3">
                Medical records will be exported as CSV and sent to the specified email.
              </p>

              <div class="mb-3">
                <label for="adminExportEmail" class="form-label">Send to email:</label>
                <input 
                  type="email" 
                  id="adminExportEmail"
                  v-model="email"
                  class="form-control"
                  :placeholder="patientEmail || 'Enter email address'"
                />
                <div class="form-text">Leave empty to use patient's registered email</div>
              </div>


              <div v-if="message && messageType === 'success'" class="alert alert-success py-2" role="alert">
                <small>{{ message }}</small>
              </div>


              <div v-if="message && messageType === 'error'" class="alert alert-danger py-2" role="alert">
                <small>{{ message }}</small>
              </div>
            </div>


            <div class="modal-footer">
              <button 
                type="button" 
                class="btn btn-secondary btn-sm" 
                @click="closeModal"
              >
                Cancel
              </button>
              <button 
                type="button" 
                class="btn btn-primary btn-sm d-inline-flex align-items-center gap-2"
                @click="exportRecords"
                :disabled="loading"
              >
                <span 
                  v-if="loading" 
                  class="spinner-border spinner-border-sm" 
                  role="status"
                  aria-hidden="true"
                ></span>
                <span>{{ loading ? 'Sending...' : 'Send to Email' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const props = defineProps({
  patientId: {
    type: Number,
    required: true
  },
  patientName: {
    type: String,
    default: 'Patient'
  },
  patientEmail: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['exported'])

const showModal = ref(false)
const loading = ref(false)
const email = ref('')
const message = ref('')
const messageType = ref('success')

const closeModal = () => {
  showModal.value = false
  message.value = ''
  email.value = ''
}

const exportRecords = async () => {
  loading.value = true
  message.value = ''

  try {
    const payload = email.value ? { email: email.value } : {}
    const response = await api.post(`/admin/${props.patientId}/export-records`, payload)

    messageType.value = 'success'
    message.value = `Records sent to ${response.data.email} (${response.data.records_count} records)`
    
    emit('exported', response.data)

    setTimeout(() => {
      closeModal()
    }, 3000)

  } catch (error) {
    messageType.value = 'error'
    message.value = error.response?.data?.error || 'Failed to export records'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal.show {
  background: rgba(0, 0, 0, 0.5);
}
</style>