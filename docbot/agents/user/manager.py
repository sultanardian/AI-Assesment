import json_repair
import uuid
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.types import Command
from typing import TypedDict, Literal, Annotated
from typing_extensions import TypedDict

import os, sys
path_this = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([path_this])

from allocator import allocator
from general import general
from cs import cs_schedule, cs_queue

class Manager:
    def __init__(self):
        self.graph = self.__compile()
        self.thread_id = str(uuid.uuid4())

    def __allocator(self, node):
        last = node["messages"][-1].dict()

        if "intent" in last:
            node = last["intent"]
        else:
            node = END

        if node == "finish":
            self.thread_id = str(uuid.uuid4())

        return node

    def __compile(self):
        workflow = StateGraph(MessagesState)
        workflow.add_node("allocator", allocator)
        workflow.add_node("general", general)
        workflow.add_node("internal_schedule", cs_schedule)
        workflow.add_node("internal_queue", cs_queue)
        workflow.add_node("finish", general)

        workflow.add_edge(START, "allocator")
        workflow.add_conditional_edges("allocator", self.__allocator, {
            "general" : "general",
            "internal_schedule" : "internal_schedule",
            "internal_queue" : "internal_queue",
            "finish" : "finish"
        })
        workflow.add_edge("finish", END)

        memory = MemorySaver()
        graph = workflow.compile(checkpointer = memory)
        return graph

    def __call__(self, query):
        config = {
            "configurable" : {
                "thread_id" : self.thread_id
            }
        }
        return self.graph.invoke({
            "messages" : [("user", query)]
        }, config = config)["messages"][-1].content