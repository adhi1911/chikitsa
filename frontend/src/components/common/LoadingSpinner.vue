<template>
  <div class="loading-spinner text-center" :class="containerClass">
    <div 
      class="spinner-border" 
      :class="[`text-${variant}`, sizeClass]"
      role="status"
    >
      <span class="visually-hidden">Loading...</span>
    </div>
    <p v-if="text" class="mt-2 text-muted" :class="textClass">{{ text }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    variant: {
      type: String,
      default: 'primary'
    },
    size: {
      type: String,
      default: 'md',
      validator: (v) => ['sm', 'md', 'lg'].includes(v)
    },
    text: {
      type: String,
      default: ''
    },
    fullPage: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    sizeClass() {
      if (this.size === 'sm') return 'spinner-border-sm';
      if (this.size === 'lg') return 'spinner-border-lg';
      return '';
    },
    containerClass() {
      return this.fullPage ? 'py-5' : 'py-3';
    },
    textClass() {
      return this.size === 'sm' ? 'small' : '';
    }
  }
};
</script>

<style scoped>
.spinner-border-lg {
  width: 3rem;
  height: 3rem;
}
</style>