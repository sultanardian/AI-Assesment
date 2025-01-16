import streamlit as st
from streamlit_chat import message

import os, sys
path_this = os.path.dirname(os.path.abspath(__file__))
path_module = os.path.abspath(os.path.join(path_this, "../agents/user"))
sys.path.append(path_module)

from manager import Manager

if "manager" not in st.session_state:
    st.session_state["manager"] = Manager()

st.set_page_config(page_title="DocBot", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>DocBot 🤖</h1>", unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = [] 

st.sidebar.title("Sidebar")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state["manager"] = Manager()

def generate_response(query):
    response = st.session_state["manager"](query)
    return response

response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))