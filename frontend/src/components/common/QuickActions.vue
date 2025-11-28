<template>
  <div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-0 py-3">
      <h5 class="mb-0 fw-semibold">
        <i class="bi bi-lightning me-2 text-warning"></i>{{ title }}
      </h5>
    </div>
    <div class="card-body">
      <div class="d-grid gap-2">
        <router-link 
          v-for="action in actions" 
          :key="action.to"
          :to="action.to" 
          class="btn text-start"
          :class="action.btnClass || 'btn-outline-primary'"
        >
          <i :class="action.icon" class="me-2"></i>{{ action.label }}
        </router-link>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickActions',
  props: {
    title: {
      type: String,
      default: 'Quick Actions'
    },
    actions: {
      type: Array,
      default: () => []
      // { to: '/path', icon: 'bi bi-icon', label: 'Label', btnClass: 'btn-outline-primary' }
    }
  }
};
</script>