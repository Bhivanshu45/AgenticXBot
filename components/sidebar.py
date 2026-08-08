import streamlit as st
from bot_backend import chatbot
from langchain_core.messages import HumanMessage
from utils import generate_thread_id


# --------------- UTILITY FUNCTIONS -----------------

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id, name="New Chat"):
    for thread in st.session_state['chat_threads']:
        if thread['id'] == thread_id:
            # Thread already exists
            return

    st.session_state['chat_threads'].append({
        'id': thread_id,
        'name': name
    })


def load_chat_history(thread_id):
    CONFIG = {'configurable': {'thread_id': thread_id}}
    state = chatbot.get_state(config=CONFIG)

    if not state.values:
        return []

    return state.values.get('messages', [])


# ----------------- SIDEBAR -----------------

def sidebar_ui():

    st.sidebar.title("AgenticXBot")

    if st.sidebar.button("New Chat"):
        reset_chat()

    st.sidebar.header("My Conversations")

    # ------------------ RENDER CHAT THREADS ------------------

    for thread in st.session_state['chat_threads'][::-1]:

        if st.sidebar.button(
            thread['name'],
            key=f"thread_{thread['id']}"
        ):

            st.session_state['thread_id'] = thread['id']

            messages = load_chat_history(thread['id'])

            temp_messages = []

            for message in messages:

                if isinstance(message, HumanMessage):
                    role = 'user'
                else:
                    role = 'assistant'

                temp_messages.append({
                    'role': role,
                    'content': message.content
                })

            st.session_state['message_history'] = temp_messages