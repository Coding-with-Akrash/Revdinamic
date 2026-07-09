# Vehicle data model and database
from typing import Dict, List

VEHICLES_DB: Dict[str, Dict] = {
    'bmw-m3': {'make': 'BMW', 'model': 'M3', 'type': 'sedan', 'engine': 'I6 Twin-Turbo', 'basePower': 503, 'torque': 550, 'weight': 1500, 'Drivetrain': 'RWD', 'redline': 7200, 'turbo': True, 'cylinders': 6, 'displacement': '3.0L', 'year': 2024},
    'mustang-gt': {'make': 'Ford', 'model': 'Mustang GT', 'type': 'coupe', 'engine': 'V8 NA', 'basePower': 480, 'torque': 420, 'weight': 1700, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': False, 'cylinders': 8, 'displacement': '5.0L', 'year': 2024},
    'audi-rs6': {'make': 'Audi', 'model': 'RS6 Avant', 'type': 'wagon', 'engine': 'V8 Twin-Turbo', 'basePower': 591, 'torque': 800, 'weight': 2000, 'Drivetrain': 'AWD', 'redline': 6800, 'turbo': True, 'cylinders': 8, 'displacement': '4.0L', 'year': 2024},
    'amg-gt': {'make': 'Mercedes', 'model': 'AMG GT', 'type': 'coupe', 'engine': 'V8 Twin-Turbo', 'basePower': 577, 'torque': 700, 'weight': 1800, 'Drivetrain': 'RWD', 'redline': 6800, 'turbo': True, 'cylinders': 8, 'displacement': '4.0L', 'year': 2024},
    'supra': {'make': 'Toyota', 'model': 'GR Supra', 'type': 'coupe', 'engine': 'I6 Twin-Turbo', 'basePower': 382, 'torque': 500, 'weight': 1500, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': True, 'cylinders': 6, 'displacement': '3.0L', 'year': 2024},
    'gtr': {'make': 'Nissan', 'model': 'GT-R', 'type': 'coupe', 'engine': 'V6 Twin-Turbo', 'basePower': 565, 'torque': 633, 'weight': 1740, 'Drivetrain': 'AWD', 'redline': 7000, 'turbo': True, 'cylinders': 6, 'displacement': '3.8L', 'year': 2024},
    'civic-type-r': {'make': 'Honda', 'model': 'Civic Type R', 'type': 'hatchback', 'engine': 'I4 Turbo', 'basePower': 315, 'torque': 420, 'weight': 1430, 'Drivetrain': 'FWD', 'redline': 7000, 'turbo': True, 'cylinders': 4, 'displacement': '2.0L', 'year': 2024},
    'corvette': {'make': 'Chevrolet', 'model': 'Corvette C8', 'type': 'coupe', 'engine': 'V8 Twin-Turbo', 'basePower': 670, 'torque': 760, 'weight': 1600, 'Drivetrain': 'RWD', 'redline': 6500, 'turbo': True, 'cylinders': 8, 'displacement': '5.5L', 'year': 2024},
}

VEHICLE_DATABASE: Dict[str, List[str]] = {
    'bmw': ['M3', 'M5', 'M4', 'X5 M', '3 Series', '5 Series'],
    'audi': ['RS6', 'RS7', 'A4', 'A6'],
    'mercedes': ['AMG GT', 'C63 AMG', 'E63 AMG'],
    'toyota': ['GR Supra', 'Camry', 'Corolla', 'Yaris'],
    'nissan': ['GT-R', 'Altima', 'Maxima'],
    'honda': ['Civic Type R', 'Accord', 'CR-V'],
    'ford': ['Mustang GT', 'Focus ST'],
    'chevrolet': ['Corvette C8', 'Camaro SS'],
}