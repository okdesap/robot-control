import json
import subprocess
import vosk

MODEL_PATH = "/home/ros/ros/projects/takecontrol/LM/vosk-model-de-0.21"

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 48000)  # Deine Hardware-Rate

print("Live-Stream (hw:2,0, 48kHz Stereo)...")

proc = subprocess.Popen([
    "arecord", "-D", "hw:2,0", 
    "-r", "41100", "-c", "2", "-f", "S16_LE", "-t", "raw"
], stdout=subprocess.PIPE, bufsize=0)

try:
    while True:
        data = proc.stdout.read(16000)  # 48000*2channels*2bytes=192kB/s, 16kB Chunks
        if len(data) == 0: break
        
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get('text', '').strip()
            if text: print(f"\n✅ '{text}'")
        else:
            partial = json.loads(rec.PartialResult())
            print(f"\r⏳ {partial.get('partial', '')}", end='', flush=True)
except KeyboardInterrupt:
    print("\nBeendet!")
proc.terminate()