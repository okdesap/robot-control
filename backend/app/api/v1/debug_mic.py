"""
LINUX AUDIO DIAGNOSTIC TOOL
---------------------------
Operation: Sequential (Record -> Save -> Process)

1. Records 5s of raw audio to 'debug_test.wav' using the native Linux command 'arecord'.
2. Loads the WAV file back and feeds it into Vosk for offline recognition.

GOAL: Helps to debug hardware issues (Sample Rate, Mic Gain) by creating a 
listenable file, isolating physical audio problems from real-time streaming logic.
"""

import sys
import os
import json
import vosk
import subprocess
import wave
import time


# Path to your downloaded model (adjust this path!)
MODEL_PATH = "vosk-model-small-de-0.15" 

# Filename for the temporary debug file
OUTPUT_FILENAME = "debug_test.wav"

# Recording duration in seconds
DURATION = 5 

# Sample rate (Must match Microphone capabilities AND Vosk)
# 48000 or 44100 are standard.
SAMPLE_RATE = 48000 

# Hardware Device ID (Check with 'arecord -l')
# hw:2,0 means Card 2, Device 0. 
# might need "hw:1,0" or "default" depending on setup.
AUDIO_DEVICE = "hw:2,0" 

def main():
    # 1. Check and Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model path '{MODEL_PATH}' not found.")
        sys.exit(1)

    print(f"🧠 Loading Vosk model from '{MODEL_PATH}'...")
    # Load the model ONCE at the beginning
    model = vosk.Model(MODEL_PATH)
    print("✅ Model loaded successfully.")

    while True:
        print("\n" + "="*40)
        print("   AUDIO DEBUG TOOL (Record -> Process)")
        print("="*40)
        
        # 2. User Trigger
        user_input = input(f"👉 Press ENTER to start recording ({DURATION}s) or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

        # 3. Recording Phase (using Linux 'arecord')
        print(f"\n🎙️  RECORDING NOW for {DURATION} seconds... (Speak!)")
        
        # Constructing the Linux command:
        # arecord -D hw:2,0 -d 5 -f S16_LE -r 48000 -c 1 output.wav
        cmd = [
            "arecord",
            "-D", AUDIO_DEVICE,    # Device ID
            "-d", str(DURATION),   # Duration
            "-f", "S16_LE",        # Format (Standard 16-bit)
            "-r", str(SAMPLE_RATE),# Rate (CRITICAL!)
            "-c", "1",             # Channels (Mono is better for recognition)
            OUTPUT_FILENAME
        ]

        try:
            # Run the command and wait until it finishes
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
            print("✅ Recording finished. File saved.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Recording failed. Is the microphone ID '{AUDIO_DEVICE}' correct?")
            print(f"   Error details: {e}")
            continue

        # 4. Processing Phase (Vosk)
        print("🔍 Analyzing audio file with Vosk...")
        
        if not os.path.exists(OUTPUT_FILENAME):
            print("❌ WAV file was not created.")
            continue

        try:
            # Open the saved WAV file
            wf = wave.open(OUTPUT_FILENAME, "rb")
            
            # Validation: Check if the file actually has the correct rate
            if wf.getframerate() != SAMPLE_RATE:
                print(f"WARNING: File has {wf.getframerate()}Hz, but code expected {SAMPLE_RATE}Hz.")
                print("This causes pitch shifts!")

            # Initialize Recognizer with the file's actual framerate
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            
            final_text = ""
            
            # Read the file chunk by chunk
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    final_text += res.get("text", "") + " "
            
            # Get the remaining result (last words)
            res = json.loads(rec.FinalResult())
            final_text += res.get("text", "")

            # 5. Output Result
            print("-" * 20)
            if final_text.strip():
                print(f"🗣️  RECOGNIZED: '{final_text.strip()}'")
            else:
                print("🤷‍♂️ NOTHING RECOGNIZED.")
            print("-" * 20)
            
            # Closing file
            wf.close()

        except Exception as e:
            print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    main()