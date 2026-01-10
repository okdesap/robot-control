"""
TTS API - offline with Pico (pico2wave)
"""
import subprocess
import os
import tempfile

def pico_tts(text: str, lang: str = "de-DE"):
    # temporary WAV-file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        # pico2wave: text -> WAV-Datei
        subprocess.run(
            [
                "pico2wave",
                "-l", lang,
                "-w", wav_path,
                text,
            ],
            check=True
        )

        # play with aplay (from the alsa-utils package) or sox/play
        subprocess.run(["aplay", wav_path], check=True)
    

    finally:
        # delete temporary WAV-file
        if os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    test_text = "Hallo, das ist ein Test mit Pico T T S."
    pico_tts(test_text)

