# Robot Control System

Backend zur Steuerung von ROS2-Robotern über eine Web-API.

## Start (Windows PowerShell)

```powershell
cd backend
$env:ROBOT_BACKEND="sim"   # sim = turtlesim, real = turtlebot
python app/main.py
```

Hinweis (TurtleBot cmd_vel):
- Standard ist `CMD_VEL_TOPIC=/cmd_vel` und `CMD_VEL_MSG_TYPE=Twist`.
- Falls dein Robot auf `TwistStamped` hört, setze zusätzlich:
```powershell
$env:CMD_VEL_MSG_TYPE="TwistStamped"
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

Windows PowerShell (empfohlen):
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/control/command" `
  -ContentType "application/json" `
  -Body '{"command":"forward 2.0"}'
```

Linux/WSL/macOS:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 2.0"}'
```

Mehrere Kommandos schnell hintereinander (Queue):

Windows PowerShell (Beispiel):
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/control/command" -ContentType "application/json" -Body '{"command":"forward 2"}'
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/control/command" -ContentType "application/json" -Body '{"command":"left 1"}'
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/control/command" -ContentType "application/json" -Body '{"command":"forward 1"}'
```

Linux/WSL/macOS:
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

Debug (auf dem Robot/ROS Rechner):
```bash
ros2 topic info /cmd_vel
ros2 topic list | grep cmd_vel
```
Wenn `ros2 topic info /cmd_vel` als Typ **TwistStamped** zeigt, starte das Backend mit:
```powershell
$env:ROBOT_BACKEND="real"
$env:CMD_VEL_MSG_TYPE="TwistStamped"
python app/main.py
```

2) Backend starten (real):
```bash
cd backend
export ROBOT_BACKEND=real
python app/main.py
```

3) Kommando senden:

Windows PowerShell (empfohlen):
```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/control/command" `
  -ContentType "application/json" `
  -Body '{"command":"forward 1.0"}'
```

Linux/WSL/macOS:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/control/command \
	-H "Content-Type: application/json" \
	-d '{"command":"forward 1.0"}'
```

```bash
curl -s http://127.0.0.1:8000/api/v1/control/health
```