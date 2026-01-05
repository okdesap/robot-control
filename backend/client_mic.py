"""
client_mic.py
----------------
Live-Client für den Raspberry Pi / Team (DEMO).
Benötigt: pip install sounddevice websockets
"""
import asyncio
import websockets
# ist noch nicht in requirements, von daher noch unbekannt
import sounddevice as sd
import sys

# Adresse des Backends
SERVER_URL = "ws://localhost:8000/api/v1/stt/ws/audio"

async def run_mic_client():
    print(f"Verbinde zu {SERVER_URL} ...")
    
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("✅ Verbunden! Mikrofon ist aktiv.")
            print("Sprich Befehle (Vorne, Links, Stop...)")
            print("❌ Beenden mit STRG+C")

            loop = asyncio.get_running_loop()
            input_queue = asyncio.Queue()

            def callback(indata, frames, time, status):
                if status:
                    print(f"Status: {status}", file=sys.stderr)
                loop.call_soon_threadsafe(input_queue.put_nowait, bytes(indata))

            # 16kHz Mono Aufnahme <- Voraussetzung Vosk
            with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                                   channels=1, callback=callback):
                while True:
                    data = await input_queue.get()
                    await websocket.send(data)
                    
                    # Kurz auf Antwort lauschen (non-blocking)
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                        print(f"Feedback: {response}")
                    except asyncio.TimeoutError:
                        pass

    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    try:
        # "Event Loop" (Manager) erstellen, damit die async Funktion läuft
        asyncio.run(run_mic_client())
    # damit es "sauber" aussieht wenn ein Programm beendet wird (Fehlermeldung abfangen uns stattdessen eine Ausgabe)
    except KeyboardInterrupt:
        print("\n Client beendet.")