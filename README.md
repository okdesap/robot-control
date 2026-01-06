Tests für Ai-Function calling
Modelle sollten:
- free to use
- auf cpu laufbar
- offline nutzbar/downloadbare

- gleiche Größe 1B Parameter (sehr klein, skalierung auf größere Modelle möglich)
- gleicher Prompt (Funktions definitionen + Aufgabe + Beispiele + user_input + "Betonung auf Json output")

Modelle von "Hugging Face"
LiquidAI/LFM2.5-1.2B-Instruct
-> keine externer sofware nötig
=> kein korrektes Json

Modell von "Ollama"
llama3.2:1b
-> download von Ollama 
-> sehr einfach zu nutzen
=> korrektes Json

ToDo:
-> mehr tests aud komplexeren Anfragen
-> größere Modelle testen