// RevDynamics - Vehicle Database Client
// This file now fetches data from the Python backend API

const vehicleDatabase = {
    makes: [],
    models: {},
    years: [],
    obdProtocols: [
        'ISO 15765-4 (CAN)',
        'ISO 14230-4 (KWP)',
        'ISO 9141-2',
        'SAE J1850 VPW',
        'SAE J1850 PWM',
        'SAE J1939'
    ],
    adapters: [
        { id: 'simulated', name: 'No Adapter - Simulated Data' },
        { id: 'elm327-bt', name: 'ELM327 Bluetooth' },
        { id: 'elm327-wifi', name: 'ELM327 WiFi' },
        { id: 'vcds', name: 'VAG-COM / VCDS' },
        { id: 'torque', name: 'Torque Pro (Android)' },
        { id: 'carista', name: 'Carista OBD2' },
        { id: 'fixd', name: 'FIXD Smart OBD2' },
        { id: 'bluedriver', name: 'BlueDriver' },
        { id: 'obdfusion', name: 'OBD Fusion (iOS)' },
        { id: 'dashcommand', name: 'DashCommand' },
        { id: 'obddoctor', name: 'OBD Doctor' },
        { id: 'other', name: 'Other OBD2 Adapter' }
    ]
};

async function loadVehicleDatabase() {
    try {
        vehicleDatabase.makes = await window.apiClient.getMakes();
    } catch (err) {
        console.error('Failed to load vehicle makes');
    }
}