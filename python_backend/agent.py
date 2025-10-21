import os
from langchain_openai import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage,
)

from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing import TypedDict, Annotated, Sequence, Optional
from serpapi import GoogleSearch
import json
from pprint import pprint
from ToolLogger import tool_logger

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    trip_id: Optional[str]


@tool
def search_places(query: str) -> str:
    """Search the web for places to visit in the given query. Give a maximum of 5 results."""
    print(
        f"========================= USING TOOL: Searching for places in {query} =========================\n"
    )
    params = {
        "q": query,
        "engine": "google_maps",
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    tool_logger.log_tool_result(
        tool_name="search_places", query=query, result=results, success=True
    )
    print("Full search results saved to tool_results.json")

    places = []
    for result in results.get("local_results", [])[:5]:
        places.append(
            {
                # Use 'result.get' to access data from the current item in the loop
                "name": result.get("title", "Unknown place"),
                "rating": result.get("rating", "No rating"),
                "address": result.get("address", "No address"),
                "description": result.get("description", "No description"),
            }
        )
    return json.dumps(places)


@tool
def search_trip_planning(destination: str, start_date: str, end_date: str) -> str:
    """Search the web for trip planning information for the given destination, start date, and end date. If the user asks you for something else, say that you are trying to find trip planning information and ask them to rephrase their query."""
    # add debuggin
    print(
        f" ========================= USING TOOL: Searching for trip planning in {destination} from {start_date} to {end_date} ========================= \n"
    )
    query = f"trip planning for {destination} from {start_date} to {end_date}"
    params = {
        "q": f"trip planning for {destination} from {start_date} to {end_date}",
        "engine": "google",
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    # Log the complete results to JSON file for debugging
    tool_logger.log_tool_result(
        tool_name="search_trip_planning", query=query, result=results, success=True
    )
    print(f"📝 Full search results saved to tool_results.json")

    trip_planning_info = results.get("trip_planning", [])
    print(
        f"The trip planning information is {trip_planning_info} for the given destination, start date, and end date."
    )
    return trip_planning_info


tools = [search_places, search_trip_planning]
tool_node = ToolNode(tools)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6).bind_tools(tools)
system_prompt = SystemMessage(
    content="""You are Max, a helpful travel assistant with personality. You can:
    1. Search for places, restaurants, attractions
    2. Get weather information
    3. Help plan trips with detailed itineraries
    
    You have access to real-time data through your tools. Use them to provide accurate, up-to-date information.
    Be helpful, concise, and a bit whimsical in your responses. 
    If you do not know, explain calmly."""
)


def should_use_tools(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def chat(state: AgentState) -> AgentState:
    messages = [system_prompt, *state["messages"]]
    print(f"Messages: {messages}")
    response = llm.invoke(messages)
    print(f"Response: {response}")
    return {"messages": [response]}


graph = StateGraph(AgentState)
graph.add_node("chat", chat)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", should_use_tools, {"tools": "tools", "end": END})
graph.add_edge("tools", "chat")

app = graph.compile()


async def generate_ai_response_stream_async(
    user_input: str, user_id: str, trip_id: Optional[str] = None
):
    print(f"Starting AI response generation for: {user_input}")

    try:
        # Use astream_events for token-by-token streaming
        async for event in app.astream_events(
            {
                "messages": [HumanMessage(content=user_input)],
                "user_id": user_id,
                "trip_id": trip_id,
            },
            version="v2",
        ):
            kind = event["event"]

            # Stream tokens from the LLM
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    print(f"Yielding token: {content}")
                    yield content

            # Handle tool calls if needed
            elif kind == "on_tool_start":
                print(f"Tool started: {event['name']}")

    except Exception as e:
        print(f"Error in AI processing: {e}")
        yield f"Error in AI processing: {str(e)}"
