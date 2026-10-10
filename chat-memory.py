
from ollama import chat

# Step 1: Model configuration
MODEL = "qwen3.5:4b"
MAX_HISTORY = 10  # Keep last 10 conversation messages

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a helpful AI assistant. "
        "Give clear, accurate answers. "
        "Explain programming concepts step by step."
    )
}

# Step 2: Create conversation history
messages = [SYSTEM_MESSAGE]

print("AI Chatbot Started!")
print(f"Model: {MODEL}")
print("Commands: /model, /clear, exit\n")

while True:

    # Step 3: Get user input
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if question.lower() == "/model":
        print(f"\nActive model: {MODEL}\n")
        continue

    if question.lower() == "/clear":
        messages = [SYSTEM_MESSAGE]
        print("\nConversation memory cleared.\n")
        continue

    if not question:
        continue

    # Step 4: Store user question
    messages.append({
        "role": "user",
        "content": question
    })

    try:
        # Step 5: Send limited conversation history
        conversation = [
            SYSTEM_MESSAGE,
            *messages[1:][-MAX_HISTORY:]
        ]

        # Step 6: Stream the response from Ollama
        response = chat(
            model=MODEL,
            messages=conversation,
            stream=True,
            options={
                "temperature": 0.5,
                "num_ctx": 4096
            }
        )

        print("\nAI: ", end="", flush=True)

        answer_parts = []

        for chunk in response:
            content = chunk.message.content or ""

            if content:
                print(content, end="", flush=True)
                answer_parts.append(content)

        answer = "".join(answer_parts)

        # Step 7: Store AI response
        messages.append({
            "role": "assistant",
            "content": answer
        })

        print("\n")

    except Exception as e:
        # Remove the unanswered user question
        messages.pop()
        print("\nError:", e)
