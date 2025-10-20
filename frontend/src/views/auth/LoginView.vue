<template>
  <div class="login-page bg-light min-vh-100 d-flex flex-column">
    <Navbar />
    <div class="container flex-grow-1 d-flex align-items-center justify-content-center">
      <LoginForm :role="role" />
    </div>
    <Footer />
  </div>
</template>

<script>
import Navbar from '@/components/common/Navbar.vue'
import Footer from '@/components/common/Footer.vue'
import LoginForm from '@/components/forms/LoginForm.vue'

export default {
    name: 'LoginView',
    components: {
        Navbar, Footer, LoginForm
    },
    computed: {
        role() {
            return this.$route.params.role || 'user';
        }
    }

}
</script>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>