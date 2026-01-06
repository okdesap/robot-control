import ollama
#curl -fsSL https://ollama.com/install.sh | sh
#pip install ollama

client = ollama.Client()
model  = "llama3.2:1b"


user_input = "Lasse den Roboter für 3 Sekunden vorwärts fahren."

functions_text1 = """
1. move_forward(duration: float)
   - Lässt den Roboter vorwärts fahren
   - Parameter:
       - duration (Sekunden, z. B. 2.5)

2. turn_left(duration: float)
   - Lässt den Roboter nach links drehen
   - Parameter:
       - duration (Sekunden, z. B. 1.0)

3. turn_right(duration: float)
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
    "name": "stop",
    "arguments": {{}}
}}
}}

Deine Aufgabe: Lies die folgende Benutzeranfrage und wähle **die passende Funktion** mit passenden Parametern aus:

Benutzeranfrage: "{user_input}"
GIB NUR DAS JSON WIEDER
"""


response = client.generate(model=model, prompt=prompt)

print(response["response"])