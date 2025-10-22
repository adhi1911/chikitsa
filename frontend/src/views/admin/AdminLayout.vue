<template>
  <div class='admin-layout'>
    <Navbar/>
    <router-view/>
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