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

## Start (Linux – TurtleBot Real, empfohlen)

Nutze das Script, damit ROS2‑Umgebung + venv automatisch geladen werden:

```bash
./backend/run_backend.sh
```

Wichtige Umgebungsvariablen (optional):

```bash
# Command Velocity Typ (TurtleBot4 nutzt i.d.R. TwistStamped)
export CMD_VEL_MSG_TYPE=TwistStamped

# Kamera-Topics (Standard + OAKD Preview)
export CAMERA_TOPIC=/camera/image_raw
export OAKD_CAMERA_TOPIC=/oakd/rgb/preview/image_raw

# Docking ohne Nav2 erzwingen (Standard: aus)
export DOCK_REQUIRE_NAV2=0
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
./backend/run_backend.sh
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

## Docking / Undocking (TurtleBot)

Docking nutzt Action‑Server `/dock` und `/undock`.
Status prüfen:

```bash
curl -s http://127.0.0.1:8000/api/v1/control/dock_status
```

Wenn `available=true`, können die UI‑Buttons „Dock“/„Undock“ verwendet werden.

Hinweis: Nav2 ist **nicht** zwingend erforderlich (DOCK_REQUIRE_NAV2=0). Falls du Nav2 erzwingen möchtest, setze:

```bash
export DOCK_REQUIRE_NAV2=1
```

## Kamera / Foto

Die Foto‑Funktion nutzt ROS2‑Images. Standard‑Topics:

```bash
/camera/image_raw
/oakd/rgb/preview/image_raw
```

Falls dein Robot andere Topics verwendet, setze:

```bash
export CAMERA_TOPIC=/dein/camera/topic
export OAKD_CAMERA_TOPIC=/dein/oakd/topic
```

Nach „FOTO MACHEN“ wird ein PNG als base64 geliefert und direkt in der UI angezeigt.