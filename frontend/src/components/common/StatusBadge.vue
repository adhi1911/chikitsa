<template>
  <span class="badge" :class="badgeClass">{{ displayText }}</span>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    status: {
      type: String,
      required: true
    },
    statusMap: {
      type: Object,
      default: () => ({
        scheduled: { class: 'bg-info-subtle text-info', text: 'Scheduled' },
        completed: { class: 'bg-success-subtle text-success', text: 'Completed' },
        cancelled: { class: 'bg-danger-subtle text-danger', text: 'Cancelled' },
        no_show: { class: 'bg-warning-subtle text-warning', text: 'No Show' },
        pending: { class: 'bg-warning-subtle text-warning', text: 'Pending' },
        active: { class: 'bg-success-subtle text-success', text: 'Active' },
        inactive: { class: 'bg-secondary-subtle text-secondary', text: 'Inactive' },
        approved: { class: 'bg-success-subtle text-success', text: 'Approved' },
        rejected: { class: 'bg-danger-subtle text-danger', text: 'Rejected' }
      })
    }
  },
  computed: {
    statusInfo() {
      return this.statusMap[this.status] || { class: 'bg-secondary', text: this.status };
    },
    badgeClass() {
      return this.statusInfo.class;
    },
    displayText() {
      return this.statusInfo.text;
    }
  }
};
</script>