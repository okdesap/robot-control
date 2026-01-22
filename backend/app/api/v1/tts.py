"""
Offline TTS mit pico2wave - fester String
"""
import subprocess
import os
import tempfile

def pico_tts(text: str, lang: str = "de-DE"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        # pico2wave erzeugt WAV
        subprocess.run([
            "pico2wave", "-l", lang, "-w", wav_path, text
        ], check=True)

        # aplay spielt ab (Default-Speaker)
        subprocess.run(["aplay", wav_path], check=True)
        
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    # DEIN FESTER STRING HIER
    mein_text = "Hallo, das ist ein Test mit Pico TTS auf deinem Computer."
    pico_tts(mein_text, "de-DE")

