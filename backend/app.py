import os
import secrets
import re
import random
import smtplib
import sqlite3
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, List, Optional

DB_PATH = Path(__file__).parent / 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        vehicle_id TEXT NOT NULL,
        FOREIGN KEY (email) REFERENCES users(email)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_tunes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        vehicle_id TEXT NOT NULL,
        afr REAL,
        timing REAL,
        boost REAL,
        knock TEXT,
        installed_parts TEXT,
        FOREIGN KEY (email) REFERENCES users(email)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_builds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        vehicle_id TEXT NOT NULL,
        installed_parts TEXT,
        total_power INTEGER DEFAULT 0,
        total_torque INTEGER DEFAULT 0,
        total_cost INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (email) REFERENCES users(email)
    )''')
    # Migration: add installed_parts if missing
    c.execute('PRAGMA table_info(user_tunes)')
    columns = [col[1] for col in c.fetchall()]
    if 'installed_parts' not in columns:
        c.execute('ALTER TABLE user_tunes ADD COLUMN installed_parts TEXT')
    conn.commit()
    conn.close()

def get_user(email: str) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT email, password, name FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'email': row[0], 'password': row[1], 'name': row[2]}
    return None

def save_user(email: str, password: str, name: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (email, password, name) VALUES (?, ?, ?)', (email, password, name))
    conn.commit()
    conn.close()

def update_user_profile(email: str, name: str, new_password: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if new_password:
        c.execute('UPDATE users SET name = ?, password = ? WHERE email = ?', (name, generate_password_hash(new_password), email))
    else:
        c.execute('UPDATE users SET name = ? WHERE email = ?', (name, email))
    conn.commit()
    conn.close()

BASE_DIR = Path(__file__).parent.parent
STATIC_FOLDER = str(BASE_DIR / 'frontend')

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USER)
GPT_API_KEY = os.environ.get('GPT_API_KEY', os.environ.get('OPEN_AI_KEY', ''))

VEHICLES_DB: Dict[str, Dict] = {
    # Original vehicles
    'bmw-m3': {'make': 'BMW', 'model': 'M3', 'type': 'sedan', 'engine': 'I6 Twin-Turbo', 'basePower': 503, 'torque': 550, 'weight': 1500, 'Drivetrain': 'RWD', 'redline': 7200, 'turbo': True, 'cylinders': 6, 'displacement': '3.0L', 'year': 2024},
    'mustang-gt': {'make': 'Ford', 'model': 'Mustang GT', 'type': 'coupe', 'engine': 'V8 NA', 'basePower': 480, 'torque': 420, 'weight': 1700, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': False, 'cylinders': 8, 'displacement': '5.0L', 'year': 2024},
    'audi-rs6': {'make': 'Audi', 'model': 'RS6 Avant', 'type': 'wagon', 'engine': 'V8 Twin-Turbo', 'basePower': 591, 'torque': 800, 'weight': 2000, 'Drivetrain': 'AWD', 'redline': 6800, 'turbo': True, 'cylinders': 8, 'displacement': '4.0L', 'year': 2024},
    'amg-gt': {'make': 'Mercedes', 'model': 'AMG GT', 'type': 'coupe', 'engine': 'V8 Twin-Turbo', 'basePower': 577, 'torque': 700, 'weight': 1600, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': True, 'cylinders': 8, 'displacement': '4.0L', 'year': 2024},
    'supra': {'make': 'Toyota', 'model': 'GR Supra', 'type': 'coupe', 'engine': 'I6 Twin-Turbo', 'basePower': 382, 'torque': 369, 'weight': 1500, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': True, 'cylinders': 6, 'displacement': '3.0L', 'year': 2024},
    'gtr': {'make': 'Nissan', 'model': 'GT-R', 'type': 'coupe', 'engine': 'V6 Twin-Turbo', 'basePower': 565, 'torque': 481, 'weight': 1700, 'Drivetrain': 'AWD', 'redline': 7100, 'turbo': True, 'cylinders': 6, 'displacement': '3.8L', 'year': 2024},
    'civic-type-r': {'make': 'Honda', 'model': 'Civic Type R', 'type': 'hatchback', 'engine': 'I4 NA', 'basePower': 315, 'torque': 295, 'weight': 1300, 'Drivetrain': 'FWD', 'redline': 7200, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2024},
    'corvette': {'make': 'Chevrolet', 'model': 'Corvette C8', 'type': 'coupe', 'engine': 'V8 NA', 'basePower': 670, 'torque': 465, 'weight': 1500, 'Drivetrain': 'RWD', 'redline': 7000, 'turbo': False, 'cylinders': 8, 'displacement': '6.2L', 'year': 2024},
    
    # Pakistani Market Vehicles
    'toyota-corolla': {'make': 'Toyota', 'model': 'Corolla Altis', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 138, 'torque': 173, 'weight': 1250, 'Drivetrain': 'FWD', 'redline': 6200, 'turbo': False, 'cylinders': 4, 'displacement': '1.8L', 'year': 2023},
    'toyota-camry': {'make': 'Toyota', 'model': 'Camry', 'type': 'sedan', 'engine': 'I4 Hybrid', 'basePower': 208, 'torque': 221, 'weight': 1550, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '2.5L', 'year': 2023},
    'toyota-fortuner': {'make': 'Toyota', 'model': 'Fortuner', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 171, 'torque': 366, 'weight': 1850, 'Drivetrain': 'AWD', 'redline': 5600, 'turbo': True, 'cylinders': 4, 'displacement': '2.7L', 'year': 2023},
    'toyota-landcruiser': {'make': 'Toyota', 'model': 'Land Cruiser', 'type': 'suv', 'engine': 'V8 NA', 'basePower': 305, 'torque': 650, 'weight': 2400, 'Drivetrain': 'AWD', 'redline': 6200, 'turbo': False, 'cylinders': 8, 'displacement': '4.6L', 'year': 2023},
    'honda-civic': {'make': 'Honda', 'model': 'Civic', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 158, 'torque': 215, 'weight': 1200, 'Drivetrain': 'FWD', 'redline': 6800, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'honda-city': {'make': 'Honda', 'model': 'City', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 118, 'torque': 145, 'weight': 1100, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '1.2L', 'year': 2023},
    'honda-accord': {'make': 'Honda', 'model': 'Accord', 'type': 'sedan', 'engine': 'I4 Hybrid', 'basePower': 212, 'torque': 232, 'weight': 1500, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'honda-br-v': {'make': 'Honda', 'model': 'BR-V', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 118, 'torque': 145, 'weight': 1150, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '1.2L', 'year': 2023},
    'suzuki-mehran': {'make': 'Suzuki', 'model': 'Mehran', 'type': 'hatchback', 'engine': 'I3 NA', 'basePower': 39, 'torque': 54, 'weight': 850, 'Drivetrain': 'FWD', 'redline': 5600, 'turbo': False, 'cylinders': 3, 'displacement': '0.66L', 'year': 2022},
    'suzuki-alto': {'make': 'Suzuki', 'model': 'Alto', 'type': 'hatchback', 'engine': 'I3 NA', 'basePower': 47, 'torque': 64, 'weight': 800, 'Drivetrain': 'FWD', 'redline': 5400, 'turbo': False, 'cylinders': 3, 'displacement': '0.66L', 'year': 2023},
    'suzuki-swift': {'make': 'Suzuki', 'model': 'Swift', 'type': 'hatchback', 'engine': 'I4 NA', 'basePower': 125, 'torque': 148, 'weight': 1050, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '1.2L', 'year': 2023},
    'suzuki-wagon-r': {'make': 'Suzuki', 'model': 'Wagon R', 'type': 'hatchback', 'engine': 'I3 NA', 'basePower': 67, 'torque': 90, 'weight': 950, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 3, 'displacement': '1.0L', 'year': 2023},
    'suzuki-cultus': {'make': 'Suzuki', 'model': 'Cultus', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 95, 'torque': 128, 'weight': 980, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 4, 'displacement': '1.0L', 'year': 2023},
    'suzuki-jimny': {'make': 'Suzuki', 'model': 'Jimny', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 101, 'torque': 132, 'weight': 1100, 'Drivetrain': 'AWD', 'redline': 6200, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'mitsubishi-pajero': {'make': 'Mitsubishi', 'model': 'Pajero Sport', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 179, 'torque': 343, 'weight': 1950, 'Drivetrain': 'AWD', 'redline': 5400, 'turbo': True, 'cylinders': 4, 'displacement': '2.4L', 'year': 2023},
    'mitsubishi-lancer': {'make': 'Mitsubishi', 'model': 'Lancer Evolution', 'type': 'sedan', 'engine': 'I4 Turbo', 'basePower': 295, 'torque': 311, 'weight': 1400, 'Drivetrain': 'AWD', 'redline': 7000, 'turbo': True, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'mitsubishi-outlander': {'make': 'Mitsubishi', 'model': 'Outlander', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 128, 'torque': 147, 'weight': 1450, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.4L', 'year': 2023},
    'nissan-sunny': {'make': 'Nissan', 'model': 'Sunny', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 139, 'torque': 200, 'weight': 1180, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '1.6L', 'year': 2023},
    'nissan-sentra': {'make': 'Nissan', 'model': 'Sentra', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 149, 'torque': 200, 'weight': 1250, 'Drivetrain': 'FWD', 'redline': 6600, 'turbo': False, 'cylinders': 4, 'displacement': '1.8L', 'year': 2023},
    'nissan-x-trail': {'make': 'Nissan', 'model': 'X-Trail', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 165, 'torque': 200, 'weight': 1450, 'Drivetrain': 'AWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'hyundai-tucson': {'make': 'Hyundai', 'model': 'Tucson', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 150, 'torque': 192, 'weight': 1400, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'hyundai-elantra': {'make': 'Hyundai', 'model': 'Elantra', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 120, 'torque': 151, 'weight': 1250, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.6L', 'year': 2023},
    'hyundai-sonata': {'make': 'Hyundai', 'model': 'Sonata', 'type': 'sedan', 'engine': 'I4 Hybrid', 'basePower': 177, 'torque': 221, 'weight': 1450, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'kia-sportage': {'make': 'KIA', 'model': 'Sportage', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 150, 'torque': 192, 'weight': 1400, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'kia-picanto': {'make': 'KIA', 'model': 'Picanto', 'type': 'hatchback', 'engine': 'I3 NA', 'basePower': 67, 'torque': 94, 'weight': 900, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 3, 'displacement': '1.0L', 'year': 2023},
    'faw-v2': {'make': 'FAW', 'model': 'V2', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 139, 'torque': 200, 'weight': 1200, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'faw-v5': {'make': 'FAW', 'model': 'V5', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 147, 'torque': 221, 'weight': 1250, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'changan-alsvin': {'make': 'Changan', 'model': 'Alsvin', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 147, 'torque': 221, 'weight': 1150, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'changan-karvaan': {'make': 'Changan', 'model': 'Karvaan', 'type': 'mpv', 'engine': 'I4 NA', 'basePower': 85, 'torque': 115, 'weight': 1200, 'Drivetrain': 'FWD', 'redline': 5800, 'turbo': False, 'cylinders': 4, 'displacement': '1.3L', 'year': 2023},
    'haval-h6': {'make': 'Haval', 'model': 'H6', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 197, 'torque': 340, 'weight': 1600, 'Drivetrain': 'AWD', 'redline': 6400, 'turbo': True, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'haval-jolion': {'make': 'Haval', 'model': 'Jolion', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 197, 'torque': 340, 'weight': 1550, 'Drivetrain': 'AWD', 'redline': 6400, 'turbo': True, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'mg-hs': {'make': 'MG', 'model': 'HS', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 195, 'torque': 353, 'weight': 1550, 'Drivetrain': 'AWD', 'redline': 6400, 'turbo': True, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'mg-zs': {'make': 'MG', 'model': 'ZS', 'type': 'hatchback', 'engine': 'I4 NA', 'basePower': 147, 'torque': 221, 'weight': 1150, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'proton-saga': {'make': 'Proton', 'model': 'Saga', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 95, 'torque': 128, 'weight': 1050, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 4, 'displacement': '1.3L', 'year': 2023},
    'proton-x70': {'make': 'Proton', 'model': 'X70', 'type': 'suv', 'engine': 'I4 Turbo', 'basePower': 177, 'torque': 340, 'weight': 1500, 'Drivetrain': 'AWD', 'redline': 6400, 'turbo': True, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'dfsk-glory': {'make': 'DFSK', 'model': 'Glory 580', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 128, 'torque': 147, 'weight': 1450, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'jac-s5': {'make': 'JAC', 'model': 'S5', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 128, 'torque': 147, 'weight': 1450, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'zotye-z300': {'make': 'ZOTYE', 'model': 'Z300', 'type': 'sedan', 'engine': 'I4 NA', 'basePower': 138, 'torque': 173, 'weight': 1200, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '1.5L', 'year': 2023},
    'lifan-x60': {'make': 'Lifan', 'model': 'X60', 'type': 'suv', 'engine': 'I4 NA', 'basePower': 128, 'torque': 147, 'weight': 1400, 'Drivetrain': 'FWD', 'redline': 6400, 'turbo': False, 'cylinders': 4, 'displacement': '2.0L', 'year': 2023},
    'peugeot-2008': {'make': 'Peugeot', 'model': '2008', 'type': 'suv', 'engine': 'I3 NA', 'basePower': 115, 'torque': 162, 'weight': 1150, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 3, 'displacement': '1.2L', 'year': 2023},
    'peugeot-3008': {'make': 'Peugeot', 'model': '3008', 'type': 'suv', 'engine': 'I3 NA', 'basePower': 115, 'torque': 162, 'weight': 1300, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 3, 'displacement': '1.2L', 'year': 2023},
    'peugeot-5008': {'make': 'Peugeot', 'model': '5008', 'type': 'mpv', 'engine': 'I3 NA', 'basePower': 115, 'torque': 162, 'weight': 1350, 'Drivetrain': 'FWD', 'redline': 6000, 'turbo': False, 'cylinders': 3, 'displacement': '1.2L', 'year': 2023},
}

PARTS_DB: List[Dict] = [
    # Intake Systems
    {'id': 'cold-air-intake', 'name': 'Cold Air Intake System', 'category': 'intake', 'powerGain': 12, 'torqueGain': 18, 'boostGain': 0, 'timingGain': 0, 'cost': 499, 'difficulty': 1, 'stages': [1], 'description': 'High-flow conical air filter with smooth intake piping.', 'compatible': ['all']},
    {'id': 'short-ram-intake', 'name': 'Short Ram Intake', 'category': 'intake', 'powerGain': 8, 'torqueGain': 12, 'boostGain': 0, 'timingGain': 0, 'cost': 299, 'difficulty': 1, 'stages': [1], 'description': 'Compact intake for tight engine bays.', 'compatible': ['all']},
    {'id': 'high-flow-filter', 'name': 'High-Flow Air Filter', 'category': 'intake', 'powerGain': 5, 'torqueGain': 8, 'boostGain': 0, 'timingGain': 0, 'cost': 129, 'difficulty': 1, 'stages': [1], 'description': 'Reusable cotton gauze filter replacement.', 'compatible': ['all']},
    
    # Exhaust Systems
    {'id': 'cat-back-exhaust', 'name': 'Cat-Back Exhaust System', 'category': 'exhaust', 'powerGain': 18, 'torqueGain': 15, 'boostGain': 0, 'timingGain': 2, 'cost': 1299, 'difficulty': 2, 'stages': [1], 'description': 'Stainless steel performance exhaust with polished tips.', 'compatible': ['all']},
    {'id': 'turbo-back-exhaust', 'name': 'Turbo-Back Exhaust', 'category': 'exhaust', 'powerGain': 35, 'torqueGain': 25, 'boostGain': 2, 'timingGain': 3, 'cost': 2499, 'difficulty': 3, 'stages': [2, 3], 'description': 'Full race exhaust including downpipe.', 'compatible': ['turbo']},
    {'id': 'axle-back-exhaust', 'name': 'Axle-Back Exhaust', 'category': 'exhaust', 'powerGain': 12, 'torqueGain': 10, 'boostGain': 0, 'timingGain': 1, 'cost': 899, 'difficulty': 2, 'stages': [1], 'description': 'Designed for optimal flow and sound.', 'compatible': ['all']},
    
    # ECU Tuning
    {'id': 'ecu-remap', 'name': 'ECU Performance Remap', 'category': 'tuning', 'powerGain': 45, 'torqueGain': 60, 'boostGain': 3, 'timingGain': 8, 'cost': 799, 'difficulty': 1, 'stages': [1], 'description': 'Custom ECU tune for increased boost and timing.', 'compatible': ['turbo']},
    {'id': 'stand-alone-ecu', 'name': 'Standalone ECU System', 'category': 'tuning', 'powerGain': 120, 'torqueGain': 150, 'boostGain': 5, 'timingGain': 12, 'cost': 3499, 'difficulty': 5, 'stages': [3], 'description': 'Complete engine management replacement.', 'compatible': ['all']},
    
    # Forced Induction
    {'id': 'turbo-upgrade', 'name': 'Turbocharger Upgrade', 'category': 'forced-induction', 'powerGain': 80, 'torqueGain': 100, 'boostGain': 8, 'timingGain': 5, 'cost': 2999, 'difficulty': 4, 'stages': [2, 3], 'description': 'Larger ball-bearing turbo with increased flow.', 'compatible': ['turbo']},
    {'id': 'supercharger-kit', 'name': 'Supercharger Kit', 'category': 'forced-induction', 'powerGain': 75, 'torqueGain': 85, 'boostGain': 0, 'timingGain': 10, 'cost': 2799, 'difficulty': 4, 'stages': [2, 3], 'description': 'Positive displacement supercharger system.', 'compatible': ['na']},
    {'id': 'intercooler', 'name': 'Front Mount Intercooler', 'category': 'forced-induction', 'powerGain': 25, 'torqueGain': 30, 'boostGain': 0, 'timingGain': 0, 'cost': 1199, 'difficulty': 3, 'stages': [2], 'description': 'Aluminum intercooler for reduced intake temps.', 'compatible': ['turbo']},
    {'id': 'wastegate-upgrade', 'name': 'External Wastegate', 'category': 'forced-induction', 'powerGain': 15, 'torqueGain': 20, 'boostGain': 4, 'timingGain': 0, 'cost': 499, 'difficulty': 2, 'stages': [2], 'description': 'Upgraded wastegate for precise boost control.', 'compatible': ['turbo']},
    
    # Fuel System
    {'id': 'fuel-injectors', 'name': 'High-Flow Fuel Injectors', 'category': 'fuel', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 699, 'difficulty': 3, 'stages': [2, 3], 'description': '1000cc injectors for supporting modifications.', 'compatible': ['all']},
    {'id': 'fuel-pump', 'name': 'High-Pressure Fuel Pump', 'category': 'fuel', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 1299, 'difficulty': 4, 'stages': [3], 'description': 'Upgraded pump for high-horsepower builds.', 'compatible': ['all']},
    
    # Internal Engine
    {'id': 'forged-pistons', 'name': 'Forged Pistons', 'category': 'engine', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 5, 'cost': 1899, 'difficulty': 5, 'stages': [3], 'description': 'High-strength pistons for boosted applications.', 'compatible': ['turbo']},
    {'id': 'connecting-rods', 'name': 'Connecting Rods', 'category': 'engine', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 1499, 'difficulty': 5, 'stages': [3], 'description': 'H-beam rods for increased strength.', 'compatible': ['all']},
    {'id': 'valve-springs', 'name': 'Upgrade Valve Springs', 'category': 'engine', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 8, 'cost': 599, 'difficulty': 4, 'stages': [2, 3], 'description': 'High-rev valve springs for 8000+ RPM.', 'compatible': ['all']},
    
    # Brakes
    {'id': 'brake-kit-front', 'name': 'Front Big Brake Kit', 'category': 'brakes', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 2499, 'difficulty': 3, 'stages': [2, 3], 'description': '6-piston calipers with 380mm rotors.', 'compatible': ['all']},
    {'id': 'brake-kit-rear', 'name': 'Rear Brake Kit', 'category': 'brakes', 'powerGain': 0, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 1299, 'difficulty': 2, 'stages': [1, 2], 'description': '4-pot calipers with slotted rotors.', 'compatible': ['all']},
    
    # Wheels & Tires
    {'id': 'wheels-18x9', 'name': '18x9 Lightweight Wheels', 'category': 'wheels', 'powerGain': 10, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 1999, 'difficulty': 2, 'stages': [1], 'description': 'Forged wheels for reduced unsprung weight.', 'compatible': ['all']},
    {'id': 'racing-slicks', 'name': 'Racing Slicks', 'category': 'wheels', 'powerGain': 15, 'torqueGain': 0, 'boostGain': 0, 'timingGain': 0, 'cost': 899, 'difficulty': 1, 'stages': [2], 'description': 'Track-focused tire compound.', 'compatible': ['all']},
]

VEHICLE_DATABASE: Dict[str, List[str]] = {
    'bmw': ['M3', 'M5'],
    'audi': ['RS6', 'A4'],
    'mercedes': ['AMG GT'],
    'toyota': ['GR Supra', 'Corolla Altis', 'Camry', 'Fortuner', 'Land Cruiser'],
    'nissan': ['GT-R', 'Sunny', 'Sentra', 'X-Trail'],
    'honda': ['Civic Type R', 'Civic', 'City', 'Accord', 'BR-V'],
    'ford': ['Mustang GT'],
    'chevrolet': ['Corvette C8'],
    'suzuki': ['Mehran', 'Alto', 'Swift', 'Wagon R', 'Cultus', 'Jimny'],
    'mitsubishi': ['Pajero Sport', 'Lancer Evolution', 'Outlander'],
    'hyundai': ['Tucson', 'Elantra', 'Sonata'],
    'kia': ['Sportage', 'Picanto'],
    'faw': ['V2', 'V5'],
    'changan': ['Alsvin', 'Karvaan'],
    'haval': ['H6', 'Jolion'],
    'mg': ['HS', 'ZS'],
    'proton': ['Saga', 'X70'],
    'dfsk': ['Glory 580'],
    'jac': ['S5'],
    'zotye': ['Z300'],
    'lifan': ['X60'],
    'peugeot': ['2008', '3008', '5008']
}

USERS: Dict[str, Dict] = {}
VERIFICATION_TOKENS: Dict[str, Dict] = {}
PENDING_USERS: Dict[str, Dict] = {}
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
OBD_SIMULATORS: Dict[str, Dict] = {}
TUNE_DB: Dict[str, Dict] = {}

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'revdynamics-secret-key')
    CORS(app)
    init_db()
    return app

app = create_app()

@app.route('/')
def index_page():
    return send_from_directory(os.path.join(STATIC_FOLDER, 'static'), 'welcome.html')

@app.route('/<path:filename>')
def serve_static(filename):
    static_path = os.path.join(STATIC_FOLDER, 'static', filename)
    if os.path.exists(static_path):
        return send_from_directory(os.path.join(STATIC_FOLDER, 'static'), filename)
    static_path = os.path.join(STATIC_FOLDER, filename)
    if os.path.exists(static_path):
        return send_from_directory(STATIC_FOLDER, filename)
    return jsonify({'error': 'File not found'}), 404

def send_verification_email(email, token):
    if not SMTP_USER or not SMTP_PASS:
        return False
    msg = EmailMessage()
    msg['Subject'] = 'RevDynamics - Verify Your Email'
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    verification_url = f'http://localhost:5000/verify-email.html?token={token}'
    msg.set_content(f'''
Hello,

Thank you for registering with RevDynamics! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

- RevDynamics Team
''')
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'Email send failed: {e}')
        return False

def send_verification_email_code(email, code):
    if not SMTP_USER or not SMTP_PASS:
        return False
    msg = EmailMessage()
    msg['Subject'] = 'RevDynamics - Your Verification Code'
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    msg.set_content(f'''
Hello,

Thank you for registering with RevDynamics! Your verification code is:

{code}

Enter this code to complete your registration.

This code will expire in 24 hours.

- RevDynamics Team
''')
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'Email send failed: {e}')
        return False

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Generate 6-digit verification code
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    PENDING_USERS[email] = {'password': generate_password_hash(password), 'name': data.get('name', '') or data.get('fullName', ''), 'code': verification_code, 'expires': datetime.now() + timedelta(hours=24)}
    
    has_smtp = bool(SMTP_USER and SMTP_PASS)
    if has_smtp:
        email_sent = send_verification_email_code(email, verification_code)
        if email_sent:
            message = 'Verification code sent to your email. Please check your inbox.'
        else:
            message = 'Could not send verification email. Use code: ' + verification_code
    else:
        message = 'Registration successful. Use verification code: ' + verification_code
    
    return jsonify({'success': True, 'message': message}), 201

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json() or {}
    email = data.get('email', '').lower().strip()
    code = data.get('code', '')
    
    pending = PENDING_USERS.get(email)
    if not pending:
        return jsonify({'error': 'No pending registration found'}), 400
    if pending['expires'] < datetime.now():
        PENDING_USERS.pop(email, None)
        return jsonify({'error': 'Verification code expired'}), 400
    if pending['code'] != code:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    # Move to verified users
    save_user(email, pending['password'], pending['name'])
    PENDING_USERS.pop(email, None)
    
    return jsonify({'success': True, 'message': 'Email verified successfully! You can now log in.'})

@app.route('/api/tune', methods=['POST'])
def generate_tune():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId', '')
    tune = {
        'afr': float(data.get('afr', 12.5)),
        'timing': float(data.get('timing', 24)),
        'boost': float(data.get('boost', 14.5)),
        'knock': data.get('knock', 'standard')
    }
    TUNE_DB[vehicle_id] = tune
    return jsonify({'success': True, 'tune': tune, 'message': 'Tune generated and applied successfully'})

@app.route('/api/dyno-start', methods=['POST'])
def dyno_start():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId', '')
    if vehicle_id in OBD_SIMULATORS:
        OBD_SIMULATORS[vehicle_id]['rpm'] = 800
        OBD_SIMULATORS[vehicle_id]['dynoRunning'] = True
    else:
        OBD_SIMULATORS[vehicle_id] = {'rpm': 800, 'speed': 0, 'horsepower': 0, 'torque': 0, 'dynoRunning': True}
    return jsonify({'success': True})

@app.route('/api/dyno-stop', methods=['POST'])
def dyno_stop():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId', '')
    if vehicle_id in OBD_SIMULATORS:
        OBD_SIMULATORS[vehicle_id]['dynoRunning'] = False
    return jsonify({'success': True})

@app.route('/api/verify-email')
def verify_email():
    token = request.args.get('token', '')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    token_data = VERIFICATION_TOKENS.get(token)
    if not token_data:
        return jsonify({'error': 'Invalid or expired token'}), 400
    if token_data['expires'] < datetime.now():
        del VERIFICATION_TOKENS[token]
        return jsonify({'error': 'Token has expired'}), 400
    email = token_data['email']
    USERS[email] = {'password': token_data['password'], 'name': token_data['name'], 'email': email}
    del VERIFICATION_TOKENS[token]
    return jsonify({'success': True, 'message': f'Email {email} verified successfully!'})

@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json() or {}
    email = data.get('email', '').lower().strip()
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email address'}), 400
    matching_tokens = [(t, d) for t, d in VERIFICATION_TOKENS.items() if d['email'] == email]
    if matching_tokens:
        token, token_data = matching_tokens[0]
    else:
        token = secrets.token_urlsafe(32)
        VERIFICATION_TOKENS[token] = {'email': email, 'password': '', 'name': '', 'expires': datetime.now() + timedelta(hours=24)}
    send_verification_email(email, token)
    return jsonify({'success': True, 'message': f'Verification email sent to {email}. Check your inbox.', 'verificationToken': token})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    user = get_user(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user_id'] = email
    return jsonify({'success': True, 'user': {'email': email, 'name': user['name']}})

@app.route('/api/vehicles')
def get_vehicles():
    vehicles = []
    for key, v in VEHICLES_DB.items():
        vehicles.append({
            'id': key,
            'make': v.get('make', ''),
            'model': v.get('model', ''),
            'type': v.get('type', ''),
            'engine': v.get('engine', ''),
            'basePower': v.get('basePower', 300),
            'torque': v.get('torque', 300),
            'weight': v.get('weight', 1500),
            'Drivetrain': v.get('Drivetrain', 'FWD'),
            'redline': v.get('redline', 6000),
            'turbo': v.get('turbo', False),
            'cylinders': v.get('cylinders', 4),
            'displacement': v.get('displacement', '2.0L'),
            'year': v.get('year', 2023)
        })
    return jsonify(vehicles)

@app.route('/api/obd-connect/<vehicle_id>', methods=['POST'])
def obd_connect(vehicle_id):
    data = request.get_json() or {}
    action = data.get('action', 'connect')
    adapter_name = data.get('adapterName', '')
    port = data.get('port', '')
    baud_rate = data.get('baudRate', '38400')
    
    if vehicle_id not in OBD_SIMULATORS:
        OBD_SIMULATORS[vehicle_id] = {'rpm': 800, 'speed': 0, 'horsepower': 0, 'torque': 0, 'dynoRunning': False, 'connected': False, 'adapterName': '', 'port': '', 'baudRate': ''}
    
    if action == 'connect':
        if not adapter_name or not port:
            return jsonify({'success': False, 'error': 'Adapter name and port are required'}), 400
        OBD_SIMULATORS[vehicle_id]['connected'] = True
        OBD_SIMULATORS[vehicle_id]['adapterName'] = adapter_name
        OBD_SIMULATORS[vehicle_id]['port'] = port
        OBD_SIMULATORS[vehicle_id]['baudRate'] = baud_rate
        OBD_SIMULATORS[vehicle_id]['rpm'] = 800
        OBD_SIMULATORS[vehicle_id]['speed'] = 0
        OBD_SIMULATORS[vehicle_id]['horsepower'] = 0
        OBD_SIMULATORS[vehicle_id]['torque'] = 0
    else:
        OBD_SIMULATORS[vehicle_id]['connected'] = False
        OBD_SIMULATORS[vehicle_id]['dynoRunning'] = False
    
    return jsonify({'success': True, 'connected': OBD_SIMULATORS[vehicle_id]['connected'], 'adapterName': adapter_name, 'port': port, 'baudRate': baud_rate})

@app.route('/api/obd-data/<vehicle_id>')
def get_obd_data(vehicle_id):
    vehicle = VEHICLES_DB.get(vehicle_id, {})
    
    # Initialize simulator entry if not exists
    if vehicle_id not in OBD_SIMULATORS:
        OBD_SIMULATORS[vehicle_id] = {'rpm': 800, 'speed': 0, 'horsepower': 0, 'torque': 0, 'dynoRunning': False, 'connected': False}
    
    sim = OBD_SIMULATORS[vehicle_id]
    
    # Only return meaningful data if OBD is connected
    if not sim.get('connected', False):
        return jsonify({'rpm': None, 'speed': None, 'horsepower': None, 'torque': None, 'coolantTemp': None, 'connected': False})
    
    # Get base values
    base_power = vehicle.get('basePower', 300)
    base_torque = vehicle.get('torque', 300)
    
    # Get saved tune/performance gains from database
    tune = TUNE_DB.get(vehicle_id, {})
    total_power_gain = 0
    total_torque_gain = 0
    total_boost_gain = 0
    total_timing_gain = 0
    
    # Get installed parts from database for authenticated users
    if 'user_id' in session:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT installed_parts FROM user_tunes WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            try:
                parts_ids = json.loads(row[0])
                for p in PARTS_DB:
                    if p['id'] in parts_ids:
                        total_power_gain += p.get('powerGain', 0)
                        total_torque_gain += p.get('torqueGain', 0)
                        total_boost_gain += p.get('boostGain', 0)
                        total_timing_gain += p.get('timingGain', 0)
            except:
                pass
    
    if sim.get('dynoRunning'):
        sim['rpm'] = min(8000, sim['rpm'] + 300)
    else:
        sim['rpm'] = max(800, min(8000, sim['rpm'] + (random.random() - 0.5) * 200))
    
    sim['speed'] = max(0, min(200, sim['speed'] + (random.random() - 0.5) * 20))
    sim['coolantTemp'] = int(80 + random.random() * 20)
    
    if sim['rpm'] >= 1000:
        rpm_ratio = sim['rpm'] / 7200
        power = int((base_power + total_power_gain) * rpm_ratio * 0.85 + (tune.get('boost', 0) + total_boost_gain) * 5)
        torque = int((base_torque + total_torque_gain) * (1 - (sim['rpm'] - 4000) / 8000 * 0.3)) if sim['rpm'] > 4000 else int((base_torque + total_torque_gain) * (sim['rpm'] / 4000) * 0.7)
        sim['horsepower'] = max(power, 50)
        sim['torque'] = max(torque, 50)
    else:
        sim['horsepower'] = 0
        sim['torque'] = 0
    
    return jsonify({'rpm': int(sim['rpm']), 'speed': int(sim['speed']), 'horsepower': sim['horsepower'], 'torque': sim['torque'], 'coolantTemp': sim['coolantTemp'], 'connected': True})

@app.route('/api/parts')
def get_parts():
    return jsonify(PARTS_DB)

@app.route('/api/parts/filter')
def filter_parts():
    category = request.args.get('category', 'all')
    stage = request.args.get('stage', 'all')
    maxPrice = request.args.get('maxPrice', 'all')
    goal = request.args.get('goal', 'all')
    
    goal_categories = {
        'daily': ['intake', 'exhaust', 'fuel', 'brakes'],
        'street': ['intake', 'exhaust', 'tuning', 'fuel', 'brakes'],
        'track': ['intake', 'exhaust', 'tuning', 'forced-induction', 'brakes', 'wheels'],
        'drag': ['forced-induction', 'fuel', 'tuning']
    }
    
    filtered = PARTS_DB
    if category != 'all':
        filtered = [p for p in filtered if p.get('category') == category]
    if goal != 'all':
        filtered = [p for p in filtered if p.get('category') in goal_categories.get(goal, [])]
    if stage != 'all':
        filtered = [p for p in filtered if int(stage) in p.get('stages', [])]
    if maxPrice != 'all':
        try:
            max_price = int(maxPrice)
            filtered = [p for p in filtered if p.get('cost', 0) <= max_price]
        except (ValueError, TypeError):
            pass
    
    return jsonify(filtered)

@app.route('/api/parts/category/<category>')
def get_parts_by_category(category):
    if category == 'all':
        return jsonify(PARTS_DB)
    filtered = [p for p in PARTS_DB if p.get('category') == category]
    return jsonify(filtered)

MAKE_NAMES = {
    'bmw': 'BMW', 'audi': 'Audi', 'mercedes': 'Mercedes', 'toyota': 'Toyota', 
    'nissan': 'Nissan', 'honda': 'Honda', 'ford': 'Ford', 'chevrolet': 'Chevrolet',
    'suzuki': 'Suzuki', 'mitsubishi': 'Mitsubishi', 'hyundai': 'Hyundai', 'kia': 'KIA',
    'faw': 'FAW', 'changan': 'Changan', 'haval': 'Haval', 'mg': 'MG',
    'proton': 'Proton', 'dfsk': 'DFSK', 'jac': 'JAC', 'zotye': 'ZOTYE', 'lifan': 'Lifan',
    'peugeot': 'Peugeot'
}

@app.route('/api/makes')
def get_makes():
    makes = [{'id': make, 'name': MAKE_NAMES.get(make, make.title())} for make in VEHICLE_DATABASE.keys()]
    return jsonify(makes)

@app.route('/api/models/<make_id>')
def get_models(make_id):
    models = VEHICLE_DATABASE.get(make_id, [])
    return jsonify(models)

@app.route('/api/dyno-curve/<vehicle_id>')
def get_dyno_curve(vehicle_id):
    vehicle = VEHICLES_DB.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    tune = TUNE_DB.get(vehicle_id, {})
    base_power = vehicle.get('basePower', 300)
    base_torque = vehicle.get('torque', 300)
    boost_gain = tune.get('boost', 0) * 5
    
    total_power_gain = 0
    total_torque_gain = 0
    total_boost_gain = 0
    
    if 'user_id' in session:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT installed_parts FROM user_tunes WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            try:
                parts_ids = json.loads(row[0])
                for p in PARTS_DB:
                    if p['id'] in parts_ids:
                        total_power_gain += p.get('powerGain', 0)
                        total_torque_gain += p.get('torqueGain', 0)
                        total_boost_gain += p.get('boostGain', 0)
            except:
                pass
    
    curve = []
    for rpm in range(1000, 8500, 500):
        power = int((base_power + total_power_gain) * (rpm / 7200) * 0.85 + (boost_gain + total_boost_gain * 5))
        torque = int((base_torque + total_torque_gain) * (1 - (rpm - 4000) / 8000 * 0.3)) if rpm > 4000 else int((base_torque + total_torque_gain) * (rpm / 4000) * 0.7)
        curve.append({'rpm': rpm, 'horsepower': max(power, 50), 'torque': max(torque, 50)})
    return jsonify(curve)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId', '')
    goal = data.get('goal', 'daily')
    max_budget = data.get('maxBudget', 5000)
    current_parts = data.get('installedParts', [])
    
    vehicle = VEHICLES_DB.get(vehicle_id, {})
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
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
    
    for part in PARTS_DB:
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
    
    # Try GPT for enhanced tuning recommendations
    gpt_notes = []
    if GPT_API_KEY:
        try:
            import requests
            gpt_prompt = f"""You are a performance tuning expert. For a {vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')} ({vehicle.get('engine', '')}), 
            recommend a specific tune setup for {goal} driving. Include AFR, timing advance, and boost settings with brief explanations."""
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {GPT_API_KEY}', 'Content-Type': 'application/json'},
                json={'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': gpt_prompt}], 'max_tokens': 300},
                timeout=15
            )
            if response.status_code == 200:
                gpt_notes = [response.json()['choices'][0]['message']['content']]
        except Exception:
            gpt_notes = [f"GPT-4 recommended tune for {goal} driving with your {vehicle['model']}.", "Consider professional installation for forced induction parts."]
    else:
        gpt_notes = [f"Build optimized for {goal} driving with your {vehicle['model']}.", "Consider professional installation for forced induction parts."]
    
    return jsonify({
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
        'parts': recommendations[:8],
        'notes': gpt_notes,
        'estimated0_60': round(estimated_0_60, 1)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    
    try:
        import requests
        if GPT_API_KEY:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {GPT_API_KEY}', 'Content-Type': 'application/json'},
                json={'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': message}], 'max_tokens': 200},
                timeout=10
            )
            if response.status_code == 200:
                return jsonify({'response': response.json()['choices'][0]['message']['content']})
    except Exception:
        pass
    
    responses = {
        'hello': "Hello! I'm your AI tuning assistant. How can I help?",
        'help': "I can help with OBD-II data interpretation, tuning recommendations, and performance analysis.",
        'default': "I understand you're asking about your vehicle. Check the live dashboard for real-time data or browse our parts catalog for tuning options."
    }
    response_key = 'default'
    for key in responses:
        if key in message.lower():
            response_key = key
            break
    return jsonify({'response': responses[response_key]})

@app.route('/api/vehicles/<vehicle_id>')
def get_vehicle(vehicle_id):
    vehicle = VEHICLES_DB.get(vehicle_id)
    if vehicle:
        return jsonify(vehicle)
    return jsonify({'error': 'Vehicle not found'}), 404

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})


@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session:
        user = get_user(session['user_id'])
        if user:
            return jsonify({'authenticated': True, 'user': {'email': session['user_id'], 'name': user['name']}})
    return jsonify({'authenticated': False})

@app.route('/api/profile', methods=['GET', 'PUT'])
def profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    email = session['user_id']
    
    if request.method == 'GET':
        user = get_user(email)
        if user:
            return jsonify({'email': user['email'], 'name': user['name']})
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        name = data.get('name', '')
        password = data.get('password', '')
        
        update_user_profile(email, name, password if password else None)
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    
@app.route('/api/vehicle-build', methods=['POST'])
def save_vehicle_build():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401

    data = request.get_json() or {}
    vehicle_id = data.get('vehicleId', '')
    installed_parts = data.get('installedParts', [])

    import json

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    total_power = sum(p.get('powerGain', 0) for p in installed_parts)
    total_torque = sum(p.get('torqueGain', 0) for p in installed_parts)
    total_cost = sum(p.get('cost', 0) for p in installed_parts)

    c.execute('SELECT id FROM user_builds WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id))
    existing = c.fetchone()
    
    if existing:
        c.execute('''UPDATE user_builds SET 
            installed_parts = ?, total_power = ?, total_torque = ?, total_cost = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?''', 
            (json.dumps(installed_parts), total_power, total_torque, total_cost, existing[0]))
    else:
        c.execute('''INSERT INTO user_builds 
            (email, vehicle_id, installed_parts, total_power, total_torque, total_cost) 
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (session['user_id'], vehicle_id, json.dumps(installed_parts), total_power, total_torque, total_cost))
    
    conn.commit()
    conn.close()

    return jsonify({
        'success': True, 
        'message': 'Build saved successfully',
        'totalPower': total_power,
        'totalTorque': total_torque,
        'totalCost': total_cost
    })

@app.route('/api/vehicle-build/<vehicle_id>')
def get_vehicle_build(vehicle_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated', 'success': False}), 401

    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT installed_parts, total_power, total_torque, total_cost, created_at FROM user_builds WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id))
    row = c.fetchone()
    conn.close()

    if row and row[0]:
        try:
            installed_parts = json.loads(row[0])
            return jsonify({
                'success': True,
                'installedParts': installed_parts,
                'totalPower': row[1],
                'totalTorque': row[2],
                'totalCost': row[3],
                'savedAt': row[4]
            })
        except:
            pass
    return jsonify({'success': True, 'installedParts': []})

@app.route('/api/compare-vehicles', methods=['POST'])
def compare_vehicles_route():
    data = request.get_json() or {}
    vehicle_id_1 = data.get('vehicleId1', '')
    vehicle_id_2 = data.get('vehicleId2', '')
    
    build_1 = []
    build_2 = []
    tune_1 = {}
    tune_2 = {}
    
    if 'user_id' in session:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('SELECT installed_parts FROM user_builds WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id_1))
        row = c.fetchone()
        if row and row[0]:
            try:
                build_1 = json.loads(row[0])
            except:
                build_1 = []
        
        c.execute('SELECT installed_parts FROM user_builds WHERE email = ? AND vehicle_id = ?', (session['user_id'], vehicle_id_2))
        row = c.fetchone()
        if row and row[0]:
            try:
                build_2 = json.loads(row[0])
            except:
                build_2 = []
        
        tune_1 = TUNE_DB.get(vehicle_id_1, {})
        tune_2 = TUNE_DB.get(vehicle_id_2, {})
        
        conn.close()
    
    from services.vehicle_comparison_service import compare_vehicles_with_performance
    result = compare_vehicles_with_performance(vehicle_id_1, vehicle_id_2, VEHICLES_DB, PARTS_DB, build_1, build_2, tune_1, tune_2)
    
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)

@app.route('/dashboard')
def dashboard():
    return send_from_directory(os.path.join(STATIC_FOLDER, 'static'), 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
