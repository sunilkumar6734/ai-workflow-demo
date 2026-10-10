
from ollama import chat

print("Local AI Assistant is ready!")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI Data Analyst assistant."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    print("\nAI:", response.message.content, "\n")
