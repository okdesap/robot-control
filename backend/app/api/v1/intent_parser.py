from typing import Optional
import re

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

    for phrase, command in COMMAND_MAP.items():
        if phrase in normalized:
            return f"{command} {duration}"

    return None
