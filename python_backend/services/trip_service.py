"""
Service layer for trip-related operations.
Handles communication with Next.js API for trip data.
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

NEXTJS_API_BASE = os.getenv("NEXTJS_API_BASE", "http://localhost:3000")


class TripService:
    """Service for trip data operations"""

    @staticmethod
    def fetch_user_trips(user_id: str) -> Optional[str]:
        """
        Fetch user trips and format as context string for the AI.

        Args:
            user_id: The user's ID

        Returns:
            Formatted string of trip data or None if error
        """
        try:
            response = requests.get(
                f"{NEXTJS_API_BASE}/api/ai/trips",
                params={"userId": user_id},
                timeout=5,
            )

            if response.status_code != 200:
                print(f"Error fetching trips: {response.status_code}")
                return None

            data = response.json()
            trips = data.get("trips", [])

            if not trips:
                return None

            # Format trips for AI context
            trips_text = f"You have {len(trips)} trip(s):\n\n"
            for i, trip in enumerate(trips, 1):
                trips_text += f"{i}. {trip['title']}\n"
                trips_text += f"   Description: {trip['description']}\n"
                trips_text += (
                    f"   Dates: {trip['startDate'][:10]} to {trip['endDate'][:10]}\n"
                )
                if trip.get("locations"):
                    location_names = [loc["name"] for loc in trip["locations"]]
                    trips_text += f"   Locations: {', '.join(location_names)}\n"
                trips_text += "\n"

            return trips_text

        except Exception as e:
            print(f"Error in fetch_user_trips: {e}")
            return None
