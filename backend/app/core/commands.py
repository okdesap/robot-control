"""
Command Parser
"""


def parse_command(command_text: str) -> dict:
    """
    Text -> Befehl
    
    "forward 2.0" -> {"action": "forward", "duration": 2.0}
    "stop" -> {"action": "stop", "duration": 0.0}
    """
    parts = command_text.strip().lower().split()
    
    if not parts:
        raise ValueError("Leerer Befehl")
    
    action = parts[0]
    
    if action == "stop":
        return {"action": "stop", "duration": 0.0}
    
    duration = float(parts[1]) if len(parts) > 1 else 1.0
    
    return {"action": action, "duration": duration}
