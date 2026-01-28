"""
Command Parser
"""

from app.core.models.command import (
    ForwardCommand,
    StopCommand,
    TurnLeftCommand,
    TurnRightCommand,
)


def parse_command(command_text: str):
    """
    Text -> Befehl

    "forward 2.0" -> ForwardCommand(duration_s=2.0)
    "stop" -> StopCommand()
    """
    parts = command_text.strip().lower().split()
    
    if not parts:
        raise ValueError("Leerer Befehl")
    
    action = parts[0]
    
    if action == "stop":
        return StopCommand()
    
    duration = float(parts[1]) if len(parts) > 1 else 1.0

    if action == "forward":
        return ForwardCommand(duration_s=duration)
    if action == "left":
        return TurnLeftCommand(duration_s=duration)
    if action == "right":
        return TurnRightCommand(duration_s=duration)

    raise ValueError(f"Unknown Action: {action}")
