import os
import streamlit as st
from composio_langchain import App, ComposioToolSet
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain_community.llms import HuggingFaceEndpoint

# Retrieve the Hugging Face API token from Streamlit secrets
hf_key = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta", huggingfacehub_api_token=hf_key
)

chat_model = ChatHuggingFace(llm=llm, huggingfacehub_api_token=hf_key)
# Import from composio_langchain
# setup tools
composio_toolset = ComposioToolSet()
# we use composio to add the tools we need
# this gives agents, the ability to use tools, in this case we need SERPAPI
tools = composio_toolset.get_tools(apps=[App.SERPAPI])

# setup ReAct style prompt
prompt = hub.pull("hwchase17/react-json")
prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)

# define the agent
chat_model_with_stop = chat_model.bind(stop=["\nInvalidStop"])
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
    }
    | prompt
    | chat_model_with_stop
    | ReActJsonSingleInputOutputParser()
)

# instantiate AgentExecutor
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)
