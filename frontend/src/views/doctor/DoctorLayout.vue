<template>
  <div class="doctor-layout bg-light min-vh-100">
    <Navbar />
    <div class="d-flex">
      <!-- Sidebar -->
      <div 
        class="sidebar bg-white shadow-sm" 
        :class="{ 'sidebar-collapsed': sidebarCollapsed }"
      >
        <!-- Doctor Info Header -->
        <!-- <div class="sidebar-header p-3 border-bottom"> -->
          <!-- <div v-if="!sidebarCollapsed && user" class="d-flex align-items-center">
            <div class="avatar bg-success-subtle rounded-circle me-2">
              <span class="text-success fw-bold">{{ doctorInitials }}</span>
            </div>
            <div class="overflow-hidden">
              <div class="fw-semibold text-truncate small">Dr. {{ doctorName }}</div>
              <small class="text-muted text-truncate d-block" style="font-size: 0.75rem;">{{ specialization }}</small>
            </div>
          </div>
          <div v-else-if="sidebarCollapsed" class="text-center">
            <div class="avatar-sm bg-success-subtle rounded-circle mx-auto">
              <span class="text-success fw-bold small">{{ doctorInitials }}</span>
            </div>
          </div>
          <div v-else>
            <i class="bi bi-person-circle text-success fs-4"></i>
          </div> -->
        <!-- </div> -->

        <!-- Navigation -->
        <nav class="sidebar-nav p-2">
          <ul class="nav flex-column">
            <li class="nav-item mb-1">
              <router-link 
                to="/doctor/dashboard" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/doctor/dashboard') }"
              >
                <i class="bi bi-grid-1x2 me-2"></i>
                <span v-if="!sidebarCollapsed">Dashboard</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/doctor/appointments" 
                class="nav-link rounded d-flex align-items-center"
                :class="{ 'active': isActive('/doctor/appointments') }"
              >
                <i class="bi bi-calendar-check me-2"></i>
                <span v-if="!sidebarCollapsed" class="flex-grow-1">Appointments</span>
                <span v-if="!sidebarCollapsed && todayCount > 0" class="badge bg-primary rounded-pill">
                  {{ todayCount }}
                </span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/doctor/patients" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/doctor/patients') }"
              >
                <i class="bi bi-people me-2"></i>
                <span v-if="!sidebarCollapsed">My Patients</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/doctor/schedule" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/doctor/schedule') }"
              >
                <i class="bi bi-clock me-2"></i>
                <span v-if="!sidebarCollapsed">Schedule</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/doctor/profile" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/doctor/profile') }"
              >
                <i class="bi bi-person me-2"></i>
                <span v-if="!sidebarCollapsed">Profile</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- Sidebar Footer -->
        <div class="sidebar-footer p-3 border-top mt-auto">
          <button 
            class="btn btn-outline-success btn-sm w-100"
            @click="toggleSidebar"
          >
            <i :class="sidebarCollapsed ? 'bi bi-chevron-right' : 'bi bi-chevron-left'"></i>
            <span v-if="!sidebarCollapsed" class="ms-2">Collapse</span>
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="main-content flex-grow-1">
        <div class="container-fluid py-4 px-4">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import api from '@/services/api';
import Navbar from '@/components/common/Navbar.vue';

export default {
  name: 'DoctorLayout',
  components: {
    Navbar
  },
  data() {
    return {
      sidebarCollapsed: false,
      todayCount: 0
    };
  },
  computed: {
    ...mapGetters('auth', ['user', 'isAuthenticated']),
    // doctorName() {
    //   if (!this.user) return 'Doctor';
    //   return `${this.user.first_name || ''} ${this.user.last_name || ''}`.trim() || 'Doctor';
    // },
    // doctorInitials() {
    //   if (!this.user) return 'DR';
    //   const first = this.user.first_name?.[0] || '';
    //   const last = this.user.last_name?.[0] || '';
    //   return (first + last).toUpperCase() || 'DR';
    // },
    // specialization() {
    //   return this.user?.specialization || 'General';
    // }
  },
  methods: {
    ...mapActions('auth', ['logout']),
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
    isActive(path) {
      return this.$route.path.startsWith(path);
    },
    async fetchTodayCount() {
      try {
        const response = await api.get('/doctor/dashboard/stats');
        if (response.data.status === 'success') {
          this.todayCount = response.data.data.stats?.today?.pending || 0;
        }
      } catch (error) {
        console.error('Error fetching today count:', error);
      }
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.fetchTodayCount();
    }
  }
};
</script>


<style scoped>
.sidebar {
  width: 220px;
  min-height: calc(100vh - 56px);
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
}
.sidebar-collapsed {
  width: 70px;
}
.sidebar-nav .nav-link {
  color: #495057;
  padding: 0.6rem 1rem;
  display: flex;
  align-items: center;
}
.sidebar-nav .nav-link:hover {
  background: #e3f2fd;
  color: #0d6efd;
}
.sidebar-nav .nav-link.active {
  background: #0d6efd;
  color: white;
}
.main-content {
  min-height: calc(100vh - 56px);
  overflow-y: auto;
}
</style>

