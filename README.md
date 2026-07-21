# cursor-cloud-agent

An interactive AI chatbot powered by the [Anthropic API](https://docs.anthropic.com/) and Python.

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Add your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

Or export it directly:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Get an API key from the [Anthropic Console](https://console.anthropic.com/).

## Run the chatbot

```bash
uv run chatbot
```

Or:

```bash
uv run python -m chatbot
```

## Jupyter notebook practice

A practice notebook is included for experimenting with the Anthropic API in Python:

```bash
uv sync
cp .env.example .env   # add your API key
uv run jupyter notebook notebooks/anthropic_practice.ipynb
```

Or use JupyterLab:

```bash
uv run jupyter lab notebooks/anthropic_practice.ipynb
```

The notebook covers:
- Sending your first message
- Streaming responses
- Multi-turn conversations
- System prompts
- Token usage metadata
- Open-ended practice exercises

## Usage

- Type a message and press Enter to chat.
- `exit`, `quit`, or `q` — end the session.
- `/clear` — clear conversation history.

## Optional configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Model to use for responses |
