import json
import os
import streamlit as st

st.header("Dashboard Antrian")

path_this = os.path.dirname(os.path.abspath(__file__))
path_json = os.path.abspath(os.path.join(path_this, "queue.json"))

queue = json.load(open(path_json, "r"))
st.table(queue)