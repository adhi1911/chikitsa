<template>
    <div class="card shadow-sm p-4" style="max-width:800px; width:100%">
        <div class="text-center mb-4">
            <div class="register-icon mb-3">
                <i class="bis bi-person-plus-fill"></i>
            </div>
        </div>
        <h3 class="fw-">
            New Registration
        </h3>
        <p class="text-muted small">Register yourself as a Patient</p>
        
        <!-- Registeration Form -->
        <form @submit.prevent="handleRegister" class="row g-3">

            <!-- username -->
            <div class="col-12">
                <label class="form-label">Username</label>
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="bi bi-person"></i>
                    </span>
                    <input 
                        type="text"
                        v-model="form.username"
                        class="form-control"
                        :class="{'is-invalid': errors.username}"
                        placeholder="Choose a username"
                        required
                    />
                </div>
                <div class="invalid-feedback" v-if="errors.username">
                    {{ errors.username }}
                </div>
            </div>

            <!-- email -->
            <div class="col-12">
                <label class="form-label">Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input 
                        type="email"
                        v-model="form.email"
                        class="form-control"
                        :class="{'is-invalid': errors.email}"
                        placeholder="Enter your email"
                        required
                    />
                </div>
                <div class="invalid-feedback" v-if="errors.email">
                    {{ errors.email }}
                </div>
            </div>

            <!-- password -->
            <div class="col-12">
                <label class="form-label">Password</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input 
                        v-model="form.password"
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control"
                        :class="{'is-invalid': errors.password}"
                        placeholder="Create a password"
                        required
                    />
                    <button 
                        class="btn btn-outline-secondary" 
                        type="button"
                        @click="togglePassword"
                    >
                        <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                </div>
                <div class="invalid-feedback" v-if="errors.password">
                    {{ errors.password }}
                </div>
            </div>

            <!-- name fieldss -->
            <div class="col-md-6">
                <label class="form-label">First Name</label>
                <input 
                    type="text"
                    v-model="form.first_name"
                    class="form-control"
                    :class="{'is-invalid': errors.first_name}"
                    required
                />
                <div class="invalid-feedback" v-if="errors.first_name">
                    {{ errors.first_name }}
                </div>
            </div>

            <div class="col-md-6">
                <label class="form-label">Last Name</label>
                <input 
                    type="text"
                    v-model="form.last_name"
                    class="form-control"
                    :class="{'is-invalid': errors.last_name}"
                    required
                />
                <div class="invalid-feedback" v-if="errors.last_name">
                    {{ errors.last_name }}
                </div>
            </div>

            <!-- dob -->
            <div class="col-md-6">
                <label class="form-label">Date of Birth</label>
                <input 
                    type="date"
                    v-model="form.dob"
                    class="form-control"
                    :class="{'is-invalid': errors.dob}"
                    required
                />
                <div class="invalid-feedback" v-if="errors.dob">
                    {{ errors.dob }}
                </div>
            </div>

            <!-- gender -->
            <div class="col-md-6">
                <label class="form-label">Gender</label>
                <select 
                    v-model="form.gender"
                    class="form-select"
                    :class="{'is-invalid': errors.gender}"
                    required
                >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
                <div class="invalid-feedback" v-if="errors.gender">
                    {{ errors.gender }}
                </div>
            </div>

            <!-- blood group -->
             <div class="col-md-6">
                <label class="form-label">Blood Group</label>
                <select 
                    v-model="form.blood_group"
                        class="form-select"
                        :class="{'is-invalid' : errors.blood_group}"
                    >
                        <option value="">Select blood group</option>
                        <option v-for="group in bloodGroups" :key="group" :value="group">
                            {{ group }}
                        </option> 
                    </select>
                    <div class="invalid-feedback" v-if="errors.blood_group">
                        {{ errors.blood_group }}
                    </div>
             </div>

            <!-- phone -->
            <div class="col-md-6">
                <label class="form-label">Phone Number</label>
                <input 
                    type="tel"
                    v-model="form.phone"
                    class="form-control"
                    :class="{'is-invalid': errors.phone}"
                    pattern="^\d{10}$"
                    placeholder="10-digit phone number"
                    required
                />
                <div class="invalid-feedback" v-if="errors.phone">
                    {{ errors.phone }}
                </div>
            </div>

            <!-- address -->
            <div class="col-12">
                <label class="form-label">Address</label>
                <textarea 
                    v-model="form.address"
                    class="form-control"
                    :class="{'is-invalid': errors.address}"
                    rows="2"
                ></textarea>
                <div class="invalid-feedback" v-if="errors.address">
                    {{ errors.address }}
                </div>
            </div>

            <!-- emergency contact -->
            <div class="col-md-6">
                <label class="form-label">Emergency Contact Name</label>
                <input 
                    type="text"
                    v-model="form.emergency_contact_name"
                    class="form-control"
                    :class="{'is-invalid': errors.emergency_contact_name}"
                />
                <div class="invalid-feedback" v-if="errors.emergency_contact_name">
                    {{ errors.emergency_contact_name }}
                </div>
            </div>

            <div class="col-md-6">
                <label class="form-label">Emergency Contact Phone</label>
                <input 
                    type="tel"
                    v-model="form.emergency_contact_phone"
                    class="form-control"
                    :class="{'is-invalid': errors.emergency_contact_phone}"
                    pattern="^\d{10}$"
                    placeholder="10-digit phone number"
                />
                <div class="invalid-feedback" v-if="errors.emergency_contact_phone">
                    {{ errors.emergency_contact_phone }}
                </div>
            </div>

            <!-- medical history -->
            <div class="col-12">
                <label class="form-label">Medical History</label>
                <textarea 
                    v-model="form.medical_history"
                    class="form-control"
                    :class="{'is-invalid': errors.medical_history}"
                    rows="3"
                    placeholder="Any pre-existing conditions, allergies, or important medical information"
                ></textarea>
                <div class="invalid-feedback" v-if="errors.medical_history">
                    {{ errors.medical_history }}
                </div>
            </div>

            <!-- submit button -->
            <div class="col-12">
                <button 
                    type="submit" 
                    class="btn btn-primary w-100 py-2"
                    :disabled="loading"
                >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Registering...' : 'Register' }}
                </button>
            </div>

            <div v-if="error" class="col-12">
                <div class="alert alert-danger d-flex align-items-center" role="alert">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    {{ error }}
                </div>
            </div>

            <div class="col-12 text-center mt-3">
                <p class="text-muted mb-0">
                    Already have an account? 
                    <router-link 
                        to="/login/patient" 
                        class="text-primary text-decoration-none fw-medium"
                    >
                        Login here
                    </router-link>
                </p>
            </div>
        </form>

    </div>
</template>

<script>
import config from '@/config.js'

export default {
    name: 'RegisterForm',
    data() {
        return {
            form: {
                username: '',
                email: '',
                password: '',
                first_name: '',
                last_name: '',
                dob: '',
                gender: 'male',
                blood_group: '',
                phone: '',
                address: '',
                emergency_contact_name: '',
                emergency_contact_phone: '',
                medical_history: ''
            },
            bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            error: '',
            errors: {},
            loading: false,
            showPassword: false,
            apiUrl: config.apiBaseUrl
        }
    },
    methods:{
        togglePassword(){
            this.showPassword = !this.showPassword;
        },
        validateForm() {
            this.errors = {}
            
            if (!this.form.username || this.form.username.length < 3) {
                this.errors.username = 'Username must be at least 3 characters'
            }
            
            if (!this.form.email || !this.form.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                this.errors.email = 'Please enter a valid email address'
            }
            
            if (!this.form.password || this.form.password.length < 8) {
                this.errors.password = 'Password must be at least 8 characters'
            }
            
            if (!this.form.phone || !this.form.phone.match(/^\d{10}$/)) {
                this.errors.phone = 'Please enter a valid 10-digit phone number'
            }
            
            if (this.form.emergency_contact_phone && !this.form.emergency_contact_phone.match(/^\d{10}$/)) {
                this.errors.emergency_contact_phone = 'Please enter a valid 10-digit phone number'
            }
            
            return Object.keys(this.errors).length === 0
        },
        async handleRegister(){
            if(!this.validateForm()){
                return
            }

            this.error = ''
        this.loading = true

            try{

                // console.log('Registering with data:', this.form)
                const response = await fetch(`${this.apiUrl}/auth/register/patient`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.form)
                })

                const data = await response.json()

                if(data.status === 'success'){

                    if(data.data?.access_token){
                        localStorage.setItem('access_token', data.data.access_token)
                        localStorage.setItem('refresh_token', data.data.refresh_token)
                    }

                    this.$router.push('/patient/dashboard')
                }else   {
                    this.error = data.message || 'Registration failed. Please try again.'
                }
            }catch(error){
                console.error('Registration error:', error)
                this.error = 'Registration failed. Please try again.'
            }finally{
                this.loading = false
            }
        }
    }

}
</script>

<style>
.card{
        background: #fff;
    border-radius: 1.5rem;
    box-shadow: 0 8px 32px rgba(44,62,80,0.08);
    border: none;
}

.register-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
}

.form-control, .form-select {
    border-radius: 0.5rem;
    padding: 0.6rem 1rem;
}

.input-group-text {
    background: transparent;
}

.alert {
    border-radius: 0.5rem;
    font-size: 0.9rem;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,123,255,0.2);
}
</style>
<!-- 
    username: str = Field(...,min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(...,min_length=8)
    first_name: str
    last_name: str
    dob: date
    gender: str = Field(...,pattern='^(male|female|other)$')
    blood_group: Optional[str]
    phone: str = Field(...,pattern='^\d{10}$')
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_history: Optional[str]

-->