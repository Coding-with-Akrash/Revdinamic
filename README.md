# RevDynamics

Real-time OBD-II vehicle diagnostics and AI-powered tuning platform.

## Architecture

```
rev-dynamics/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── run.py              # Application runner with dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vehicle.py      # Vehicle database and specs
│   │   └── part.py         # Performance parts catalog
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py  # Authentication endpoints
│   │   └── api_routes.py   # API endpoints (vehicles, parts, OBD, chat)
│   └── services/
│       ├── __init__.py
│       ├── obd_service.py  # OBD data simulation
│       └── recommendation_service.py  # AI recommendations
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── static/
│   │   ├── welcome.html    # Welcome/authentication entry point
│   │   ├── index.html      # Main dashboard (protected)
│   │   ├── dyno-tune.html  # Dyno tuning interface (protected)
│   │   ├── vehicle-select.html  # Vehicle selection (protected)
│   │   ├── parts-catalog.html   # Parts catalog with AI (protected)
│   │   ├── registration.html    # User registration
│   │   ├── owner-login.html     # Owner login
│   │   ├── tuner-login.html     # Tuner login
│   │   ├── verify-email.html    # Email verification
│   │   ├── forgot-password.html # Password recovery
│   │   └── recover-password.html # Password reset
│   └── js/
│       ├── api-client.js   # Backend API client
│       ├── main.js         # Main application controller
│       ├── vehicle-manager.js  # Vehicle state management
│       └── auth-guard.js   # Authentication guard for protected pages
│   └── css/
│       └── style.css       # Main stylesheet
├── package.json
└── README.md
```
autodyno-ai/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── run.py              # Application runner with dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vehicle.py      # Vehicle database and specs
│   │   └── part.py         # Performance parts catalog
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py  # Authentication endpoints
│   │   └── api_routes.py   # API endpoints (vehicles, parts, OBD, chat)
│   └── services/
│       ├── __init__.py
│       ├── obd_service.py  # OBD data simulation
│       └── recommendation_service.py  # AI recommendations
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── static/
│   │   ├── index.html      # Main dashboard
│   │   ├── dyno-tune.html  # Dyno tuning interface
│   │   ├── vehicle-select.html  # Vehicle selection
│   │   ├── parts-catalog.html   # Parts catalog with AI
│   │   ├── registration.html    # User registration
│   │   ├── owner-login.html     # Owner login
│   │   ├── tuner-login.html     # Tuner login
│   │   ├── verify-email.html    # Email verification
│   │   ├── forgot-password.html # Password recovery
│   │   └── recover-password.html # Password reset
│   └── js/
│       ├── api-client.js   # Backend API client
│       ├── main.js         # Main application controller
│       └── vehicle-manager.js  # Vehicle state management
│   └── css/
│       └── style.css       # Main stylesheet
├── package.json
└── README.md
```

## Features

- Real-time OBD-II data simulation (RPM, speed, coolant temp, horsepower, torque)
- Dyno tuning interface with live charts
- AI-powered parts recommendations
- Vehicle performance predictions
- Chat assistant for tuning advice
- User authentication with email verification

## Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the Flask server:
```bash
python run.py
# or
flask run --host=0.0.0.0 --port=5000
```

3. Open `http://localhost:5000` in your browser

## API Endpoints

- `GET /api/vehicles` - List all vehicles
- `GET /api/vehicles/<id>` - Get specific vehicle
- `GET /api/obd-data/<vehicle_id>` - Get simulated OBD data
- `GET /api/parts` - List performance parts with filters
- `GET /api/dyno-curve/<vehicle_id>` - Get dyno curve data
- `POST /api/recommendations` - Get AI tuning recommendations
- `POST /api/tune` - Generate ECU tune
- `POST /api/chat` - Chat with AI assistant
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/verify-email?token=xxx` - Email verification