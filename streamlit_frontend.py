import queue

import streamlit as st
from bot_backend import chatbot
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from utils import generate_thread_id
from components.sidebar import sidebar_ui, add_thread
from bot_backend import submit_async_task, retrieve_all_threads


# ----------------- SESSION STATE INITIALIZATION -----------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    all_threads = retrieve_all_threads()
    st.session_state['chat_threads'] = all_threads


# ----------------- SIDEBAR -----------------

sidebar_ui()


# ----------------- LOAD CONVERSATION HISTORY -----------------

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')


if user_input:

    # check this is first message or not
    first_message = len(st.session_state['message_history']) == 0

    if first_message:

        st.session_state['chat_threads'].append({
            'id': st.session_state['thread_id'],
            'name': user_input[:20]
        })


    # first add the message to message_history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })


    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {
        "configurable": {
            'thread_id': st.session_state['thread_id']
        },
        "metadata": {
            "thread_id": st.session_state['thread_id']
        },
        "run_name": "chat_turn",
    }


    # ----------------- ASSISTANT STREAMING -----------------

    with st.chat_message('assistant'):

        # Used to store the status box
        status_holder = {"box": None}


        def ai_only_stream():

            event_queue: queue.Queue = queue.Queue()


            async def run_stream():

                try:

                    async for message_chunk, metadata in chatbot.astream(
                        {'messages': [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages"
                    ):

                        event_queue.put((message_chunk, metadata))


                except Exception as exc:

                    event_queue.put(("error", exc))


                finally:

                    event_queue.put(None)


            # Run async function separately
            submit_async_task(run_stream())


            # Read events synchronously
            while True:

                item = event_queue.get()


                if item is None:
                    break


                message_chunk, metadata = item


                if message_chunk == "error":
                    raise metadata


                # ----------------- MCP TOOL STATUS -----------------

                if isinstance(message_chunk, ToolMessage):

                    tool_name = getattr(
                        message_chunk,
                        "name",
                        "tool"
                    )


                    if status_holder["box"] is None:

                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …",
                            expanded=True
                        )

                    else:

                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True
                        )


                # ----------------- STREAM AI TOKENS -----------------

                if isinstance(message_chunk, AIMessage):

                    yield message_chunk.content


        ai_message = st.write_stream(ai_only_stream())


        # Tool was used → mark status as completed
        if status_holder["box"] is not None:

            status_holder["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False
            )


    # ----------------- SAVE ASSISTANT MESSAGE -----------------

    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })


    if first_message:
        st.rerun()