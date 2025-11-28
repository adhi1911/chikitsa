<template>
  <div class="slot-picker">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border spinner-border-sm text-primary me-2"></div>
      <span class="text-muted">Loading available slots...</span>
    </div>

    <!-- No Date Selected -->
    <div v-else-if="!dateSelected" class="text-center py-4 bg-light rounded">
      <i class="bi bi-calendar3 text-muted fs-1"></i>
      <p class="text-muted mb-0 mt-2">Select a date to see available slots</p>
    </div>

    <!-- No Slots Available -->
    <div v-else-if="availableSlots.length === 0" class="text-center py-4 bg-light rounded">
      <i class="bi bi-calendar-x text-danger fs-1"></i>
      <p class="text-muted mb-0 mt-2">No slots available on this date</p>
      <small class="text-muted">Try selecting a different date</small>
    </div>

    <!-- Slots Grid -->
    <div v-else>
      <!-- Morning Slots -->
      <div v-if="morningSlots.length > 0" class="mb-3">
        <small class="text-muted fw-medium d-block mb-2">
          <i class="bi bi-sunrise me-1"></i>Morning
        </small>
        <div class="d-flex flex-wrap gap-2">
          <button
            v-for="slot in morningSlots"
            :key="slot.time"
            type="button"
            class="btn btn-sm slot-btn"
            :class="selected === slot.time ? 'btn-primary' : 'btn-outline-primary'"
            @click="$emit('select', slot.time)"
          >
            {{ formatTime(slot.time) }}
          </button>
        </div>
      </div>

      <!-- Afternoon Slots -->
      <div v-if="afternoonSlots.length > 0" class="mb-3">
        <small class="text-muted fw-medium d-block mb-2">
          <i class="bi bi-sun me-1"></i>Afternoon
        </small>
        <div class="d-flex flex-wrap gap-2">
          <button
            v-for="slot in afternoonSlots"
            :key="slot.time"
            type="button"
            class="btn btn-sm slot-btn"
            :class="selected === slot.time ? 'btn-primary' : 'btn-outline-primary'"
            @click="$emit('select', slot.time)"
          >
            {{ formatTime(slot.time) }}
          </button>
        </div>
      </div>

      <!-- Evening Slots -->
      <div v-if="eveningSlots.length > 0">
        <small class="text-muted fw-medium d-block mb-2">
          <i class="bi bi-sunset me-1"></i>Evening
        </small>
        <div class="d-flex flex-wrap gap-2">
          <button
            v-for="slot in eveningSlots"
            :key="slot.time"
            type="button"
            class="btn btn-sm slot-btn"
            :class="selected === slot.time ? 'btn-primary' : 'btn-outline-primary'"
            @click="$emit('select', slot.time)"
          >
            {{ formatTime(slot.time) }}
          </button>
        </div>
      </div>

      <!-- Slots Count -->
      <div class="mt-3 pt-3 border-top">
        <small class="text-muted">
          <i class="bi bi-info-circle me-1"></i>
          {{ availableSlots.length }} slot{{ availableSlots.length > 1 ? 's' : '' }} available
        </small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SlotPicker',
  props: {
    slots: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    selected: { type: String, default: '' },
    dateSelected: { type: Boolean, default: false }
  },
  emits: ['select'],
  computed: {
    // Filter only available slots (not booked, not past)
    availableSlots() {
      return this.slots.filter(s => s.is_available && !s.is_booked && !s.is_past);
    },
    morningSlots() {
      return this.availableSlots.filter(s => {
        const hour = parseInt(s.time.split(':')[0]);
        return hour < 12;
      });
    },
    afternoonSlots() {
      return this.availableSlots.filter(s => {
        const hour = parseInt(s.time.split(':')[0]);
        return hour >= 12 && hour < 17;
      });
    },
    eveningSlots() {
      return this.availableSlots.filter(s => {
        const hour = parseInt(s.time.split(':')[0]);
        return hour >= 17;
      });
    }
  },
  methods: {
    formatTime(time) {
      if (!time) return '';
      const [h, m] = time.split(':');
      const hour = parseInt(h);
      return `${hour % 12 || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    }
  }
};
</script>

<style scoped>
.slot-btn {
  min-width: 90px;
  transition: all 0.2s;
}
.slot-btn:hover {
  transform: translateY(-1px);
}
</style>