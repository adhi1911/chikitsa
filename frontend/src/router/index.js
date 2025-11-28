// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView
  },
  {
    path: '/login/:role',
    name: 'login',
    component: () => import('../views/auth/LoginView.vue'),
    props: true
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/auth/RegisterView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/admin/DashboardView.vue')
      },
      {
        path: 'departments',
        name: 'department-list',
        component: () => import('../views/admin/DepartmentListView.vue')
      },
      {
        path: 'doctors',
        name: 'doctor-list',
        component: () => import('../views/admin/DoctorListView.vue')
      },
      {
        path: 'patients',
        name: 'patient-list',
        component: () => import('../views/admin/PatientListView.vue')
      },
      {
        path: 'appointments',
        name: 'appointment-list',
        component: () => import('../views/admin/AppointmentListView.vue')
      }
    ]
  },
  {
    path: '/doctor',
    name: 'doctor',
    component: () => import('../views/doctor/DoctorLayout.vue'),
    meta: { requiresAuth: true, role: 'doctor' },
    children: [
      {
        path: 'dashboard',
        name: 'doctor-dashboard',
        component: () => import('../views/doctor/DashboardView.vue')
      },
      {
        path: 'appointments',
        name: 'doctor-appointments',
        component: () => import('../views/doctor/AppointmentsView.vue')
      },
      {
        path: 'patients',
        name: 'doctor-patients',
        component: () => import('../views/doctor/PatientsView.vue')
      },
      {
        path: 'patients/:id',
        name: 'doctor-patient-details',
        component: () => import('../views/doctor/PatientDetailView.vue'),
        props: true
      },
      {
        path:'schedule',
        name: 'doctor-schedule',
        component: () => import('../views/doctor/ScheduleView.vue')
      },
      {
        path: 'profile',
        name: 'doctor-profile',
        component: () => import('../views/doctor/ProfileView.vue')
      }

    ]
  },
  {
    path: '/patient',
    name: 'patient',
    component: () => import('../views/patient/PatientLayout.vue'),
    meta: { requiresAuth: true, role: 'patient' },
    children: [
      {
        path: 'dashboard',
        name: 'patient-dashboard',
        component: () => import('../views/patient/DashboardView.vue')
      },
      {
        path: 'doctors',
        name: 'patient-doctors',
        component: () => import('../views/patient/DoctorsView.vue')
      },
      {
        path: 'appointments',
        name: 'patient-appointments',
        component: () => import('../views/patient/AppointmentsView.vue')
      },
      {
        path: 'records',
        name: 'patient-records',
        component: () => import('../views/patient/MedicalRecordsView.vue')
      },
      {
        path: 'profile',
        name: 'patient-profile',
        component: () => import('../views/patient/ProfileView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router