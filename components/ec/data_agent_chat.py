import uuid
from typing import Any, Iterator

import pandas as pd
import streamlit as st
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command, Interrupt

from .data_agent.bigquery_utils import get_tables_info
from .data_agent.data_agent import data_agent_graph
from .data_agent.tools import (
    ExecuteBigQuerySqlArgs,
    ExecuteBigQuerySqlErrorResult,
    ExecuteBigQuerySqlSuccessResult,
    ExecutePythonCodeArgs,
    ExecutePythonCodeErrorResult,
    ExecutePythonCodeSuccessResult,
    execute_bigquery_sql,
    execute_python_code,
)


class SessionManager:
    def __init__(self):
        if "thread_id" not in st.session_state:
            st.session_state["thread_id"] = str(uuid.uuid4())

        if "interrupted_response_command" not in st.session_state:
            st.session_state["interrupted_response_command"] = None

    def get_thread_id(self):
        return st.session_state["thread_id"]

    def reset_thread(self):
        st.session_state["thread_id"] = str(uuid.uuid4())

    def set_next_command(self, command: Command):
        st.session_state["interrupted_response_command"] = command

    def reset_command(self):
        st.session_state["interrupted_response_command"] = None

    def get_interrupted_response_command(self):
        return st.session_state["interrupted_response_command"]


def data_agent_chat():
    session_manager = SessionManager()

    config: RunnableConfig = {
        "configurable": {"thread_id": session_manager.get_thread_id()}
    }

    def render_tool_args(tool_args: dict[str, Any]):
        if args := ExecuteBigQuerySqlArgs.safe_model_validate(tool_args):
            st.code(args.sql, language="sql")
            st.code(tool_args, language="json")
        elif args := ExecutePythonCodeArgs.safe_model_validate(tool_args):
            st.code(args.code, language="python")
            st.code(tool_args, language="json")
        else:
            st.code(tool_args, language="json")

    def render_message(message: BaseMessage):
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
                for tool_call in message.tool_calls:
                    with st.container(border=True):
                        st.write(f"Calling tool {tool_call.get('name')}")
                        render_tool_args(tool_call.get("args"))
        elif isinstance(message, ToolMessage):
            with st.chat_message("tool"):
                st.write(f"Result of tool {message.name}")

                if message.name == execute_bigquery_sql.name:
                    if (
                        tool_result
                        := ExecuteBigQuerySqlSuccessResult.safe_model_validate_json(
                            str(message.content)
                        )
                    ):
                        st.write(f"Saved to {tool_result.output_file_path}")
                        st.dataframe(pd.read_csv(tool_result.output_file_path))
                    elif (
                        tool_result
                        := ExecuteBigQuerySqlErrorResult.safe_model_validate_json(
                            str(message.content)
                        )
                    ):
                        st.write(f"Error: {tool_result.error_message}")
                elif message.name == execute_python_code.name:
                    if (
                        tool_result
                        := ExecutePythonCodeSuccessResult.safe_model_validate_json(
                            str(message.content)
                        )
                    ):
                        with st.expander("Standard Output"):
                            st.code(tool_result.stdout, language="python")
                        with st.expander("Standard Error"):
                            st.code(tool_result.stderr, language="python")
                        with st.expander("Error"):
                            st.code(tool_result.error_message)
                        st.write("Output files:")
                        for output_file_path in tool_result.output_files:
                            st.write(f"{output_file_path}")
                            if output_file_path.endswith((".png", ".jpg", ".jpeg")):
                                st.download_button(
                                    label=f"Download {output_file_path}",
                                    data=open(output_file_path, "rb").read(),
                                    file_name=output_file_path,
                                )
                                st.image(open(output_file_path, "rb").read())
                            elif output_file_path.endswith(".csv"):
                                st.dataframe(pd.read_csv(output_file_path))
                            elif output_file_path.endswith(".txt"):
                                st.write(open(output_file_path).read())
                            else:
                                st.write(f"Unknown file type: {output_file_path}")
                    elif (
                        tool_result
                        := ExecutePythonCodeErrorResult.safe_model_validate_json(
                            str(message.content)
                        )
                    ):
                        st.write(f"Error: {tool_result.error_message}")
                else:
                    st.code(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)

    def render_stream_result(events: Iterator[dict[str, Any] | Any]):
        for event in events:
            for value in event.values():
                if isinstance(value, dict) and "messages" in value:
                    for message in value["messages"]:
                        if isinstance(message, BaseMessage):
                            render_message(message)

                if isinstance(value, tuple) and isinstance(value[0], Interrupt):
                    with st.chat_message("ai"):
                        st.markdown(value[0].value["question"])
                        tool_call = value[0].value["tool_call"]
                        st.write(f"Tool: {tool_call['name']}")
                        with st.expander("Arguments"):
                            render_tool_args(tool_call.get("args"))
                    st.button(
                        "Accept",
                        on_click=lambda: session_manager.set_next_command(
                            Command(resume={"action": "continue"})
                        ),
                    )
                    st.button(
                        "Reject",
                        on_click=lambda: session_manager.set_next_command(
                            Command(resume={"action": "reject"})
                        ),
                    )

    def render_templates():
        templates = [
            "Can you tell me what tables there are?",
            "Can you show sales trends by brand with monthly data all on one graph, filtered to the top 5 brands by sales volume during this period?",
        ]

        with st.expander("Templates"):
            for template in templates:
                st.code(template, language="text")

    def render_tables_info():
        @st.cache_data
        def cached_get_tables_info():
            return get_tables_info()

        table_info = cached_get_tables_info()

        with st.expander("Table Schema"):
            table_names = [table.table_name for table in table_info.tables]
            selected_table = st.selectbox("Select a table", table_names)
            if selected_table:
                table_schema = next(
                    (t for t in table_info.tables if t.table_name == selected_table),
                    None,
                )
                if table_schema:
                    st.markdown(f"### Schema of {selected_table}")
                    schema_df = pd.DataFrame(
                        [
                            {
                                "Name": col.column_name,
                                "Type": col.data_type,
                                "Nullable": "✅" if col.is_nullable else "",
                            }
                            for col in table_schema.columns
                        ]
                    )
                    st.dataframe(schema_df, hide_index=True)

    messages: list[BaseMessage] = data_agent_graph.get_state(config=config).values.get(
        "messages", []
    )

    st.title("🤖 AI Data Analysis Agent")

    render_templates()

    render_tables_info()

    for message in messages:
        render_message(message)

    if (
        interrupted_response_command
        := session_manager.get_interrupted_response_command()
    ):
        session_manager.reset_command()
        render_stream_result(
            data_agent_graph.stream(
                interrupted_response_command,
                config=config,
                stream_mode="updates",
            ),
        )

    if prompt := st.chat_input("Enter your message..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        render_stream_result(
            data_agent_graph.stream(
                {"messages": [{"role": "user", "content": prompt}]},
                config=config,
                stream_mode="updates",
            )
        )
