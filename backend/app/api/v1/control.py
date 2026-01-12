"""
Control API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.controller import controller


router = APIRouter()


class CommandRequest(BaseModel):
    command: str


@router.post("/command")
def execute_command(request: CommandRequest):
    """POST /api/v1/control/command"""
    controller.execute_command(request.command)
    return {"status": "success", "command": request.command}


@router.post("/stop")
def emergency_stop():
    """POST /api/v1/control/stop"""
    controller.execute_command("stop")
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