<template>
  <div class="card border-0 shadow-sm h-100" :class="cardClass">
    <div class="card-body">
      <div class="d-flex align-items-center" :class="{ 'flex-row-reverse justify-content-between': iconRight }">
        <div class="stat-icon rounded-3 p-3" :class="[bgClass, iconRight ? 'ms-3' : 'me-3']">
          <i class="fs-4" :class="[icon, iconClass]"></i>
        </div>
        <div :class="{ 'text-end': iconRight }" class="px-2">
          <h3 class="fw-bold mb-0" :class="valueClass">{{ formattedValue }}</h3>
          <small class="text-muted">{{ label }}</small>
          <div v-if="trend !== null" class="mt-1">
            <small :class="trendClass">
              <i :class="trendIcon"></i> {{ Math.abs(trend) }}%
            </small>
          </div>
        </div>
      </div>
      <div v-if="$slots.footer" class="mt-3 pt-3 border-top">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    value: {
      type: [Number, String],
      default: 0
    },
    label: {
      type: String,
      required: true
    },
    variant: {
      type: String,
      default: 'primary',
      validator: (v) => ['primary', 'success', 'warning', 'info', 'danger', 'secondary'].includes(v)
    },
    iconRight: {
      type: Boolean,
      default: false
    },
    trend: {
      type: Number,
      default: null
    },
    cardClass: {
      type: String,
      default: ''
    },
    valueClass: {
      type: String,
      default: ''
    },
    formatNumber: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    bgClass() {
      return `bg-${this.variant}-subtle`;
    },
    iconClass() {
      return `text-${this.variant}`;
    },
    formattedValue() {
      if (!this.formatNumber || typeof this.value !== 'number') return this.value;
      return this.value.toLocaleString('en-IN');
    },
    trendClass() {
      return this.trend >= 0 ? 'text-success' : 'text-danger';
    },
    trendIcon() {
      return this.trend >= 0 ? 'bi bi-arrow-up' : 'bi bi-arrow-down';
    }
  }
};
</script>

<style scoped>
.stat-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>