<template>
  <div class='admin-layout bg-light min-vh-100'>
    <Navbar/>
    <div class="container py-4">
      <router-view/>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/common/Navbar.vue';
export default {
  name: 'AdminLayout',
  components:{
    Navbar
  }
}
</script>

<style>

</style>