import config from '@/config.js'

const state = {
    user: null,
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    userRole: localStorage.getItem('user_role') || null,
    loading: false
}

const getters = {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    userRole: state => state.userRole,
    token: state => state.token,
    loading: state => state.loading,
    refreshToken: state => state.refreshToken,
    isAdmin: state => state.userRole == 'admin',
    isDoctor: state => state.userRole == 'doctor',
    isPatient: state => state.userRole == 'patient',
}

const mutations = {

    //  loading 
    SET_AUTH_LOADING(state, loading){
        state.loading = loading
    },

    // if auth succeeds
    SET_AUTH_SUCCESS(state, {user, token, refreshToken, role}){
        state.user = user
        state.token = token
        state.refreshToken = refreshToken
        state.userRole = role
        state.isAuthenticated = true
        state.loading = false

        localStorage.setItem('access_token',token)
        localStorage.setItem('refresh_token',refreshToken)
        localStorage.setItem('user_role',role)
    },
    
    // else any error
    SET_AUTH_ERROR(state){
        state.user = null
        state.token = null
        state.refreshToken = null
        state.userRole = null
        state.isAuthenticated = false
        state.loading = false
    },

    // clearing state after logout
    LOGOUT(state){
    state.user = null
    state.token = null
    state.refreshToken = null
    state.userRole = null
    state.isAuthenticated = false
    state.loading = false
    
    // clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    },

}

const actions = {

    // login 
    async login({ commit }, loginData){
        try{
            commit('SET_AUTH_LOADING',true)

            const response = await fetch(`${config.apiBaseUrl}/auth/login`,{
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(loginData)
            })

            const data = await response.json()

            if(data.status === 'success'){
                commit('SET_AUTH_SUCCESS',{
                    user: data.data.user,
                    token: data.data.access_token,
                    refreshToken: data.data.refresh_token,
                    role: loginData.role
                })
                return {success: true}
            }else {
                commit('SET_AUTH_ERROR')
            return { success: false, message: data.message || 'Invalid credentials' }
            }
        }catch(error){
            commit('SET_AUTH_ERROR')
            console.error('Login error:', error)
            return { success: false, message: 'Network Error' }
        }finally{
            commit('SET_AUTH_LOADING',false)
        }
    },

    async register({ commit }, registerData){
        try{
            commit('SET_AUTH_LOADING',true)

            const response = await fetch(`${config.apiBaseUrl}/auth/register/patient`,{
                method: 'POST',
                headers:{
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerData)
            })

            const data = await response.json()
           if (data.status === 'success') {
                if (data.data?.access_token) {
                commit('SET_AUTH_SUCCESS', {
                    user: data.data.user,
                    token: data.data.access_token,
                    refreshToken: data.data.refresh_token,
                    role: 'patient'
                })
                }
                return { success: true }
            } else {
                commit('SET_AUTH_ERROR')
                return { success: false, message: data.message }
            }

        } catch (error) {
        commit('SET_AUTH_ERROR')
        return { success: false, message: 'Network error' }
        }      
        
    },

    async logout({ commit, state }){
        try {
            console.log('Token being sent:', state.token);
            if (!state.token) {
                console.log('No token found');
                commit('LOGOUT');
                return;
            }

            const response = await fetch(`${config.apiBaseUrl}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${state.token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            console.log('Logout response:', data);

            if (!response.ok) {
                throw new Error(data.message || 'Logout failed');
            }

        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            commit('LOGOUT');
        }
    },

    // initializing auth state from localstorage
    initializeAuth({commit}){
        const token = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        const userRole = localStorage.getItem('user_role')
        
        if (token && userRole) {
        commit('SET_AUTH_SUCCESS', {
            user: userData ? JSON.parse(userData) : null,
            token,
            refreshToken,
            role: userRole
        })
        }
    }

}


export default{
    namespaced: true,
    state, 
    getters,
    mutations,
    actions
}