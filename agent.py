from dapr_agents import DurableAgent
from dapr_agents.workflow.runners import AgentRunner

runner = AgentRunner()
agent = DurableAgent(name="Assistant")
print(runner.run_sync(agent, {"task": "Write a haiku about programming."}))
runner.shutdown(agent)