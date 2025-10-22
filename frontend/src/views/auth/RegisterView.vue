<template>
  <div class="register-page bg-light min-vh-100 d-flex flex-column">
    <Navbar />
    <div class="container flex-grow-1 d-flex align-items-center justify-content-center">
      <RegisterForm/>
    </div>
    <Footer/>
  </div>
</template>

<script>
import Navbar from '@/components/common/Navbar.vue'
import Footer from '@/components/common/Footer.vue'
import RegisterForm from '@/components/forms/RegisterForm.vue'

export default {
    name: 'RegisterView',
    components: {
        Navbar, Footer, RegisterForm
    }

}
</script>

<style scoped>
.register-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>


