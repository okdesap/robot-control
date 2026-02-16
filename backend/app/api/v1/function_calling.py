import ollama
import json
from app.core.controller import controller

client = ollama.Client()
model = "llama3:8b"
#All Models must be installeb before use
# ollama run {name}
#llama3.2:1b 1.3GB, 3B Parameter
#llama3:8b   4.7GB, 8B Parameter 

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
"""

def function_calling(user_input: str):
    """
    Parses the user input using the LLM and enqueues each command individually.
    """
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

    response = client.generate(model=model, prompt=prompt)
    data_old = response["response"]
    print("Raw LLM response:", data_old)

    try:
        data = json.loads(data_old)

        for cmd in data.get("function_calls", []):
            name = cmd["name"]
            if name == "stop":
                command_str = "stop"
            else:
                duration = cmd.get("arguments", {}).get("duration", 1.5)
                command_str = f"{name} {duration}"

            # Execute immediately
            print("Command to be executed:", command_str)
            controller.enqueue_command(command_str)

        # Return a generic message or the first command for TTS
        first_cmd = data.get("function_calls", [])[0] if data.get("function_calls") else None
        if first_cmd:
            action = first_cmd["name"]
            return _reply_for_intent(action)
        return "Befehl(en) ausgeführt."

    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        print("LLM output:", data_old)
        return "Fehler beim Verarbeiten des Befehls."