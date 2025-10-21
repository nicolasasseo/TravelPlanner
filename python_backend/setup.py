from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from agent import generate_ai_response_stream_async
from search_weather import search_weather
from fastapi.responses import StreamingResponse
import json

app = FastAPI()


class CurrentWeather(BaseModel):
    location: str
    temperature_f: Optional[float]
    temperature_c: Optional[float]
    condition: Optional[str]
    humidity: Optional[str]
    wind: Optional[str]


class ForecastDay(BaseModel):
    day: str
    condition: Optional[str]
    high_f: Optional[float]
    low_f: Optional[float]


class WeatherResponse(BaseModel):
    current: Optional[CurrentWeather]
    forecast: List[ForecastDay]
    error: Optional[str] = None


class LocationData(BaseModel):
    name: str
    lat: float
    lng: float
    order: int


class TripWeatherRequest(BaseModel):
    trip_id: str
    user_id: str
    locations: List[LocationData]
    start_date: str
    end_date: str
    trip_title: str
    trip_description: str


# Add CORS middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatTripRequest(BaseModel):
    user_input: str
    user_id: str


class ChatTripResponse(BaseModel):
    ai_response: str


@app.post("/chat-trip")
async def chat_trip(request: ChatTripRequest):
    print(f"Received request: {request}")

    # Fetch user's trips to pass in context
    import requests

    user_trips_data = None
    try:
        response = requests.get(
            f"http://localhost:3000/api/ai/trips",
            params={"userId": request.user_id},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            trips = data.get("trips", [])

            if trips:
                # Format trips for context
                trips_text = f"You have {len(trips)} trip(s):\n\n"
                for i, trip in enumerate(trips, 1):
                    trips_text += f"{i}. {trip['title']}\n"
                    trips_text += f"   Description: {trip['description']}\n"
                    trips_text += f"   Dates: {trip['startDate'][:10]} to {trip['endDate'][:10]}\n"
                    if trip.get("locations"):
                        location_names = [loc["name"] for loc in trip["locations"]]
                        trips_text += f"   Locations: {', '.join(location_names)}\n"
                    trips_text += "\n"
                user_trips_data = trips_text
    except Exception as e:
        print(f"Error fetching trips: {e}")

    async def generate_stream():
        try:
            async for token in generate_ai_response_stream_async(
                user_input=request.user_input,
                user_id=request.user_id,
                user_trips=user_trips_data,
            ):
                if token:  # Ensure we don't send empty data
                    yield f"data: {json.dumps({'ai_response': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'ai_response': f'Error: {e}'})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.post("/trip-weather")
async def get_trip_weather(request: TripWeatherRequest):
    """
    Get weather information for a trip with all its locations.
    This gives the LLM full context: locations, dates, trip details.
    """
    # Extract location names for the weather query
    location_names = [loc.name for loc in request.locations]
    print(
        f"================================================ Location names: {location_names} ================================================"
    )

    # Get weather for all locations in the trip
    if location_names:
        weather_response = search_weather(location_names)
        print(f"Weather response: {weather_response}")
        return weather_response
    return {"error": "No locations provided for weather query."}
