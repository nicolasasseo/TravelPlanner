import os
import requests
from langchain_core.tools import tool
from typing import Optional, List, Dict
from search_weather import search_weather
from dotenv import load_dotenv
from serpapi import GoogleSearch
import json
from datetime import datetime
from trip_utils import (
    parse_date_flexible,
    extract_locations_from_text,
    create_locations_json,
    parse_trip_request,
)

load_dotenv()

# Base URL for the Next.js API
NEXTJS_API_BASE = os.getenv("NEXTJS_API_BASE", "http://localhost:3000")


@tool
def get_trip_weather(user_id: str, trip_title: Optional[str] = None) -> str:
    """Get weather information for a trip's locations.
    If trip_title is provided, gets weather for that specific trip.
    If trip_title is not provided, gets weather for all upcoming trips.

    Args:
        user_id: The ID of the user
        trip_title: Optional title of the trip to get weather for
    """
    print(
        f"========================= USING TOOL: Fetching weather for trip '{trip_title or 'all trips'}' =========================\n"
    )

    try:
        response = requests.get(
            f"{NEXTJS_API_BASE}/api/ai/trips",
            params={"userId": user_id},
            timeout=10,
        )

        if response.status_code != 200:
            return f"Error fetching trips: {response.status_code}"

        data = response.json()
        trips = data.get("trips", [])

        if not trips:
            return "You don't have any trips to check weather for."

        # If trip_title is provided, find that specific trip
        if trip_title:
            matching_trip = None
            for trip in trips:
                if trip_title.lower() in trip["title"].lower():
                    matching_trip = trip
                    break

            if not matching_trip:
                return f"Could not find a trip with title matching '{trip_title}'"

            trips = [matching_trip]

        # Get weather for all locations in the selected trips
        result = ""
        for trip in trips:
            if not trip["locations"]:
                result += f"\n**{trip['title']}**: No locations added yet.\n"
                continue

            location_names = [loc["name"] for loc in trip["locations"]]
            weather_data = search_weather(location_names)

            if "error" in weather_data:
                result += f"\n**{trip['title']}**: {weather_data['error']}\n"
                continue

            result += f"\n**{trip['title']}** ({trip['startDate'][:10]} to {trip['endDate'][:10]}):\n\n"

            for i, loc_weather in enumerate(weather_data.get("locations", [])):
                location_name = (
                    location_names[i] if i < len(location_names) else "Unknown"
                )
                current = loc_weather.get("current", {})

                result += f"📍 **{location_name}**\n"
                result += f"   Current: {current.get('condition', 'N/A')}, {current.get('temperature_f', 'N/A')}°F ({current.get('temperature_c', 'N/A')}°C)\n"
                result += f"   Humidity: {current.get('humidity', 'N/A')}, Wind: {current.get('wind', 'N/A')}\n"

                forecast = loc_weather.get("forecast", [])
                if forecast:
                    result += "   Forecast:\n"
                    for day in forecast[:3]:  # Show 3-day forecast
                        result += f"      - {day.get('day', 'N/A')}: {day.get('condition', 'N/A')}, "
                        result += f"High: {day.get('high_f', 'N/A')}°F, Low: {day.get('low_f', 'N/A')}°F\n"
                result += "\n"

        return result if result else "Could not fetch weather data."

    except Exception as e:
        print(f"Error in get_trip_weather: {e}")
        return f"Error fetching weather: {str(e)}"


@tool
def create_trip(
    user_id: str,
    title: str,
    start_date: str,
    end_date: str,
    description: str = "",
    locations: str = "",
    summary: str = "",
) -> str:
    """Create a new trip for the user with locations and AI-generated summary.

    CRITICAL: Only ask for information you DON'T already have from the conversation!

    EXAMPLES:
    - User: "New York and Boston from October 17th to October 28th" → YOU HAVE EVERYTHING, just create it!
    - User: "Paris next week" → YOU HAVE EVERYTHING, just create it!
    - User: "Create a trip" → Ask for destination and dates

    USAGE RULES:
    - If user mentioned destination AND dates → CREATE THE TRIP IMMEDIATELY
    - If user only mentioned destination → Ask for dates ONCE
    - If user only mentioned dates → Ask for destination ONCE
    - Convert any date format to YYYY-MM-DD yourself
    - You can add destinations yourself when using create_trip tool. Just scan the user input for distinct locations and add them to the trip. Then add them to the database.
    - After gathering info, use search_places and search_weather to research
    - Generate a personalized 2-3 paragraph summary
    - Then call this tool

    Minimum required info:
    1. Destination (if not mentioned, ask ONCE)
    2. Dates (if not mentioned, ask ONCE) - accept ANY format
    3. Trip type is OPTIONAL - skip if not mentioned

    Args:
        user_id: The ID of the user
        title: Title of the trip (e.g., "Romantic Getaway to New York & Boston")
        start_date: Start date in YYYY-MM-DD format (YOU convert from any format user gives)
        end_date: End date in YYYY-MM-DD format (YOU convert from any format user gives)
        description: Brief description (1-2 sentences)
        locations: JSON string of locations array. Format: [{"name": "New York", "lat": 40.7128, "lng": -74.0060}, {"name": "Boston", "lat": 42.3601, "lng": -71.0589}]
        summary: AI-generated personalized summary with itinerary suggestions, weather tips, and highlights (2-3 paragraphs)
    """
    print(f"\n{'='*80}")
    print(f"CREATE_TRIP TOOL CALLED")
    print(f"User ID: {user_id}")
    print(f"Title: {title}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Description: {description}")
    print(f"Locations: {locations}")
    print(f"Summary length: {len(summary)} chars")
    print(f"{'='*80}")

    try:
        # Parse locations if provided
        locations_list = []
        if locations:
            try:
                locations_list = json.loads(locations)
                print(f"PARSED LOCATIONS: {len(locations_list)} locations")
            except json.JSONDecodeError as e:
                print(f"JSON PARSE ERROR: {e}")
                return "Error: locations must be valid JSON array"

        # Validate dates
        try:
            from datetime import datetime

            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            print(f"DATE VALIDATION ERROR: {e}")
            return f"Error: Invalid date format. Expected YYYY-MM-DD, got start_date='{start_date}', end_date='{end_date}'"

        print(f"CALLING NEXT.JS API: {NEXTJS_API_BASE}/api/ai/trips/create")

        response = requests.post(
            f"{NEXTJS_API_BASE}/api/ai/trips/create",
            json={
                "userId": user_id,
                "title": title,
                "description": description,
                "summary": summary,
                "startDate": start_date,
                "endDate": end_date,
                "locations": locations_list,
            },
            timeout=10,
        )

        print(f"API RESPONSE STATUS: {response.status_code}")
        print(f"API RESPONSE TEXT: {response.text[:200]}...")

        if response.status_code == 200:
            data = response.json()
            trip = data.get("trip", {})

            result = f"✅ Trip created successfully!\n\n"
            result += f"**{trip['title']}**\n"
            result += f"Dates: {start_date} to {end_date}\n"

            if trip.get("locations"):
                result += f"\nLocations ({len(trip['locations'])}):\n"
                for loc in trip["locations"]:
                    result += f"  • {loc['locationTitle']}\n"

            result += f"\nYou can view this trip in your dashboard!"
            print(f"TRIP CREATED SUCCESSFULLY")
            return result
        else:
            error_msg = f"Error creating trip: {response.status_code} - {response.text}"
            print(f"TRIP CREATION FAILED: {error_msg}")
            return error_msg

    except Exception as e:
        print(f"CREATE_TRIP EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        return f"Error creating trip: {str(e)}"


@tool
def add_destination_to_trip(
    user_id: str,
    trip_title: str,
    destination_name: str,
    lat: float = 0.0,
    lng: float = 0.0,
) -> str:
    """Add a destination to an existing trip.

    Args:
        user_id: The ID of the user
        trip_title: Title of the trip to add the destination to
        destination_name: Name of the destination to add
        lat: Latitude (optional, defaults to 0.0)
        lng: Longitude (optional, defaults to 0.0)
    """
    print(
        f"========================= USING TOOL: Adding destination '{destination_name}' to trip '{trip_title}' =========================\n"
    )

    try:
        # First, fetch the user's trips to find the matching trip
        response = requests.get(
            f"{NEXTJS_API_BASE}/api/ai/trips",
            params={"userId": user_id},
            timeout=10,
        )

        if response.status_code != 200:
            return f"Error fetching trips: {response.status_code}"

        data = response.json()
        trips = data.get("trips", [])

        if not trips:
            return "You don't have any trips to add destinations to."

        # Find the matching trip
        matching_trip = None
        for trip in trips:
            if trip_title.lower() in trip["title"].lower():
                matching_trip = trip
                break

        if not matching_trip:
            return f"Could not find a trip with title matching '{trip_title}'"

        # Add the destination to the trip
        add_response = requests.post(
            f"{NEXTJS_API_BASE}/api/trips/{matching_trip['id']}/locations",
            json={
                "locationTitle": destination_name,
                "lat": lat,
                "lng": lng,
            },
            timeout=10,
        )

        if add_response.status_code == 200:
            return f"✅ Added '{destination_name}' to your trip '{matching_trip['title']}'!"
        else:
            return f"Error adding destination: {add_response.status_code} - {add_response.text}"

    except Exception as e:
        print(f"Error in add_destination_to_trip: {e}")
        return f"Error adding destination: {str(e)}"


@tool
def get_trip_details(user_id: str, trip_title: Optional[str] = None) -> str:
    """Get detailed information about user's trips.

    Args:
        user_id: The ID of the user
        trip_title: Optional title of specific trip to get details for
    """
    print(
        f"========================= USING TOOL: Getting trip details for '{trip_title or 'all trips'}' =========================\n"
    )

    try:
        response = requests.get(
            f"{NEXTJS_API_BASE}/api/ai/trips",
            params={"userId": user_id},
            timeout=10,
        )

        if response.status_code != 200:
            return f"Error fetching trips: {response.status_code}"

        data = response.json()
        trips = data.get("trips", [])

        if not trips:
            return "You don't have any trips yet."

        # If specific trip requested, filter
        if trip_title:
            matching_trips = [
                trip for trip in trips if trip_title.lower() in trip["title"].lower()
            ]
            if not matching_trips:
                return f"Could not find a trip with title matching '{trip_title}'"
            trips = matching_trips

        result = f"You have {len(trips)} trip(s):\n\n"

        for i, trip in enumerate(trips, 1):
            result += f"{i}. **{trip['title']}**\n"
            result += f"   Description: {trip.get('description', 'No description')}\n"
            result += f"   Dates: {trip['startDate'][:10]} to {trip['endDate'][:10]}\n"

            if trip.get("locations"):
                location_names = [loc["name"] for loc in trip["locations"]]
                result += f"   Locations: {', '.join(location_names)}\n"
            else:
                result += f"   Locations: No locations added yet\n"

            if trip.get("summary"):
                result += f"   Summary: {trip['summary'][:100]}...\n"
            result += "\n"

        return result

    except Exception as e:
        print(f"Error in get_trip_details: {e}")
        return f"Error fetching trip details: {str(e)}"


@tool
def get_llm_context(user_id: str) -> str:
    """Get the current context and state information for debugging purposes.

    This tool provides insight into:
    - User's trip information
    - Current conversation state
    - Available tools and their purposes
    - System configuration

    Args:
        user_id: The ID of the user requesting context information
    """
    print(
        f"========================= USING TOOL: Getting LLM context for user {user_id} =========================\n"
    )

    try:
        context_info = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "available_tools": [
                "get_trip_weather - Get weather for trip locations",
                "create_trip - Create a new trip with destinations and dates",
                "add_destination_to_trip - Add a destination to existing trip",
                "get_trip_details - Get detailed trip information",
                "get_travel_recommendations - Get personalized travel recommendations",
                "get_llm_context - Get current context and debugging info",
            ],
            "system_info": {
                "nextjs_api_base": NEXTJS_API_BASE,
                "python_backend_version": "1.0.0",
            },
        }

        # Get user's trip information
        try:
            response = requests.get(
                f"{NEXTJS_API_BASE}/api/ai/trips",
                params={"userId": user_id},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                trips = data.get("trips", [])
                context_info["user_trips"] = {
                    "total_trips": len(trips),
                    "trip_summaries": [
                        {
                            "id": trip.get("id"),
                            "title": trip.get("title"),
                            "start_date": trip.get("startDate"),
                            "end_date": trip.get("endDate"),
                            "location_count": len(trip.get("locations", [])),
                            "has_summary": bool(trip.get("summary")),
                        }
                        for trip in trips
                    ],
                }
            else:
                context_info["user_trips"] = {
                    "error": f"Failed to fetch trips: {response.status_code}",
                    "total_trips": 0,
                }
        except Exception as e:
            context_info["user_trips"] = {
                "error": f"Exception fetching trips: {str(e)}",
                "total_trips": 0,
            }

        # Format the context information
        result = "🔍 **LLM Context Information**\n\n"
        result += f"**User ID:** {context_info['user_id']}\n"
        result += f"**Timestamp:** {context_info['timestamp']}\n\n"

        result += "**Available Tools:**\n"
        for tool in context_info["available_tools"]:
            result += f"  • {tool}\n"

        result += f"\n**System Configuration:**\n"
        result += (
            f"  • Next.js API Base: {context_info['system_info']['nextjs_api_base']}\n"
        )
        result += f"  • Backend Version: {context_info['system_info']['python_backend_version']}\n"

        result += f"\n**User Trip Information:**\n"
        if "error" in context_info["user_trips"]:
            result += f"  • Error: {context_info['user_trips']['error']}\n"
        else:
            result += f"  • Total Trips: {context_info['user_trips']['total_trips']}\n"
            if context_info["user_trips"]["trip_summaries"]:
                result += "  • Trip Details:\n"
                for trip in context_info["user_trips"]["trip_summaries"]:
                    result += f"    - {trip['title']} ({trip['start_date'][:10]} to {trip['end_date'][:10]})\n"
                    result += f"      Locations: {trip['location_count']}, Has Summary: {trip['has_summary']}\n"

        result += f"\n**Usage Instructions:**\n"
        result += "  • Use 'get_trip_weather' to check weather for your trips\n"
        result += (
            "  • Use 'create_trip' to plan new trips with destinations and dates\n"
        )
        result += (
            "  • Use 'get_travel_recommendations' for destination-specific advice\n"
        )
        result += "  • Use 'get_trip_details' to see all your trip information\n"

        return result

    except Exception as e:
        print(f"Error in get_llm_context: {e}")
        return f"Error getting context: {str(e)}"


@tool
def get_travel_recommendations(
    user_id: str, destination: str, trip_type: str = "general"
) -> str:
    """Get personalized travel recommendations for a destination.

    Args:
        user_id: The ID of the user
        destination: The destination to get recommendations for
        trip_type: Type of trip (adventure, cultural, relaxation, business, etc.)
    """
    print(
        f"========================= USING TOOL: Getting travel recommendations for {destination} ({trip_type}) =========================\n"
    )

    try:
        # Get user's past trips for context
        response = requests.get(
            f"{NEXTJS_API_BASE}/api/ai/trips",
            params={"userId": user_id},
            timeout=10,
        )

        user_context = ""
        if response.status_code == 200:
            data = response.json()
            trips = data.get("trips", [])
            if trips:
                user_context = f"User has {len(trips)} previous trip(s). "
                recent_destinations = [
                    loc["name"]
                    for trip in trips[-3:]
                    for loc in trip.get("locations", [])
                ]
                if recent_destinations:
                    user_context += (
                        f"Recent destinations: {', '.join(recent_destinations)}. "
                    )

        # Search for recommendations
        query = f"{trip_type} travel recommendations {destination}"
        params = {
            "q": query,
            "engine": "google",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # Format recommendations
        result = f"🌍 **Travel Recommendations for {destination}**\n\n"
        result += f"Trip Type: {trip_type.title()}\n"
        if user_context:
            result += f"Based on your travel history: {user_context}\n"

        # Extract useful information from search results
        organic_results = results.get("organic_results", [])[:5]
        if organic_results:
            result += "\n**Top Recommendations:**\n"
            for i, item in enumerate(organic_results, 1):
                title = item.get("title", "No title")
                snippet = item.get("snippet", "No description")
                result += f"{i}. **{title}**\n   {snippet}\n\n"

        return result

    except Exception as e:
        print(f"Error in get_travel_recommendations: {e}")
        return f"Error getting recommendations: {str(e)}"
