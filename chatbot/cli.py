import argparse
import getpass
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

DEFAULT_MODEL = "claude-sonnet-4-20250514"
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Answer clearly and concisely unless the user asks for more detail."
)
EXIT_COMMANDS = {"exit", "quit", "q", "/exit", "/quit"}
ENV_PATH = Path(".env")


def write_env_file(api_key: str, model: str | None = None) -> None:
    lines = [f"ANTHROPIC_API_KEY={api_key}"]
    if model:
        lines.append(f"ANTHROPIC_MODEL={model}")
    ENV_PATH.write_text("\n".join(lines) + "\n")
    ENV_PATH.chmod(0o600)


def setup_api_key(from_env: bool = False, api_key_arg: str | None = None) -> None:
    load_dotenv()

    if ENV_PATH.exists() and os.getenv("ANTHROPIC_API_KEY") and sys.stdin.isatty():
        overwrite = input(".env already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite not in {"y", "yes"}:
            print("Setup cancelled.")
            return

    api_key = (api_key_arg or "").strip()
    if not api_key and from_env:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key and not sys.stdin.isatty():
        api_key = sys.stdin.read().strip()
    if not api_key and sys.stdin.isatty():
        api_key = getpass.getpass("Enter your Anthropic API key: ").strip()

    if not api_key or api_key == "your-api-key-here":
        print(
            "Error: a valid API key is required.\n"
            "Provide it with one of:\n"
            "  uv run chatbot setup --from-env\n"
            "  uv run chatbot setup --key 'your-key'\n"
            "  echo 'your-key' | uv run chatbot setup",
            file=sys.stderr,
        )
        raise SystemExit(1)

    model = os.getenv("ANTHROPIC_MODEL", "").strip() or None
    write_env_file(api_key, model)
    print(f"Saved API key to {ENV_PATH.resolve()}")


def get_client() -> anthropic.Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "Run setup to add your key:\n"
            "  uv run chatbot setup\n"
            "Or set it manually:\n"
            "  export ANTHROPIC_API_KEY='your-key-here'",
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


def run_chat() -> None:
    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    client = get_client()
    chat_loop(client, model)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anthropic API chatbot")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("chat", help="Start the interactive chatbot (default)")
    setup_parser = subparsers.add_parser("setup", help="Save your Anthropic API key to .env")
    setup_parser.add_argument(
        "--from-env",
        action="store_true",
        help="Use ANTHROPIC_API_KEY from the environment instead of prompting",
    )
    setup_parser.add_argument(
        "--key",
        help="API key to save (non-interactive)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "setup":
        setup_api_key(from_env=args.from_env, api_key_arg=args.key)
        return

    run_chat()


if __name__ == "__main__":
    main()
