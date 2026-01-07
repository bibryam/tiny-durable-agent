# Tiniest Durable Agent

The tiniest durable agent possible that is production-ready too. Built with [Dapr Agents](https://diagrid.ws/dapr-agents-doc).

## Prerequisites
- [An OpenAI API key](https://platform.openai.com/api-keys) or another supported LLM
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/desktop/)

## Setup

* Install Dapr locally

On macOS do as below (or check [here](https://docs.dapr.io/getting-started/install-dapr-selfhost/) for other platforms)
```bash
brew install dapr/tap/dapr-cli
dapr init
```

* Add your OpenAI or other LLM provider key to `resources/llm-provider.yaml`.

* Create a virtual environment and install dapr-agents:

```bash
python3.10 -m venv .venv && source .venv/bin/activate && pip install "dapr-agents>=0.10.5"
```


## Run tiniest Durable Agent in embedded mode

This is the entire agent [implementation](./durable_agent_minimal.py).

```python
from dapr_agents import DurableAgent
from dapr_agents.workflow.runners import AgentRunner

runner = AgentRunner()
agent = DurableAgent(name="Assistant")
print(runner.run_sync(agent, {"task": "Write a haiku about programming."}))
runner.shutdown(agent)
```
* Run the agent

```bash
dapr run --app-id durable-agent-minimal --resources-path ./resources --log-level error -- python durable_agent_minimal.py
```

This command runs a Dapr sidecar and the agent. The prompt triggers a durable workflow that prints a haiku about programming (shown below) and then shuts down.

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

## Run tiniest Durable Agent in standalone mode

This is the entire agent [implementation](./durable_agent_service.py).

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

* Run the agent

```bash
dapr run --app-id durable-agent-service --resources-path ./resources -p 8001 --log-level warn -- python durable_agent_service.py
```


### Despite its size, this Agent does the following
* Exposes the agent on `http://localhost:8001/run`
* Uses the [Dapr Conversation API](https://docs.dapr.io/developing-applications/building-blocks/conversation/) to talk to an OpenAI model
* Uses the [Dapr Pub/Sub API](https://docs.dapr.io/developing-applications/building-blocks/pubsub/) to subscribe to Redis on `assistant.topic`
* Uses the [Dapr Workflow API](https://docs.dapr.io/developing-applications/building-blocks/workflow/) as a durable execution engine to persist agent actions into Redis
* Uses the [Dapr State Store API](https://docs.dapr.io/developing-applications/building-blocks/state-management/) to persist conversation history to Redis
* Uses the Dapr State Store API to register itself in Redis for discovery by other agents
* Uses [Dapr observability features](https://docs.dapr.io/operations/observability/tracing/tracing-overview/) to send execution traces to Zipkin at `http://localhost:9411/`


### Trigger the agent over HTTP

In a separate terminal, prompt the agent over HTTP:

```bash
curl -i -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a haiku about programming."}'
```

You will get back the workflow instance ID started by the prompt.

```bash
HTTP/1.1 200 OK
content-type: application/json
{"instance_id":"b6a43bd858f148d5b95048ada055406a","status_url":"/v1.0/workflows/dapr/b6a43bd858f148d5b95048ada055406a"}%
```

### Trigger the agent over PubSub

Prompt the agent by publishing the prompt to a PubSub topic:

```bash
dapr publish --publish-app-id durable-agent-service --pubsub agent-pubsub --topic assistant.topic --data '{"task": "Write a haiku about programming."}'
```


You will get confirmation that the event was published

```bash
✅  Event published successfully
```

## Examine workflow executions

In a separate terminal, launch the [Diagrid Dashboard](https://www.diagrid.io/blog/improving-the-local-dapr-workflow-experience-diagrid-dashboard):

```bash
docker run -p 8080:8080 ghcr.io/diagridio/diagrid-dashboard:latest
```
View agent workflows triggered by the prompts at `http://localhost:8080/`

![diagrid-dashboard.png](images/diagrid-dashboard.png)

## Examine agent traces in Zipkin

The Dapr CLI installs and runs Zipkin by default. View agent traces at: `http://localhost:9411/`

If Zipkin is not running, start it with:

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```
![zipkin.png](images/zipkin.png)

## Examine Prometheus-compatible metrics 

`http://localhost:9090/`

## Examine Redis storage

Launch Redis Insight:

```bash 
docker run --rm -d --name redisinsight -p 5540:5540 redis/redisinsight:latest
```

View Redis Insight at: `http://localhost:5540/`. Connect to local Redis at `host.docker.internal:6379` (Mac or Windows) or `172.17.0.1:6379` (Linux). Inspect persisted conversation history, workflow execution, and PubSub messages.

![redis-insights.png](images/redis-insights.png)

## Next Steps

For a detailed visualization of agent workflow execution, follow [this quickstart guide](https://diagrid.ws/durable-agent-qs)

![diagrid-catalyst.png](images/diagrid-catalyst.png)
