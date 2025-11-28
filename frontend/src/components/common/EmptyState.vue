<template>
  <div class="empty-state text-center py-5">
    <i :class="icon" class="display-4 text-muted opacity-50"></i>
    <p class="mt-3 text-muted mb-0">{{ message }}</p>
    <div v-if="$slots.default" class="mt-3">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    icon: {
      type: String,
      default: 'bi bi-inbox'
    },
    message: {
      type: String,
      default: 'No data found'
    }
  }
};
</script>