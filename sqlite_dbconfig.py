import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect(database="chatbot_state.db", check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

def retrieve_all_threads():
    all_threads = list()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        if not any(thread['id'] == thread_id for thread in all_threads):
            all_threads.append({'id': thread_id, 'name': "New Chat"})

    return all_threads