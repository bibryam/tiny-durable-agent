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

    llm=DaprChatClient(component_name="llm-provider"),

    memory=AgentMemoryConfig(
        store=ConversationDaprStateMemory(
            store_name="agent-statestore",
            session_id="assistant-session-id",
        )
    ),

    state=AgentStateConfig(
        store=StateStoreService(store_name="agent-wfstatestore"),
    ),

    pubsub=AgentPubSubConfig(
        pubsub_name="agent-pubsub",
        agent_topic="assistant.requests",
        broadcast_topic="agents.broadcast",
    ),

    registry=AgentRegistryConfig(
        store=StateStoreService(store_name="agent-registry"),
    ),
)

try:
    runner.serve(agent, host="0.0.0.0", port=8001)
finally:
    runner.shutdown(agent)