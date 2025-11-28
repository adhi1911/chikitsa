<template>
  <div class="profile-view">
    <PageHeader 
      title="My Profile" 
      subtitle="Manage your profile and settings"
    />

    <LoadingSpinner v-if="loading" variant="success" text="Loading profile..." />

    <div v-else class="row g-4">
      <!-- Profile Card -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center py-4">
            <!-- Avatar -->
            <div class="avatar-xl bg-success-subtle rounded-circle mx-auto mb-3">
              <span class="text-success fw-bold display-6">{{ doctorInitials }}</span>
            </div>
            
            <h4 class="mb-1">Dr. {{ profile.name }}</h4>
            <p class="text-muted mb-2">{{ profile.specialization || 'General Physician' }}</p>
            
            <div class="d-flex justify-content-center gap-2 mb-3">
              <span class="badge bg-success-subtle text-success">
                <i class="bi bi-patch-check-fill me-1"></i>Verified
              </span>
              <span v-if="profile.experience_years" class="badge bg-primary-subtle text-primary">
                {{ profile.experience_years }} yrs exp
              </span>
            </div>

            <hr>

            <div class="text-start small">
              <div class="mb-2">
                <i class="bi bi-envelope text-muted me-2"></i>
                {{ profile.email }}
              </div>
              <div class="mb-2">
                <i class="bi bi-telephone text-muted me-2"></i>
                {{ profile.phone || 'Not provided' }}
              </div>
              <div v-if="profile.qualification" class="mb-2">
                <i class="bi bi-mortarboard text-muted me-2"></i>
                {{ profile.qualification }}
              </div>
              <div v-if="profile.license_number">
                <i class="bi bi-card-text text-muted me-2"></i>
                License: {{ profile.license_number }}
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="card border-0 shadow-sm mt-4">
          <div class="card-header bg-white border-0 py-3">
            <h6 class="mb-0 fw-semibold">
              <i class="bi bi-bar-chart me-2 text-success"></i>Statistics
            </h6>
          </div>
          <div class="card-body">
            <div class="row g-3 text-center">
              <div class="col-6">
                <div class="bg-light rounded-3 p-3">
                  <h4 class="fw-bold text-success mb-1">{{ profileStats.total_patients || 0 }}</h4>
                  <small class="text-muted">Total Patients</small>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-light rounded-3 p-3">
                  <h4 class="fw-bold text-primary mb-1">{{ profileStats.total_appointments || 0 }}</h4>
                  <small class="text-muted">Appointments</small>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-light rounded-3 p-3">
                  <h4 class="fw-bold text-info mb-1">{{ profileStats.this_month?.total  || 0 }}</h4>
                  <small class="text-muted">This Month</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Profile Form -->
      <div class="col-lg-8">
        <!-- Personal Information -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-person me-2 text-primary"></i>Personal Information
            </h5>
            <button 
              class="btn btn-sm btn-outline-primary"
              @click="toggleEdit('personal')"
            >
              <i :class="editing.personal ? 'bi bi-x-lg' : 'bi bi-pencil'" class="me-1"></i>
              {{ editing.personal ? 'Cancel' : 'Edit' }}
            </button>
          </div>
          <div class="card-body">
            <form @submit.prevent="savePersonalInfo">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.name"
                    :disabled="!editing.personal"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    v-model="form.email"
                    disabled
                  >
                  <small class="text-muted">Email cannot be changed</small>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Phone</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="form.phone"
                    :disabled="!editing.personal"
                    placeholder="Enter phone number"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Date of Birth</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="form.date_of_birth"
                    :disabled="!editing.personal"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Gender</label>
                  <select class="form-select" v-model="form.gender" :disabled="!editing.personal">
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Address</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.address"
                    :disabled="!editing.personal"
                    placeholder="Enter address"
                  >
                </div>
              </div>

              <div v-if="editing.personal" class="mt-3">
                <button type="submit" class="btn btn-success" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-lg me-2"></i>Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Professional Information -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-briefcase me-2 text-success"></i>Professional Information
            </h5>
            <button 
              class="btn btn-sm btn-outline-success"
              @click="toggleEdit('professional')"
            >
              <i :class="editing.professional ? 'bi bi-x-lg' : 'bi bi-pencil'" class="me-1"></i>
              {{ editing.professional ? 'Cancel' : 'Edit' }}
            </button>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveProfessionalInfo">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Specialization</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.specialization"
                    :disabled="!editing.professional"
                    placeholder="e.g., Cardiologist"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Qualification</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.qualification"
                    :disabled="!editing.professional"
                    placeholder="e.g., MBBS, MD"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">License Number</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.license_number"
                    :disabled="!editing.professional"
                    placeholder="Medical license number"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Experience (Years)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="form.experience_years"
                    :disabled="!editing.professional"
                    min="0"
                    placeholder="Years of experience"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-medium">Consultation Fee (₹)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="form.consultation_fee"
                    :disabled="!editing.professional"
                    min="0"
                    placeholder="Fee per consultation"
                  >
                </div>
                <div class="col-12">
                  <label class="form-label small fw-medium">Bio / About</label>
                  <textarea 
                    class="form-control" 
                    v-model="form.bio"
                    :disabled="!editing.professional"
                    rows="3"
                    placeholder="Brief description about yourself..."
                  ></textarea>
                </div>
              </div>

              <div v-if="editing.professional" class="mt-3">
                <button type="submit" class="btn btn-success" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-lg me-2"></i>Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import { mapGetters, mapActions } from 'vuex';

import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';

export default {
  name: 'ProfileView',
  components: {
    PageHeader,
    LoadingSpinner
  },
  data() {
    return {
      loading: true,
      saving: false,
      profile: {},
      profileStats: {},
      form: {
        name: '',
        email: '',
        phone: '',
        date_of_birth: '',
        gender: '',
        address: '',
        specialization: '',
        qualification: '',
        license_number: '',
        experience_years: '',
        consultation_fee: '',
        bio: ''
      },
      editing: {
        personal: false,
        professional: false,
      }
    };
  },
  computed: {
    ...mapGetters('auth', ['user']),
    doctorInitials() {
      if (!this.profile.name) return '?';
      return this.profile.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },
    isPasswordValid() {
      return this.passwordForm.current_password &&
             this.passwordForm.new_password &&
             this.passwordForm.new_password.length >= 6 &&
             this.passwordForm.new_password === this.passwordForm.confirm_password;
    }
  },
  methods: {
    ...mapActions('auth', ['fetchUser']),

    async fetchProfile() {
      try {
        this.loading = true;
        const response = await api.get('/doctor/profile');

        if (response.data.status === 'success') {
          this.profile = response.data.data.doctor;
          this.populateForm();
        //   console.log('Profile data:', this.profile);
        }
      } catch (error) {
        console.error('Failed to fetch profile:', error);
      } finally {
        this.loading = false;
      }
    },

    async fetchProfileStats() {
      try {
        const response = await api.get('/doctor/dashboard/stats');
        if (response.data.status === 'success') {
          this.profileStats = response.data.data.stats;
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    },

    populateForm() {
      this.form = {
        name: this.profile.name || '',
        email: this.profile.email || '',
        phone: this.profile.phone || '',
        date_of_birth: this.profile.date_of_birth || '',
        gender: this.profile.gender || '',
        address: this.profile.address || '',
        specialization: this.profile.specialization || '',
        qualification: this.profile.qualification || '',
        license_number: this.profile.license_number || '',
        experience_years: this.profile.experience_years || '',
        consultation_fee: this.profile.consultation_fee || '',
        bio: this.profile.bio || ''
      };
    },

    toggleEdit(section) {
      this.editing[section] = !this.editing[section];
      if (!this.editing[section]) {
        this.populateForm();
        if (section === 'password') {
          this.resetPasswordForm();
        }
      }
    },

    async savePersonalInfo() {
      try {
        this.saving = true;
        const data = {
          name: this.form.name,
          phone: this.form.phone,
          date_of_birth: this.form.date_of_birth,
          gender: this.form.gender,
          address: this.form.address
        };

        await api.put('/doctor/profile', data);
        await this.fetchProfile();
        await this.fetchUser();
        this.editing.personal = false;
        alert('Personal information updated successfully!');
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update profile');
      } finally {
        this.saving = false;
      }
    },

    async saveProfessionalInfo() {
      try {
        this.saving = true;
        const data = {
          specialization: this.form.specialization,
          qualification: this.form.qualification,
          license_number: this.form.license_number,
          experience_years: this.form.experience_years,
          consultation_fee: this.form.consultation_fee,
          bio: this.form.bio
        };

        await api.put('/doctor/profile', data);
        await this.fetchProfile();
        this.editing.professional = false;
        alert('Professional information updated successfully!');
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update profile');
      } finally {
        this.saving = false;
      }
    },

  },

  mounted() {
    this.fetchProfile();
    this.fetchProfileStats();
  }
};
</script>

<style scoped>
.avatar-xl {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-control:disabled,
.form-select:disabled {
  background-color: #f8f9fa;
}
</style>