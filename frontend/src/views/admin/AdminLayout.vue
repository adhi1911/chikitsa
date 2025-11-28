<template>
  <div class="admin-layout bg-light min-vh-100">
    <Navbar />

    <div class="d-flex">
      <!-- Sidebar -->
      <div 
        class="sidebar bg-light shadow-sm" 
        :class="{ 'sidebar-collapsed': sidebarCollapsed }"
      >
        <div class="sidebar-header p-3 border-bottom">
          <span v-if="!sidebarCollapsed" class="fw-bold text-primary">
            <i class="bi bi-shield-lock me-2"></i>Admin Panel
          </span>
          <i v-else class="bi bi-shield-lock text-primary"></i>
        </div>

        <nav class="sidebar-nav p-2">
          <ul class="nav flex-column">
            <li class="nav-item mb-1">
              <router-link 
                to="/admin/dashboard" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/admin/dashboard') }"
              >
                <i class="bi bi-speedometer2 me-2"></i>
                <span v-if="!sidebarCollapsed">Dashboard</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/admin/patients" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/admin/patients') }"
              >
                <i class="bi bi-people me-2"></i>
                <span v-if="!sidebarCollapsed">Patients</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/admin/doctors" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/admin/doctors') }"
              >
                <i class="bi bi-person-badge me-2"></i>
                <span v-if="!sidebarCollapsed">Doctors</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/admin/departments" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/admin/departments') }"
              >
                <i class="bi bi-building me-2"></i>
                <span v-if="!sidebarCollapsed">Departments</span>
              </router-link>
            </li>

            <li class="nav-item mb-1">
              <router-link 
                to="/admin/appointments" 
                class="nav-link rounded"
                :class="{ 'active': isActive('/admin/appointments') }"
              >
                <i class="bi bi-calendar-check me-2"></i>
                <span v-if="!sidebarCollapsed">Appointments</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- Collapse Toggle -->
        <div class="sidebar-footer p-3 border-top mt-auto">
          <button 
            class="btn btn-outline-primary btn-sm w-100"
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
import Navbar from '@/components/common/Navbar.vue';
export default {
  name: 'AdminLayout',
  components: {
    Navbar
  },
  data() {
    return {
      sidebarCollapsed: false
    };
  },
  methods: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
    isActive(path) {
      return this.$route.path.startsWith(path);
    }
  }
};
</script>

<style scoped>
/* Sidebar Styles */
.sidebar {
  width: 250px;
  min-height: calc(100vh - 76px);
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa; /* Light gray background */
  border-right: 1px solid #dee2e6; /* Subtle border */
}

.sidebar-collapsed {
  width: 70px;
}

.sidebar-header {
  font-size: 1.2rem;
  font-weight: 600;
  color: #0d6efd; /* Primary blue for branding */
}

.sidebar-nav .nav-link {
  padding: 10px 15px;
  transition: all 0.2s ease;
  color: #495057; /* Neutral text color */
  font-size: 0.95rem;
}

.sidebar-nav .nav-link:hover {
  background-color: rgba(13, 110, 253, 0.1); /* Subtle blue hover */
  color: #0d6efd; /* Blue text on hover */
}

.sidebar-nav .nav-link.active {
  background-color: #0d6efd; /* Primary blue for active */
  color: #ffffff !important; /* White text for active */
  font-weight: 600;
}

.sidebar-footer {
  padding: 10px;
}

.sidebar-footer .btn {
  font-size: 0.9rem;
  color: #0d6efd;
  border-color: #0d6efd;
}

.sidebar-footer .btn:hover {
  background-color: #0d6efd;
  color: #ffffff;
}

/* Main Content */
.main-content {
  min-height: calc(100vh - 76px);
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 1000;
    left: -250px;
  }

  .sidebar.show {
    left: 0;
  }

  .sidebar-collapsed {
    left: -70px;
  }
}
</style>