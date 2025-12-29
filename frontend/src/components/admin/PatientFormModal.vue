<template>
  <div class="modal fade" ref="modal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content border-0 shadow">
       <!-- header -->
        <div class="modal-header" :class="isEdit ? 'bg-warning-subtle' : 'bg-primary text-white'">
          <h5 class="modal-title">
            <i :class="isEdit ? 'bi bi-pencil' : 'bi bi-person-plus'" class="me-2"></i>
            {{ isEdit ? 'Edit Patient' : 'Add Patient' }}
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            :class="{ 'btn-close-white': !isEdit }"
            data-bs-dismiss="modal"
          ></button>
        </div>

      <!-- body -->
        <form @submit.prevent="handleSubmit">
          <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
            
           <!-- acc info -->
            <div v-if="!isEdit">
              <h6 class="fw-semibold mb-3 text-primary">
                <i class="bi bi-person-badge me-2"></i>Account Information
              </h6>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label">Username <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input 
                      type="text" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.username }"
                      v-model="form.username"
                      placeholder="Choose a username"
                    >
                  </div>
                  <small v-if="errors.username" class="text-danger">{{ errors.username }}</small>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input 
                      type="email" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.email }"
                      v-model="form.email"
                      placeholder="patient@example.com"
                    >
                  </div>
                  <small v-if="errors.email" class="text-danger">{{ errors.email }}</small>
                </div>
                <div class="col-12">
                  <label class="form-label">Password <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input 
                      :type="showPassword ? 'text' : 'password'" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.password }"
                      v-model="form.password"
                      placeholder="Min 8 characters"
                    >
                    <button type="button" class="btn btn-outline-secondary" @click="showPassword = !showPassword">
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                  <small v-if="errors.password" class="text-danger">{{ errors.password }}</small>
                </div>
              </div>
            </div>

            <!-- personal  -->
            <h6 class="fw-semibold mb-3 text-primary">
              <i class="bi bi-card-list me-2"></i>Personal Details
            </h6>
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <label class="form-label">First Name <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control"
                  :class="{ 'is-invalid': errors.first_name }"
                  v-model="form.first_name"
                  placeholder="First name"
                >
                <small v-if="errors.first_name" class="text-danger">{{ errors.first_name }}</small>
              </div>
              <div class="col-md-6">
                <label class="form-label">Last Name <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control"
                  :class="{ 'is-invalid': errors.last_name }"
                  v-model="form.last_name"
                  placeholder="Last name"
                >
                <small v-if="errors.last_name" class="text-danger">{{ errors.last_name }}</small>
              </div>
              <div class="col-md-6">
                <label class="form-label">Date of Birth <span class="text-danger">*</span></label>
                <input 
                  type="date" 
                  class="form-control"
                  :class="{ 'is-invalid': errors.dob }"
                  v-model="form.dob"
                  :max="today"
                >
                <small v-if="errors.dob" class="text-danger">{{ errors.dob }}</small>
              </div>
              <div class="col-md-6">
                <label class="form-label">Gender <span class="text-danger">*</span></label>
                <select 
                  class="form-select"
                  :class="{ 'is-invalid': errors.gender }"
                  v-model="form.gender"
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
                <small v-if="errors.gender" class="text-danger">{{ errors.gender }}</small>
              </div>
              <div class="col-md-6">
                <label class="form-label">Blood Group</label>
                <select class="form-select" v-model="form.blood_group">
                  <option value="">Select blood group</option>
                  <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone <span class="text-danger">*</span></label>
                <input 
                  type="tel" 
                  class="form-control"
                  :class="{ 'is-invalid': errors.phone }"
                  v-model="form.phone"
                  placeholder="10-digit phone number"
                  maxlength="10"
                >
                <small v-if="errors.phone" class="text-danger">{{ errors.phone }}</small>
              </div>
              <div class="col-12">
                <label class="form-label">Address</label>
                <textarea 
                  class="form-control" 
                  v-model="form.address" 
                  rows="2"
                  placeholder="Full address"
                ></textarea>
              </div>
            </div>

            <!-- emergency -->
            <h6 class="fw-semibold mb-3 text-primary">
              <i class="bi bi-telephone me-2"></i>Emergency Contact
            </h6>
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <label class="form-label">Contact Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="form.emergency_contact_name"
                  placeholder="Emergency contact name"
                >
              </div>
              <div class="col-md-6">
                <label class="form-label">Contact Phone</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="form.emergency_contact_phone"
                  placeholder="10-digit phone"
                  maxlength="10"
                >
              </div>
            </div>

            <!-- medical history -->
            <h6 class="fw-semibold mb-3 text-primary">
              <i class="bi bi-heart-pulse me-2"></i>Medical History
            </h6>
            <div class="mb-3">
              <textarea 
                class="form-control" 
                v-model="form.medical_history" 
                rows="3"
                placeholder="Any pre-existing conditions, allergies, or important medical information"
              ></textarea>
            </div>

            <!-- error alert -->
            <div v-if="error" class="alert alert-danger">
              <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
            </div>
          </div>

          <!-- footer -->
          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="submit" 
              class="btn"
              :class="isEdit ? 'btn-warning' : 'btn-primary'"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ isEdit ? 'Update Patient' : 'Register Patient' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/services/api';

export default {
  name: 'PatientFormModal',
  emits: ['saved'],
  data() {
    return {
      modal: null,
      isEdit: false,
      patientId: null,
      saving: false,
      showPassword: false,
      error: '',
      errors: {},
      form: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        dob: '',
        gender: '',
        blood_group: '',
        phone: '',
        address: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        medical_history: ''
      },
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
      today: new Date().toISOString().split('T')[0]
    };
  },
  methods: {
    show(patient = null) {
      this.resetForm();
      
      if (patient) {
        this.isEdit = true;
        this.patientId = patient.id;
        this.form = {
          username: patient.username || '',
          email: patient.email || '',
          password: '',
          first_name: patient.first_name || '',
          last_name: patient.last_name || '',
          dob: patient.dob || '',
          gender: patient.gender || '',
          blood_group: patient.blood_group || '',
          phone: patient.phone || '',
          address: patient.address || '',
          emergency_contact_name: patient.emergency_contact_name || '',
          emergency_contact_phone: patient.emergency_contact_phone || '',
          medical_history: patient.medical_history || ''
        };
      }
      
      this.modal.show();
    },

    hide() {
      this.modal.hide();
    },

    resetForm() {
      this.form = {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        dob: '',
        gender: '',
        blood_group: '',
        phone: '',
        address: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        medical_history: ''
      };
      this.errors = {};
      this.error = '';
      this.isEdit = false;
      this.patientId = null;
      this.showPassword = false;
    },

    validate() {
      this.errors = {};

      if (!this.isEdit) {
        if (!this.form.username || this.form.username.length < 3) {
          this.errors.username = 'Username must be at least 3 characters';
        }
        if (!this.form.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
          this.errors.email = 'Valid email is required';
        }
        if (!this.form.password || this.form.password.length < 8) {
          this.errors.password = 'Password must be at least 8 characters';
        }
      }


      if (!this.form.first_name?.trim()) {
        this.errors.first_name = 'First name is required';
      }
      if (!this.form.last_name?.trim()) {
        this.errors.last_name = 'Last name is required';
      }
      if (!this.form.dob) {
        this.errors.dob = 'Date of birth is required';
      }
      if (!this.form.gender) {
        this.errors.gender = 'Gender is required';
      }
      if (!this.form.phone || !/^\d{10}$/.test(this.form.phone)) {
        this.errors.phone = 'Valid 10-digit phone is required';
      }

      return Object.keys(this.errors).length === 0;
    },

    async handleSubmit() {
      if (!this.validate()) return;

      try {
        this.saving = true;
        this.error = '';

        const payload = {
          first_name: this.form.first_name.trim(),
          last_name: this.form.last_name.trim(),
          dob: this.form.dob,
          gender: this.form.gender,
          blood_group: this.form.blood_group || null,
          phone: this.form.phone,
          address: this.form.address?.trim() || null,
          emergency_contact_name: this.form.emergency_contact_name?.trim() || null,
          emergency_contact_phone: this.form.emergency_contact_phone || null,
          medical_history: this.form.medical_history?.trim() || null
        };

        if (this.isEdit) {
          await api.patch(`/admin/patients/${this.patientId}`, payload);
        } else {
          payload.username = this.form.username.trim();
          payload.email = this.form.email.trim();
          payload.password = this.form.password;
          await api.post('/admin/patients', payload);
        }

        this.$emit('saved');
        this.hide();
      } catch (e) {
        console.error('Failed to save patient:', e);
        const msg = e.response?.data?.message || 'Failed to save patient';
        
        if (msg.toLowerCase().includes('username')) {
          this.errors.username = msg;
        } else if (msg.toLowerCase().includes('email')) {
          this.errors.email = msg;
        } else {
          this.error = msg;
        }
      } finally {
        this.saving = false;
      }
    }
  },
  mounted() {
    this.modal = new Modal(this.$refs.modal);
  }
};
</script>