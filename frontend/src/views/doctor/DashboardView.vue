<template>
    <div class="doctor-dashboard">
    <PageHeader 
      title="Dashboard" 
      :subtitle="formattedDate"
    />

    <LoadingSpinner v-if="loading" :text="'Loading dashboard...'" />

    <div v-else>

      <!-- stats cards -->
       <div class="row g-4 mb-4">
        <div class="col-md-3 col-sm-6">
          <StatsCard
            icon="bi bi-calendar-day"
            :value="stats.today?.total || 0"
            label="Today's Appointments"
            variants="primary"
          />
        </div>
         <div class="col-md-3 col-sm-6">
          <StatsCard 
            icon="bi bi-clock" 
            :value="stats.today?.pending || 0" 
            label="Pending"
            variant="warning"
          />
        </div>
        <div class="col-md-3 col-sm-6">
          <StatsCard 
            icon="bi bi-check-circle" 
            :value="stats.today?.completed || 0" 
            label="Completed Today"
            variant="success"
          />
        </div>
        <div class="col-md-3 col-sm-6">
          <StatsCard 
            icon="bi bi-people" 
            :value="stats.total_patients || 0" 
            label="Total Patients"
            variant="info"
          />
        </div>
       </div>

       <!-- major content -->
        <div class="row g-4">
          <div class="col-lg-8">
            <DataTable
            title="Todays' Schedule"
            icon="bi bi-calendar-check"
            :columns="appointmentColumns"
            :items="todayAppointments"
            :loading="false"
            empty-icon="bi bi-calendar-x"
            empty-message="No appointments Today"
            variant="success"
            >
            <template #header-actions>
              <router-link to="/doctor/appointments" class="btn btn-sm btn-outline-success">
                View All
              </router-link>
            </template>

            <template #cell-appointment_time="{ value }">
              <span class="fw-semibold text-success">{{ formatTime(value) }}</span>
            </template>

            <template #cell-patient_name="{ item }">
              <div class="d-flex align-items-center">
                <div class="avatar-sm bg-primary-subtle rounded-circle me-2">
                  <span class="text-primary small fw-bold">{{ getInitials(item.patient_name) }}</span>
                </div>
                <div>
                  <div class="fw-medium">{{ item.patient_name }}</div>
                  <small class="text-muted">{{ item.booking_notes || 'General Consultation' }}</small>
                </div>
              </div>
            </template>

            <template #cell-status="{item}">
              <StatusBadge :status="item.status" />
            </template>

            <template #actions="{ item }">
              <div class="btn-group btn-group-sm">
                <button 
                  v-if="item.status === 'scheduled'"
                  class="btn btn-success"
                  @click="startConsultation(item)"
                  title="Start Consultation"
                >
                  <i class="bi bi-play-fill"></i>
                </button>
                <button 
                  v-if="item.status === 'scheduled'"
                  class="btn btn-outline-danger"
                  @click="confirmNoShow(item)"
                  title="No Show"
                >
                  <i class="bi bi-person-x"></i>
                </button>
                <button 
                  v-if="item.status === 'completed'"
                  class="btn btn-outline-primary"
                  @click="viewRecord(item)"
                  title="View Record"
                >
                  <i class="bi bi-file-text"></i>
                </button>
              </div>
            </template>

            </DataTable>
          </div>

          <div class="col-lg-4">
            <QuickActions 
              title="Quick Actions"
              :actions="quickActions"
            />

            <!-- weekly summary -->
            <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-0 py-3">
              <h5 class="mb-0 fw-semibold">
                <i class="bi bi-bar-chart me-2 text-info"></i>This Week
              </h5>
            </div>
            <div class="card-body">
              <div class="row text-center g-3">
                <div class="col-6">
                  <div class="p-3 bg-light rounded-3">
                    <h4 class="fw-bold text-success mb-1">{{ stats.this_week?.total || 0 }}</h4>
                    <small class="text-muted">Appointments</small>
                  </div>
                </div>
                <div class="col-6">
                  <div class="p-3 bg-light rounded-3">
                    <h4 class="fw-bold text-primary mb-1">{{ stats.upcoming || 0 }}</h4>
                    <small class="text-muted">Upcoming</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div> <!--main content div-->
      
    </div> <!--else div-->

    <ConsultationModal
      ref="consultationModal"
      :appointment="selectedAppointment"
      :loading="submitting"
      @submit="submitConsultation"
    />

    <MedicalRecordModal
      ref="medicalRecordModal"
      :record="selectedRecord"
      :show-doctor-notes="true"
    />

    <ConfirmModal
      ref="noShowModal"
      title="Mark as No Show"
      message="Are you sure you want to mark this appointment as No Show?"
      icon="bi bi-person-x"
      variant="warning"
      confirm-text="Yes, No Show"
      :loading="submitting"
      @confirm="handleNoShow"
    />



    </div>   <!--main div-->
  
</template>

<script>
import api from '@/services/api';

import PageHeader from '@/components/common/PageHeader.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import StatsCard from '@/components/common/StatsCard.vue';
import DataTable from '@/components/common/DataTable.vue';
import StatusBadge from '@/components/common/StatusBadge.vue';
import QuickActions from '@/components/common/QuickActions.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';
import ConsultationModal from '@/components/doctor/ConsultationModal.vue';
import MedicalRecordModal from '@/components/medicalRecord/MedicalRecordModal.vue';

export default {
  name: 'DoctorDashboard',
  components:{
    PageHeader,
    LoadingSpinner,
    StatsCard,
    DataTable,
    StatusBadge,
    QuickActions,
    ConfirmModal,
    ConsultationModal,
    MedicalRecordModal
  },
  data(){
    return{
      loading:true,
      submitting: false, 
      stats:{},
      todayAppointments:[],
      selectedAppointment:null,
      selectedRecord:null,
      appointmentColumns: [
        { key: 'appointment_time', label: 'Time' },
        { key: 'patient_name', label: 'Patient' },
        { key: 'status', label: 'Status' }
      ],
      quickActions: [
        { to: '/doctor/appointments', icon: 'bi bi-calendar-plus', label: 'View Appointments', btnClass: 'btn-outline-success' },
        { to: '/doctor/patients', icon: 'bi bi-people', label: 'My Patients', btnClass: 'btn-outline-primary' },
        { to: '/doctor/schedule', icon: 'bi bi-clock', label: 'Manage Availability', btnClass: 'btn-outline-info' }
      ]
      }
    },
    computed: {
      formattedDate() {
        return new Date().toLocaleDateString('en-IN', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      }
    },
    methods:{
      async fetchDashboardData() {
        try {
          this.loading = true;
          const today = new Date().toISOString().split('T')[0];

          const [statsRes, aptsRes] = await Promise.all([
            api.get('/doctor/dashboard/stats'),
            api.get('/doctor/appointments', { params: { start_date: today, end_date: today } })
          ]);

          if (statsRes.data.status === 'success') {
            this.stats = statsRes.data.data.stats;
          }
          if (aptsRes.data.status === 'success') {
            this.todayAppointments = aptsRes.data.data.appointments.sort(
              (a, b) => a.appointment_time.localeCompare(b.appointment_time)
            );
          }
        } catch (error) {
          console.error('Failed to fetch dashboard:', error);
        } finally {
          this.loading = false;
        }
      },


      formatTime(time) {
        if (!time) return '';
        const [hours, minutes] = time.split(':');
        const h = parseInt(hours);
        return `${h % 12 || 12}:${minutes} ${h >= 12 ? 'PM' : 'AM'}`;
      },

      getInitials(name){
        if(!name) return '';
        return name.split(' ').map(n => n.charAt(0).toUpperCase()).join('');
      },

      
      startConsultation(appointment) {
        this.selectedAppointment = appointment;
        this.$refs.consultationModal.show();
      },
      
      async submitConsultation(formData) {
        try {
          this.submitting = true;
          await api.post(`/doctor/appointments/${this.selectedAppointment.id}/complete`, formData);
          this.$refs.consultationModal.hide();
          await this.fetchDashboardData();
        } catch (error) {
          alert(error.response?.data?.message || 'Failed to complete consultation');
        } finally {
          this.submitting = false;
        }
      },

      confirmNoShow(appointment) {
        this.selectedAppointment = appointment;
        this.$refs.noShowModal.show();
      },

      async handleNoShow() {
        try {
          this.submitting = true;
          await api.patch(`/doctor/appointments/${this.selectedAppointment.id}/status`, { status: 'no_show' });
          this.$refs.noShowModal.hide();
          await this.fetchDashboardData();
        } catch (error) {
          alert(error.response?.data?.message || 'Failed to update');
        } finally {
          this.submitting = false;
        }
      },

      async viewRecord(appointment) {
      try {
          const response = await api.get(`/doctor/appointments/${appointment.id}/record`);
          if (response.data.status === 'success') {
            this.selectedRecord = response.data.data.record;
            this.$refs.medicalRecordModal.show();
          }
        } catch (error) {
          alert('Failed to load medical record');
          console.error(error);
        }
      }

    },
    mounted(){
      this.fetchDashboardData();
    }
}
</script>

<style>

</style>