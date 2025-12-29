<template>
  <div class="export-records">
    <!-- Export Button -->
    <button 
      @click="showModal = true"
      class="btn btn-outline-secondary d-inline-flex align-items-center gap-2"
      :disabled="loading"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <span>Export Records</span>
    </button>

    <!-- Modal -->
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
            <!-- Modal Header -->
            <div class="modal-header">
              <h5 class="modal-title">Export Medical Records</h5>
              <button 
                type="button" 
                class="btn-close" 
                @click="closeModal"
                aria-label="Close"
              ></button>
            </div>

            <!-- Modal Body -->
            <div class="modal-body">
              <p class="text-muted mb-3">
                Your medical records will be exported as a CSV file and sent to your email address.
              </p>

              <div class="mb-3">
                <label for="exportEmail" class="form-label">Send to email:</label>
                <input 
                  type="email" 
                  id="exportEmail"
                  v-model="email"
                  class="form-control"
                  :placeholder="defaultEmail || 'Enter email address'"
                />
                <div class="form-text">Leave empty to use your registered email</div>
              </div>

              <!-- Success Message -->
              <div v-if="message && messageType === 'success'" class="alert alert-success" role="alert">
                {{ message }}
              </div>

              <!-- Error Message -->
              <div v-if="message && messageType === 'error'" class="alert alert-danger" role="alert">
                {{ message }}
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="modal-footer">
              <button 
                type="button" 
                class="btn btn-secondary" 
                @click="closeModal"
              >
                Cancel
              </button>
              <button 
                type="button" 
                class="btn btn-primary d-inline-flex align-items-center gap-2"
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
  defaultEmail: {
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
    const response = await api.post('/patient/export-records', payload)

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