from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from .bigquery_utils import (
    BIGQUERY_DATASET_NAME,
    GOOGLE_CLOUD_PROJECT_ID,
    get_tables_info,
)
from .state import DataAgentState
from .tools import (
    execute_bigquery_sql,
    execute_python_code,
)

load_dotenv()

all_tools = [execute_bigquery_sql, execute_python_code]

# Nodes
llm = init_chat_model("google_genai:gemini-2.0-flash", temperature=0.7).bind_tools(
    all_tools
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a data analysis agent. Please use tools to fulfill user requests.

## About BigQuery

- Follow BigQuery best practices (use standard SQL, avoid SELECT *, utilize WITH clauses and structured queries, optimize query costs, etc.).
- Available table and column schema information is as follows. Treat any tables/columns not listed here as non-existent.
- Target project details:
    Google Cloud Project ID: {GOOGLE_CLOUD_PROJECT_ID}
    Google Cloud Dataset ID: {BIGQUERY_DATASET_NAME}
- Table schema
    Schema is shown in JSON format below. Treat any tables/columns not listed here as non-existent.

    ```json
    {tables_info}
    ```
- Do not use LIMIT if it would negatively impact proper data analysis.

## Python Visualization
- When legends are needed, place them outside the graph

## Note
- When presenting SQL, please provide an explanation.
- [IMPORTANT] If there is SQL or Python code that should be executed, call the tools yourself without waiting for explicit execution instructions.

User request: {messages}

""",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


def call_llm_node(state: DataAgentState):
    messages = prompt_template.format_messages(
        messages=state.messages,
        GOOGLE_CLOUD_PROJECT_ID=GOOGLE_CLOUD_PROJECT_ID,
        BIGQUERY_DATASET_NAME=BIGQUERY_DATASET_NAME,
        tables_info=get_tables_info().model_dump_json(),
    )

    return {"messages": [llm.invoke(messages)]}


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    tools_by_name: dict[str, BaseTool]

    def __init__(self, tools: list[BaseTool]) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: DataAgentState):
        last_ai_message = inputs.get_last_ai_message()
        new_messages = []
        for tool_call in last_ai_message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            new_messages.append(
                ToolMessage(
                    content=tool_result.model_dump_json(),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": new_messages}


tool_node = BasicToolNode(all_tools)


def human_tool_review_node(
    state: DataAgentState,
) -> Command[Literal["call_llm", "tools"]]:
    last_ai_message = state.get_last_ai_message()
    tool_call = last_ai_message.tool_calls[-1]

    review_required_tools = [execute_bigquery_sql.name, execute_python_code.name]

    should_review = any(
        tool_call["name"] in review_required_tools
        for tool_call in last_ai_message.tool_calls
    )
    if not should_review:
        return Command(goto="tools")

    # this is the value we'll be providing via Command(resume=<human_review>)
    human_review = interrupt(
        {
            "question": "Is it okay to use tools?",
            # Surface tool calls for review
            "tool_call": tool_call,
        }
    )

    review_action = human_review["action"]
    review_data = human_review.get("data")

    # if approved, call the tool
    if review_action == "continue":
        return Command(goto="tools")

    # if rejected, return to the llm call
    elif review_action == "reject":
        # NOTE: we're adding feedback message as a ToolMessage
        # to preserve the correct order in the message history
        # (AI messages with tool calls need to be followed by tool call messages)
        tool_message = {
            "role": "tool",
            "content": "Tool call rejected",
            "name": tool_call["name"],
            "tool_call_id": tool_call["id"],
        }
        return Command(goto="call_llm", update={"messages": [tool_message]})

    # update the AI message AND call tools
    elif review_action == "update":
        updated_message = {
            "role": "ai",
            "content": last_ai_message.content,
            "tool_calls": [
                {
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    # This the update provided by the human
                    "args": review_data,
                }
            ],
            # This is important - this needs to be the same as the message you replacing!
            # Otherwise, it will show up as a separate message
            "id": last_ai_message.id,
        }
        return Command(goto="tools", update={"messages": [updated_message]})

    # provide feedback to LLM
    elif review_action == "feedback":
        # NOTE: we're adding feedback message as a ToolMessage
        # to preserve the correct order in the message history
        # (AI messages with tool calls need to be followed by tool call messages)
        tool_message = {
            "role": "tool",
            # This is our natural language feedback
            "content": review_data,
            "name": tool_call["name"],
            "tool_call_id": tool_call["id"],
        }
        return Command(goto="call_llm", update={"messages": [tool_message]})

    raise ValueError(f"Invalid review action: {review_action}")


# Edges
def route_after_llm(
    state: DataAgentState,
):
    ai_message = state.get_last_ai_message()

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "human_tool_review"
    return END


# Build Graph

graph_builder = StateGraph(DataAgentState)

graph_builder.set_entry_point("call_llm")
graph_builder.add_node("call_llm", call_llm_node)
graph_builder.add_node("human_tool_review", human_tool_review_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "call_llm", route_after_llm, {"human_tool_review": "human_tool_review", END: END}
)
graph_builder.add_edge("tools", "call_llm")


memory = MemorySaver()
data_agent_graph = graph_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    png_graph = data_agent_graph.get_graph().draw_mermaid_png()
    with open("data_agent_graph.png", "wb") as f:
        f.write(png_graph)
