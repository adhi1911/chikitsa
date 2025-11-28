<template>
  <div class="medical-history">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-semibold mb-0">
        <i class="bi bi-clock-history me-2 text-primary"></i>{{ title }}
      </h5>
      <div v-if="showFilters" class="d-flex gap-2">
        <select class="form-select form-select-sm" v-model="filter" style="width: auto;">
          <option value="all">All Records</option>
          <option value="recent">Last 30 Days</option>
          <option value="year">This Year</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <LoadingSpinner v-if="loading" size="sm" text="Loading records..." />

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredRecords.length === 0"
      icon="bi bi-file-medical"
      message="No medical records found"
    />

    <!-- Records List -->
    <div v-else>
      <!-- Grouped by Date -->
      <div v-if="groupByDate">
        <div v-for="(group, date) in groupedRecords" :key="date" class="mb-4">
          <h6 class="text-muted small fw-semibold mb-3">
            <i class="bi bi-calendar3 me-1"></i>{{ formatGroupDate(date) }}
          </h6>
          <MedicalRecordCard
            v-for="record in group"
            :key="record.id"
            :record="record"
            :show-print="showPrint"
            @view="handleView"
            @print="handlePrint"
          />
        </div>
      </div>

      <!-- Flat List -->
      <div v-else>
        <MedicalRecordCard
          v-for="record in displayedRecords"
          :key="record.id"
          :record="record"
          :show-print="showPrint"
          @view="handleView"
          @print="handlePrint"
        />
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !groupByDate" class="text-center mt-3">
        <button class="btn btn-outline-primary btn-sm" @click="loadMore">
          <i class="bi bi-arrow-down-circle me-1"></i>Load More
        </button>
      </div>
    </div>

    <!-- Medical Record Modal -->
    <MedicalRecordModal
      ref="recordModal"
      :record="selectedRecord"
      :show-doctor-notes="showDoctorNotes"
    />
  </div>
</template>

<script>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import MedicalRecordCard from './MedicalRecordCard.vue';
import MedicalRecordModal from './MedicalRecordModal.vue';

export default {
  name: 'MedicalHistory',
  components: {
    LoadingSpinner,
    EmptyState,
    MedicalRecordCard,
    MedicalRecordModal
  },
  props: {
    title: {
      type: String,
      default: 'Medical History'
    },
    records: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    showFilters: {
      type: Boolean,
      default: true
    },
    showPrint: {
      type: Boolean,
      default: true
    },
    showDoctorNotes: {
      type: Boolean,
      default: true
    },
    groupByDate: {
      type: Boolean,
      default: false
    },
    initialLimit: {
      type: Number,
      default: 5
    }
  },
  emits: ['view', 'print'],
  data() {
    return {
      filter: 'all',
      displayLimit: this.initialLimit,
      selectedRecord: null
    };
  },
  computed: {
    filteredRecords() {
      let records = [...this.records];
      
      const now = new Date();
      if (this.filter === 'recent') {
        const thirtyDaysAgo = new Date(now.setDate(now.getDate() - 30));
        records = records.filter(r => new Date(r.visit_date || r.created_at) >= thirtyDaysAgo);
      } else if (this.filter === 'year') {
        const startOfYear = new Date(now.getFullYear(), 0, 1);
        records = records.filter(r => new Date(r.visit_date || r.created_at) >= startOfYear);
      }

      // Sort by date descending
      return records.sort((a, b) => 
        new Date(b.visit_date || b.created_at) - new Date(a.visit_date || a.created_at)
      );
    },
    displayedRecords() {
      return this.filteredRecords.slice(0, this.displayLimit);
    },
    hasMore() {
      return this.filteredRecords.length > this.displayLimit;
    },
    groupedRecords() {
      const groups = {};
      this.filteredRecords.forEach(record => {
        const date = (record.visit_date || record.created_at)?.split('T')[0];
        if (!groups[date]) {
          groups[date] = [];
        }
        groups[date].push(record);
      });
      return groups;
    }
  },
  methods: {
    formatGroupDate(date) {
      return new Date(date).toLocaleDateString('en-IN', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    },
    loadMore() {
      this.displayLimit += this.initialLimit;
    },
    handleView(record) {
      this.selectedRecord = record;
      this.$refs.recordModal.show();
      this.$emit('view', record);
    },
    handlePrint(record) {
      this.$emit('print', record);
    }
  },
  watch: {
    records: {
      handler() {
        this.displayLimit = this.initialLimit;
      },
      deep: true
    }
  }
};
</script>