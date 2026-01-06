from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("LiquidAI/LFM2.5-1.2B-Instruct")
model = AutoModelForCausalLM.from_pretrained("LiquidAI/LFM2.5-1.2B-Instruct")

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

functions_text2 = [
    {
        "name": "move_forward",
        "description": "Lässt den Roboter vorwärts fahren",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {"type": "number", "description": "Dauer in Sekunden"}
            },
            "required": ["duration"]
        },
    },
    {
        "name": "turn_left",
        "description": "Lässt den Roboter nach links drehen",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {"type": "number", "description": "Dauer in Sekunden"}
            },
            "required": ["duration"]
        },
    },
    {
        "name": "turn_right",
        "description": "Lässt den Roboter nach rechts drehen",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {"type": "number", "description": "Dauer in Sekunden"}
            },
            "required": ["duration"]
        },
    },
    {
        "name": "stop",
        "description": "Lässt den Roboter sofort stoppen",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
]

prompt = f"""
Du bist ein Roboter-KI-Assistent.
Du kannst folgende Funktionen ausführen, um den Roboter zu steuern:
{functions_text2}

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



messages = [
    {"role": "user", "content": prompt},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))