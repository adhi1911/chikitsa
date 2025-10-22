<template>
  <div class="patient-layout bg-light min-vh-100 d-flex flex-column">
    <Navbar />
    <div class="container flex-grow-1 py-5">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script>
import Navbar from '@/components/common/Navbar.vue'
import Footer from '@/components/common/Footer.vue'

export default {
  name: 'PatientLayout',
  components: { Navbar, Footer }
}
</script>

<style scoped>
.patient-layout {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>