"""
Control API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.controller import controller


router = APIRouter()


class CommandRequest(BaseModel):
    command: str


class NavigateRequest(BaseModel):
    x: float
    y: float
    yaw_deg: float = 0.0


@router.post("/command")
def execute_command(request: CommandRequest):
    """POST /api/v1/control/command"""
    command_id = controller.enqueue_command(request.command)
    return {"status": "accepted", "command_id": command_id, "command": request.command}


@router.post("/navigate")
def navigate_to_pose(request: NavigateRequest):
    """POST /api/v1/control/navigate"""
    command_text = f"nav {request.x} {request.y} {request.yaw_deg}"
    command_id = controller.enqueue_command(command_text)
    return {"status": "accepted", "command_id": command_id, "command": command_text}


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


@router.get("/map")
def get_map():
    """GET /api/v1/control/map"""
    return controller.get_map()


@router.get("/nav_status")
def get_nav_status():
    """GET /api/v1/control/nav_status"""
    return controller.get_nav_status()


@router.get("/battery")
def get_battery():
    """GET /api/v1/control/battery"""
    return controller.get_battery()


@router.get("/camera")
def get_camera():
    """GET /api/v1/control/camera"""
    return controller.get_camera_info()