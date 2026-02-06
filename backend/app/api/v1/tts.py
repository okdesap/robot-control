"""Offline TTS (pico2wave) exposed as API."""
import os
import subprocess
import tempfile

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    lang: str = "de-DE"


def pico_tts(text: str, lang: str = "de-DE") -> None:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        subprocess.run(["pico2wave", "-l", lang, "-w", wav_path, text], check=True)
        subprocess.run(["paplay", wav_path], check=True)
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


@router.post("/say")
def say(body: TTSRequest):
    try:
        pico_tts(body.text, body.lang)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=f"pico2wave or paplay not available: {exc}")
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail=f"TTS command failed: {exc}")
    return {"status": "ok"}


if __name__ == "__main__":
    pico_tts("Hallo, das ist ein Test mit Pico TTS auf deinem Computer.", "de-DE")

