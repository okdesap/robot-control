from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.v1.intent_parser import parse_intent
from app.core.controller import controller


router = APIRouter()


class STTTextRequest(BaseModel):
    text: str


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
    return {"status": "accepted", "intent": intent, "command_id": command_id}


# Optional: keep the CLI streaming demo for local testing without affecting FastAPI startup.
def _run_live_stream(device: str = "hw:3,0", sample_rate: int = 16000) -> None:
    import json
    import subprocess
    import vosk

    model_path = "/home/ros/ros/projects/takecontrol/LM/vosk-model-de-0.21"
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
            else:
                partial = json.loads(recognizer.PartialResult())
                print(f"\rTeil: {partial.get('partial', '')}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBeendet!")
    finally:
        proc.terminate()


if __name__ == "__main__":
    _run_live_stream()