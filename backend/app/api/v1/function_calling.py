"""LLM function-calling helper (Ollama).

This module is intentionally *side-effect free* (no controller imports, no enqueuing).
It only converts a user utterance into one or more backend intent strings.

The intents returned by :func:`function_calling` are compatible with the backend's
command pipeline (the same format as parse_intent returns):

- "forward <duration>"
- "left <duration>"
- "right <duration>"
- "stop"
- "dock" / "undock"
- "nav <x> <y> <yaw>"
- "take_photo"
- "get_battery_status"

Runtime configuration:
- OLLAMA_HOST (optional)
- OLLAMA_MODEL (default: llama3:8b)
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import ollama


logger = logging.getLogger("backend.api.function_calling")


def _ollama_client() -> ollama.Client:
    host = (os.getenv("OLLAMA_HOST") or "").strip()
    return ollama.Client(host=host) if host else ollama.Client()


def _pick_model() -> str:
    return (os.getenv("OLLAMA_MODEL") or "llama3:8b").strip()


functions_text1 = """
1. forward(duration: float)
   - Lässt den Roboter vorwärts fahren
   - Parameter:
       - duration (Sekunden, z. B. 2.5)

2. left(duration: float)
   - Lässt den Roboter nach links drehen
   - Parameter:
       - duration (Sekunden, z. B. 1.0)

3. right(duration: float)
   - Lässt den Roboter nach rechts drehen
   - Parameter:
       - duration (Sekunden, z. B. 1.0)

4. stop()
   - Lässt den Roboter sofort stoppen
   - Keine Parameter

5. get_battery_status()
    - Gibt den aktuellen Batteriestatus zurück
    - Keine Parameter

6. take_photo()
    - Lässt den Roboter ein Foto aufnehmen
    - Keine Parameter

7. dock()
    - Lässt den Roboter andocken
    - Keine Parameter

8. undock()
    - Lässt den Roboter abdocken
    - Keine Parameter

9. nav(x: float, y: float, yaw: float = 0.0)
   - Lässt den Roboter zu einer bestimmten Position navigieren
   - Parameter:
       - x (Ziel-X-Koordinate im Karten- oder Weltkoordinatensystem)
       - y (Ziel-Y-Koordinate im Karten- oder Weltkoordinatensystem)
       - yaw (Ziel-Orientierungswinkel in Grad oder Radiant, Standard: 0.0)
"""


def _extract_json_object(text: str) -> str | None:
    """Try to extract a JSON object from a potentially noisy LLM response."""
    if not text:
        return None

    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text

    # Heuristic: grab the first {...} block.
    m = re.search(r"\{[\s\S]*\}", text)
    return m.group(0) if m else None


def _to_intent(name: str, arguments: dict[str, Any] | None) -> str | None:
    name = (name or "").strip()
    arguments = arguments or {}

    if name in {"stop", "dock", "undock", "take_photo", "get_battery_status"}:
        return name

    if name in {"forward", "left", "right"}:
        duration = arguments.get("duration", 1.5)
        try:
            duration_f = float(duration)
        except Exception:
            duration_f = 1.5
        duration_f = max(0.1, min(60.0, duration_f))
        return f"{name} {duration_f}"

    if name == "nav":
        x = arguments.get("x")
        y = arguments.get("y")
        yaw = arguments.get("yaw", 0.0)
        try:
            xf = float(x)
            yf = float(y)
            yawf = float(yaw)
        except Exception:
            return None
        return f"nav {xf} {yf} {yawf}"

    return None


def function_calling(user_input: str) -> list[str]:
    """Parse user input via LLM and return a list of intent command strings."""
    prompt = f"""
Du bist ein Roboter-KI-Assistent.
Du kannst folgende Funktionen ausführen, um den Roboter zu steuern:
{functions_text1}

Aufgabe:  
- Antworte **nur im JSON-Format**.
- Wenn der Benutzer mehrere Aktionen möchte, gebe **eine Liste von Funktionen** zurück.
- Format:

{{
  "function_calls": [
    {{
      "name": "funktion_name",
      "arguments": {{
        "... hier die Parameter ..."
      }}
    }}
  ]
}}

Benutzeranfrage: "{user_input}"

GIB NUR DAS KORREKTE JSON WIEDER
"""

    client = _ollama_client()
    model = _pick_model()

    response = client.generate(model=model, prompt=prompt)
    raw = response.get("response") if isinstance(response, dict) else None
    raw_text = (raw or "").strip()
    if not raw_text:
        return []

    json_text = _extract_json_object(raw_text)
    if not json_text:
        logger.warning("LLM did not return JSON: %s", raw_text)
        return []

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        logger.warning("Could not parse LLM JSON: %s", json_text)
        return []

    calls = data.get("function_calls", []) if isinstance(data, dict) else []
    if not isinstance(calls, list):
        return []

    intents: list[str] = []
    for call in calls:
        if not isinstance(call, dict):
            continue
        name = call.get("name")
        args = call.get("arguments")
        args_dict = args if isinstance(args, dict) else {}
        intent = _to_intent(str(name or ""), args_dict)
        if intent:
            intents.append(intent)

    return intents
