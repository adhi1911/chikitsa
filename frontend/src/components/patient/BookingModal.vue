<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">
            <i class="bi bi-calendar-plus me-2"></i>Book Appointment
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body">
          <!-- Doctor Info -->
          <div v-if="doctor" class="d-flex align-items-center p-3 bg-light rounded mb-4">
            <div class="avatar bg-primary-subtle text-primary rounded-circle me-3">
              {{ doctorInitials }}
            </div>
            <div>
              <h6 class="mb-0 fw-semibold">Dr. {{ doctor.first_name }} {{ doctor.last_name }}</h6>
              <small class="text-muted">{{ doctor.department_name || 'General' }}</small>
              <span v-if="doctor.consultation_fee" class="badge bg-success-subtle text-success ms-2">
                ₹{{ doctor.consultation_fee }}
              </span>
            </div>
          </div>

          <!-- Step 1: Select Date -->
          <div class="mb-4">
            <label class="form-label fw-medium">
              <i class="bi bi-calendar3 me-2"></i>Select Date
            </label>
            <input 
              type="date" 
              class="form-control" 
              v-model="selectedDate"
              :min="minDate"
              :max="maxDate"
              @change="fetchSlots"
            >
          </div>

          <!-- Step 2: Select Time Slot -->
          <div class="mb-4">
            <label class="form-label fw-medium">
              <i class="bi bi-clock me-2"></i>Available Slots
            </label>
            <SlotPicker 
              :slots="slots" 
              :loading="loadingSlots" 
              :selected="selectedSlot"
              :date-selected="!!selectedDate"
              @select="selectedSlot = $event"
            />
          </div>

          <!-- Step 3: Notes -->
          <div>
            <label class="form-label fw-medium">
              <i class="bi bi-chat-left-text me-2"></i>Any Notes for us? (Optional)
            </label>
            <textarea 
              class="form-control" 
              v-model="notes" 
              rows="2"
              placeholder="Brief description of your concern..."
              maxlength="500"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-primary" 
            :disabled="!canBook || booking"
            @click="bookAppointment"
          >
            <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-check-lg me-2"></i>
            Confirm Booking
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
  name: 'BookingModal',
  components: { SlotPicker },
  props: {
    doctor: { type: Object, default: null }
  },
  emits: ['booked'],
  data() {
    return {
      modal: null,
      selectedDate: '',
      selectedSlot: '',
      notes: '',
      slots: [],
      loadingSlots: false,
      booking: false
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
    canBook() {
      return this.selectedDate && this.selectedSlot;
    },
    doctorInitials() {
      if (!this.doctor) return '';
      return ((this.doctor.first_name?.[0] || '') + (this.doctor.last_name?.[0] || '')).toUpperCase();
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
      this.selectedDate = '';
      this.selectedSlot = '';
      this.notes = '';
      this.slots = [];
    },

    async fetchSlots() {
      if (!this.selectedDate || !this.doctor) return;
      
      try {
        this.loadingSlots = true;
        this.selectedSlot = '';
        const res = await api.get(`/appointments/slots/${this.doctor.id}`, {
          params: { date: this.selectedDate }
        });

        this.slots = res.data?.data?.slots || [];
      } catch (e) {
        console.error('Failed to fetch slots:', e);
        this.slots = [];
      } finally {
        this.loadingSlots = false;
      }
    },

    async bookAppointment() {
      if (!this.canBook) return;

      try {
        this.booking = true;
        await api.post('/patient/appointments', {
          doctor_id: this.doctor.id,
          appointment_date: this.selectedDate,
          appointment_time: this.selectedSlot,
          notes: this.notes || null
        });
        this.hide();
        this.$emit('booked');
      } catch (e) {
        alert(e.response?.data?.message || 'Failed to book appointment');
      } finally {
        this.booking = false;
      }
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>