"""
TTS API - Placeholder
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/synthesize")
def synthesize_speech(text: str):
    """TODO: OpenAI TTS"""
    return {"status": "TODO"}
