from typing import Dict, List, Optional

try:
    from ..models.vehicle import VEHICLES_DB as _VEHICLES_DB
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models.vehicle import VEHICLES_DB as _VEHICLES_DB

VEHICLES_DB = _VEHICLES_DB

def compare_vehicles(vehicle_id_1: str, vehicle_id_2: str, vehicles_db: Dict = None) -> Dict:
    db = vehicles_db or VEHICLES_DB
    vehicle_1 = db.get(vehicle_id_1)
    vehicle_2 = db.get(vehicle_id_2)
    
    if not vehicle_1 or not vehicle_2:
        return {'error': 'One or both vehicles not found'}
    
    def calculate_power_to_weight_ratio(vehicle: Dict) -> float:
        return vehicle['basePower'] / vehicle['weight']
    
    def calculate_torque_to_weight_ratio(vehicle: Dict) -> float:
        return vehicle['torque'] / vehicle['weight']
    
    def calculate_performance_score(vehicle: Dict) -> float:
        pwr = calculate_power_to_weight_ratio(vehicle)
        redline_factor = vehicle['redline'] / 8000
        return round(pwr * redline_factor * 100, 2)
    
    comparison = {
        'vehicles': {
            'vehicle_1': vehicle_1,
            'vehicle_2': vehicle_2
        },
        'metrics': {
            'power_comparison': {
                'vehicle_1': {
                    'power': vehicle_1['basePower'],
                    'difference': vehicle_1['basePower'] - vehicle_2['basePower'],
                    'better': vehicle_1['basePower'] > vehicle_2['basePower']
                },
                'vehicle_2': {
                    'power': vehicle_2['basePower'],
                    'difference': vehicle_2['basePower'] - vehicle_1['basePower'],
                    'better': vehicle_2['basePower'] > vehicle_1['basePower']
                }
            },
            'torque_comparison': {
                'vehicle_1': {
                    'torque': vehicle_1['torque'],
                    'difference': vehicle_1['torque'] - vehicle_2['torque'],
                    'better': vehicle_1['torque'] > vehicle_2['torque']
                },
                'vehicle_2': {
                    'torque': vehicle_2['torque'],
                    'difference': vehicle_2['torque'] - vehicle_1['torque'],
                    'better': vehicle_2['torque'] > vehicle_1['torque']
                }
            },
            'weight_comparison': {
                'vehicle_1': {
                    'weight': vehicle_1['weight'],
                    'difference': vehicle_1['weight'] - vehicle_2['weight'],
                    'better': vehicle_1['weight'] < vehicle_2['weight']
                },
                'vehicle_2': {
                    'weight': vehicle_2['weight'],
                    'difference': vehicle_2['weight'] - vehicle_1['weight'],
                    'better': vehicle_2['weight'] < vehicle_1['weight']
                }
            },
            'power_to_weight_ratio': {
                'vehicle_1': calculate_power_to_weight_ratio(vehicle_1),
                'vehicle_2': calculate_power_to_weight_ratio(vehicle_2)
            },
            'torque_to_weight_ratio': {
                'vehicle_1': calculate_torque_to_weight_ratio(vehicle_1),
                'vehicle_2': calculate_torque_to_weight_ratio(vehicle_2)
            },
            'performance_score': {
                'vehicle_1': calculate_performance_score(vehicle_1),
                'vehicle_2': calculate_performance_score(vehicle_2)
            }
        },
        'winner': _determine_winner(vehicle_1, vehicle_2, calculate_power_to_weight_ratio, calculate_performance_score)
    }
    
    return comparison

def _determine_winner(v1: Dict, v2: Dict, pwr_fn, perf_fn) -> str:
    v1_score = perf_fn(v1)
    v2_score = perf_fn(v2)
    
    if v1_score > v2_score:
        return f"{v1['make']} {v1['model']}"
    elif v2_score > v1_score:
        return f"{v2['make']} {v2['model']}"
    return "Tie"

def compare_vehicles_with_performance(
    vehicle_id_1: str, 
    vehicle_id_2: str, 
    vehicles_db: Dict = None,
    parts_db: List[Dict] = None,
    build_1: List[Dict] = None,
    build_2: List[Dict] = None,
    tune_1: Dict = None,
    tune_2: Dict = None
) -> Dict:
    db = vehicles_db or VEHICLES_DB
    vehicle_1 = db.get(vehicle_id_1)
    vehicle_2 = db.get(vehicle_id_2)
    
    if not vehicle_1 or not vehicle_2:
        return {'error': 'One or both vehicles not found'}
    
    parts_list = parts_db or []
    
    def calculate_projected_power(vehicle: Dict, build: List[Dict] = None, tune: Dict = None) -> int:
        power = vehicle['basePower']
        if build:
            for part in build:
                power += part.get('powerGain', 0)
        if tune and vehicle.get('turbo', False):
            power += int(tune.get('boost', 0) * 5)
        return power
    
    def calculate_projected_torque(vehicle: Dict, build: List[Dict] = None, tune: Dict = None) -> int:
        torque = vehicle['torque']
        if build:
            for part in build:
                torque += part.get('torqueGain', 0)
        return torque
    
    def calculate_projected_weight(vehicle: Dict, build: List[Dict] = None) -> int:
        weight = vehicle['weight']
        if build:
            for part in build:
                if part.get('category') == 'wheels':
                    weight -= 20
        return weight
    
    v1_power = calculate_projected_power(vehicle_1, build_1, tune_1)
    v2_power = calculate_projected_power(vehicle_2, build_2, tune_2)
    v1_torque = calculate_projected_torque(vehicle_1, build_1, tune_1)
    v2_torque = calculate_projected_torque(vehicle_2, build_2, tune_2)
    v1_weight = calculate_projected_weight(vehicle_1, build_1)
    v2_weight = calculate_projected_weight(vehicle_2, build_2)
    
    v1_pwr_ratio = v1_power / v1_weight
    v2_pwr_ratio = v2_power / v2_weight
    v1_tqr_ratio = v1_torque / v1_weight
    v2_tqr_ratio = v2_torque / v2_weight
    
    def calculate_perf_score(pwr: int, weight: int, redline: int) -> float:
        return round((pwr / weight) * (redline / 8000) * 100, 2)
    
    v1_score = calculate_perf_score(v1_power, v1_weight, vehicle_1.get('redline', 7000))
    v2_score = calculate_perf_score(v2_power, v2_weight, vehicle_2.get('redline', 7000))
    
    return {
        'vehicles': {
            'vehicle_1': vehicle_1,
            'vehicle_2': vehicle_2
        },
        'metrics': {
            'power_comparison': {
                'vehicle_1': {'power': v1_power, 'difference': v1_power - v2_power, 'better': v1_power > v2_power},
                'vehicle_2': {'power': v2_power, 'difference': v2_power - v1_power, 'better': v2_power > v1_power}
            },
            'torque_comparison': {
                'vehicle_1': {'torque': v1_torque, 'difference': v1_torque - v2_torque, 'better': v1_torque > v2_torque},
                'vehicle_2': {'torque': v2_torque, 'difference': v2_torque - v1_torque, 'better': v2_torque > v1_torque}
            },
            'weight_comparison': {
                'vehicle_1': {'weight': v1_weight, 'difference': v1_weight - v2_weight, 'better': v1_weight < v2_weight},
                'vehicle_2': {'weight': v2_weight, 'difference': v2_weight - v1_weight, 'better': v2_weight < v1_weight}
            },
            'base_power_comparison': {
                'vehicle_1': {'power': vehicle_1['basePower'], 'difference': vehicle_1['basePower'] - vehicle_2['basePower'], 'better': vehicle_1['basePower'] > vehicle_2['basePower']},
                'vehicle_2': {'power': vehicle_2['basePower'], 'difference': vehicle_2['basePower'] - vehicle_1['basePower'], 'better': vehicle_2['basePower'] > vehicle_1['basePower']}
            },
            'base_torque_comparison': {
                'vehicle_1': {'torque': vehicle_1['torque'], 'difference': vehicle_1['torque'] - vehicle_2['torque'], 'better': vehicle_1['torque'] > vehicle_2['torque']},
                'vehicle_2': {'torque': vehicle_2['torque'], 'difference': vehicle_2['torque'] - vehicle_1['torque'], 'better': vehicle_2['torque'] > vehicle_1['torque']}
            },
            'projected_weight': {
                'vehicle_1': v1_weight,
                'vehicle_2': v2_weight
            },
            'power_to_weight_ratio': {
                'vehicle_1': v1_pwr_ratio,
                'vehicle_2': v2_pwr_ratio
            },
            'torque_to_weight_ratio': {
                'vehicle_1': v1_tqr_ratio,
                'vehicle_2': v2_tqr_ratio
            },
            'performance_score': {
                'vehicle_1': v1_score,
                'vehicle_2': v2_score
            }
        },
        'builds': {
            'vehicle_1': {
                'parts_count': len(build_1) if build_1 else 0,
                'total_power_gain': sum(p.get('powerGain', 0) for p in (build_1 or [])),
                'total_torque_gain': sum(p.get('torqueGain', 0) for p in (build_1 or [])),
                'total_cost': sum(p.get('cost', 0) for p in (build_1 or [])),
                'tune': tune_1
            },
            'vehicle_2': {
                'parts_count': len(build_2) if build_2 else 0,
                'total_power_gain': sum(p.get('powerGain', 0) for p in (build_2 or [])),
                'total_torque_gain': sum(p.get('torqueGain', 0) for p in (build_2 or [])),
                'total_cost': sum(p.get('cost', 0) for p in (build_2 or [])),
                'tune': tune_2
            }
        },
        'winner': f"{vehicle_1['make']} {vehicle_1['model']}" if v1_score > v2_score else f"{vehicle_2['make']} {vehicle_2['model']}" if v2_score > v1_score else "Tie"
    }