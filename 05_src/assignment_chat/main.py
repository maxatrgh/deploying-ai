# main.py

from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage,  HumanMessage

from dotenv import load_dotenv
import os

from assignment_chat.prompts import return_instructions
from assignment_chat.tools_meals import get_recipe_by_ingredient
from assignment_chat.tools_leftovers import leftover_tips_helper
from assignment_chat.tools_meal_planner import quick_meal_planner
from utils.logger import get_logger

_logs = get_logger(__name__)
load_dotenv(".env")
#load_dotenv(".secrets")
load_dotenv(".secrets_max")

chat_agent = init_chat_model(
    "openai:gpt-4o-mini",
)

tools = [
    get_recipe_by_ingredient,
    leftover_tips_helper,
    quick_meal_planner,
]

instructions = return_instructions()

# @traceable(run_type="llm")
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    response = chat_agent.bind_tools(tools).invoke(
        [SystemMessage(content=instructions)] + state["messages"]
    )
    return {
        "messages": [response]
    }

def get_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph
