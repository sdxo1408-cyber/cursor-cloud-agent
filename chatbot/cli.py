import os
import sys

import anthropic
from dotenv import load_dotenv

DEFAULT_MODEL = "claude-sonnet-4-20250514"
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Answer clearly and concisely unless the user asks for more detail."
)
EXIT_COMMANDS = {"exit", "quit", "q", "/exit", "/quit"}


def get_client() -> anthropic.Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "Set it in your environment or in a .env file:\n"
            "  export ANTHROPIC_API_KEY='your-key-here'\n"
            "  # or copy .env.example to .env and add your key",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return anthropic.Anthropic(api_key=api_key)


def chat_loop(client: anthropic.Anthropic, model: str) -> None:
    messages: list[dict[str, str]] = []

    print("Anthropic Chatbot")
    print(f"Model: {model}")
    print("Type your message and press Enter. Commands: /clear, exit")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("Goodbye!")
            break

        if user_input.lower() == "/clear":
            messages.clear()
            print("Conversation cleared.")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nAssistant: ", end="", flush=True)
        assistant_text = ""

        try:
            with client.messages.stream(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    assistant_text += text
        except anthropic.APIError as exc:
            messages.pop()
            print(f"\nAPI error: {exc}", file=sys.stderr)
            continue

        print()
        messages.append({"role": "assistant", "content": assistant_text})


def main() -> None:
    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    client = get_client()
    chat_loop(client, model)


if __name__ == "__main__":
    main()
