from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest stock price for a given symbol (e.g. 'AAPL','TSLA')
    using Alpha Vantage API key in the URL.
    """
    try:

        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=4BEUX8UCAQO8ZB16"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


tools = [get_stock_price, search_tool]