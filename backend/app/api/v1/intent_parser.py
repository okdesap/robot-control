from typing import Optional
import re
import os

STOP_KEYWORDS = ["stop", "stopp", "halt", "halte an"]

COMMAND_MAP = {
    # FORWARD
    "fahr vor": "forward",
    "vorwärts": "forward",
    "geradeaus": "forward",
    "fahr": "forward",

    # LEFT
    "dreh links": "left",
    "nach links": "left",
    "links": "left",

    # RIGHT
    "dreh rechts": "right",
    "nach rechts": "right",
    "rechts": "right",

    # DOCK / UNDOCK
    "dock": "dock",
    "andocken": "dock",
    "docke an": "dock",
    "undock": "undock",
    "abdocken": "undock",
    "docke ab": "undock",
}

def extract_number(text: str) -> Optional[float]:
    """
    Extracts a number from STT message (supports float).
    """
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if match:
        return float(match.group().replace(",", "."))
    return None


def parse_intent(stt_text: str) -> Optional[str]:
    """
    Changes raw STT-Text into correct command
    """
    if not stt_text:
        return None

    normalized = stt_text.lower().strip()
    
    for key in STOP_KEYWORDS:
        if key in normalized:
            return "stop"

    duration = extract_number(normalized)
    if duration == None:
        duration = 1.5  # Default duration, if they user forgets or dont know

    # Default speeds can be tuned to match the UI sliders.
    try:
        default_linear = float(os.getenv("STT_DEFAULT_LINEAR", "0.5") or "0.5")
    except Exception:
        default_linear = 0.5
    try:
        default_angular = float(os.getenv("STT_DEFAULT_ANGULAR", "0.5") or "0.5")
    except Exception:
        default_angular = 0.5

    for phrase, command in COMMAND_MAP.items():
        if phrase in normalized:
            if command == "forward":
                return f"{command} {duration} {default_linear}"
            if command in {"left", "right"}:
                return f"{command} {duration} {default_angular}"
            return f"{command} {duration}"

    return None
