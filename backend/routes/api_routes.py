# API Routes - Vehicle, Parts, OBD, Chat endpoints
from flask import request, jsonify

try:
    from ..models.vehicle import VEHICLES_DB, VEHICLE_DATABASE
    from ..models.part import PARTS_DB
    from ..services.obd_service import get_data as get_obd_data, generate_dyno_curve
    from ..services.recommendation_service import get_recommendations, generate_tune
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models.vehicle import VEHICLES_DB, VEHICLE_DATABASE
    from models.part import PARTS_DB
    from services.obd_service import get_data as get_obd_data, generate_dyno_curve
    from services.recommendation_service import get_recommendations, generate_tune

def get_vehicles():
    return jsonify(list(VEHICLES_DB.values()))

def get_vehicle(vehicle_id: str):
    vehicle = VEHICLES_DB.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    return jsonify(vehicle)

def get_obd(vehicle_id: str):
    data = get_obd_data(vehicle_id)
    return jsonify(data)

def get_parts():
    category = request.args.get('category', 'all')
    stage = request.args.get('stage', 'all')
    max_price = request.args.get('maxPrice', 'all')
    goal = request.args.get('goal', 'all')
    
    goal_categories = {
        'daily': ['intake', 'exhaust', 'fuel', 'brakes'],
        'street': ['intake', 'exhaust', 'tuning', 'fuel', 'brakes'],
        'track': ['intake', 'exhaust', 'tuning', 'forced-induction', 'brakes', 'wheels'],
        'drag': ['forced-induction', 'fuel', 'tuning']
    }
    
    parts = PARTS_DB.copy()
    
    if category != 'all':
        parts = [p for p in parts if p['category'] == category]
    
    if goal != 'all':
        parts = [p for p in parts if p['category'] in goal_categories.get(goal, [])]
    
    if stage != 'all':
        stage_int = int(stage)
        parts = [p for p in parts if stage_int in p['stages']]
    
    if max_price != 'all':
        parts = [p for p in parts if p['cost'] <= int(max_price)]
    
    return jsonify(parts)

def get_dyno_curve(vehicle_id: str):
    curve = generate_dyno_curve(vehicle_id)
    return jsonify(curve)

def get_part_categories():
    categories = list(set(p['category'] for p in PARTS_DB))
    return jsonify(categories)

def get_parts_by_category(category: str):
    if category == 'all':
        return jsonify(PARTS_DB)
    parts = [p for p in PARTS_DB if p['category'] == category]
    return jsonify(parts)

def get_recommendations_route():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId')
    goal = data.get('goal', 'daily')
    max_budget = data.get('maxBudget', 5000)
    current_parts = data.get('installedParts', [])
    
    result = get_recommendations(vehicle_id, goal, max_budget, current_parts)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)

def generate_tune_route():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId')
    parts_installed = data.get('installedParts', [])
    driving_style = data.get('drivingStyle', 'balanced')
    
    result = generate_tune(vehicle_id, parts_installed, driving_style)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)

def get_makes():
    return jsonify([{'id': k, 'name': k.title()} for k in VEHICLE_DATABASE.keys()])

def get_models(make_id: str):
    models = VEHICLE_DATABASE.get(make_id, [])
    return jsonify(models)

def chat():
    data = request.get_json() or {}
    query = data.get('message', '').lower()
    
    obd_data = {'rpm': 5500, 'speed': 120, 'coolantTemp': 90, 'horsepower': 380, 'torque': 450}
    
    if 'rpm' in query:
        return jsonify({'response': f"Current RPM: {obd_data['rpm'] / 1000:.1f}k"})
    if 'speed' in query:
        return jsonify({'response': f"Current speed: {obd_data['speed']} km/h"})
    if 'power' in query or 'hp' in query:
        return jsonify({'response': f"Power: {obd_data['horsepower']} HP | Torque: {obd_data['torque']} Nm"})
    if 'temp' in query:
        return jsonify({'response': f"Coolant temp: {obd_data['coolantTemp']}°C"})
    if 'tuning' in query or 'recommend' in query:
        return jsonify({'response': "For daily driving, try Stage 1 ECU tune with intake/exhaust. For track, add intercooler and Stage 2 tune."})
    if 'parts' in query or 'upgrade' in query:
        return jsonify({'response': "Top upgrades: Cold air intake (+15HP), Cat-back exhaust (+20HP), ECU remap (+45HP), Intercooler (+25HP)."})
    
    return jsonify({'response': "I can help with OBD data, tuning advice, parts recommendations, and dyno analysis. What do you need?"})