// API Client for AutoDyno AI Backend
const API_BASE = '/api';

class APIClient {
    constructor() {
        this.baseURL = API_BASE;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        };
        const response = await fetch(url, { ...defaults, ...options });
        return response.json();
    }

    async register(userData) {
        return this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return this.request('/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async logout() {
        return this.request('/logout', { method: 'POST' });
    }

    async verifyEmail(token) {
        return this.request(`/verify-email?token=${token}`);
    }
    
    async verifyCode(data) {
        return this.request('/verify-code', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async resendVerification(email) {
        return this.request('/resend-verification', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    async getVehicles() {
        return this.request('/vehicles');
    }

    async getVehicle(vehicleId) {
        return this.request(`/vehicles/${vehicleId}`);
    }

    async getOBDData(vehicleId) {
        return this.request(`/obd-data/${vehicleId}`);
    }

    async getParts(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        const endpoint = Object.keys(filters).length > 0 ? `/parts/filter?${params}` : '/parts';
        return this.request(endpoint);
    }

    async getPartsByCategory(category) {
        return this.request(`/parts/category/${category}`);
    }

    async getRecommendations(data) {
        return this.request('/recommendations', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async generateTune(data) {
        return this.request('/tune', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async applyTune(tuneData) {
        return this.request('/tune', {
            method: 'POST',
            body: JSON.stringify(tuneData)
        });
    }
    
    async startDyno(vehicleId) {
        return this.request('/dyno-start', {
            method: 'POST',
            body: JSON.stringify({ vehicleId })
        });
    }
    
    async stopDyno(vehicleId) {
        return this.request('/dyno-stop', {
            method: 'POST',
            body: JSON.stringify({ vehicleId })
        });
    }

    async getMakes() {
        return this.request('/makes');
    }

    async getModels(makeId) {
        return this.request(`/models/${makeId}`);
    }

    async getDynoCurve(vehicleId) {
        return this.request(`/dyno-curve/${vehicleId}`);
    }

    async chat(message) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }

    async saveVehicleBuild(data) {
        return this.request('/vehicle-build', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getVehicleBuild(vehicleId) {
        return this.request(`/vehicle-build/${vehicleId}`);
    }

    async getSavedBuild(vehicleId) {
        return this.request(`/vehicle-build/${vehicleId}/saved`);
    }
}

window.apiClient = new APIClient();