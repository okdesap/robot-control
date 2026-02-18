# Robot Control Backend (ROS2 Jazzy, TurtleBot 4)

Dieses Repository enthält das **Backend** für die Steuerung eines ROS2-Roboters (insbesondere **TurtleBot 4**, ROS2 **Jazzy**) oder einer Simulation (Turtlesim). Das Backend stellt eine REST-API (FastAPI) bereit und kann zusätzlich Sprach-Text-Kommandos (STT→Text) in Steuerbefehle übersetzen.

## Wichtig: Web-UI wird separat benötigt

Für die Bedienung im Browser braucht ihr zusätzlich die Web-UI (Quasar):

- UI-Repository: https://projectbase.medien.hs-duesseldorf.de/dsai/tftb/take-control/web-ui

Das Backend läuft standardmäßig auf `http://127.0.0.1:8000`.

## Features (Backend)

- Robot Control via API: vor/zurück/links/rechts/stop, optional Dock/Undock und Navigation
- Kamera-Foto (Base64 Data-URL)
- Batteriestatus / Telemetrie / Status
- State-Stream per Server-Sent Events (SSE) für UI-Updates
- STT-Text Endpoint: `POST /api/v1/stt/execute` (Text → Intent → Ausführung + TTS-Reply)

## Voraussetzungen

### Für echten Roboter / Turtlesim (empfohlen: Linux / WSL2)

- **ROS2 Jazzy** installiert und gesourct
- **Python 3.12** + `pip`

### Für reine API-/UI-Entwicklung (ohne ROS2)

- Python 3.12

Hinweis: Das Backend kann ohne ROS2 starten, aber Robot-Funktionen sind dann nicht verfügbar (Commands schlagen zur Laufzeit fehl).

### Optional (Audio)

- TTS: mindestens eine Engine verfügbar: `pico2wave` + `paplay/aplay` **oder** `spd-say` **oder** `espeak/espeak-ng`
- STT Live-Demo (CLI): `arecord` + Vosk Modell

## Quickstart

### 1) Backend installieren

Aus dem Repo-Root:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

**Linux/WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2) Backend konfigurieren

Das Backend lädt beim Start automatisch eine `.env`, wenn vorhanden.

```bash
cp backend/.env.example backend/.env
```

Wichtige Variable:

- `ROBOT_BACKEND=sim` (Turtlesim) oder `ROBOT_BACKEND=real` (Robot)

### 3) Backend starten

```bash
python backend/app/main.py
```

API Docs (Swagger): `http://127.0.0.1:8000/docs`

## Vollständiges System (inkl. Audio + AI Function Calling)

Für TurtleBot 4 + ROS2 Jazzy ist ein Linux-Setup (oder WSL2) am zuverlässigsten, insbesondere für Audio (`arecord`, `paplay`) und ROS2.

### Audio installieren (TTS + optional STT)

**Ubuntu/Debian (typisch für ROS2 Jazzy):**

```bash
sudo apt update

# Audio Aufnahme (STT Live)
sudo apt install -y alsa-utils

# Audio Ausgabe (TTS Playback)
sudo apt install -y pulseaudio-utils

# TTS Engines (mindestens eine davon reicht)
sudo apt install -y libttspico-utils speech-dispatcher espeak-ng
```

**TTS testen** (Backend muss laufen):

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/tts/say \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hallo, Testausgabe.","lang":"de-DE"}'
```

TTS-Konfiguration (optional):

- `TTS_ENGINE=auto` (oder `pico2wave`, `spd-say`, `espeak`)
- `TTS_PLAYER=paplay` (oder `aplay`)
- `TTS_ENABLED=0` (deaktiviert TTS)

### STT Live (Vosk) – optional

Das Backend enthält zusätzlich eine Live-STT-Demo (Vosk + `arecord`). Dafür braucht ihr ein Vosk-Modell.

- Modellpfad setzen: `STT_MODEL_PATH=/pfad/zum/vosk-modell`
- Mikrofon wählen: `STT_DEVICE` (Wert aus `arecord -L`)

Geräte anzeigen:

```bash
arecord -L
arecord -l
```

STT Live starten/stoppen über API:

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/stt/live/start -H 'Content-Type: application/json' -d '{}'
curl -sS http://127.0.0.1:8000/api/v1/stt/live/status
curl -sS -X POST http://127.0.0.1:8000/api/v1/stt/live/stop -H 'Content-Type: application/json' -d '{}'
```

### AI Function Calling (Ollama)

Das Backend kann statt regelbasierter Intent-Erkennung ein LLM via **Ollama** nutzen.

1) **Ollama installieren** und den Dienst starten (Ollama muss lokal erreichbar sein).
2) Modell laden (Default ist `llama3:8b`):

```bash
ollama pull llama3:8b
```

3) In `backend/.env` aktivieren:

```dotenv
INTENT_MODE=function_calling

# optional:
OLLAMA_MODEL=llama3:8b
# OLLAMA_HOST=http://127.0.0.1:11434
```

4) Test über STT-Endpoint (Text → LLM → Intent → Ausführung):

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/stt/execute \
  -H 'Content-Type: application/json' \
  -d '{"text":"fahre 2 sekunden vorwärts und dann stop"}'
```

Hinweis: Wenn das LLM keine gültige JSON-Antwort liefert oder Ollama nicht erreichbar ist, fällt das Backend automatisch auf die regelbasierte Erkennung zurück.

## UI starten

Siehe UI-Repo: https://projectbase.medien.hs-duesseldorf.de/dsai/tftb/take-control/web-ui

Wichtig: Die UI erwartet standardmäßig das Backend unter `http://127.0.0.1:8000`.

## Betrieb: Simulation (Turtlesim)

1) In einer ROS2-Shell:

```bash
ros2 run turtlesim turtlesim_node
```

2) Backend mit `ROBOT_BACKEND=sim` starten (z.B. über `backend/.env`).

## Betrieb: echter Roboter (TurtleBot 4)

- ROS2 Jazzy sourcen (und ggf. eigenes Workspace-Setup)

```bash
source /opt/ros/jazzy/setup.bash
# optional, falls ihr ein eigenes ROS2-Workspace habt:
# source ~/ros2_ws/install/setup.bash
```

- `ROBOT_BACKEND=real`

Hinweis: In diesem Repo wird das Backend direkt über `python backend/app/main.py` gestartet. Falls ihr ein eigenes Start-Script für ROS2-Sourcing + venv braucht, erstellt es passend zu eurer Umgebung (die Pfade sind je Setup unterschiedlich).

## API Kurzüberblick

- `GET /api/v1/control/health`
- `POST /api/v1/control/command` – Body: `{ "command": "forward 1.0 0.5" }`
- `POST /api/v1/control/stop`
- `GET /api/v1/control/photo`
- `GET /api/v1/control/battery`
- `GET /api/v1/control/dock_status`
- `GET /api/v1/state/snapshot`
- `GET /api/v1/state/stream` (SSE)
- `POST /api/v1/stt/execute` – Body: `{ "text": "fahre vorwärts" }`
- `POST /api/v1/tts/say` – Body: `{ "text": "Hallo", "lang": "de-DE" }`

Die komplette API ist in Swagger dokumentiert: `http://127.0.0.1:8000/docs`.

## STT (Text → Intent → Ausführung)

Das Backend nimmt Text entgegen und leitet daraus einen Intent ab.

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/stt/execute \
  -H 'Content-Type: application/json' \
  -d '{"text":"fahre vorwärts"}'
```

Optionales Tuning für STT-Default-Geschwindigkeiten (passt zu UI-Slidern):

- `STT_DEFAULT_LINEAR` (Default `0.5`)
- `STT_DEFAULT_ANGULAR` (Default `0.5`)

## Troubleshooting

### Port 8000 belegt

Wenn `address already in use` kommt, läuft bereits ein Prozess auf Port 8000.

- Windows: `netstat -ano | findstr :8000`
- Linux: `ss -ltnp | grep ':8000'`

### Kein ROS2 / rclpy importierbar

Wenn ROS2 nicht gesourct ist oder auf dem System fehlt, kann das Backend zwar starten, aber der ausgewählte Robot-Backend-Treiber ist nicht verfügbar. Nutze in dem Fall `ROBOT_BACKEND=sim` (mit ROS2) oder starte nur für UI/API-Entwicklung.