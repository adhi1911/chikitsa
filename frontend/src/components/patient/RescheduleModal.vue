<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title">
            <i class="bi bi-calendar-event me-2"></i>Reschedule Appointment
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body">
          <!-- Current Appointment Info -->
          <div v-if="appointment" class="alert alert-light mb-4">
            <small class="text-muted">Current Appointment:</small>
            <div class="fw-medium">{{ formatDate(appointment.appointment_date) }} at {{ formatTime(appointment.appointment_time) }}</div>
            <div class="small text-muted">{{ appointment.doctor_name }}</div>
          </div>

          <!-- New Date -->
          <div class="mb-4">
            <label class="form-label fw-medium">New Date</label>
            <input 
              type="date" 
              class="form-control" 
              v-model="newDate"
              :min="minDate"
              :max="maxDate"
              @change="fetchSlots"
            >
          </div>

          <!-- New Time Slot -->
          <div>
            <label class="form-label fw-medium">New Time Slot</label>
            <SlotPicker 
              :slots="slots" 
              :loading="loadingSlots" 
              :selected="newSlot"
              :date-selected="!!newDate"
              @select="newSlot = $event"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-warning" 
            :disabled="!canReschedule || rescheduling"
            @click="reschedule"
          >
            <span v-if="rescheduling" class="spinner-border spinner-border-sm me-2"></span>
            Confirm Reschedule
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';
import SlotPicker from '@/components/patient/SlotPicker.vue';

export default {
  name: 'RescheduleModal',
  components: { SlotPicker },
  props: {
    appointment: { type: Object, default: null }
  },
  emits: ['rescheduled'],
  data() {
    return {
      modal: null,
      newDate: '',
      newSlot: '',
      slots: [],
      loadingSlots: false,
      rescheduling: false
    };
  },
  computed: {
    minDate() {
      return new Date().toISOString().split('T')[0];
    },
    maxDate() {
      const d = new Date();
      d.setDate(d.getDate() + 30);
      return d.toISOString().split('T')[0];
    },
    canReschedule() {
      return this.newDate && this.newSlot;
    }
  },
  methods: {
    show() {
      this.reset();
      this.modal.show();
    },
    hide() {
      this.modal.hide();
    },
    reset() {
      this.newDate = '';
      this.newSlot = '';
      this.slots = [];
    },

    async fetchSlots() {
      if (!this.newDate || !this.appointment) return;
      
      try {
        this.loadingSlots = true;
        this.newSlot = '';
        const res = await api.get(`/appointments/slots/${this.appointment.doctor_id}`, {
          params: { date: this.newDate }
        });
        this.slots = res.data?.data?.slots || [];
      } catch (e) {
        console.error('Failed to fetch slots:', e);
        this.slots = [];
      } finally {
        this.loadingSlots = false;
      }
    },

    async reschedule() {
      if (!this.canReschedule) return;

      try {
        this.rescheduling = true;
        // Fix: Use correct field names expected by backend
        await api.put(`/patient/appointments/${this.appointment.id}/reschedule`, {
          appointment_date: this.newDate,
          appointment_time: this.newSlot
        });
        this.hide();
        this.$emit('rescheduled');
      } catch (e) {
        alert(e.response?.data?.message || 'Failed to reschedule appointment');
      } finally {
        this.rescheduling = false;
      }
    },

    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    },
    formatTime(time) {
      if (!time) return '';
      const [h, m] = time.split(':');
      const hour = parseInt(h);
      return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>