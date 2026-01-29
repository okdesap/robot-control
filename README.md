# Robot Control System

Backend zur Steuerung von ROS2-Robotern über eine Web-API.

## Start (Windows PowerShell)

```powershell
cd backend
$env:ROBOT_BACKEND="sim"   # sim = turtlesim, real = turtlebot
python app/main.py
```

## Start (Linux/WSL)

```bash
cd backend
export ROBOT_BACKEND=sim    # sim = turtlesim, real = turtlebot
python app/main.py
```

## UI starten (Quasar)

Im Ordner web-ui/quasar-project:
```bash
cd web-ui/quasar-project
npm install
npm run dev
```

Danach im Browser öffnen: http://localhost:9000

## Backend + UI zusammen (kurz)

Terminal A (Backend):
```bash
cd backend
export ROBOT_BACKEND=sim
python app/main.py
```

Terminal B (UI):
```bash
cd web-ui/quasar-project
npm install
npm run dev
```

Dann im Browser öffnen: http://localhost:9000

## API

- `POST /api/v1/control/command` Body: `{"command":"forward 2.0"}`
- `POST /api/v1/control/stop`
- `GET /api/v1/control/health`

Swagger UI: http://localhost:8000/docs

## Turtlesim testen (ROS2 muss laufen)

1) ROS2 turtlesim starten:
```bash
ros2 run turtlesim turtlesim_node
```

2) Backend starten (sim):
```bash
cd backend
export ROBOT_BACKEND=sim
python app/main.py
```

3) Kommando senden:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 2.0"}'
```

Mehrere Kommandos schnell hintereinander (Queue):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 2"}'

curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"left 1"}'

curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 1"}'
```

## TurtleBot testen (Robot muss laufen)

1) TurtleBot ist online und hört auf `/cmd_vel`.

2) Backend starten (real):
```bash
cd backend
export ROBOT_BACKEND=real
python app/main.py
```

3) Kommando senden:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 1.0"}'
```

```bash
curl -s http://127.0.0.1:8000/api/v1/control/health
```