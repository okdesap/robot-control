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
   ROBOT_BACKEND=bot   # TurtleBot
   ```

4. **Befehle als Text**:
   ```
   "forward 2.0"   → Roboter fährt 2 Sekunden vorwärts
   "left 1.5"      → Roboter dreht 1,5 Sekunden links
   "stop"          → Roboter stoppt
   ```

## Schnellstart

### 1. Einfacher Test (ohne ROS):
```bash
cd backend
python test_backend.py
```

### 2. Backend konfigurieren:
```bash
# .env Datei anpassen
ROBOT_BACKEND=sim
```

### 3. Dependencies installieren:
```bash
pip install -r requirements.txt
```

### 4. Server starten:
```bash
python -m app.main
```

### 5. API testen:
Öffne: http://localhost:8000/docs

## API Beispiele

### Roboter steuern:
```bash
POST http://localhost:8000/api/v1/control/command
{
  "command": "forward 2.0"
}
```

### Stop:
```bash
POST http://localhost:8000/api/v1/control/stop
```

## Aktueller Status

- ✅ Grundstruktur steht
- ✅ Command Parser funktioniert
- ✅ Controller-Logik implementiert
- ✅ Interface-System funktioniert
- ⏳ ROS2 Integration (TODOs in turtlesim_robot.py)
- ⏳ TurtleBot4 Backend
- ⏳ STT/TTS Features

## Nächste Schritte

1. ROS2 in `turtlesim_robot.py` implementieren
2. Backend mit echtem Turtlesim testen
3. TurtleBot4 Backend entwickeln
4. Frontend (Quasar) anbinden
5. Speech-Features hinzufügen

## Warum so modular?

**Problem:** Wenn wir später von Turtlesim auf TurtleBot wechseln wollen, müssen wir nicht das ganze Backend umschreiben.

**Lösung:** Einfach `.env` ändern:
```bash
ROBOT_BACKEND=bot  # Fertig!
```

Der Rest bleibt gleich.

## Test-Ergebnisse (06.12.2025)

### Test 1: Backend-Logik 
```bash
cd backend
python test_backend.py
```
**Ergebnis:** Erfolgreich
- Command Parser funktioniert (`"forward 2.0"` → `{'action': 'forward', 'duration': 2.0}`)
- Controller ruft korrekt Robot-Funktionen auf
- Backend-System (Turtlesim) gibt korrekte Ausgaben

### Test 2: FastAPI Server 
```bash
python -m app.main
```
**Ergebnis:** Erfolgreich
- Server startet auf `http://localhost:8000`
- API-Dokumentation verfügbar unter `http://localhost:8000/docs`
- POST `/api/v1/control/command` funktioniert
- POST `/api/v1/control/stop` funktioniert

Kurzer Hinweis!
- Swagger also die Ui die sich öffnet. 
- Ist eine Art Playground dort können wir die API's Endpoints testen
- dort wird angezeigt welche Parameter auch zum testen nötig sind
- zeigt auch Beispiele

Beispiel: 
1. POST /api/v1/control/command
2. "Try it out"
3. Gibst ein: {"command": "forward 2.0"}
4. "Execute"
5. Siehst sofort die Antwort!

### Was funktioniert JETZT schon:
- Vollständige Backend-Struktur  
- REST API (FastAPI)  
- Command-Parsing (`"forward 2.0"` → Roboter-Funktion)  
- Controller-Logik (ohne direkte ROS-Abhängigkeit)  
- Modulares Backend-System (Turtlesim/TurtleBot)  
- Swagger UI für API-Tests  

### Was noch fehlt:
- ROS2 Integration (nur Platzhalter-Code vorhanden)  
- Echte Turtle-Steuerung in Turtlesim  
- TurtleBot4 Implementierung  
- Speech-to-Text / Text-to-Speech  

**Stand:** Das Backend-Framework ist komplett einsatzbereit. Die ROS2-Anbindung kann jetzt Schritt für Schritt implementiert wer