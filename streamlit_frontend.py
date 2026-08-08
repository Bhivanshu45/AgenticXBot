import streamlit as st
from bot_backend import chatbot
from langchain_core.messages import HumanMessage
from utils import generate_thread_id
from components.sidebar import sidebar_ui, add_thread


# ----------------- SESSION STATE INITIALIZATION -----------------

# st.session_state -> dict ->

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])


# ----------------- SIDEBAR -----------------

sidebar_ui()


# loading the conversation history

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')


if user_input:

    # check this is first message or not
    first_message = len(st.session_state['message_history']) == 0

    if first_message:

        for thread in st.session_state['chat_threads']:

            if thread['id'] == st.session_state['thread_id']:
                thread['name'] = user_input[:20]
                break

    # first add the message to message_history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {
        'configurable': {
            'thread_id': st.session_state['thread_id']
        }
    }


    # import chatbot and stream the assistant message
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

        # after printing store it
        st.session_state['message_history'].append({
            'role': 'assistant',
            'content': ai_message
        })


    if first_message:
        st.rerun()