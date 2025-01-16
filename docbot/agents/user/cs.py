import json
import json_repair
from typing import Annotated
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.types import Command

import os, sys
path_this = os.path.dirname(os.path.abspath(__file__))
file_queue = os.path.abspath(os.path.join(path_this, "../../app/queue.json"))
file_doc = os.path.abspath(os.path.join(path_this, "files/document.txt"))
sys.path.extend([path_this])
from modules import llm

MD = open(file_doc, "r").read()

def cs_schedule(state: MessagesState) -> str:
    sys_prompt = """You are a hospital customer service. Your job is to provide answers from users regarding the doctor's schedule."""

    human_prompt = (
        "# QUERY"
        f"\n{state['messages'][-2].content}"
        "\n\n# DOCTOR SCHEDULE"
        f"\n{MD}"
    )
    
    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = human_prompt)
    ]

    response = llm.invoke(messages)
    response = response.content

    state["messages"].append(HumanMessage(
        content = response, name = "INTERNAL:schedule"
    ))

    return Command(update = {
        "messages" : response
    }, goto = END)


def update_queue(file_queue, information):
    if os.path.exists(file_queue):
        with open(file_queue, "r") as file:
            queue = json.load(file)
    else:
        queue = {}

    doctor = information["doctor"]
    day_visit = information["day_visit"]
    time_visit = information["time_visit"]

    if doctor not in queue:
        queue[doctor] = {}

    if day_visit not in queue[doctor]:
        queue[doctor][day_visit] = {}

    if time_visit not in queue[doctor][day_visit]:
        queue[doctor][day_visit][time_visit] = []

    current_queue = queue[doctor][day_visit][time_visit]
    queue_number = len(current_queue) + 1

    patient_info = {
        "queue_number": queue_number,
        "user_name": information["user_name"],
        "cellphone": information["cellphone"],
        "address": information["address"]
    }

    current_queue.append(patient_info)

    with open(file_queue, "w") as file:
        json.dump(queue, file, indent=4)

    return queue_number


def cs_queue(state: MessagesState) -> str:
    sys_prompt = """Your job is to create a queue of users. Ensure the following as user information:
- intended doctor
- user name
- cell phone number
- user address
- datetime visit (must match with intended doctor's schedule in day and time)
Always speak in Indonesian"""
    
    contents = "\n".join([m.content for m in state["messages"]])

    human_prompt = (
        "Extract user information from the content provided under the existing conditions.\n"
        " Create it in JSON format.\n"
        "\nIf there is no information in the field, then give a null value."
        """ ```json{{"user_name" : <user name>, "cellphone" : <user cellphone>, "address" : <user address>, "doctor" : <doctor name>, "time_visit" : <user time visit>, "day_visit" : <user day visit>}}```"""
        "\nRepair the reserved data of the doctor's name and schedule (day and time) according to the doctor information."
        "\nNever provide any information outside the given format. Never ask for more confirmation."
        "\n# INFORMATION"
        f"\n{contents}"
        "\n\n# DOCTOR INFORMATION"
        f"\n{MD}"
    )

    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = human_prompt)
    ]

    response = llm.invoke(messages)
    response = response.content

    information = json_repair.loads(response)
    clear = True

    for v in information.values():
        if not v:
            clear = False

    if clear:
        n_queue = update_queue(file_queue, information)
        human_prompt = (
            f"Inform the user that he/she gets queue {n_queue}."
            "\nProvide information on the doctor's schedule to arrive on time."
            "\n# USER INFORMATION"
            f"\n{response}"
            "\nDOCTOR SCHEDULE"
            f"\n{MD}"
            "\nNever write any JSON in your response, instead describe the JSON."
            "\nNever provide any information outside the given information."
            "\nNever ask for any questions or any confirmations."
        )
    else:
        human_prompt = (
            f"Ask the user to complete the blank data."
            "\n# USER INFORMATION"
            f"\n{response}"
            "\nNever write any JSON in your response, instead describe the JSON."
        )

    messages = [
        SystemMessage(content = sys_prompt),
        HumanMessage(content = human_prompt)
    ]
    response = llm.invoke(messages)
    response = response.content

    state["messages"].append(HumanMessage(
        content = response, name = "INTERNAL:queue"
    ))

    return Command(update = {
        "messages" : response
    }, goto = END)