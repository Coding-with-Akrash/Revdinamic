# AI Recommendation Service
from typing import Dict, List, Optional

try:
    from ..models.vehicle import VEHICLES_DB
    from ..models.part import PARTS_DB
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models.vehicle import VEHICLES_DB
    from models.part import PARTS_DB

def get_recommendations(vehicle_id: str, goal: str = 'daily', max_budget: int = 5000, current_parts: List[str] = None) -> Dict:
    vehicle = VEHICLES_DB.get(vehicle_id)
    if not vehicle:
        return {'error': 'Vehicle not found'}
    
    current_parts = current_parts or []
    
    goal_config = {
        'daily': {'focus': 'drivability', 'powerPreference': 'moderate', 'minStage': 1},
        'track': {'focus': 'performance', 'powerPreference': 'high', 'minStage': 1},
        'drag': {'focus': 'straight-line', 'powerPreference': 'extreme', 'minStage': 2},
        'street': {'focus': 'balanced', 'powerPreference': 'high', 'minStage': 1}
    }.get(goal, {'focus': 'drivability', 'powerPreference': 'moderate', 'minStage': 1})
    
    recommendations = []
    total_cost = 0
    total_power_gain = 0
    total_torque_gain = 0
    total_boost_gain = 0
    total_timing_gain = 0
    
    eligible_parts = [p for p in PARTS_DB if p.get('compatible') == ['all'] or p.get('compatible') is None]
    
    for part in eligible_parts:
        if part['id'] in current_parts:
            continue
        if goal_config['powerPreference'] == 'low' and part['powerGain'] > 30:
            continue
        if total_cost + part['cost'] <= max_budget:
            recommendations.append({
                **part,
                'priority': 'high' if part['powerGain'] > 50 else 'medium',
                'reason': f"{part['name']} - {part['description'][:60]}"
            })
            total_cost += part['cost']
            total_power_gain += part['powerGain']
            total_torque_gain += part['torqueGain']
            total_boost_gain += part.get('boostGain', 0)
            total_timing_gain += part.get('timingGain', 0)
    
    estimated_0_60 = max(2.5, 10.5 - ((vehicle['basePower'] + total_power_gain) / vehicle['weight'] * 1000 * 0.15))
    
    return {
        'vehicle': vehicle,
        'basePower': vehicle['basePower'],
        'baseTorque': vehicle['torque'],
        'projectedPower': vehicle['basePower'] + total_power_gain,
        'projectedTorque': vehicle['torque'] + total_torque_gain,
        'totalCost': total_cost,
        'totalPowerGain': total_power_gain,
        'totalTorqueGain': total_torque_gain,
        'totalBoostGain': total_boost_gain,
        'totalTimingGain': total_timing_gain,
        'goal': goal,
        'recommendations': recommendations[:8],
        'notes': [f"Build optimized for {goal} driving with your {vehicle['model']}.", "Consider professional installation for forced induction parts."],
        'estimated0_60': round(estimated_0_60, 1)
    }

def generate_tune(vehicle_id: str, parts_installed: List[str] = None, driving_style: str = 'balanced') -> Dict:
    vehicle = VEHICLES_DB.get(vehicle_id)
    if not vehicle:
        return {'error': 'Vehicle not found'}
    
    parts_installed = parts_installed or []
    total_power_gain = sum(p['powerGain'] for p in PARTS_DB if p['id'] in parts_installed)
    
    base_map = {
        'fuelTrim': 0,
        'timingAdvance': 24,
        'boostTarget': vehicle.get('turbo', False) and 14.5 or 0,
        'revLimit': vehicle['redline'],
        'launchControl': False,
        'tractionControl': 70,
        'afrTarget': 14.7,
        'camAdvance': 0
    }
    
    power_factor = min(total_power_gain / 100, 1.5)
    if vehicle.get('turbo', False):
        base_map['boostTarget'] = round(14.5 + power_factor * 10, 1)
        base_map['timingAdvance'] = round(24 + power_factor * 8, 1)
        base_map['afrTarget'] = 12.5
    else:
        base_map['timingAdvance'] = round(min(38, 24 + power_factor * 12), 1)
    
    style_factors = {
        'aggressive': {'launch': True, 'tc': 20, 'timing': 2},
        'balanced': {'launch': False, 'tc': 50, 'timing': 0},
        'conservative': {'launch': False, 'tc': 90, 'timing': -2},
        'daily': {'launch': False, 'tc': 70, 'timing': -1}
    }
    style = style_factors.get(driving_style, style_factors['balanced'])
    base_map['launchControl'] = style['launch']
    base_map['tractionControl'] = style['tc']
    base_map['timingAdvance'] += style['timing']
    
    return {
        'vehicle': f"{vehicle['make']} {vehicle['model']}",
        'basePower': vehicle['basePower'],
        'projectedPower': vehicle['basePower'] + total_power_gain,
        'map': base_map,
        'notes': ['Tune optimized for your vehicle configuration and driving style.']
    }