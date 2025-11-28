<template>
  <div class="card border-0 shadow-sm">
    <!-- Header -->
    <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
      <h5 class="mb-0 fw-semibold">
        <i v-if="icon" :class="icon" class="me-2" :style="{ color: iconColor }"></i>
        {{ title }}
      </h5>
      <slot name="header-actions"></slot>
    </div>

    <!-- Body -->
    <div class="card-body p-0">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border" :class="`text-${variant}`"></div>
        <p class="mt-2 text-muted small">{{ loadingText }}</p>
      </div>

      <!-- Empty State -->
      <EmptyState 
        v-else-if="items.length === 0"
        :icon="emptyIcon"
        :message="emptyMessage"
      >
        <slot name="empty-action"></slot>
      </EmptyState>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th 
                v-for="col in columns" 
                :key="col.key"
                :class="col.headerClass"
                :style="col.width ? { width: col.width } : {}"
              >
                {{ col.label }}
              </th>
              <th v-if="$slots.actions" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in items" :key="item.id || index">
              <td 
                v-for="col in columns" 
                :key="col.key"
                :class="col.cellClass"
              >
                <slot :name="`cell-${col.key}`" :item="item" :value="getNestedValue(item, col.key)">
                  {{ formatValue(getNestedValue(item, col.key), col.format) }}
                </slot>
              </td>
              <td v-if="$slots.actions" class="text-end">
                <slot name="actions" :item="item" :index="index"></slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer" class="card-footer bg-white border-0 py-3">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
import EmptyState from './EmptyState.vue';

export default {
  name: 'DataTable',
  components: {
    EmptyState
  },
  props: {
    title: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    iconColor: {
      type: String,
      default: ''
    },
    columns: {
      type: Array,
      required: true
      // { key: 'name', label: 'Name', format: 'text', width: '200px', headerClass: '', cellClass: '' }
    },
    items: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    loadingText: {
      type: String,
      default: 'Loading...'
    },
    emptyIcon: {
      type: String,
      default: 'bi bi-inbox'
    },
    emptyMessage: {
      type: String,
      default: 'No data found'
    },
    variant: {
      type: String,
      default: 'primary'
    }
  },
  methods: {
    getNestedValue(obj, path) {
      return path.split('.').reduce((o, k) => (o || {})[k], obj);
    },
    formatValue(value, format) {
      if (value === null || value === undefined) return '-';
      
      switch (format) {
        case 'date':
          return new Date(value).toLocaleDateString('en-IN', { 
            day: 'numeric', 
            month: 'short', 
            year: 'numeric' 
          });
        case 'time':
          if (!value) return '-';
          const [hours, minutes] = value.split(':');
          const h = parseInt(hours);
          return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
        case 'datetime':
          return new Date(value).toLocaleString('en-IN');
        case 'currency':
          return `₹${Number(value).toLocaleString('en-IN')}`;
        case 'number':
          return Number(value).toLocaleString('en-IN');
        default:
          return value;
      }
    }
  }
};
</script>