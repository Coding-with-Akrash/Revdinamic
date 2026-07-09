// Vehicle Manager - Client-side vehicle state management
window.vehicleManager = {
    currentVehicle: localStorage.getItem('selectedVehicle') || 'bmw-m3',
    vehicleBuilds: {},  // Per-vehicle installed parts: { vehicleId: [partIds] }
    vehiclesCache: null,
    vehicleData: null,

    init() {
        const saved = localStorage.getItem('vehicleBuilds');
        if (saved) {
            try { this.vehicleBuilds = JSON.parse(saved); } catch (e) { this.vehicleBuilds = {}; }
        }
    },

    async fetchVehicles() {
        if (this.vehiclesCache) return this.vehiclesCache;
        try {
            const response = await fetch('/api/vehicles');
            const data = await response.json();
            this.vehiclesCache = data;
            return data;
        } catch (e) {
            console.error('Failed to fetch vehicles:', e);
            return [];
        }
    },

    async loadVehicleData(vehicleId) {
        try {
            const response = await fetch('/api/vehicles/' + vehicleId);
            const data = await response.json();
            this.vehicleData = data;
            this.saveBuilds();
            return data;
        } catch (e) {
            console.error('Failed to load vehicle:', e);
            return null;
        }
    },

    saveBuilds() {
        localStorage.setItem('vehicleBuilds', JSON.stringify(this.vehicleBuilds));
    },

    setVehicle(vehicleId) {
        this.currentVehicle = vehicleId;
        localStorage.setItem('selectedVehicle', vehicleId);
        // Load installed parts for this specific vehicle
        if (window.vehicleManager) {
            this.installedParts = this.vehicleBuilds[vehicleId] || [];
        }
        this.loadVehicleData(vehicleId);
        const event = new CustomEvent('vehicleChanged', { detail: { vehicleId } });
        window.dispatchEvent(event);
    },

    getVehicle() {
        if (this.vehicleData) {
            return {
                make: this.vehicleData.make,
                model: this.vehicleData.model,
                basePower: this.vehicleData.basePower,
                torque: this.vehicleData.torque,
                year: this.vehicleData.year,
                engine: this.vehicleData.engine,
                turbo: this.vehicleData.turbo,
                Drivetrain: this.vehicleData.Drivetrain,
                redline: this.vehicleData.redline
            };
        }
        const defaultVehicles = {
            'bmw-m3': { make: 'BMW', model: 'M3', basePower: 503, torque: 550, redline: 7200 },
            'mustang-gt': { make: 'Ford', model: 'Mustang GT', basePower: 480, torque: 420, redline: 7000 },
            'audi-rs6': { make: 'Audi', model: 'RS6', basePower: 591, torque: 800, redline: 6500 },
            'amg-gt': { make: 'Mercedes', model: 'AMG GT', basePower: 577, torque: 700, redline: 7000 },
            'supra': { make: 'Toyota', model: 'GR Supra', basePower: 382, torque: 369, redline: 7000 },
            'gtr': { make: 'Nissan', model: 'GT-R', basePower: 565, torque: 481, redline: 7200 },
            'civic-type-r': { make: 'Honda', model: 'Civic Type R', basePower: 315, torque: 295, redline: 7000 },
            'corvette': { make: 'Chevrolet', model: 'Corvette C8', basePower: 670, torque: 465, redline: 6500 },
            'toyota-corolla': { make: 'Toyota', model: 'Corolla Altis', basePower: 138, torque: 173, redline: 6000 },
            'toyota-camry': { make: 'Toyota', model: 'Camry', basePower: 208, torque: 221, redline: 6200 },
            'toyota-fortuner': { make: 'Toyota', model: 'Fortuner', basePower: 171, torque: 366, redline: 4500 },
            'toyota-landcruiser': { make: 'Toyota', model: 'Land Cruiser', basePower: 305, torque: 650, redline: 5000 },
            'honda-civic': { make: 'Honda', model: 'Civic', basePower: 158, torque: 215, redline: 6800 },
            'honda-city': { make: 'Honda', model: 'City', basePower: 118, torque: 145, redline: 6200 },
            'honda-accord': { make: 'Honda', model: 'Accord', basePower: 212, torque: 232, redline: 6500 },
            'honda-br-v': { make: 'Honda', model: 'BR-V', basePower: 118, torque: 145, redline: 6200 },
            'suzuki-mehran': { make: 'Suzuki', model: 'Mehran', basePower: 39, torque: 54, redline: 5500 },
            'suzuki-alto': { make: 'Suzuki', model: 'Alto', basePower: 47, torque: 64, redline: 5800 },
            'suzuki-swift': { make: 'Suzuki', model: 'Swift', basePower: 125, torque: 148, redline: 6500 },
            'suzuki-wagon-r': { make: 'Suzuki', model: 'Wagon R', basePower: 67, torque: 90, redline: 5500 },
            'suzuki-cultus': { make: 'Suzuki', model: 'Cultus', basePower: 95, torque: 128, redline: 5800 },
            'suzuki-jimny': { make: 'Suzuki', model: 'Jimny', basePower: 101, torque: 132, redline: 4500 },
            'mitsubishi-pajero': { make: 'Mitsubishi', model: 'Pajero Sport', basePower: 179, torque: 343, redline: 4800 },
            'mitsubishi-lancer': { make: 'Mitsubishi', model: 'Lancer Evolution', basePower: 295, torque: 311, redline: 7000 },
            'mitsubishi-outlander': { make: 'Mitsubishi', model: 'Outlander', basePower: 128, torque: 147, redline: 5800 },
            'nissan-sunny': { make: 'Nissan', model: 'Sunny', basePower: 139, torque: 200, redline: 6000 },
            'nissan-sentra': { make: 'Nissan', model: 'Sentra', basePower: 149, torque: 200, redline: 6200 },
            'nissan-x-trail': { make: 'Nissan', model: 'X-Trail', basePower: 165, torque: 200, redline: 6000 },
            'hyundai-tucson': { make: 'Hyundai', model: 'Tucson', basePower: 150, torque: 192, redline: 6000 },
            'hyundai-elantra': { make: 'Hyundai', model: 'Elantra', basePower: 120, torque: 151, redline: 6500 },
            'hyundai-sonata': { make: 'Hyundai', model: 'Sonata', basePower: 177, torque: 221, redline: 6200 },
            'kia-sportage': { make: 'KIA', model: 'Sportage', basePower: 150, torque: 192, redline: 6000 },
            'kia-picanto': { make: 'KIA', model: 'Picanto', basePower: 67, torque: 94, redline: 5500 },
            'faw-v2': { make: 'FAW', model: 'V2', basePower: 139, torque: 200, redline: 5800 },
            'faw-v5': { make: 'FAW', model: 'V5', basePower: 147, torque: 221, redline: 5900 },
            'changan-alsvin': { make: 'Changan', model: 'Alsvin', basePower: 147, torque: 221, redline: 5900 },
            'changan-karvaan': { make: 'Changan', model: 'Karvaan', basePower: 85, torque: 115, redline: 4500 },
            'haval-h6': { make: 'Haval', model: 'H6', basePower: 197, torque: 340, redline: 5200 },
            'haval-jolion': { make: 'Haval', model: 'Jolion', basePower: 197, torque: 340, redline: 5200 },
            'mg-hs': { make: 'MG', model: 'HS', basePower: 195, torque: 353, redline: 5200 },
            'mg-zs': { make: 'MG', model: 'ZS', basePower: 147, torque: 221, redline: 5800 },
            'proton-saga': { make: 'Proton', model: 'Saga', basePower: 95, torque: 128, redline: 5500 },
            'proton-x70': { make: 'Proton', model: 'X70', basePower: 177, torque: 340, redline: 5200 },
            'dfsk-glory': { make: 'DFSK', model: 'Glory 580', basePower: 128, torque: 147, redline: 5000 },
            'jac-s5': { make: 'JAC', model: 'S5', basePower: 128, torque: 147, redline: 5000 },
            'zotye-z300': { make: 'ZOTYE', model: 'Z300', basePower: 138, torque: 173, redline: 5500 },
            'lifan-x60': { make: 'Lifan', model: 'X60', basePower: 128, torque: 147, redline: 5800 },
            'peugeot-2008': { make: 'Peugeot', model: '2008', basePower: 115, torque: 162, redline: 5800 },
            'peugeot-3008': { make: 'Peugeot', model: '3008', basePower: 115, torque: 162, redline: 5800 },
            'peugeot-5008': { make: 'Peugeot', model: '5008', basePower: 115, torque: 162, redline: 5800 }
        };
        return defaultVehicles[this.currentVehicle] || defaultVehicles['bmw-m3'];
    },

    getInstalledParts() {
        return this.vehicleBuilds[this.currentVehicle] || [];
    },

    getInstalledPartsForVehicle(vehicleId) {
        return this.vehicleBuilds[vehicleId] || [];
    },

    installPart(partId) {
        if (!this.vehicleBuilds[this.currentVehicle]) {
            this.vehicleBuilds[this.currentVehicle] = [];
        }
        if (!this.vehicleBuilds[this.currentVehicle].includes(partId)) {
            this.vehicleBuilds[this.currentVehicle].push(partId);
            this.saveBuilds();
        }
    },

    removePart(partId) {
        if (this.vehicleBuilds[this.currentVehicle]) {
            this.vehicleBuilds[this.currentVehicle] = this.vehicleBuilds[this.currentVehicle].filter(p => p !== partId);
            this.saveBuilds();
        }
    },

    setInstalledParts(parts, vehicleId) {
        const vid = vehicleId || this.currentVehicle;
        this.vehicleBuilds[vid] = parts || [];
        this.saveBuilds();
    },

    clearInstalledParts(vehicleId) {
        const vid = vehicleId || this.currentVehicle;
        this.vehicleBuilds[vid] = [];
        this.saveBuilds();
    }
};
