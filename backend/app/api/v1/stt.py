"""
STT API - Placeholder
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/transcribe")
def transcribe_audio():
    """TODO: Whisper Integration"""
    return {"text": "TODO"}
