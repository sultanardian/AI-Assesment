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

BASE_PROMPT = (
            "You are a helpful AI assistant, collaborating with other assistants."
            " Your job is to help users answer their questions."
            " Your name is **DocBOT**, an AI assistant in charge of a hospital."
            " Your job is to help users answer their questions regarding"
            " doctor's appointments (in the hospital) and general questions (outside the hospital)."
            " Your tasks vary, details will be explained below."
            " Use the provided tools to progress towards answering the question."
            " If you are unable to fully answer, that's OK, another assistant with different tools"
            " will help where you left off. Execute what you can to make progress."
            " Here are your tasks in detail."
            " {suffix}"
        )

ALLOCATOR_PROMPT = (
    "You have to classify questions from users."
    "There will be 2 possible questions from users, which are general questions and questions about internal hospital."
    "Classify user queries with the following 2 labels:"
    "- general, If the user's enquiry is about general enquiry."
    "- internal_schedule, If the user's enquiry is about an internal hospital enquiry especially doctor's schedule."
    "- internal_queue, If the user's enquiry is about an internal hospital enquiry especially if the user wants to create a visit, queue, check-up schedule."
    " If the user wants to end the conversation, then generate FINAL."
    " Just produce the label answer, don't beat around the bush."
)

allocator_agent = create_react_agent(
    llm,
    tools = [],
    state_modifier = BASE_PROMPT.format(suffix = ALLOCATOR_PROMPT)
)

def allocator(state: MessagesState) -> Command[Literal["general", "internal_schedule", "internal_queue"]]:
    result = allocator_agent.invoke(state)

    if "general" in result["messages"][-1].content:
        update = "general"
    elif "internal_schedule" in result["messages"][-1].content:
        update = "internal_schedule"
    elif "internal_queue" in result["messages"][-1].content:
        update = "internal_queue"
    else:
        update = "finish"

    result["messages"][-1] = HumanMessage(
        content = state["messages"][-1].content, name = "allocator", intent = update
    )

    return Command(update = {
        "messages" : result["messages"]
    }, goto = update.lower())