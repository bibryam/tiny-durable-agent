# Tiniest Durable Agent

A minimal, production-ready durable agent built with [Dapr Agents](https://diagrid.ws/dapr-agents-doc). This example shows how little code is required to build a durable and at the same time production-ready AI agent.

![dapr-agents.png](images/dapr-agents.png)


## Prerequisites
- [OpenAI API key](https://platform.openai.com/api-keys) or another supported LLM provider
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/desktop/)

## Setup

### Install Dapr locally

On macOS:

```bash
brew install dapr/tap/dapr-cli
dapr init
````

For other platforms, see [https://docs.dapr.io/getting-started/install-dapr-selfhost/](https://docs.dapr.io/getting-started/install-dapr-selfhost/)

### Configure your LLM provider

Add your OpenAI or other LLM provider credentials to:

```
resources/llm-provider.yaml
```

### Create a virtual environment and install dapr-agents

```bash
python3.10 -m venv .venv && source .venv/bin/activate && pip install "dapr-agents>=0.10.5"
```

## Run the tiniest Durable Agent (embedded mode)

This is the complete agent implementation: [`durable_agent_minimal.py`](./durable_agent_minimal.py).

```python
from dapr_agents import DurableAgent
from dapr_agents.workflow.runners import AgentRunner

runner = AgentRunner()
agent = DurableAgent(name="Assistant")
print(runner.run_sync(agent, {"task": "Write a haiku about programming."}))
runner.shutdown(agent)
```

Run the agent:

```bash
dapr run --app-id durable-agent-minimal --resources-path ./resources -- python durable_agent_minimal.py
```

This command starts a Dapr sidecar and executes the agent. The prompt triggers a durable workflow, prints the response, and exits.

Example output:

```bash
== APP == user:
== APP == Write a haiku about programming.
== APP ==
== APP == --------------------------------------------------------------------------------
== APP ==
== APP == Assistant(assistant):
== APP == Lines of logic flow,
== APP == Silent thoughts in coded streams—
== APP == Dreams compile to life.
== APP ==
== APP == --------------------------------------------------------------------------------
== APP ==
```

## Run the tiniest Durable Agent (standalone service mode)

This is the complete service-style implementation: [`durable_agent_service.py`](./durable_agent_service.py).

```python
from dapr_agents import DurableAgent
from dapr_agents.workflow.runners import AgentRunner

runner = AgentRunner()
agent = DurableAgent(name="Assistant", system_prompt="You are a helpful assistant")

try:
    runner.serve(agent, host="0.0.0.0", port=8001)
finally:
    runner.shutdown(agent)
```

Run the agent as a long-running service:

```bash
dapr run --app-id durable-agent-service --resources-path ./resources -p 8001 --log-level warn --metrics-port=9090 --dapr-http-port=3500 --enable-api-logging -- python durable_agent_service.py
```

## What this agent does

Despite its size, this agent:

- Exposes an HTTP endpoint at `http://localhost:8001/run`
- Subscribes to Redis via the [Dapr Pub/Sub API](https://docs.dapr.io/developing-applications/building-blocks/pubsub/) on `assistant.topic`
- Uses the [Dapr Conversation API](https://docs.dapr.io/developing-applications/building-blocks/conversation/) to decouple interaction with LLM providers
- Uses the [Dapr Workflow API](https://docs.dapr.io/developing-applications/building-blocks/workflow/) to execute agent logic durably
- Persists conversation history using the [Dapr State Store API](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- Registers itself into an agent registry for discovery by other agents
- Is assigned a workload identity based on SPIFFE via [Dapr’s built-in mTLS](https://docs.dapr.io/concepts/security-concept/#identity) and identity system
- Supports automatic authentication between agents and callers via Dapr [sidecar-to-sidecar security](https://docs.dapr.io/concepts/security-concept/#authentication)
- Consumes configuration values from external configuration stores using the [Dapr Configuration API](https://docs.dapr.io/developing-applications/building-blocks/configuration/)
- Retrieves secrets such as LLM credentials using the [Dapr Secrets API](https://docs.dapr.io/developing-applications/building-blocks/secrets/)
- Emits distributed traces via [Dapr observability](https://docs.dapr.io/operations/observability/tracing/tracing-overview/) to Zipkin at `http://localhost:9411/`
- Exposes [Prometheus-compatible metrics](https://docs.dapr.io/operations/observability/metrics/metrics-overview/)
- Logs all [API interactions](https://docs.dapr.io/operations/troubleshooting/api-logs-troubleshooting/) with backing infrastructure such as Redis, Pub/Sub brokers, and LLM providers

### Capabilities not enabled in this example (but easily added)

The following Dapr capabilities are not enabled in this example, but can be added without changing application code:

- **Resiliency policies**  
  Add retries, timeouts, and circuit breakers when interacting with state stores, Pub/Sub systems, and LLM providers using the [Dapr Resiliency API](https://docs.dapr.io/developing-applications/building-blocks/resiliency/resiliency-overview/)

- **Durable retries and compensation logic**  
  Configure retry behavior and failure handling directly in workflows using the [Dapr Workflow API](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)

- **Authorization and access control**  
  Control which callers can invoke this agent and which operations are permitted using [Dapr access control policies](https://docs.dapr.io/operations/security/app-api-token/) and [Dapr mTLS authorization](https://docs.dapr.io/operations/security/mtls/mtls-overview/)

**Operational by default**

All of these capabilities come from running the agent with a Dapr sidecar. Identity, security, durability, observability, configuration, and integration with backing systems are provided uniformly by Dapr.

## Trigger the agent over HTTP

In a separate terminal:

```bash
curl -i -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a haiku about programming."}'
```

The response includes the workflow instance ID created for this request.

## Trigger the agent over Pub/Sub

Publish a prompt to the subscribed topic:

```bash
curl -i -X POST http://localhost:3500/v1.0/publish/agent-pubsub/assistant.topic \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a haiku about programming."}'
```

Dapr confirms that the event was published.

## Examine workflow executions

Launch the Diagrid Dashboard in a separate terminal:

```bash
docker run -p 8080:8080 ghcr.io/diagridio/diagrid-dashboard:latest
```

View agent workflows at:

```
http://localhost:8080/
```

![diagrid-dashboard.png](images/diagrid-dashboard.png)

## Examine agent traces in Zipkin

The Dapr CLI starts Zipkin by default. Open:

```
http://localhost:9411/
```

If Zipkin is not running:

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

![zipkin.png](images/zipkin.png)

## Examine Prometheus-compatible metrics

```
http://localhost:9090/
```

## Examine Redis storage

Start Redis Insight:

```bash
docker run --rm -d --name redisinsight -p 5540:5540 redis/redisinsight:latest
```

Open:

```
http://localhost:5540/
```

Connect to Redis:

* macOS or Windows: `host.docker.internal:6379`
* Linux: `172.17.0.1:6379`

Inspect conversation state, workflow history, and Pub/Sub messages.

![redis-insights.png](images/redis-insights.png)

## Next steps

For a deeper walkthrough and visual exploration of agent workflows, see:
[https://diagrid.ws/durable-agent-qs](https://diagrid.ws/durable-agent-qs)

![diagrid-catalyst.png](images/diagrid-catalyst.png)

