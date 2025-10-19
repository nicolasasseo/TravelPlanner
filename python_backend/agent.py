from langchain_openai import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
    BaseMessage,
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing import TypedDict, Annotated, Sequence, Optional


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    trip_id: Optional[str]
