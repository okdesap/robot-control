"""Command parser."""

from app.core.models.command import (
    DockCommand,
    ForwardCommand,
    NavigateToPoseCommand,
    StopCommand,
    TurnLeftCommand,
    TurnRightCommand,
    UndockCommand,
)


def parse_command(command_text: str):
    """Convert text to a command model.

    "forward 2.0" -> ForwardCommand(duration_s=2.0)
    "stop" -> StopCommand()
    """
    parts = command_text.strip().lower().split()
    
    if not parts:
        raise ValueError("Empty command")
    
    action = parts[0]
    
    if action == "stop":
        return StopCommand()

    if action == "dock":
        return DockCommand()

    if action == "undock":
        return UndockCommand()

    if action in {"nav", "goto", "pose", "navigate"}:
        if len(parts) < 3:
            raise ValueError("Navigation command requires x and y")
        x = float(parts[1])
        y = float(parts[2])
        yaw = float(parts[3]) if len(parts) > 3 else 0.0
        return NavigateToPoseCommand(x=x, y=y, yaw_deg=yaw)
    
    duration = float(parts[1]) if len(parts) > 1 else 1.0

    if action == "forward":
        return ForwardCommand(duration_s=duration)
    if action == "left":
        return TurnLeftCommand(duration_s=duration)
    if action == "right":
        return TurnRightCommand(duration_s=duration)

    raise ValueError(f"Unknown Action: {action}")
