<template>
  <div class="prescription-view">
    <div v-if="!prescription || prescription.length === 0" class="text-center py-4">
      <i class="bi bi-capsule text-muted fs-1"></i>
      <p class="text-muted mt-2">No prescription</p>
    </div>

    <div v-else>
      <!-- Medicines List -->
      <div class="table-responsive">
        <table class="table table-sm mb-0">
          <thead class="table-light">
            <tr>
              <th>#</th>
              <th>Medicine</th>
              <th>Dosage</th>
              <th>Frequency</th>
              <th>Duration</th>
              <th v-if="showInstructions">Instructions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(med, index) in prescription" :key="index">
              <td>{{ index + 1 }}</td>
              <td class="fw-medium">{{ med.medicine_name || med.name }}</td>
              <td>{{ med.dosage }}</td>
              <td>
                <span class="badge bg-light text-dark">
                  {{ formatFrequency(med.frequency) }}
                </span>
              </td>
              <td>{{ med.duration }}</td>
              <td v-if="showInstructions">
                <small class="text-muted">{{ med.instructions || '-' }}</small>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Print Button -->
      <div v-if="showPrint" class="mt-3">
        <button class="btn btn-outline-primary btn-sm" @click="printPrescription">
          <i class="bi bi-printer me-1"></i>Print Prescription
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrescriptionView',
  props: {
    prescription: { type: Array, default: () => [] },
    showInstructions: { type: Boolean, default: true },
    showPrint: { type: Boolean, default: false }
  },
  methods: {
    formatFrequency(frequency) {
      const map = {
        'Once daily': 'Once Daily',
        'Twice daily': 'Twice Daily',
        'Thrice daily': 'Thrice Daily',
        'once_daily': 'Once Daily',
        'twice_daily': 'Twice Daily',
        'thrice_daily': 'Thrice Daily',
        'four_times_daily': '4x Daily',
        'every_4_hours': 'Every 4 Hrs',
        'every_6_hours': 'Every 6 Hrs',
        'every_8_hours': 'Every 8 Hrs',
        'as_needed': 'As Needed',
        'As needed': 'As Needed',
        'before_meals': 'Before Meals',
        'after_meals': 'After Meals',
        'at_bedtime': 'At Bedtime'
      };
      return map[frequency] || frequency;
    },
    printPrescription() {
      window.print();
    }
  }
};
</script>