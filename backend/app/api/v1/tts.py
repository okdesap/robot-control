"""
TTS API - Offline mit Pico (pico2wave)
"""
import subprocess
import os
import tempfile

def pico_tts(text: str, lang: str = "de-DE"):
    # Temporäre WAV-Datei
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        # pico2wave: Text -> WAV-Datei
        subprocess.run(
            [
                "pico2wave",
                "-l", lang,
                "-w", wav_path,
                text,
            ],
            check=True
        )

        # Abspielen mit aplay (aus dem Paket alsa-utils) oder sox/play
        subprocess.run(["aplay", wav_path], check=True)
        # Alternativ, falls du sox/play nutzt:
        # subprocess.run(["play", wav_path], check=True)

    finally:
        # Datei wieder löschen
        if os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    test_text = "Hallo, das ist ein Test mit Pico T T S."
    pico_tts(test_text)

