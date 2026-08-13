from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from sqlite_dbconfig import _init_checkpointer
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from tools_usage import tools
from mcp_tools import client

import requests_toolbelt
import asyncio
import threading

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    # temperature=0
)


# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()

def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)

def run_async(coro):
    return _submit_async(coro).result()

def submit_async_task(coro):
    """Submit a coroutine on the backend event loop."""
    return _submit_async(coro)


def load_mcp_tools():
    try:
        return run_async(client.get_tools())
    except Exception as e:
        print(f"Error loading tools from MCP: {e}")
        return []


mcp_tools = load_mcp_tools()

tools.extend(mcp_tools)

# Make the LLM tool aware
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def chat_node(state: ChatState):
    messages = state['messages']
    system_message = SystemMessage(
        content=(
            "You are a helpful conversational assistant. "
            "For greetings and casual conversation, answer directly "
            "without using any tools. "
            "Use tools only when they are actually required to answer "
            "the user's request."
        )
    )
    response = await llm_with_tools.ainvoke([system_message] + messages)
    return {"messages": [response]}

tool_node = ToolNode(tools) if tools else None

checkpointer = run_async(_init_checkpointer())

# Graph setup
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", 'chat_node')
else:
    graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# Helper
async def _alist_threads():
    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

def retrieve_all_threads():
    thread_ids = run_async(_alist_threads())
    return [
        {
            "id": thread_id,
            "name": str(thread_id)[:20]
        }
        for thread_id in thread_ids
    ]



# chatbot.invoke
# CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# response = chatbot.invoke(
#     {'messages': [HumanMessage(content="What i have asked you buddy?")]},
#     config=CONFIG,
# )
# print(response)

# print(chatbot.get_state(config=CONFIG).values['messages'])

# stream

