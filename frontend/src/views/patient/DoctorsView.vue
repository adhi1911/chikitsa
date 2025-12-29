<template>
  <div class="doctors-view">
    <PageHeader title="Find a Doctor" subtitle="Search and book appointments" />

    <!-- Search & Filter -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search by name, specialization..."
                v-model="searchQuery"
              >
            </div>
          </div>
          <div class="col-md-4">
            <select class="form-select" v-model="filterDepartment">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="sortBy">
              <option value="name">Sort by Name</option>
              <option value="experience">Sort by Experience</option>
              <option value="fee_low">Fee: Low to High</option>
              <option value="fee_high">Fee: High to Low</option>
            </select>
          </div>
          <div class="col-md-1">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters" title="Reset">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Count -->
    <div v-if="!loading && doctors.length > 0" class="mb-3">
      <small class="text-muted">
        Showing {{ filteredDoctors.length }} of {{ doctors.length }} doctors
      </small>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Empty State -->
    <div v-else-if="filteredDoctors.length === 0" class="text-center py-5">
      <i class="bi bi-search text-muted" style="font-size: 4rem;"></i>
      <h5 class="mt-3 text-muted">No doctors found</h5>
      <p class="text-muted">
        {{ searchQuery || filterDepartment ? 'Try adjusting your search or filters' : 'No doctors available at the moment' }}
      </p>
      <button v-if="searchQuery || filterDepartment" class="btn btn-outline-primary" @click="resetFilters">
        <i class="bi bi-arrow-counterclockwise me-2"></i>Reset Filters
      </button>
    </div>

    <!-- Doctors Grid -->
    <div v-else class="row g-4">
      <div v-for="doctor in filteredDoctors" :key="doctor.id" class="col-md-6 col-lg-4">
        <DoctorCard :doctor="doctor" @book="openBooking(doctor)" />
      </div>
    </div>

    <!-- Booking Modal -->
    <BookingModal ref="bookingModal" :doctor="selectedDoctor" @booked="onBooked" />
  </div>
</template>

<script>
import api from '@/services/api';
import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import DoctorCard from '@/components/patient/DoctorCard.vue';
import BookingModal from '@/components/patient/BookingModal.vue';
export default {
  name: 'DoctorsView',
  components: { PageHeader, LoadingSpinner, DoctorCard, BookingModal },
  data() {
    return {
      loading: true,
      doctors: [],
      departments: [],
      selectedDoctor: null,
      searchQuery: '',
      filterDepartment: '',
      sortBy: 'name'
    };
  },
  computed: {
    filteredDoctors() {
      let result = [...this.doctors];

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(doc =>
          doc.first_name?.toLowerCase().includes(query) ||
          doc.last_name?.toLowerCase().includes(query) ||
          doc.department_name?.toLowerCase().includes(query) ||
          doc.qualification?.toLowerCase().includes(query)
        );
      }

      // Department filter
      if (this.filterDepartment) {
        result = result.filter(doc => doc.department_id === this.filterDepartment);
      }

      // Sorting
      result.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
          case 'experience':
            return (b.experience_years || 0) - (a.experience_years || 0);
          case 'fee_low':
            return (a.consultation_fee || 0) - (b.consultation_fee || 0);
          case 'fee_high':
            return (b.consultation_fee || 0) - (a.consultation_fee || 0);
          default:
            return 0;
        }
      });

      return result;
    }
  },
  methods: {
    async fetchDepartments() {
      try {
        const res = await api.get('/admin/departments');
        this.departments = (res.data?.data?.departments || []).filter(d => d.is_active);
      } catch (e) {
        console.error('Failed to fetch departments:', e);
      }
    },

    async fetchDoctors() {
      try {
        this.loading = true;
        const res = await api.get('/admin/doctors');

        this.doctors = res.data?.data?.doctors || [];
        console.log('Doctors loaded:', this.doctors.length); // Debug log
      } catch (e) {
        console.error('Failed to fetch doctors:', e);
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.searchQuery = '';
      this.filterDepartment = '';
      this.sortBy = 'name';
    },

    openBooking(doctor) {
      this.selectedDoctor = doctor;
      this.$refs.bookingModal.show();
    },

    onBooked() {
      this.$router.push('/patient/appointments');
    }
  },
  mounted() {
    this.fetchDepartments();
    this.fetchDoctors();
  }
};
</script>