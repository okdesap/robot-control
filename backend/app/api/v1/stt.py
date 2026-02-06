from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import os

from app.api.v1.intent_parser import parse_intent
from app.core.controller import controller
from app.core.tts_service import say_async


router = APIRouter()


class STTTextRequest(BaseModel):
    text: str


def _reply_for_intent(intent: str) -> str:
    parts = (intent or "").strip().split()
    action = parts[0] if parts else ""
    if action == "stop":
        return "Verstanden. Ich stoppe."
    if action == "forward":
        return "Verstanden. Ich fahre vorwärts."
    if action == "left":
        return "Verstanden. Ich drehe nach links."
    if action == "right":
        return "Verstanden. Ich drehe nach rechts."
    if action == "dock":
        return "Verstanden. Ich docke an."
    if action == "undock":
        return "Verstanden. Ich docke ab."
    if action in {"nav", "goto", "pose", "navigate"}:
        return "Verstanden. Ich navigiere zum Ziel."
    return f"Verstanden. Ich führe '{action}' aus."


@router.post("/parse")
def parse_stt_text(body: STTTextRequest):
    intent = parse_intent(body.text)
    if not intent:
        raise HTTPException(status_code=400, detail="No intent derived from text")
    return {"status": "ok", "intent": intent}


@router.post("/execute")
def execute_stt_text(body: STTTextRequest):
    intent = parse_intent(body.text)
    if not intent:
        raise HTTPException(status_code=400, detail="No intent derived from text")

    command_id = controller.enqueue_command(intent)
    reply = _reply_for_intent(intent)
    say_async(reply)
    return {"status": "accepted", "intent": intent, "command_id": command_id, "reply": reply}


# Optional: keep the CLI streaming demo for local testing without affecting FastAPI startup.
def _run_live_stream(device: str = "hw:3,0", sample_rate: int = 16000) -> None:
    import json
    import subprocess
    import vosk
    import requests

    model_path = os.getenv("STT_MODEL_PATH", "/home/ros/ros/projects/takecontrol/LM/vosk-model-de-0.21")
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, sample_rate)

    print(f"Live-Stream ({device}, {sample_rate}Hz Mono)...")
    proc = subprocess.Popen(
        [
            "arecord",
            "-D",
            device,
            "-r",
            str(sample_rate),
            "-c",
            "1",
            "-f",
            "S16_LE",
            "-t",
            "wav",
        ],
        stdout=subprocess.PIPE,
        bufsize=0,
    )

    try:
        while True:
            data = proc.stdout.read(16000)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"\nText: '{text}'")
                intent = parse_intent(text)
                print(f"Intent erkannt: {intent}")
                if intent:
                    try:
                        mode = (os.getenv("STT_EXECUTE_MODE", "http") or "http").strip().lower()
                        if mode == "local":
                            controller.enqueue_command(intent)
                            reply = _reply_for_intent(intent)
                            print(f"Reply: {reply}")
                            say_async(reply)
                        else:
                            base = (os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000") or "http://127.0.0.1:8000").rstrip("/")
                            res = requests.post(f"{base}/api/v1/stt/execute", json={"text": text}, timeout=5)
                            print(f"Backend: {res.status_code} {res.text}")
                    except Exception as exc:
                        print(f"Execute failed: {exc}")
            else:
                partial = json.loads(recognizer.PartialResult())
                print(f"\rTeil: {partial.get('partial', '')}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBeendet!")
    finally:
        proc.terminate()


if __name__ == "__main__":
    _run_live_stream()