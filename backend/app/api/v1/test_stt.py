import json
import subprocess
import vosk

# Path to the German language model directory. 
# This folder contains the neural network data for speech recognition.
MODEL_PATH = "/home/ros/ros/projects/takecontrol/LM/vosk-model-de-0.21"

# Initialize the Vosk model using the path defined above.
# This loads the heavy data into RAM.
model = vosk.Model(MODEL_PATH)

# Create a recognizer instance. 
# The second argument '48000' tells Vosk to expect audio data 
# at a sample rate of 48,000 Hz (48 kHz).
rec = vosk.KaldiRecognizer(model, 48000)  # Deine Hardware-Rate

print("Live-Stream (hw:2,0, 48kHz Stereo)...")

# Open a subprocess to run the Linux command-line tool 'arecord'.
# This captures audio directly from the hardware driver (ALSA).
# Arguments breakdown:
# "arecord": The Linux audio recorder tool.
# "-D", "hw:2,0": Selects the specific hardware device (Card 2, Device 0).
# "-r", "41100": Sets recording sample rate to 41,100 Hz. (WARNING: Mismatch with Vosk's 48000).
# "-c", "2": Records in Stereo (2 channels).
# "-f", "S16_LE": Format is Signed 16-bit Little Endian (standard for audio processing).
# "-t", "raw": Outputs raw data without a WAV header (important for streaming).
proc = subprocess.Popen([
    "arecord", "-D", "hw:2,0", 
    "-r", "41100", "-c", "2", "-f", "S16_LE", "-t", "raw"
], stdout=subprocess.PIPE, bufsize=0) # Pipe the audio output directly to Python, no buffering.

try:
    # Start an infinite loop to process audio in real-time.
    while True:
        # Read a chunk of raw bytes from the 'arecord' process output.
        # 16000 bytes are read in each iteration.
        data = proc.stdout.read(16000)  # 48000*2channels*2bytes=192kB/s, 16kB Chunks
        # If no data is returned, the recording process has stopped/crashed.
        if len(data) == 0: break
        
        # Feed the audio chunk to the recognizer.
        # AcceptWaveform returns True if a full sentence/phrase is detected (silence detected).
        if rec.AcceptWaveform(data):
            # Parse the final JSON result for the completed phrase.
            result = json.loads(rec.Result())
            # Extract the 'text' string from the JSON object.
            text = result.get('text', '').strip()
            # If text is not empty, print it with a green checkmark.
            if text: print(f"\n✅ '{text}'")
        else:
            # If the phrase is not yet complete (user is still speaking),
            # get the partial result (real-time feedback).
            partial = json.loads(rec.PartialResult())
            # Print the partial text, overwriting the current line (\r) to create a dynamic effect.
            print(f"\r⏳ {partial.get('partial', '')}", end='', flush=True)
# Handle the user pressing CTRL+C to stop the script gracefully.
except KeyboardInterrupt:
    print("\nBeendet!")
# Terminate the 'arecord' subprocess to release the microphone.
proc.terminate()