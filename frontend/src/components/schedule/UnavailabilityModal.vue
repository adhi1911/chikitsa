<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">
            <i class="bi bi-calendar-x me-2"></i>Add Unavailability
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <!-- Start Date & Time -->
            <div class="row g-3 mb-3">
              <div class="col-6">
                <label class="form-label fw-medium">Start Date <span class="text-danger">*</span></label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="form.startDate" 
                  :min="minDate" 
                  required
                >
              </div>
              <div class="col-6">
                <label class="form-label fw-medium">Start Time</label>
                <input type="time" class="form-control" v-model="form.startTime">
              </div>
            </div>

            <!-- End Date & Time -->
            <div class="row g-3 mb-3">
              <div class="col-6">
                <label class="form-label fw-medium">End Date <span class="text-danger">*</span></label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="form.endDate" 
                  :min="form.startDate || minDate" 
                  required
                >
              </div>
              <div class="col-6">
                <label class="form-label fw-medium">End Time</label>
                <input type="time" class="form-control" v-model="form.endTime">
              </div>
            </div>

            <!-- Reason -->
            <div>
              <label class="form-label fw-medium">Reason (Optional)</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="form.reason" 
                placeholder="e.g., Personal leave, Conference..."
                maxlength="255"
              >
            </div>

            <!-- Duration Info -->
            <div v-if="durationText" class="alert alert-info mt-3 mb-0 py-2">
              <i class="bi bi-info-circle me-2"></i>{{ durationText }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-danger" :disabled="loading || !isValid">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Add
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'UnavailabilityModal',
  props: {
    loading: { type: Boolean, default: false }
  },
  emits: ['save'],
  data() {
    return {
      modal: null,
      form: {
        startDate: '',
        startTime: '00:00',
        endDate: '',
        endTime: '23:59',
        reason: ''
      }
    };
  },
  computed: {
    minDate() {
      return new Date().toISOString().split('T')[0];
    },
    isValid() {
      if (!this.form.startDate || !this.form.endDate) return false;
      const start = new Date(`${this.form.startDate}T${this.form.startTime}`);
      const end = new Date(`${this.form.endDate}T${this.form.endTime}`);
      return end > start;
    },
    durationText() {
      if (!this.form.startDate || !this.form.endDate) return '';
      const start = new Date(this.form.startDate);
      const end = new Date(this.form.endDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
      if (days === 1) return 'Single day unavailability';
      return `${days} days unavailability`;
    }
  },
  methods: {
    show() {
      this.form = { startDate: '', startTime: '00:00', endDate: '', endTime: '23:59', reason: '' };
      this.modal.show();
    },
    hide() {
      this.modal.hide();
    },
    handleSubmit() {
      if (!this.isValid) return;

      this.$emit('save', {
        start_datetime: `${this.form.startDate}T${this.form.startTime}:00`,
        end_datetime: `${this.form.endDate}T${this.form.endTime}:00`,
        reason: this.form.reason || null
      });
    }
  },
  watch: {
    'form.startDate'(val) {
      // Auto-set end date if empty or before start
      if (!this.form.endDate || this.form.endDate < val) {
        this.form.endDate = val;
      }
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>