"""
TTS API - Offline mit Pico (pico2wave)
"""
from fastapi import APIRouter, HTTPException 
from fastapi.responses import StreamingResponse
import os  # Für Umgebungsvariablen (noch gebraucht für Kompatibilität)
import subprocess # Für pico2wave-Aufruf
import tempfile # Für temporäre Dateien
import shutil # Für Dateiop 


@router.post("/synthesize")
def synthesize_speech(text: str):
    """
    Offline TTS mit pico2wave:
    - Eingabe: text (String)  (Name unverändert)
    - Verhalten: prüft pico2wave, erzeugt temporäre WAV-Datei, liefert sie als StreamingResponse
      und löscht die Datei danach.
    """
    # Eingabe prüfen
    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is empty") #fehlermeldung wenn text leer ist
    

    
    
    
    
    return StreamingResponse()#TODO: StreamingResponse mit WAV-Datei zurückgeben
