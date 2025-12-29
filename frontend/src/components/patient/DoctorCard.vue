<template>
  <div class="card border-0 shadow-sm h-100">
    <div class="card-body">
      <div class="d-flex align-items-center mb-3">
        <div class="avatar bg-primary-subtle text-primary rounded-circle me-3">
          {{ initials }}
        </div>
        <div>
          <h6 class="mb-0 fw-semibold">Dr. {{ doctor.first_name }} {{ doctor.last_name }}</h6>
          <small class="text-muted">{{ doctor.department_name || 'General' }}</small>
        </div>
      </div>

      <div class="mb-3">
        <div v-if="doctor.qualification" class="small text-muted mb-1">
          <i class="bi bi-mortarboard me-1"></i>{{ doctor.qualification }}
        </div>
        <div v-if="doctor.experience_years" class="small text-muted mb-1">
          <i class="bi bi-briefcase me-1"></i>{{ doctor.experience_years }} years experience
        </div>
        <div v-if="doctor.consultation_fee" class="small text-success fw-medium">
          <i class="bi bi-currency-rupee me-1"></i>{{ doctor.consultation_fee }} consultation
        </div>
      </div>

      <button class="btn btn-primary btn-sm w-100" @click="$emit('book')">
        <i class="bi bi-calendar-plus me-1"></i>Book Appointment
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoctorCard',
  props: {
    doctor: { type: Object, required: true }
  },
  emits: ['book'],
  computed: {
    initials() {
      const f = this.doctor.first_name?.[0] || '';
      const l = this.doctor.last_name?.[0] || '';
      return (f + l).toUpperCase();
    }
  }
};
</script>

<style scoped>
.avatar {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}
</style>