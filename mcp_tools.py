from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": "python",
            "args": ["arith.py"]
        },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)
