from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from agent import generate_ai_response, search_weather

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
    # maybe have an id field that links to the user id and trip id?
    user_id: str
    trip_id: Optional[str] = None


class ChatTripResponse(BaseModel):
    ai_response: str


@app.post("/chat-trip", response_model=ChatTripResponse)
async def chat_trip(request: ChatTripRequest):
    # generate_ai_response is synchronous, so we don't await it
    ai_response = generate_ai_response(
        user_input=request.user_input, user_id=request.user_id, trip_id=request.trip_id
    )

    return ChatTripResponse(ai_response=ai_response)


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

    # For now, get weather for the first location
    # Later, you can enhance this to get weather for all locations
    if location_names:
        weather_response = search_weather.invoke({"query": location_names})
        return weather_response
    return WeatherResponse(error="No locations provided for weather query.")
