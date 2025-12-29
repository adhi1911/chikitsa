<template>
  <div class="patient-layout bg-light min-vh-100">
    <Navbar />
    <div class="d-flex">
      <!-- Sidebar -->
      <div class="sidebar bg-white shadow-sm" :class="{ 'sidebar-collapsed': collapsed }">
        <nav class="sidebar-nav p-2">
          <ul class="nav flex-column">
            <li class="nav-item mb-1">
              <router-link to="/patient/dashboard" class="nav-link rounded" :class="{ active: isActive('/patient/dashboard') }">
                <i class="bi bi-grid-1x2 me-2"></i>
                <span v-if="!collapsed">Dashboard</span>
              </router-link>
            </li>
            <li class="nav-item mb-1">
              <router-link to="/patient/appointments" class="nav-link rounded" :class="{ active: isActive('/patient/appointments') }">
                <i class="bi bi-calendar-check me-2"></i>
                <span v-if="!collapsed">Appointments</span>
              </router-link>
            </li>
            <li class="nav-item mb-1">
              <router-link to="/patient/doctors" class="nav-link rounded" :class="{ active: isActive('/patient/doctors') }">
                <i class="bi bi-search me-2"></i>
                <span v-if="!collapsed">Find Doctors</span>
              </router-link>
            </li>
            <li class="nav-item mb-1">
              <router-link to="/patient/records" class="nav-link rounded" :class="{ active: isActive('/patient/records') }">
                <i class="bi bi-file-medical me-2"></i>
                <span v-if="!collapsed">Medical Records</span>
              </router-link>
            </li>
            <li class="nav-item mb-1">
              <router-link to="/patient/profile" class="nav-link rounded" :class="{ active: isActive('/patient/profile') }">
                <i class="bi bi-person me-2"></i>
                <span v-if="!collapsed">Profile</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <div class="sidebar-footer p-3 border-top mt-auto">
          <button class="btn btn-outline-primary btn-sm w-100" @click="collapsed = !collapsed">
            <i :class="collapsed ? 'bi bi-chevron-right' : 'bi bi-chevron-left'"></i>
            <span v-if="!collapsed" class="ms-2">Collapse</span>
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
import Navbar from '@/components/common/Navbar.vue'

export default {
  name: 'PatientLayout',
  components: { Navbar},
  data(){
    return{
      collapsed: false
    }
  },
  methods:{
    isActive(path){
      return this.$route.path.startsWith(path);
    }
  }
}
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