<template>
  <div class="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
    <div class="container">
        <router-link class="navbar-brand d-flex align-items-center" to="/">
            <div class="brand-icon me-2">
                <i class="fas fa-plus-circle text-primary"></i>
            </div>
            <span class="fw-blod text-dark">Chikitsa</span>
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
            <div class="navbar-nav ms-auto">
                <!-- login dropdown -->
                 <div class="nav-item dropdown me-3">
                    <a class="nav-link dropdown-toggle text-dark fw-medium" href="#" role="button" 
                        data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-sign-in-alt me-1"></i>
                        Login
                    </a>  
                    <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                        <li>
                            <a class="dropdown-item py-2" @click="navigateToLogin('admin')" href="#">
                            <i class="fas fa-user-shield text-danger me-2"></i>
                            Administrator
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item py-2" @click="navigateToLogin('doctor')" href="#">
                            <i class="fas fa-user-md text-success me-2"></i>
                            Doctor
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item py-2" @click="navigateToLogin('patient')" href="#">
                            <i class="fas fa-user text-primary me-2"></i>
                            Patient
                            </a>
                        </li>
                    </ul>
                 </div>

                <!-- register button -->
                <router-link to="/register" class="btn btn-primary px-4 rounded-pill">
                    <i class="fas fa-user-plus me-1"></i>
                    Register
                </router-link>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
export default {
    name: 'Navbar',
    methods:{
        navigateToLogin(role){
            this.$router.push({name:'login',params:{role}})
        }
    }
}
</script>

<style scoped>

.navbar-brand {
  font-size: 1.5rem;
  transition: all 0.3s ease;
}

.brand-icon {
  font-size: 1.8rem;
}

.dropdown-menu {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.dropdown-item {
  border-radius: 8px;
  margin: 2px 8px;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

</style>