# OBD Simulator Service
import random
import math
from typing import Dict, Optional

try:
    from ..models.vehicle import VEHICLES_DB
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models.vehicle import VEHICLES_DB

OBD_SIMULATORS: Dict[str, Dict] = {}

def get_simulator(vehicle_id: str) -> Dict:
    if vehicle_id not in OBD_SIMULATORS:
        OBD_SIMULATORS[vehicle_id] = {'rpm': 800, 'speed': 0, 'coolantTemp': 90, 'horsepower': 0, 'torque': 0, 'running': True}
    return OBD_SIMULATORS[vehicle_id]

def get_data(vehicle_id: str) -> Dict:
    sim = get_simulator(vehicle_id)
    vehicle = VEHICLES_DB.get(vehicle_id, {})
    
    sim['rpm'] = max(800, min(8000, sim['rpm'] + (random.random() - 0.5) * 200))
    sim['speed'] = max(0, min(200, sim['speed'] + (random.random() - 0.5) * 10))
    sim['coolantTemp'] = max(80, min(110, sim['coolantTemp'] + (random.random() - 0.5) * 2))
    
    rpm_factor = sim['rpm'] / 8000
    load_factor = random.uniform(0.3, 0.9)
    torque_multiplier = math.exp(-((sim['rpm'] - 3500) / 2000) ** 2)
    power_multiplier = math.exp(-((sim['rpm'] - 5500) / 2500) ** 2)
    
    sim['torque'] = round(450 * torque_multiplier * (0.8 + load_factor * 0.4))
    sim['horsepower'] = round(380 * power_multiplier * (0.8 + load_factor * 0.4))
    
    return {
        'rpm': int(sim['rpm']),
        'speed': int(sim['speed']),
        'coolantTemp': int(sim['coolantTemp']),
        'intakeAirTemp': 35,
        'throttlePosition': round(random.uniform(10, 90), 1),
        'fuelPressure': 300,
        'engineLoad': round(load_factor * 100, 1),
        'fuelLevel': 85,
        'voltage': round(12.6 + random.uniform(-0.5, 0.5), 1),
        'horsepower': sim['horsepower'],
        'torque': sim['torque']
    }

def generate_dyno_curve(vehicle_id: str) -> list:
    vehicle = VEHICLES_DB.get(vehicle_id)
    if not vehicle:
        return []
    
    rpm_range = (1000, 8000)
    points = 50
    step = (rpm_range[1] - rpm_range[0]) / points
    curve = []
    
    for rpm in range(rpm_range[0], rpm_range[1] + 1, int(step)):
        torque_multiplier = math.exp(-((rpm - 3500) / 2000) ** 2)
        power_multiplier = math.exp(-((rpm - 5500) / 2500) ** 2)
        curve.append({
            'rpm': rpm,
            'torque': round(450 * torque_multiplier + (random.random() - 0.5) * 10),
            'horsepower': round(380 * power_multiplier + (random.random() - 0.5) * 5)
        })
    
    return curve