# Robot Control System

Ein modulares Backend zur Steuerung von ROS2-Robotern über eine Web-API.

## Was machen wir hier?

Wir bauen ein **Backend**, das:
- Befehle von einem Web-Frontend empfängt
- Diese Befehle an ROS2-Roboter weiterleitet
- Zwischen verschiedenen Robotern wechseln kann (Turtlesim, TurtleBot4)

## Projekt-Struktur

```
robot-control/
└── backend/
    ├── app/
    │   ├── main.py              # FastAPI Server (Einstiegspunkt)
    │   │
    │   ├── api/v1/              # REST Endpoints
    │   │   ├── control.py       # POST /control/command
    │   │   ├── stt.py           # Speech-to-Text (später)
    │   │   └── tts.py           # Text-to-Speech (später)
    │   │
    │   ├── core/                # Business Logik
    │   │   ├── commands.py      # "forward 2.0" → move_forward(2.0)
    │   │   ├── config.py        # Backend-Auswahl (sim/real)
    │   │   └── controller.py    # Haupt-Controller (KEIN ROS!)
    │   │
    │   └── ros/                 # ROS2 Layer
    │       ├── robot_interface.py    # Abstract Interface
    │       ├── turtlesim_robot.py    # Turtlesim Backend
    │       └── turtlebot_robot.py    # TurtleBot Backend
    │
    ├── test_backend.py          # Einfacher Test
    ├── requirements.txt         # Python Dependencies
    └── .env                     # Konfiguration
```

## Architektur-Konzept

### **4 Schichten:**

```
Web Frontend (Quasar)
        ↓
    FastAPI
        ↓
   Controller  ← Kennt KEIN ROS!
        ↓
Robot Interface  ← Hier beginnt ROS
        ↓
   Turtlesim / TurtleBot
```

### **Wichtige Regeln:**

1. **RobotInterface** definiert alle Roboter-Funktionen:
   ```python
   move_forward(duration)
   turn_left(duration)
   turn_right(duration)
   stop()
   ```

2. **Controller** arbeitet nur mit dem Interface - nie direkt mit ROS:
   ```python
   self.robot.move_forward(2.0)  # Gut
   # Niemals: rclpy.publish(...)  # Schlecht
   ```

3. **Backend wechseln** ohne Code-Änderung:
   ```bash
   ROBOT_BACKEND=sim    # Turtlesim
   ROBOT_BACKEND=real   # TurtleBot
   ```

4. **Befehle als Text**:
   ```
   "forward 2.0"   → Roboter fährt 2 Sekunden vorwärts (Dauer in Sekunden)
   "left 1.5"      → Roboter dreht 1,5 Sekunden links
   "stop"          → Roboter stoppt
   ```

## Schnellstart

Es gibt zwei sinnvolle Startarten:
1) **API testen (ohne ROS2)**: du bekommst HTTP-Antworten und kannst die Web-Pipeline prüfen.
2) **End-to-End mit turtlesim (mit ROS2)**: du siehst echte Bewegung in der Simulation.

## API (was das Frontend aufruft)

- `POST /api/v1/control/command` → nimmt Textbefehle wie `"forward 2.0"`, `"left 1.5"`, `"right 1.0"`, `"stop"`
- `POST /api/v1/control/stop` → stoppt sofort
- `GET /api/v1/control/health` → zeigt, welches Backend aktiv ist (z.B. `TurtlesimRobot`)
- `GET /api/v1/control/photo` → aktuell nur Platzhalter-Bild (Base64 Data-URL)

Swagger UI zum Testen: http://localhost:8000/docs

## Ausführen & Testen

### 1) Nur API testen (ohne ROS2)

In WSL (oder jeder Python-Umgebung) im Ordner `backend/`:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

export ROBOT_BACKEND=sim
python -m app.main
```

Test (zweites Terminal):
```bash
curl -sS http://127.0.0.1:8000/api/v1/control/health
curl -sS -X POST http://127.0.0.1:8000/api/v1/control/command \
   -H "Content-Type: application/json" \
   -d '{"command":"forward 2.0"}'
```

### 2) Pipeline End-to-End testen (WSL + ROS2 Jazzy, 3 Terminals)

Ziel: **HTTP Request → FastAPI → Controller → ROS2 Publisher → turtlesim bewegt sich**

**Einmalige Vorbereitung (WSL, falls noch nicht da)**
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip curl
```

**Terminal A (WSL): turtlesim starten**
```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

**Terminal B (WSL): Backend starten (mit ROS2 Python sichtbar!)**
```bash
cd /mnt/c/Users/Administratorr/Desktop/robot-control/backend
source /opt/ros/jazzy/setup.bash

# venv muss ROS2 Python Pakete sehen:
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -r requirements.txt

export ROBOT_BACKEND=sim
python -m app.main
```

**Terminal C (WSL): Commands schicken**
```bash
curl -sS http://127.0.0.1:8000/api/v1/control/health

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/command \
   -H "Content-Type: application/json" \
   -d '{"command":"forward 2.0"}'

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/command \
   -H "Content-Type: application/json" \
   -d '{"command":"left 1.5"}'

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/stop
```

**Quick Debug (wenn sich nichts bewegt)**
- Prüfen, ob überhaupt Nachrichten ankommen:
   ```bash
   source /opt/ros/jazzy/setup.bash
   ros2 topic echo /turtle1/cmd_vel
   ```
- Wenn `address already in use`: es läuft schon ein Server → alten Uvicorn stoppen oder Port ändern (`--port 8001`).
- Wenn `No module named 'numpy'`: im aktivierten `.venv` `python -m pip install -r requirements.txt` ausführen.

### 3) End-to-End mit TurtleBot testen (Linux Rechner mit Verbindung zum Roboter)

Ziel: **HTTP Request → FastAPI → Controller → ROS2 Publisher → TurtleBot bewegt sich**

**Voraussetzungen**
- Auf dem Linux-Rechner ist ROS2 installiert und kann den TurtleBot erreichen (gleiche ROS2 Domain / gleiches Netzwerk).
- Der TurtleBot läuft bereits (Bringup/Navigation ist an) und hört auf `/cmd_vel`.

**A) TurtleBot-Seite kurz prüfen (auf dem Linux-Rechner)**
```bash
# ROS2 Umgebung laden (Pfad je nach Distro anpassen)
source /opt/ros/jazzy/setup.bash

ros2 topic list | grep -E "^/cmd_vel$" || true
ros2 topic info /cmd_vel || true
```

**B) Repo auschecken & Backend starten**
```bash
git clone <REPO-URL>
cd robot-control/backend

source /opt/ros/jazzy/setup.bash

# venv muss ROS2 Python Pakete sehen (rclpy, geometry_msgs)
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

python -m pip install -U pip
python -m pip install -r requirements.txt

export ROBOT_BACKEND=real

python -m app.main
```

**C) Test-Requests schicken (vom selben Linux-Rechner oder einem anderen im Netz)**
```bash
curl -sS http://127.0.0.1:8000/api/v1/control/health

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/command \
   -H "Content-Type: application/json" \
   -d '{"command":"forward 1.0"}'

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/command \
   -H "Content-Type: application/json" \
   -d '{"command":"left 0.8"}'

curl -sS -X POST http://127.0.0.1:8000/api/v1/control/stop
```

**D) Quick Debug (wenn sich nichts bewegt)**
- Prüfen, ob das Backend überhaupt auf `/cmd_vel` published:
   ```bash
   source /opt/ros/jazzy/setup.bash
   ros2 topic echo /cmd_vel
   ```
- Wenn `ROS2NotAvailableError` / `import rclpy` schlägt fehl:
   - Prüfen, ob du wirklich `source /opt/ros/<distro>/setup.bash` gemacht hast.
   - venv muss mit `--system-site-packages` erstellt sein.
- Wenn Topics nicht ankommen (DDS/Netz):
   ```bash
   echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
   echo "ROS_LOCALHOST_ONLY=$ROS_LOCALHOST_ONLY"
   ```
   `ROS_DOMAIN_ID` muss zur Roboter-Seite passen; `ROS_LOCALHOST_ONLY` sollte i.d.R. `0` sein.

## Nächste Schritte

1. TurtleBot Backend entwickeln (`ROBOT_BACKEND=real`)
2. Distanz-Kommandos ergänzen (z.B. `forward 2m` statt Sekunden)
3. STT/TTS Features hinzufügen
4. Frontend (Quasar) anbinden

## Warum so modular?

**Problem:** Wenn wir später von Turtlesim auf TurtleBot wechseln wollen, müssen wir nicht das ganze Backend umschreiben.

**Lösung:** Einfach `.env` ändern:
```bash
ROBOT_BACKEND=real  # Fertig!
```

Der Rest bleibt gleich.

## Aktueller Status

- ✅ Grundstruktur steht
- ✅ REST API (FastAPI) steht
- ✅ Command Parser + Controller (ohne ROS-Abhängigkeit)
- ✅ Turtlesim Anbindung (publisht auf `/turtle1/cmd_vel`)
- ✅ TurtleBot Backend ist verdrahtet (publisht auf `/cmd_vel`, muss am echten Bot verifiziert werden)
- ⏳ STT/TTS Features sind noch Platzhalter
- ⏳ Foto ist aktuell nur ein Dummy (Base64)