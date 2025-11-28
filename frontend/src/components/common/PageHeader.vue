<template>
  <div class="page-header d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 class="fw-bold mb-1">{{ title }}</h2>
      <p v-if="subtitle" class="text-muted mb-0">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="d-flex gap-2">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
};
</script>