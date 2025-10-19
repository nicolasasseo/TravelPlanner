from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatTripRequest(BaseModel):
    user_input: str
    # maybe have an id field that links to the user id and trip id?
    user_id: str
    trip_id: str


class ChatTripResponse(BaseModel):
    ai_response: str


@app.post("/chat-trip", response_model=ChatTripResponse)
async def chat_trip(request: ChatTripRequest):
    ai_response = await generate_ai_response(
        user_input=request.user_input, user_id=request.user_id, trip_id=request.trip_id
    )

    return ChatTripResponse(ai_response=ai_response)
