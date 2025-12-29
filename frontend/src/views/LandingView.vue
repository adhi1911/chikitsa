<template>
  <div class="landing-page">
    <Navbar/>
    <HeroSection/>
    <FeaturesSection/>
    <Footer/>
  </div>
</template>

<script>
import Navbar from '@/components/common/Navbar.vue';
import HeroSection from '@/components/common/HeroSection.vue';
import FeaturesSection from '@/components/common/FeaturesSection.vue';
import Footer from '@/components/common/Footer.vue';

export default {
    name: 'LandingView',
    components:{
        Navbar,
        HeroSection,
        FeaturesSection,
        Footer
    }

}
</script>

<style>

</style>