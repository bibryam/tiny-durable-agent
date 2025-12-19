# Dapr Agents Hello World

Minimal setup to run a DurableAgent Dapr Agent

## Prerequisites
- OpenAI or another LLM API key
- Python 3.10+ available
- Docker and Dapr CLI

## Setup
- Create a virtual environment:
```bash
python3.10 -m venv .venv && source .venv/bin/activate
````

* Install dependencies:

```bash
pip install -r requirements.txt
```

* Add your OpenAI or other LLM provider key to `resources/ll-provider.yaml`.

## Run the agent

```bash
dapr run --app-id agent --resources-path ./resources --log-level error -- python agent.py
```

The agent will run, print a haiku about programming in the longs, and shut down.

## How DurableAgent is running
* Uses Dapr Conversation API to talk to an LLM provider
* Uses Dapr Workflow API to persist agent actions to Redis
* Uses Dapr State Store API to persist conversation history to Redis
