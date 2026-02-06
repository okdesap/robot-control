from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import os
import sys

# Allow running this module as a script: `python stt.py`
# by ensuring the backend root (folder containing `app/`) is on sys.path.
if __package__ is None or __package__ == "":
    current_dir = os.path.dirname(__file__)
    backend_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

from app.api.v1.intent_parser import parse_intent


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
    # Local imports to avoid side effects when running this module as a CLI tool.
    from app.core.controller import controller
    from app.core.tts_service import say_async

    intent = parse_intent(body.text)
    if not intent:
        raise HTTPException(status_code=400, detail="No intent derived from text")

    command_id = controller.enqueue_command(intent)
    reply = _reply_for_intent(intent)
    say_async(reply)
    return {"status": "accepted", "intent": intent, "command_id": command_id, "reply": reply}


# Optional: keep the CLI streaming demo for local testing without affecting FastAPI startup.
def _run_live_stream(device: str = "hw:3", sample_rate: int = 16000) -> None:
    import json
    import subprocess
    import time
    import vosk
    import requests

    model_path = os.getenv("STT_MODEL_PATH", "/home/ros/ros/projects/takecontrol/LM/vosk-model-de-0.21")
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, sample_rate)

    base = (os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000") or "http://127.0.0.1:8000").rstrip("/")
    endpoint = os.getenv("STT_HTTP_ENDPOINT", f"{base}/api/v1/stt/execute") or f"{base}/api/v1/stt/execute"

    # PipeWire/WirePlumber often keeps the *hw* device open.
    # Using ALSA 'default' (which routes through PipeWire) avoids "device busy".
    env_device = (os.getenv("STT_DEVICE") or "").strip()
    alsa_card = (os.getenv("STT_ALSA_CARD", "ArrayUAC10") or "ArrayUAC10").strip()
    candidates: list[str]
    if env_device:
        candidates = [env_device]
    else:
        candidates = [
            f"default:CARD={alsa_card}",
            f"sysdefault:CARD={alsa_card}",
            f"dsnoop:CARD={alsa_card},DEV=0",
            "default",
            # last resort: raw hardware (can be busy)
            f"plughw:CARD={alsa_card},DEV=0",
            f"hw:CARD={alsa_card},DEV=0",
        ]

    proc = None
    chosen = None
    last_err = ""
    for dev in candidates:
        print(f"Trying capture device: {dev}")
        p = subprocess.Popen(
            [
                "arecord",
                "-D",
                dev,
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
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        # Give arecord a moment; if it fails immediately, try next device.
        time.sleep(0.25)
        if p.poll() is not None:
            try:
                err = (p.stderr.read().decode("utf-8", errors="replace") if p.stderr else "").strip()
            except Exception:
                err = ""
            last_err = err or f"arecord exited with code {p.returncode}"
            print(f"Device failed: {dev} -> {last_err}")
            continue

        proc = p
        chosen = dev
        break

    if proc is None or chosen is None:
        raise RuntimeError(
            "Could not open any audio capture device. "
            "Set STT_DEVICE to a working value from `arecord -L`. "
            f"Last error: {last_err}"
        )

    print(f"Live-Stream ({chosen}, {sample_rate}Hz Mono) -> POST {endpoint}")

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
                if text:
                    try:
                        # Send raw recognized text to the backend; backend derives intent + executes.
                        res = requests.post(endpoint, json={"text": text}, timeout=5)
                        print(f"Backend: {res.status_code} {res.text}")
                    except Exception as exc:
                        print(f"HTTP failed: {exc}")
            else:
                partial = json.loads(recognizer.PartialResult())
                print(f"\rTeil: {partial.get('partial', '')}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBeendet!")
    finally:
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    _run_live_stream()