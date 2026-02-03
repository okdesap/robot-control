import ollama
import json
from app.core.controller import controller

client = ollama.Client()

model  = "llama3:8b"

# All models must be installed before use
# ollama run {name}
# llama3.2:1b 1.3GB, 3B parameters
# llama3:8b   4.7GB, 8B parameters

# TODO: take input from frontend
user_input = "Lasse den Roboter für 3 Sekunden vorwärts fahren."


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

prompt = f"""
Du bist ein Roboter-KI-Assistent.
Du kannst folgende Funktionen ausführen, um den Roboter zu steuern:
{functions_text1}

Aufgabe:  
- Antworte **nur im JSON-Format**, das die auszuführende Funktion und ihre Parameter enthält.
- Das Format muss exakt so sein:

{{
  "function_call": {{
    "name": "funktion_name",
    "arguments": {{
      "... hier die Parameter ..."
    }}
  }}
}}

Beispiele:

1. Roboter 3 Sekunden vorwärts fahren:
{{
  "function_call": {{
    "name": "move_forward",
    "arguments": {{
      "duration": 3
    }}
  }}
}}

2. Roboter sofort stoppen:
{{
  "function_call": {{
    "name": "stop"
  }}
}}

Deine Aufgabe: Lies die folgende Benutzeranfrage und wähle **die passende Funktion** mit passenden Parametern aus:

Benutzeranfrage: "{user_input}"

GIB NUR DAS KORREKTE JSON WIEDER
"""


def use_function_calling():
    response = client.generate(model=model, prompt=prompt)
    data_old = response["response"]

    try:
        data = json.loads(data_old)
        name = data["function_call"]["name"]
        arg = data["function_call"]["arguments"]["duration"]
        controller.execute_command(name + " " + str(arg))
    except json.JSONDecodeError as e:
        print("Error in LLM:", e)
        print("LMM data:", data_old)

use_function_calling()
