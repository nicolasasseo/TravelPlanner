import os
import requests
from langchain_core.tools import tool
from typing import Optional
from search_weather import search_weather
from dotenv import load_dotenv

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
