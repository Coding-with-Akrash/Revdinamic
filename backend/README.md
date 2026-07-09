# RevDynamics Backend

Flask-based Python backend for OBD-II vehicle diagnostics and tuning.

## Structure

```
models/
  - vehicle.py      # Vehicle database and specifications
  - part.py         # Performance parts catalog
routes/
  - auth_routes.py  # User registration, login, email verification
  - api_routes.py   # Vehicle, parts, OBD, and chat endpoints
services/
  - obd_service.py        # OBD-II data simulation
  - recommendation_service.py  # AI-powered tuning recommendations
app.py              # Application factory
run.py              # Development server runner
```

## Requirements

- Python 3.8+
- Flask 3.0+
- flask-cors

## Running

```bash
python run.py
```

Server runs at http://localhost:5000