"""
Control API
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.controller import controller
from app.api.v1.intent_parser import parse_intent


router = APIRouter()


class CommandRequest(BaseModel):
    command: str

class STTRequest(BaseModel):
    original_text: str

@router.post("/command")
def execute_command(request: CommandRequest):
    """POST /api/v1/control/command"""
    command_id = controller.enqueue_command(request.command)
    return {"status": "accepted", "command_id": command_id, "command": request.command}

@router.post("/stt")
def handle_stt_command(request: STTRequest):
    """ POST /api/v1/control/stt """
    command = parse_intent(request.original_text)

    if not command:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Command could not be derived from STT text"
            )
    
    if command == "stop":
        controller.emergency_stop()
        return {"status": "stopped", "original_text": request.original_text, "command": command, "command_id": None}
    
    command_id = controller.enqueue_command(command)

    return {"status": "success","original_text": request.original_text,"command_id": command_id,"command": command}


@router.post("/stop")
def emergency_stop():
    """POST /api/v1/control/stop"""
    controller.emergency_stop()
    return {"status": "stopped"}


@router.get("/health")
def health():
    """GET /api/v1/control/health"""
    return {"status": "ok", **controller.health()}


@router.get("/photo")
def take_photo():
    """GET /api/v1/control/photo"""
    picture = controller.take_photo()
    return {
        "status": "success", 
        "photo": picture
    }

@router.get("/status")
def get_status():
    """GET /api/v1/control/status"""
    return controller.status()