# Same as durable_agent_service.py but with every Dapr config set explicitly.
from dapr_agents import DurableAgent
from dapr_agents.memory import ConversationDaprStateMemory
from dapr_agents.storage.daprstores import StateStoreService
from dapr_agents.workflow.runners import AgentRunner
from dapr_agents.agents.configs import (
    AgentMemoryConfig,
    AgentPubSubConfig,
    AgentStateConfig,
    AgentRegistryConfig,
)
from dapr_agents.llm import DaprChatClient

runner = AgentRunner()
agent = DurableAgent(
    name="Assistant",
    system_prompt="You are a helpful assistant",

    # LLM client backed by Dapr conversation component
    llm=DaprChatClient(component_name="llm-provider"),

    # Conversation memory stored in Dapr state store
    memory=AgentMemoryConfig(
        store=ConversationDaprStateMemory(
            store_name="agent-statestore",
            session_id="assistant-session-id",
        )
    ),

    # Durable workflow state persisted via Dapr state store
    state=AgentStateConfig(
        store=StateStoreService(store_name="agent-wfstatestore"),
    ),

    # Pub/Sub wiring for requests and broadcasts
    pubsub=AgentPubSubConfig(
        pubsub_name="agent-pubsub",
        agent_topic="assistant.requests",
        broadcast_topic="agents.broadcast",
    ),

    # Registry store so other agents can discover this one
    registry=AgentRegistryConfig(
        store=StateStoreService(store_name="agent-registry"),
    ),
)

try:
    # Runner hosts the agent over HTTP and listens for PubSub messages
    runner.serve(agent, host="0.0.0.0", port=8001)
finally:
    runner.shutdown(agent)