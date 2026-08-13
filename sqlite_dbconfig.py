import sqlite3
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

async def _init_checkpointer():
    conn = await aiosqlite.connect(database="chatbot_state.db")
    return AsyncSqliteSaver(conn)

