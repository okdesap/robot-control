"""
STT API - Placeholder
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from vosk import Model, KaldiRecognizer
import json
import os

from app.core.controller import controller

router = APIRouter()

# Pfad zum Modell
MODEL_PATH = "vosk-model-small-de-0.15"
model = None

# Modell sicher laden
if os.path.exists(MODEL_PATH):
    print(f"---> STT: Lade Vosk Modell aus {MODEL_PATH} ...")
    try: 
        model = Model(MODEL_PATH)
    except Exception as e:
        print(f"STT: Fehler beim Laden des Modells: {e}")
else:
    print(f"STT: Modell-Ordner nicht gefunden! Bitte {MODEL_PATH} in backend/ kopieren.")


# Hilfsfunktion: Text auswerten und Roboter steuern
def process_command(text: str):
    if not text:
        return
    
    print(f"Erkannt: '{text}'")
    cmd = text.lower()

    if "vorne" in cmd or "vorwärts" in cmd:
        print("🤖 Sende: forward 2.0")
        controller.execute_command("forward 2.0")

    elif "zurück" in cmd or "rückwärts" in cmd:
        print("🤖 Sende: forward -2.0")
        controller.execute_command("forward -2.0")

    elif "links" in cmd:
        print("🤖 Sende: left 1.5")
        controller.execute_command("left 1.5")

    elif "rechts" in cmd:
        print("🤖 Sende: right 1.5")
        controller.execute_command("right 1.5")

    elif "stop" in cmd or "halt" in cmd:
        print("🤖 Sende: stop")
        controller.execute_command("stop")


@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    if not model:
        await websocket.close(reason="Serverfehler: Kein Modell")
        return
    
    # Recognizer erstellen
    rec = KaldiRecognizer(model, 16000)

    try:
        while True:
            data = await websocket.receive_bytes()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '')
                process_command(text)

                # Feedback zurück an Client
                await websocket.send_json({"text": text})
    except WebSocketDisconnect:
        print("---> STT: Verbindung getrennt - Prüfe auf letzte Worte...")
        final_result = json.loads(rec.FinalResult())
        final_text = final_result.get('text', '')

        process_command(final_text)
        
    except Exception as e:
        print(f"STT Fehler: {e}")