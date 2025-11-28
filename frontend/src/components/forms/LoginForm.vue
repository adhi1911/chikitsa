<template>
    <div class="card shadow-sm p-4" style="max-width:400px; width:100%">
        <div class="text-center mb-4">
            <div class="login-icon mb-3">
                <i :class="roleIcon"></i>
            </div>
        </div>
        <h3 class="fw-bold">
            Login as {{ role.charAt(0).toUpperCase() + role.slice(1) }}
        </h3>
        <p class="text-muted smal">Please enter your credentials to continue</p>

        <!-- login form -->
        <form @submit.prevent="handleLogin">
            <div class="mb-3">
                <label class="form-l">Username</label>
                <div class="input-group">
                    <input type="text"
                            v-model="form.username"
                            class="form-control"
                            :class="{'is-invalid': errors.username}"
                            placeholder="Enter your username" 
                            required/>
                </div>
                <div class="invalid-feedback" v-if="errors.username">
                    {{ errors.username }}
                </div>
            </div>

            <div class="mb-4">
                <label class="form-labe">Password</label>
                <div class="input-group">
                    <input 
                        v-model="form.password" 
                        :type="showPassword ? 'text' : 'password'" 
                        class="form-control" 
                        placeholder="Enter password"
                        :class="{ 'is-invalid': errors.password }"
                        required 
                    />
                    <button 
                        class="btn btn-outline-secondary" 
                        type="button"
                        @click="togglePassword"
                    >
                        <i :class="showPassword ? 'bis bi-eye-slash' : 'bis bi-eye'"></i>
                    </button>
                </div>
                <div class="invalid-feedback" v-if="errors.password">
                    {{ errors.password }}
                </div>
            </div>
            <input type="hidden" v-model="form.role" />

            <!-- login button -->
            <button class="btn btn-primary w-100 py-2 mb-"
                    type="submit"
                    :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Logging in...' : 'Login' }}
            </button>

            <!-- error -->
            <div v-if="error" class="alert alert-danger d-flex align-items-center mt-3" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                {{ error }}
            </div>

            <!-- registration -->
            <div class="text-center mt-3" v-if="role === 'patient'">
                <p class="text-muted mb-0">
                    Don't have an account? 
                    <router-link 
                        to="/register" 
                        class="text-primary text-decoration-none fw-medium"
                    >
                        Register here
                    </router-link>
                </p>
            </div>
        </form>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {

    name: 'LoginForm',
    props: {
        role: {
            type: String,
            default: 'patient'
        }
    },
    data() {
        return {
            form: {
                username: '',
                password: '',
                role: this.role
            },
            error: '',
            errors: {},
            showPassword: false,
        }
    },
    computed: {
        roleIcon() {
        const icons = {
            admin: 'bi bi-shield-lock fs-2 text-danger',
            doctor: 'bi bi-person-badge fs-2 text-success',
            patient: 'bi bi-person fs-2 text-primary'
        }
            return icons[this.role] || icons.patient
        },
        ...mapGetters('auth',['isAuthenticated']),
        loading(){
            return this.$store.state.auth.loading
        },
    },
    methods:{
        ...mapActions('auth',['login']),
        togglePassword(){
            this.showPassword = !this.showPassword
        },

        validateForm(){
            this.errors = {}
            if(!this.form.username){
                this.errors.username = 'Username is required.'
            }
            if(!this.form.password){
                this.errors.password = 'Password is required.'
            }
            return Object.keys(this.errors).length === 0
        },

        async handleLogin(){
            if (!this.validateForm()) {return}

            this.error =''

            // console.log(JSON.stringify(this.form))

            try {
                const result = await this.login({
                    username: this.form.username,
                    password: this.form.password,
                    role: this.role
                })

                if (result.success) {
                    this.$router.push(`/${this.role}/dashboard`)
                } else {
                    this.error = result.message || 'Login failed'
                }
            } catch (error) {
                console.error('Login error:', error)
                this.error = 'Login failed. Please try again.'
            }
        }
    }

}
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 1.5rem;
  box-shadow: 0 8px 32px rgba(44,62,80,0.08);
  border: none;
}

.login-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
}

.form-control{
        border-radius: 0.5rem;
    padding: 0.6rem 1rem;
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