"""
Pydantic models for type safety and validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LocationData(BaseModel):
    """Location data model"""

    name: str
    lat: float = 0.0
    lng: float = 0.0


class TripCreate(BaseModel):
    """Request model for creating a trip"""

    user_id: str = Field(..., alias="userId")
    title: str
    description: str = ""
    summary: Optional[str] = None
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
    locations: List[LocationData] = []

    class Config:
        populate_by_name = True


class TripResponse(BaseModel):
    """Response model for trip data"""

    id: str
    title: str
    description: str
    summary: Optional[str] = None
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
    locations: List[LocationData] = []


class ChatRequest(BaseModel):
    """Chat request model"""

    user_input: str
    user_id: str


class WeatherRequest(BaseModel):
    """Weather request model"""

    locations: List[str]


class WeatherData(BaseModel):
    """Weather data model"""

    location: str
    temperature_f: Optional[float] = None
    temperature_c: Optional[float] = None
    condition: Optional[str] = None
    humidity: Optional[str] = None
    wind: Optional[str] = None


class ForecastDay(BaseModel):
    """Forecast day model"""

    day: str
    condition: Optional[str] = None
    high_f: Optional[float] = None
    low_f: Optional[float] = None
    high_c: Optional[float] = None
    low_c: Optional[float] = None
