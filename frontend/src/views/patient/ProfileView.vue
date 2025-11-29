<template>
  <div class="profile-view">
    <PageHeader 
      title="My Profile" 
      subtitle="View and manage your personal information"
    />

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-2 text-muted">Loading profile...</p>
    </div>

    <div v-else class="row g-4">
      <!-- Profile Card -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center py-5">
            <!-- Avatar -->
            <div class="avatar-circle mx-auto mb-4">
              <span class="avatar-initials">{{ initials }}</span>
            </div>
            
            <h4 class="fw-semibold mb-1">{{ patient.name }}</h4>
            <p class="text-muted mb-3">Patient</p>
            
            <!-- Quick Info -->
            <div class="d-flex justify-content-center gap-4 text-muted small">
              <div v-if="patient.gender">
                <i class="bi bi-gender-ambiguous me-1"></i>
                {{ formatGender(patient.gender) }}
              </div>
              <div v-if="patient.blood_group">
                <i class="bi bi-droplet-fill text-danger me-1"></i>
                {{ patient.blood_group }}
              </div>
              <div v-if="age">
                <i class="bi bi-calendar me-1"></i>
                {{ age }} yrs
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Card -->
        <div class="card border-0 shadow-sm mt-4">
          <div class="card-body">
            <h6 class="fw-semibold text-muted mb-3">
              <i class="bi bi-bar-chart me-2"></i>Quick Stats
            </h6>
            <div class="row g-3 text-center">
              <div class="col-6">
                <div class="bg-primary-subtle rounded-3 p-3">
                  <div class="fs-4 fw-bold text-primary">{{ stats.totalAppointments }}</div>
                  <small class="text-muted">Appointments</small>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-success-subtle rounded-3 p-3">
                  <div class="fs-4 fw-bold text-success">{{ stats.completedAppointments }}</div>
                  <small class="text-muted">Completed</small>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-info-subtle rounded-3 p-3">
                  <div class="fs-4 fw-bold text-info">{{ stats.medicalRecords }}</div>
                  <small class="text-muted">Records</small>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-warning-subtle rounded-3 p-3">
                  <div class="fs-4 fw-bold text-warning">{{ stats.upcomingAppointments }}</div>
                  <small class="text-muted">Upcoming</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Details Card -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-person-lines-fill me-2 text-primary"></i>
              Personal Information
            </h5>
            <button 
              v-if="!editing" 
              class="btn btn-outline-primary btn-sm"
              @click="startEdit"
            >
              <i class="bi bi-pencil me-1"></i>Edit
            </button>
            <div v-else>
              <button class="btn btn-light btn-sm me-2" @click="cancelledit">
                Cancel
              </button>
              <button 
                class="btn btn-primary btn-sm" 
                @click="saveProfile"
                :disabled="saving"
              >
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                Save Changes
              </button>
            </div>
          </div>
          <div class="card-body">
            <!-- View Mode -->
            <div v-if="!editing">
              <div class="row g-4">
                <div class="col-md-6">
                  <label class="text-muted small">Full Name</label>
                  <p class="fw-medium mb-0">{{ patient.full_name || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Email</label>
                  <p class="fw-medium mb-0">{{ patient.email || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Phone Number</label>
                  <p class="fw-medium mb-0">{{ patient.phone || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Date of Birth</label>
                  <p class="fw-medium mb-0">{{ formatDate(patient.dob) || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Gender</label>
                  <p class="fw-medium mb-0">{{ formatGender(patient.gender) || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Blood Group</label>
                  <p class="fw-medium mb-0">{{ patient.blood_group || '-' }}</p>
                </div>
                <div class="col-12">
                  <label class="text-muted small">Address</label>
                  <p class="fw-medium mb-0">{{ patient.address || '-' }}</p>
                </div>
              </div>

              <!-- Emergency Contact -->
              <hr class="my-4">
              <h6 class="fw-semibold mb-3">
                <i class="bi bi-telephone-fill text-danger me-2"></i>
                Emergency Contact
              </h6>
              <div class="row g-4">
                <div class="col-md-6">
                  <label class="text-muted small">Contact Name</label>
                  <p class="fw-medium mb-0">{{ patient.emergency_contact_name || '-' }}</p>
                </div>
                <div class="col-md-6">
                  <label class="text-muted small">Contact Phone</label>
                  <p class="fw-medium mb-0">{{ patient.emergency_contact_phone || '-' }}</p>
                </div>
              </div>

              <!-- Medical Info -->
              <hr class="my-4">
              <h6 class="fw-semibold mb-3">
                <i class="bi bi-heart-pulse text-danger me-2"></i>
                Medical Information
              </h6>
              <div class="row g-4">
                <div class="col-12">
                  <label class="text-muted small">Allergies</label>
                  <p class="fw-medium mb-0">{{ patient.allergies || 'None reported' }}</p>
                </div>
                <div class="col-12">
                  <label class="text-muted small">Chronic Conditions</label>
                  <p class="fw-medium mb-0">{{ patient.chronic_conditions || 'None reported' }}</p>
                </div>
              </div>
            </div>

            <!-- Edit Mode -->
            <form v-else @submit.prevent="saveProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Full Name <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.name"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    :value="patient.email"
                    disabled
                  >
                  <small class="text-muted">Email cannot be changed</small>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone Number <span class="text-danger">*</span></label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="form.phone"
                    required
                    pattern="[0-9]{10}"
                    maxlength="10"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Date of Birth</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="form.date_of_birth"
                    :max="maxDob"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Gender</label>
                  <select class="form-select" v-model="form.gender">
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Blood Group</label>
                  <select class="form-select" v-model="form.blood_group">
                    <option value="">Select Blood Group</option>
                    <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea 
                    class="form-control" 
                    v-model="form.address"
                    rows="2"
                  ></textarea>
                </div>

                <!-- Emergency Contact -->
                <div class="col-12">
                  <hr class="my-3">
                  <h6 class="fw-semibold mb-3">
                    <i class="bi bi-telephone-fill text-danger me-2"></i>
                    Emergency Contact
                  </h6>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Contact Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.emergency_contact_name"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Contact Phone</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="form.emergency_contact_phone"
                    pattern="[0-9]{10}"
                    maxlength="10"
                  >
                </div>

                <!-- Medical Info -->
                <div class="col-12">
                  <hr class="my-3">
                  <h6 class="fw-semibold mb-3">
                    <i class="bi bi-heart-pulse text-danger me-2"></i>
                    Medical Information
                  </h6>
                </div>
                <div class="col-12">
                  <label class="form-label">Allergies</label>
                  <textarea 
                    class="form-control" 
                    v-model="form.allergies"
                    rows="2"
                    placeholder="List any known allergies..."
                  ></textarea>
                </div>
                <div class="col-12">
                  <label class="form-label">Chronic Conditions</label>
                  <textarea 
                    class="form-control" 
                    v-model="form.chronic_conditions"
                    rows="2"
                    placeholder="List any chronic conditions..."
                  ></textarea>
                </div>
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
import PageHeader from '@/components/common/PageHeader.vue';

export default {
  name: 'ProfileView',
  components: { PageHeader },
  data() {
    return {
      loading: true,
      editing: false,
      saving: false,
      patient: {},
      form: {},
      stats: {
        totalAppointments: 0,
        completedAppointments: 0,
        upcomingAppointments: 0,
        medicalRecords: 0
      },
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    };
  },
  computed: {
    initials() {
      if (!this.patient.full_name) return '?';
      return this.patient.full_name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    },
    age() {
      if (!this.patient.date_of_birth) return null;
      const dob = new Date(this.patient.date_of_birth);
      const today = new Date();
      let age = today.getFullYear() - dob.getFullYear();
      const m = today.getMonth() - dob.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
        age--;
      }
      return age;
    },
    maxDob() {
      return new Date().toISOString().split('T')[0];
    }
  },
  methods: {
    async fetchProfile() {
      try {
        this.loading = true;
        const res = await api.get('/patient/profile');
        this.patient = res.data?.data?.patient || {};
      } catch (e) {
        console.error('Failed to fetch profile:', e);
      } finally {
        this.loading = false;
      }
    },

    async fetchStats() {
      try {
        // Fetch appointments
        const aptRes = await api.get('/patient/appointments');
        const appointments = aptRes.data?.data?.appointments || [];
        
        const today = new Date().toISOString().split('T')[0];
        
        this.stats.totalAppointments = appointments.length;
        this.stats.completedAppointments = appointments.filter(a => a.status === 'completed').length;
        this.stats.upcomingAppointments = appointments.filter(
          a => a.status === 'scheduled' && a.appointment_date >= today
        ).length;

        // Fetch records
        const recRes = await api.get('/patient/records');
        this.stats.medicalRecords = recRes.data?.data?.total || 0;
      } catch (e) {
        console.error('Failed to fetch stats:', e);
      }
    },

    startEdit() {
      this.form = {
        name: this.patient.full_name || '',
        phone: this.patient.phone || '',
        date_of_birth: this.patient.dob || '',
        gender: this.patient.gender || '',
        blood_group: this.patient.blood_group || '',
        address: this.patient.address || '',
        emergency_contact_name: this.patient.emergency_contact_name || '',
        emergency_contact_phone: this.patient.emergency_contact_phone || '',
        allergies: this.patient.allergies || '',
        chronic_conditions: this.patient.chronic_conditions || ''
      };
      this.editing = true;
    },

    cancelledit() {
      this.editing = false;
      this.form = {};
    },

    async saveProfile() {
      try {
        this.saving = true;
        const res = await api.put('/patient/profile', this.form);
        this.patient = res.data?.data?.patient || this.patient;
        this.editing = false;
        alert('Profile updated successfully!');
      } catch (e) {
        console.error('Failed to save profile:', e);
        alert(e.response?.data?.message || 'Failed to update profile');
      } finally {
        this.saving = false;
      }
    },

    formatDate(date) {
      if (!date) return null;
      return new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    },

    formatGender(gender) {
      if (!gender) return null;
      return gender.charAt(0).toUpperCase() + gender.slice(1);
    }
  },
  mounted() {
    this.fetchProfile();
    this.fetchStats();
  }
};
</script>

<style scoped>
.avatar-circle {
  width: 100px;
  height: 100px;
  background-color: #0d6efd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-initials {
  color: white;
  font-size: 2.5rem;
  font-weight: 600;
}

.form-label {
  font-weight: 500;
  font-size: 0.875rem;
}
</style>