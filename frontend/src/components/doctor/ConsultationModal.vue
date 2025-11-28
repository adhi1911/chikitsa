<template>
  <div class="modal fade" :id="modalId" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-xl modal-dialog-scrollable">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-success text-white">
          <h5 class="modal-title">
            <i class="bi bi-clipboard2-pulse me-2"></i>Complete Consultation
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body" v-if="appointment">
          <!-- Patient Info -->
          <div class="bg-light rounded-3 p-3 mb-4">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h5 class="mb-1">{{ appointment.patient_name }}</h5>
                <small class="text-muted">
                  <i class="bi bi-calendar me-1"></i>
                  {{ formatDate(appointment.appointment_date) }} at {{ formatTime(appointment.appointment_time) }}
                </small>
              </div>
              <div class="col-md-4 text-end">
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="$emit('view-history', appointment.patient_id)"
                >
                  <i class="bi bi-clock-history me-1"></i>View History
                </button>
              </div>
            </div>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit">
            <div class="row g-3">
              <!-- Diagnosis -->
              <div class="col-12">
                <label class="form-label fw-semibold">
                  Diagnosis <span class="text-danger">*</span>
                </label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="form.diagnosis"
                  placeholder="Primary diagnosis"
                  required
                >
              </div>

              <!-- Symptoms -->
              <div class="col-md-6">
                <label class="form-label fw-semibold">Symptoms</label>
                <textarea 
                  class="form-control" 
                  v-model="form.symptoms"
                  rows="3"
                  placeholder="Patient symptoms..."
                ></textarea>
              </div>

              <!-- Treatment Notes -->
              <div class="col-md-6">
                <label class="form-label fw-semibold">Treatment Notes</label>
                <textarea 
                  class="form-control" 
                  v-model="form.treatment_notes"
                  rows="3"
                  placeholder="Treatment plan..."
                ></textarea>
              </div>

              <!-- Doctor Notes -->
              <div class="col-12">
                <label class="form-label fw-semibold">
                  Doctor Notes <small class="text-muted">(Internal - not visible to patient)</small>
                </label>
                <textarea 
                  class="form-control" 
                  v-model="form.doctor_notes"
                  rows="2"
                  placeholder="Internal notes..."
                ></textarea>
              </div>

              <!-- Follow-up Date -->
              <div class="col-md-6">
                <label class="form-label fw-semibold">Follow-up Date</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="form.followup_date"
                  :min="minDate"
                >
              </div>

              <!-- Prescription Section -->
              <div class="col-12">
                <PrescriptionForm 
                  v-model="form.prescription_items"
                />
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-success"
            @click="handleSubmit"
            :disabled="loading || !form.diagnosis"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-check-lg me-2"></i>
            Complete & Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import PrescriptionForm from '@/components/medicalRecord/PrescriptionForm.vue'; 

export default {
  name: 'ConsultationModal',
  components: {
    PrescriptionForm
  },
  props: {
    modalId: {
      type: String,
      default: 'consultationModal'
    },
    appointment: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['submit', 'view-history'],
  data() {
    return {
      modal: null,
      form: this.getEmptyForm()
    };
  },
  computed: {
    minDate() {
      const d = new Date();
      d.setDate(d.getDate() + 1);
      return d.toISOString().split('T')[0];
    }
  },
  watch: {
    appointment: {
      handler(newVal) {
        if (newVal) {
          this.resetForm();
        }
      },
      immediate: true
    }
  },
  methods: {
    getEmptyForm() {
      return {
        diagnosis: '',
        symptoms: '',
        treatment_notes: '',
        doctor_notes: '',
        followup_date: '',
        prescription_items: []
      };
    },
    resetForm() {
      this.form = this.getEmptyForm();
    },
    formatTime(time) {
      if (!time) return '';
      const [hours, minutes] = time.split(':');
      const h = parseInt(hours);
      return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', { 
        day: 'numeric', 
        month: 'short', 
        year: 'numeric' 
      });
    },
    handleSubmit() {
      if (!this.form.diagnosis) return;
      
      const data = {
        ...this.form,
        prescription_items: (this.form.prescription_items || []).filter(
          item => item && item.medicine_name && item.medicine_name.trim()
        )
      };
      
      this.$emit('submit', data);
    },
    show() {
      this.modal?.show();
    },
    hide() {
      this.modal?.hide();
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>