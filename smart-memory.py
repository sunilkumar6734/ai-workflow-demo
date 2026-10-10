
import json
from pathlib import Path
from ollama import chat

MODEL = "llama3.2:3b"
MEMORY_FILE = Path(__file__).with_name("memory.json")


def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("facts", [])
    return []


def save_memory(facts):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"facts": facts}, f, indent=2)



def extract_memory(user_message):
    response = chat(
        model=MODEL,
        format="json",
        options={"temperature": 0},
        messages=[
            {
                "role": "system",
                "content": """
You are a personal memory extraction system.

Your ONLY task is to extract facts about the user.

IMPORTANT RULES:
- If the user tells you their name, ALWAYS save it.
- If the user mentions their profession, save it.
- If the user mentions what they are learning, save it.
- If the user mentions long-term goals, save them.
- If the user mentions preferences, save them.
- Do not save greetings or general questions.
- Never invent facts.
- Do not save passwords or sensitive information.

Examples:

Input: hi
Output: {"facts": []}

Input: i am sunil
Output: {"facts": ["User's name is Sunil"]}

Input: my name is Rahul
Output: {"facts": ["User's name is Rahul"]}

Input: I am learning Python and Ollama
Output: {"facts": ["User is learning Python and Ollama"]}

Input: I work as a Power BI developer
Output: {"facts": ["User works as a Power BI developer"]}

Input: What is Python?
Output: {"facts": []}

Return ONLY valid JSON:
{"facts": ["fact1", "fact2"]}
"""
            },
            {
                "role": "user",
                "content": f"Extract facts from this message: {user_message}"
            }
        ]
    )

    print("DEBUG - Raw extraction:", response.message.content)

    try:
        result = json.loads(response.message.content)
        facts = result.get("facts", [])

        if not isinstance(facts, list):
            return []

        return [
            fact.strip()
            for fact in facts
            if isinstance(fact, str) and fact.strip()
        ]

    except (json.JSONDecodeError, AttributeError):
        return []


facts = load_memory()
recent_messages = []

print("AI Assistant with Persistent Memory")
print("Commands: memories, exit")

while True:
    question = input("\nYou: ").strip()

    if question.lower() == "exit":
        break

    if question.lower() == "memories":
        print(json.dumps(facts, indent=2))
        continue

    if not question:
        continue

    # Extract useful memories using Ollama
    new_facts = extract_memory(question)

    for fact in new_facts:
        if fact.casefold() not in [
            saved.casefold() for saved in facts
        ]:
            facts.append(fact)

    save_memory(facts)

    print("Extracted memories:", new_facts)

    # Send saved memories and recent chat to Ollama
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Use these saved facts when relevant:\n"
                + json.dumps(facts)
            )
        }
    ]

    messages.extend(recent_messages[-4:])

    messages.append({
        "role": "user",
        "content": question
    })

    response = chat(model=MODEL, messages=messages)

    answer = response.message.content

    print("\nAI:", answer)

    recent_messages.extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer}
    ])

    recent_messages = recent_messages[-4:]
