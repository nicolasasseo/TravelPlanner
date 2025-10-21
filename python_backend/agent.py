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
from search_weather import search_weather as search_weather_function
from trip_tools import (
    create_trip,
    add_destination_to_trip,
    get_trip_details,
    get_travel_recommendations,
)

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    user_trips: Optional[str]  # Trip data passed in context


@tool
def search_places(query: str) -> str:
    """Search for places, attractions, restaurants, and things to do in a location.

    Use this when the user asks for recommendations or places to visit.
    If they specify a location, use it directly. Don't ask again.

    Examples:
    - User: "What can I do in Paris?" → Call search_places("things to do in Paris")
    - User: "Best restaurants in Tokyo" → Call search_places("best restaurants in Tokyo")
    - User: "Find places in London" → Call search_places("places to visit in London")

    Returns: Up to 5 top results with ratings and descriptions.
    """
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


@tool
def search_weather(locations: str) -> str:
    """Get current weather and forecast for one or more locations anywhere in the world.

    Use this tool when the user asks about weather for ANY location they mention.
    DO NOT ask the user for the location if they already told you - just use this tool with their location.

    Examples:
    - User: "What's the weather in Tokyo?" → Call search_weather("Tokyo")
    - User: "Weather for Paris and London?" → Call search_weather("Paris, London")
    - User: "Is it raining in New York?" → Call search_weather("New York")

    Args:
        locations: Comma-separated list of location names. Accept ANY format the user provides.
    """
    print(
        f"========================= USING TOOL: Searching weather for {locations} =========================\n"
    )

    # Parse the comma-separated locations
    location_list = [loc.strip() for loc in locations.split(",")]

    # Call the search_weather function
    weather_data = search_weather_function(location_list)

    if "error" in weather_data:
        return f"Could not fetch weather data: {weather_data['error']}"

    # Format the response
    result = ""
    for i, loc_weather in enumerate(weather_data.get("locations", [])):
        location_name = location_list[i] if i < len(location_list) else "Unknown"
        current = loc_weather.get("current", {})

        result += f"\n📍 **{location_name}**\n"
        result += f"Current: {current.get('condition', 'N/A')}, {current.get('temperature_f', 'N/A')}°F ({current.get('temperature_c', 'N/A')}°C)\n"
        result += f"Humidity: {current.get('humidity', 'N/A')}, Wind: {current.get('wind', 'N/A')}\n"

        forecast = loc_weather.get("forecast", [])
        if forecast:
            result += "Forecast:\n"
            for day in forecast[:3]:  # Show 3-day forecast
                result += (
                    f"  - {day.get('day', 'N/A')}: {day.get('condition', 'N/A')}, "
                )
                result += f"High: {day.get('high_f', 'N/A')}°F, Low: {day.get('low_f', 'N/A')}°F\n"
        result += "\n"

    return result if result else "Could not fetch weather data."


tools = [
    search_places,
    search_trip_planning,
    search_weather,
    create_trip,
    add_destination_to_trip,
    get_trip_details,
    get_travel_recommendations,
]
tool_node = ToolNode(tools)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8).bind_tools(tools)


def should_use_tools(state: AgentState) -> str:
    last_message = state["messages"][-1]
    print(f"\nDECISION NODE - Should use tools?")
    print(
        f"Last message has tool_calls: {hasattr(last_message, 'tool_calls') and bool(last_message.tool_calls)}"
    )

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"ROUTING TO TOOLS - {len(last_message.tool_calls)} tool(s) to execute")
        return "tools"
    else:
        print(f"ENDING CONVERSATION - No tools needed")
        return "end"


def chat(state: AgentState) -> AgentState:
    # Build dynamic system prompt with user's trip data
    print(f"\n{'='*80}")
    print(f"🤖 CHAT NODE - Processing user input")
    print(f"User ID: {state.get('user_id', 'Unknown')}")
    print(f"Messages count: {len(state.get('messages', []))}")
    print(f"User trips available: {bool(state.get('user_trips'))}")
    print(f"{'='*80}")

    base_prompt = """You are Max, a helpful travel assistant with personality. You can:
    1. **Create trips** for users (use create_trip tool)
    2. **Check weather** for ANY location (use search_weather tool)
    3. **Search for places**, restaurants, and attractions (use search_places tool)
    4. **Search for trip planning** information (use search_trip_planning tool)
    5. **Add destinations** to existing trips (use add_destination_to_trip tool)
    6. **Get trip details** and information (use get_trip_details tool)
    7. **Get personalized recommendations** (use get_travel_recommendations tool)
    
    ## How to Use Tools:
    
    IMPORTANT: Tools are AUTOMATIC - you call them based on what the user says. Don't ask for permission to use tools, just use them!
    
    ## Creating Trips - EXAMPLES:
    
    When a user wants to create a trip, have a natural conversation to gather missing information ONLY:
    - Destination (where they want to go) - if not mentioned, ask
    - Dates (accept ANY date format - "next week", "July 1-10", "2024-07-01", etc.) - if not mentioned, ask
    - Trip type/purpose (optional - if they don't mention it, skip it)

    Example 1:
    User: "I want to create a trip to Paris from July 1-10"
    You: "Perfect! Let me research Paris for your July 1-10 trip..." [call search_places and search_weather, then create_trip]
    
    Example 2:
    User: "I'd like to go to New York and Boston from October 17th 2025 to October 28th 2025"
    You: "Great! Let me research New York and Boston for your October 17-28 trip..." [call search_places and search_weather, then create_trip]
    
    Example 3:
    User: "I would like to go to Rome and Milan. October 18 to October 28 2025"
    You: "Fantastic! Let me research Rome and Milan for your October 18-28 trip..." [call search_places and search_weather, then create_trip]
    
    Example 4:
    User: "Create a trip"
    You: "I'd love to help! Where would you like to go?" [wait for destination]
    
    ## Adding Destinations to Existing Trips:
    
    Example 5:
    User: "Add Paris to my New York trip"
    You: "I'll add Paris to your New York trip!" [call add_destination_to_trip]
    
    Example 6:
    User: "I want to visit Tokyo on my Japan trip"
    You: "Great! I'll add Tokyo to your Japan trip!" [call add_destination_to_trip]
    
    ## Getting Trip Information:
    
    Example 7:
    User: "Show me my trips"
    You: "Let me get your trip details..." [call get_trip_details]
    
    Example 8:
    User: "What's in my Paris trip?"
    You: "Let me check your Paris trip details..." [call get_trip_details with trip_title="Paris"]
    
    ## Getting Recommendations:
    
    Example 9:
    User: "Give me recommendations for Tokyo"
    You: "I'll get personalized recommendations for Tokyo..." [call get_travel_recommendations]
    
    Example 10:
    User: "What should I do in Paris for a cultural trip?"
    You: "Let me get cultural recommendations for Paris..." [call get_travel_recommendations with trip_type="cultural"]

    You can also add destinations yourself when using create_trip tool. Just scan the user input for distinct locations and add them to the trip.
    
    CRITICAL RULES:
    - NEVER repeat questions - if they already told you something, YOU ALREADY KNOW IT
    - If user says "New York and Boston from October 17th to October 28th" → YOU HAVE EVERYTHING YOU NEED
    - If user says "Paris next week" → YOU HAVE EVERYTHING YOU NEED (convert dates yourself)
    - Accept flexible date formats - convert them yourself to YYYY-MM-DD
    - Once you have destination + dates, use search_places and search_weather to research
    - Generate a detailed 2-3 paragraph summary with itinerary, weather tips, and local recommendations
    - **THEN IMMEDIATELY call create_trip tool with all the information**
    - **DO NOT just give recommendations - CREATE THE TRIP!**
    
    ## For Weather & Places:
    
    When users ask about weather or places:
    - If they specify a location → USE THE TOOL IMMEDIATELY with that location
    - If they don't specify → Ask once which location
    - Accept ANY location format - "Tokyo", "Paris, France", "New York City", etc.
    - After using the tool, present the results in a helpful, conversational way
    
    ## General Rules:
    
    - Be conversational and natural
    - Don't repeat yourself or ask redundant questions
    - Use tools automatically when you have the information needed
    - Accept flexible user input - dates, locations, etc. in any reasonable format
    - You have access to real-time data through your tools. Use them!
    - Handle ALL types of travel queries - creation, modification, information, recommendations"""

    # Add user's trip data to context if available
    if state.get("user_trips"):
        trips_context = f"\n\nUSER'S TRIPS:\n{state['user_trips']}\n\nUse this information to answer questions about the user's trips. You don't need to call any tools to access this data - it's already here."
        system_content = base_prompt + trips_context
    else:
        system_content = base_prompt + "\n\nThe user doesn't have any trips yet."

    system_prompt = SystemMessage(content=system_content)
    messages = [system_prompt, *state["messages"]]

    print(f"\n📝 SYSTEM PROMPT LENGTH: {len(system_content)} characters")
    print(f"📝 TOTAL MESSAGES: {len(messages)}")
    print(
        f"📝 LAST USER MESSAGE: {state['messages'][-1].content if state['messages'] else 'None'}"
    )

    print(f"\n🔄 CALLING LLM...")
    response = llm.invoke(messages)

    print(f"\n✅ LLM RESPONSE RECEIVED:")
    print(f"Content: {response.content[:200]}...")
    print(
        f"Tool calls: {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0}"
    )

    if hasattr(response, "tool_calls") and response.tool_calls:
        for i, tool_call in enumerate(response.tool_calls):
            print(f"  Tool {i+1}: {tool_call['name']} with args: {tool_call['args']}")

    return {"messages": [response]}


graph = StateGraph(AgentState)
graph.add_node("chat", chat)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", should_use_tools, {"tools": "tools", "end": END})
graph.add_edge("tools", "chat")

app = graph.compile()


async def generate_ai_response_stream_async(
    user_input: str,
    user_id: str,
    user_trips: Optional[str] = None,
):
    print(f"\n{'='*80}")
    print(f"🚀 STARTING AI RESPONSE GENERATION")
    print(f"User input: '{user_input}'")
    print(f"User ID: {user_id}")
    print(f"User trips context: {bool(user_trips)}")
    print(f"{'='*80}")

    try:
        # Use astream_events for token-by-token streaming
        async for event in app.astream_events(
            {
                "messages": [HumanMessage(content=user_input)],
                "user_id": user_id,
                "user_trips": user_trips,  # Pass trip data in context
            },
            version="v2",
        ):
            kind = event["event"]
            print(f"\nEVENT: {kind}")

            # Stream tokens from the LLM
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    print(f"YIELDING TOKEN: '{content}'")
                    yield content

            # Handle tool calls if needed
            elif kind == "on_tool_start":
                tool_name = event.get("name", "Unknown")
                print(f"TOOL STARTED: {tool_name}")

            elif kind == "on_tool_end":
                tool_name = event.get("name", "Unknown")
                print(f"TOOL COMPLETED: {tool_name}")

            elif kind == "on_chat_model_start":
                print(f"CHAT MODEL STARTED")

            elif kind == "on_chat_model_end":
                print(f"CHAT MODEL ENDED")

    except Exception as e:
        print(f"\n❌ ERROR IN AI PROCESSING: {e}")
        import traceback

        traceback.print_exc()
        yield f"Error in AI processing: {str(e)}"
