from typing import Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from typing import TypedDict, Literal, Annotated

import os, sys
path_this = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([path_this])
from modules import llm

GENERAL_PROMPT = "If you are asked a question, then answer the question according to your basic knowledge. If you are given a greeting, then reply with a friendly greeting."

general_agent = create_react_agent(
    llm,
    tools = [],
    state_modifier = GENERAL_PROMPT
)

def general(state: MessagesState) -> str:
    result["messages"][-1] = HumanMessage(
        content = result["messages"][-1].content, name = "GENERAL"
    )

    return Command(update = {
        "messages" : result["messages"]
    }, goto = END)