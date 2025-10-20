from serpapi import GoogleSearch
import os
from ToolLogger import tool_logger
from dotenv import load_dotenv

load_dotenv()


def search_weather(query: list[str]) -> dict:
    """Search the web for the weather in the locations of the trip.

    Args:
        query: list[str] - The list of locations to search for weather.
    """
    print(
        f"========================= USING TOOL: Searching for weather in {query} =========================\n"
    )
    weather_data = []
    for location in query:
        weather_query = f"weather {location}"  # Simpler query works better
        params = {
            "q": weather_query,
            "engine": "google",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # Log for debugging
        tool_logger.log_tool_result(
            tool_name="search_weather",
            query=weather_query,
            result=results,
            success=True,
        )

        answer_box = results.get("answer_box", {})
        if answer_box and "weather" in answer_box:
            temp_f = answer_box.get("temperature")
            try:
                temp_c = (int(temp_f) - 32) * 5 // 9
            except (ValueError, TypeError):
                temp_c = None
            current_weather = {
                "location": answer_box.get("location", location),
                "temperature_f": temp_f,
                "temperature_c": temp_c,
                "condition": answer_box.get("weather"),
                "humidity": answer_box.get("humidity"),
                "wind": answer_box.get("wind"),
            }
            forecast_data = []
            forecast_list = answer_box.get("forecast", [])
            if forecast_list:
                for day_forecast in forecast_list[:5]:  # Get up to 5 days
                    forecast_data.append(
                        {
                            "day": day_forecast.get("day"),
                            "condition": day_forecast.get("weather"),
                            "high_f": day_forecast.get("temperature", {}).get("high"),
                            "high_c": (
                                int(day_forecast.get("temperature", {}).get("high"))
                                - 32
                            )
                            * 5
                            // 9,
                            "low_f": day_forecast.get("temperature", {}).get("low"),
                            "low_c": (
                                int(day_forecast.get("temperature", {}).get("low")) - 32
                            )
                            * 5
                            // 9,
                        }
                    )
            weather_data.append({"current": current_weather, "forecast": forecast_data})
        else:
            print(f"No answer_box with weather found for {location}")

    if not weather_data:
        return {"error": "Could not fetch weather data for any locations"}

    return {"locations": weather_data}
