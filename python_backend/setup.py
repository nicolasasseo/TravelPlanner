from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import generate_ai_response_stream_async
from models import ChatRequest, WeatherRequest
from services.trip_service import TripService
from search_weather import search_weather
import json

app = FastAPI(
    title="Travel Planner AI API",
    description="AI-powered travel planning assistant API",
    version="1.0.0",
)


# Add CORS middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat-trip", summary="Chat with AI travel assistant")
async def chat_trip(request: ChatRequest):
    """
    Stream chat responses from the AI travel assistant.
    Fetches user's trip data and passes it as context to the AI.
    """
    print(f"\n{'='*80}")
    print(f"🌐 FASTAPI CHAT ENDPOINT HIT")
    print(f"User ID: {request.user_id}")
    print(f"User input: '{request.user_input}'")
    print(f"{'='*80}")

    # Fetch user's trips using the service layer
    print(f"FETCHING USER TRIPS...")
    user_trips_data = TripService.fetch_user_trips(request.user_id)
    print(f"USER TRIPS DATA: {bool(user_trips_data)}")
    if user_trips_data:
        print(f"RIPS PREVIEW: {user_trips_data[:200]}...")

    async def generate_stream():
        try:
            print(f"STARTING STREAM GENERATION...")
            async for token in generate_ai_response_stream_async(
                user_input=request.user_input,
                user_id=request.user_id,
                user_trips=user_trips_data,
            ):
                if token:  # Ensure we don't send empty data
                    print(f"STREAMING TOKEN: '{token}'")
                    yield f"data: {json.dumps({'ai_response': token})}\n\n"
        except Exception as e:
            print(f"STREAM ERROR: {e}")
            import traceback

            traceback.print_exc()
            yield f"data: {json.dumps({'ai_response': f'Error: {e}'})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.post("/trip-weather", summary="Get weather for trip locations")
async def get_trip_weather(request: dict):
    """
    Get weather information for all locations in a trip.
    """
    print(f"Received trip weather request: {request}")

    try:
        # Extract location names from the request
        locations = request.get("locations", [])
        print(f"Locations received: {locations}")

        if not locations:
            print("No locations provided in request")
            return {"error": "No locations provided"}

        # Convert to list of location names
        location_names = [loc.get("name", "") for loc in locations if loc.get("name")]
        print(f"Location names extracted: {location_names}")

        if not location_names:
            print("No valid location names found")
            return {"error": "No valid location names found"}

        # Get weather data
        print(f"Calling search_weather with: {location_names}")
        weather_data = search_weather(location_names)
        print(f"Weather data received: {weather_data}")

        return weather_data

    except Exception as e:
        print(f"Error in trip-weather endpoint: {e}")
        import traceback

        traceback.print_exc()
        return {"error": f"Failed to fetch weather: {str(e)}"}


@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Travel Planner AI API"}
