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
    """Search the web for places to visit in the given query. Give a maximum of 5 results"""
    print(
        f" ========================= USING TOOL: Searching for places in {query} ========================= \n"
    )
    params = {"q": query, "engine": "google", "api_key": os.getenv("SERPAPI_API_KEY")}
    print(f"Params: {params} \n")
    search = GoogleSearch(params)
    print(f"Search: {search} \n")
    results = search.get_dict()
    pprint(results)
    places = []
    for result in results.get("local_results", [])[:5]:
        places.append(
            {
                "name": results.get("title", "Unknown place"),
                "url": results.get("link", "Unknown link"),
                "snippet": results.get("snippet", "Unknown snippet"),
            }
        )
    print(f"Found {len(places)} places for query: {query}")
    print(f"Places: {places} \n")
    return json.dumps(places)


@tool
def search_weather(query: str) -> str:
    """Search the web for the weather in the given query. If the user asks you for something else, say that you are trying to find the weather and ask them to rephrase their query."""
    print(
        f" ========================= USING TOOL: Searching for weather in {query} ========================= \n"
    )
    params = {"q": query, "engine": "google", "api_key": os.getenv("SERPAPI_API_KEY")}
    pprint(params)
    search = GoogleSearch(params)
    results = search.get_dict()
    pprint(results)

    # Try to extract weather from knowledge_graph.web_results
    weather_info = None
    try:
        web_results = results.get("knowledge_graph", {}).get("web_results", [])
        for result in web_results:
            if "forecast" in result:
                weather_info = result["forecast"]
                break
    except Exception as e:
        print(f"Error extracting weather from knowledge_graph: {e}")

    if weather_info:
        print(f"Found weather info: {weather_info}")
        # Extract current day's weather (first forecast)
        current_weather = weather_info[0]
        day = current_weather.get("day", "Today")
        temperature = current_weather.get("temperature", "Unknown")
        condition = current_weather.get("weather", "Unknown")
        unit = current_weather.get("unit", "degrees")

        weather_summary = (
            f"The weather in {query} for {day} is {temperature} {unit} and {condition}."
        )

        # Add forecast for next few days
        if len(weather_info) > 1:
            forecast_text = "\n\nForecast for the next few days:\n"
            for day_forecast in weather_info[1:4]:  # Next 2 days
                day_name = day_forecast.get("day", "Unknown day")
                temp = day_forecast.get("temperature", "Unknown")
                weather_cond = day_forecast.get("weather", "Unknown")
                forecast_text += f"- {day_name}: {temp} {unit}, {weather_cond}\n"
            weather_summary += forecast_text

        return weather_summary

    return f"Sorry, I could not find the weather information for {query}."


@tool
def search_trip_planning(destination: str, start_date: str, end_date: str) -> str:
    """Search the web for trip planning information for the given destination, start date, and end date. If the user asks you for something else, say that you are trying to find trip planning information and ask them to rephrase their query."""
    # add debuggin
    print(
        f" ========================= USING TOOL: Searching for trip planning in {destination} from {start_date} to {end_date} ========================= \n"
    )
    params = {
        "q": f"trip planning for {destination} from {start_date} to {end_date}",
        "engine": "google",
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }
    pprint(params)
    search = GoogleSearch(params)
    results = search.get_dict()
    pprint(results)
    trip_planning_info = results.get("trip_planning", [])
    print(
        f"The trip planning information is {trip_planning_info} for the given destination, start date, and end date."
    )
    return trip_planning_info


tools = [search_places, search_weather, search_trip_planning]
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
    return {"messages": [response]}


graph = StateGraph(AgentState)
graph.add_node("chat", chat)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", should_use_tools, {"tools": "tools", "end": END})
graph.add_edge("tools", "chat")

app = graph.compile()


def generate_ai_response(user_input: str, user_id: str, trip_id: Optional[str] = None):
    result = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_id": user_id,
            "trip_id": trip_id,
        }
    )
    return result["messages"][-1].content


print(generate_ai_response("What is the weather in Tokyo?", "123", "456"))
