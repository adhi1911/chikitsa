<template>
  <div class="modal fade" :id="modalId" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header" :class="headerClass">
          <h5 class="modal-title">
            <i v-if="icon" :class="icon" class="me-2"></i>
            {{ title }}
          </h5>
          <button type="button" class="btn-close" :class="{ 'btn-close-white': variant === 'danger' }" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p class="mb-0">{{ message }}</p>
          <slot></slot>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">
            {{ cancelText }}
          </button>
          <button 
            type="button" 
            class="btn"
            :class="`btn-${variant}`"
            @click="handleConfirm"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'ConfirmModal',
  props: {
    modalId: {
      type: String,
      default: 'confirmModal'
    },
    title: {
      type: String,
      default: 'Confirm'
    },
    message: {
      type: String,
      default: 'Are you sure?'
    },
    icon: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: 'primary'
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm'],
  data() {
    return {
      modal: null
    };
  },
  computed: {
    headerClass() {
      if (this.variant === 'danger') return 'bg-danger text-white';
      if (this.variant === 'warning') return 'bg-warning';
      return '';
    }
  },
  methods: {
    handleConfirm() {
      this.$emit('confirm');
    },
    show() {
      this.modal?.show();
    },
    hide() {
      this.modal?.hide();
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>