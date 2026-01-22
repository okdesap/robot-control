def pico_tts(text: str, lang: str = "de-DE"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        subprocess.run([
            "pico2wave", "-l", lang, "-w", wav_path, text,
        ], check=True)

        subprocess.run(["aplay", wav_path], check=True)  # <- Einrückung

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


