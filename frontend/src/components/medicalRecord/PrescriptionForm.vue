<template>
  <div class="prescription-form">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="mb-0 fw-semibold">
        <i class="bi bi-capsule me-2 text-primary"></i>Prescription
      </h6>
      <button type="button" class="btn btn-sm btn-outline-primary" @click="addMedicine">
        <i class="bi bi-plus-lg me-1"></i>Add Medicine
      </button>
    </div>

    <div v-if="items.length === 0" class="text-center py-4 bg-light rounded-3">
      <i class="bi bi-capsule text-muted fs-1"></i>
      <p class="text-muted mt-2 mb-0">No medicines added yet</p>
    </div>

    <div v-else class="medicines-list">
      <div 
        v-for="(medicine, index) in items" 
        :key="index"
        class="medicine-item card border mb-3"
      >
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="badge bg-primary">Medicine {{ index + 1 }}</span>
            <button 
              type="button"
              class="btn btn-sm btn-outline-danger"
              @click="removeMedicine(index)"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>

          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label small fw-medium">Medicine Name *</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="medicine.medicine_name"
                placeholder="e.g., Paracetamol 500mg"
                required
              >
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-medium">Dosage</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="medicine.dosage"
                placeholder="e.g., 1 tablet"
              >
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-medium">Frequency</label>
              <select class="form-select" v-model="medicine.frequency">
                <option value="">Select</option>
                <option value="once_daily">Once Daily</option>
                <option value="twice_daily">Twice Daily</option>
                <option value="thrice_daily">Thrice Daily</option>
                <option value="four_times_daily">Four Times Daily</option>
                <option value="every_4_hours">Every 4 Hours</option>
                <option value="every_6_hours">Every 6 Hours</option>
                <option value="every_8_hours">Every 8 Hours</option>
                <option value="as_needed">As Needed (SOS)</option>
                <option value="before_meals">Before Meals</option>
                <option value="after_meals">After Meals</option>
                <option value="at_bedtime">At Bedtime</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-medium">Duration</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="medicine.duration"
                placeholder="e.g., 5 days"
              >
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-medium">Instructions</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="medicine.instructions"
                placeholder="e.g., Take with food"
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrescriptionForm',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  computed: {
    items() {
      return this.modelValue || [];
    }
  },
  methods: {
    addMedicine() {
      const newItems = [...this.items, {
        medicine_name: '',
        dosage: '',
        frequency: '',
        duration: '',
        instructions: ''
      }];
      this.$emit('update:modelValue', newItems);
    },
    removeMedicine(index) {
      const newItems = this.items.filter((_, i) => i !== index);
      this.$emit('update:modelValue', newItems);
    }
  }
};
</script>

<style scoped>
.medicine-item {
  transition: box-shadow 0.2s;
}
.medicine-item:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
</style>