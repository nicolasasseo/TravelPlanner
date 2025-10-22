import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
from geopy.geocoders import Nominatim


def parse_date_flexible(date_str: str) -> Optional[str]:
    """
    Parse various date formats and return YYYY-MM-DD format.

    Args:
        date_str: Date string in various formats

    Returns:
        Date in YYYY-MM-DD format or None if parsing fails
    """
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip().lower()

    # Handle relative dates
    today = datetime.now()

    if "today" in date_str:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next week" in date_str:
        return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
    elif "next month" in date_str:
        next_month = today.replace(day=1) + timedelta(days=32)
        return next_month.replace(day=1).strftime("%Y-%m-%d")

    # Handle specific date patterns
    patterns = [
        # YYYY-MM-DD
        (r"(\d{4})-(\d{1,2})-(\d{1,2})", "%Y-%m-%d"),
        # MM/DD/YYYY
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%m/%d/%Y"),
        # DD/MM/YYYY
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%d/%m/%Y"),
        # Month DD, YYYY
        (r"([a-z]+)\s+(\d{1,2}),?\s+(\d{4})", "%B %d, %Y"),
        # DD Month YYYY
        (r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", "%d %B %Y"),
        # Month DD
        (r"([a-z]+)\s+(\d{1,2})", "%B %d"),
        # DD Month
        (r"(\d{1,2})\s+([a-z]+)", "%d %B"),
    ]

    for pattern, date_format in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                # For patterns without year, assume current year
                if "%Y" not in date_format:
                    date_str_with_year = f"{match.group(0)} {today.year}"
                    parsed_date = datetime.strptime(
                        date_str_with_year, f"{date_format} %Y"
                    )
                else:
                    parsed_date = datetime.strptime(match.group(0), date_format)

                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return None


def extract_locations_from_text(text: str) -> List[str]:
    """
    Extract location names from text using various patterns.

    Args:
        text: Input text to extract locations from

    Returns:
        List of location names found
    """
    if not text:
        return []

    locations = []
    text_lower = text.lower()

    # Common location patterns - improved to handle more cases
    location_patterns = [
        # "to [location]" - handle "To New York with my Mum"
        r"\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+with|\s+and|\s+from|\s+to|\s+in|\s+at|$)",
        # "in [location]"
        r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "at [location]"
        r"\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "visit [location]"
        r"\bvisit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "go to [location]"
        r"\bgo\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "travel to [location]"
        r"\btravel\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "from [location] to [location]"
        r"\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # "[location] and [location]"
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        # Direct city names (fallback)
        r"\b(New York|Paris|London|Tokyo|Rome|Barcelona|Amsterdam|Berlin|Prague|Vienna|Madrid|Florence|Venice|Milan|Naples|Sicily|Santorini|Mykonos|Athens|Istanbul|Dubai|Singapore|Hong Kong|Bangkok|Sydney|Melbourne|Cairo|Marrakech|Cape Town|Rio de Janeiro|Buenos Aires|Lima|Cusco|Machu Picchu|Galapagos|Peru|Ecuador|Colombia|Brazil|Argentina|Chile|Mexico|Costa Rica|Panama|Guatemala|Belize|Honduras|Nicaragua|El Salvador|Cuba|Jamaica|Dominican Republic|Puerto Rico|Trinidad|Barbados|Bahamas|Bermuda|Iceland|Norway|Sweden|Finland|Denmark|Netherlands|Belgium|Switzerland|Austria|Czech Republic|Poland|Hungary|Croatia|Slovenia|Slovakia|Estonia|Latvia|Lithuania|Portugal|Spain|France|Italy|Germany|United Kingdom|Ireland|Scotland|Wales|Canada|United States|Australia|New Zealand|Japan|South Korea|China|India|Thailand|Vietnam|Cambodia|Laos|Myanmar|Malaysia|Indonesia|Philippines|Taiwan|Mongolia|Nepal|Bhutan|Sri Lanka|Maldives|Mauritius|Seychelles|Madagascar|Kenya|Tanzania|Uganda|Rwanda|Ethiopia|Morocco|Tunisia|Algeria|Egypt|Jordan|Israel|Lebanon|Turkey|Georgia|Armenia|Azerbaijan|Kazakhstan|Uzbekistan|Kyrgyzstan|Tajikistan|Turkmenistan|Afghanistan|Pakistan|Bangladesh|Sri Lanka|Maldives|Mauritius|Seychelles|Madagascar|Kenya|Tanzania|Uganda|Rwanda|Ethiopia|Morocco|Tunisia|Algeria|Egypt|Jordan|Israel|Lebanon|Turkey|Georgia|Armenia|Azerbaijan|Kazakhstan|Uzbekistan|Kyrgyzstan|Tajikistan|Turkmenistan|Afghanistan|Pakistan|Bangladesh)\b",
    ]

    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                locations.extend([m.strip() for m in match if m.strip()])
            else:
                if match.strip():
                    locations.append(match.strip())

    # Remove duplicates and common false positives
    common_false_positives = {
        "the",
        "and",
        "or",
        "but",
        "for",
        "with",
        "from",
        "to",
        "in",
        "at",
        "on",
        "next",
        "this",
        "that",
        "week",
        "month",
        "year",
        "day",
        "time",
        "trip",
        "vacation",
        "holiday",
        "travel",
        "visit",
        "go",
        "want",
        "plan",
        "book",
    }

    locations = list(
        set([loc for loc in locations if loc.lower() not in common_false_positives])
    )

    return locations


def create_locations_json(locations: List[str]) -> str:
    """
    Create JSON string of locations with coordinates.

    Args:
        locations: List of location names

    Returns:
        JSON string of locations with coordinates
    """
    if not locations:
        return "[]"

    geolocator = Nominatim(user_agent="travel_planner")
    locations_data = []

    for location in locations:
        try:
            # Get coordinates for the location
            location_obj = geolocator.geocode(location, timeout=10)
            if location_obj:
                locations_data.append(
                    {
                        "name": location,
                        "lat": location_obj.latitude,
                        "lng": location_obj.longitude,
                    }
                )
            else:
                # If geocoding fails, add with default coordinates
                locations_data.append({"name": location, "lat": 0.0, "lng": 0.0})
        except Exception as e:
            print(f"Error geocoding {location}: {e}")
            # Add with default coordinates if geocoding fails
            locations_data.append({"name": location, "lat": 0.0, "lng": 0.0})

    return json.dumps(locations_data)


def parse_trip_request(text: str) -> Dict[str, Optional[str]]:
    """
    Parse trip request text to extract start and end dates.

    Args:
        text: Input text containing trip information

    Returns:
        Dictionary with start_date and end_date keys
    """
    result = {"start_date": None, "end_date": None}

    if not text:
        return result

    text_lower = text.lower()

    # Look for date ranges
    date_range_patterns = [
        # "from X to Y"
        r"from\s+([^to]+)\s+to\s+([^,\s]+)",
        # "X to Y"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}|\w+\s+\d{1,2})\s+to\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}|\w+\s+\d{1,2})",
        # "X - Y"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}|\w+\s+\d{1,2})\s*-\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}|\w+\s+\d{1,2})",
    ]

    for pattern in date_range_patterns:
        match = re.search(pattern, text_lower)
        if match:
            start_str = match.group(1).strip()
            end_str = match.group(2).strip()

            start_date = parse_date_flexible(start_str)
            end_date = parse_date_flexible(end_str)

            if start_date and end_date:
                result["start_date"] = start_date
                result["end_date"] = end_date
                return result

    # Look for single dates (assume it's start date)
    single_date_patterns = [
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4})",
        r"(\w+\s+\d{1,2})",
        r"(next\s+week)",
        r"(next\s+month)",
    ]

    for pattern in single_date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            date_str = match.group(1).strip()
            parsed_date = parse_date_flexible(date_str)
            if parsed_date:
                result["start_date"] = parsed_date
                # Assume trip duration of 7 days if no end date
                start_dt = datetime.strptime(parsed_date, "%Y-%m-%d")
                end_dt = start_dt + timedelta(days=7)
                result["end_date"] = end_dt.strftime("%Y-%m-%d")
                return result

    return result
