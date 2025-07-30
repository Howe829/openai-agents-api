from agents import Agent, RunContextWrapper, function_tool
from _agents.models import qwen_max_latest
from _agents.context import AgentContext

INSTRUCTIONS = """
You are a helpful assistant.
Before answering questions, you must use the get_context tool to get conversation context information.
If you can't solve the user's request, please transfer the request to the appropriate assistant.
If the user gives you a file ID, you need to use the set_current_file_id tool to set it to the current conversation context.
"""


@function_tool(
    name_override="get_context", description_override="get current conversation context"
)
def get_context(wrapper: RunContextWrapper[AgentContext]) -> dict:
    return wrapper.context.model_dump()


@function_tool(
    name_override="set_current_file_id",
    description_override="set current file id to conversation context",
)
def set_current_file_id(
    wrapper: RunContextWrapper[AgentContext], current_file_id: str
) -> bool:
    wrapper.context.current_file_id = current_file_id
    return True


triage_agent = Agent[AgentContext](
    name="Triage Agent",
    instructions=INSTRUCTIONS,
    model=qwen_max_latest,
    tools=[get_context, set_current_file_id],
)
