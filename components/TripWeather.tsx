"use client"
import React, { useState, useEffect } from "react"
import { TripWithLocations } from "./TripClientDetail"

import {
  WiDaySunny,
  WiCloudy,
  WiRain,
  WiSnow,
  WiThermometer,
  WiStrongWind,
  WiHumidity,
} from "react-icons/wi"
import { IconType } from "react-icons"

interface CurrentWeather {
  location: string
  temperature_f?: number
  temperature_c?: number
  condition?: string
  humidity?: string
  wind?: string
}

interface ForecastDay {
  day: string
  condition?: string
  high_f?: number
  low_f?: number
}

interface WeatherResponse {
  current?: CurrentWeather
  forecast?: ForecastDay[]
  error?: string
}

const getWeatherIcon = (condition: string | undefined): React.ReactElement => {
  if (!condition) return <WiDaySunny size={32} /> // Default icon
  const lowerCaseCondition = condition.toLowerCase()

  if (
    lowerCaseCondition.includes("rain") ||
    lowerCaseCondition.includes("drizzle")
  ) {
    return <WiRain size={32} className="text-blue-500" />
  }
  if (
    lowerCaseCondition.includes("cloudy") ||
    lowerCaseCondition.includes("overcast")
  ) {
    return <WiCloudy size={32} className="text-gray-500" />
  }
  if (lowerCaseCondition.includes("snow")) {
    return <WiSnow size={32} className="text-blue-300" />
  }
  // Default to sunny if no match
  return <WiDaySunny size={32} className="text-yellow-500" />
}

interface TripWeatherProps {
  trip: TripWithLocations
}

const TripWeather = ({ trip }: TripWeatherProps) => {
  const [weather, setWeather] = useState<WeatherResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Only fetch if there are locations
    if (trip.locations.length === 0) {
      setLoading(false)
      return
    }

    const fetchWeather = async () => {
      try {
        const response = await fetch("http://localhost:8000/trip-weather", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            trip_id: trip.id,
            user_id: trip.userId,
            locations: trip.locations.map((l) => ({
              name: l.locationTitle,
              lat: l.lat,
              lng: l.lng,
              order: l.order,
            })),
            start_date: trip.startDate.toISOString(),
            end_date: trip.endDate.toISOString(),
            trip_title: trip.title,
            trip_description: trip.description,
          }),
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setWeather(data)
      } catch (err) {
        console.error("Error fetching weather:", err)
        setError(err instanceof Error ? err.message : "Failed to fetch weather")
      } finally {
        setLoading(false)
      }
    }

    fetchWeather()
  }, [trip])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <span className="ml-3">Loading weather information...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Error Loading Weather
        </h3>
        <p className="text-red-600">{error}</p>
        <p className="text-sm text-red-500 mt-2">
          Make sure the Python backend is running on port 8000
        </p>
      </div>
    )
  }

  if (trip.locations.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p className="text-lg mb-2">No locations added yet</p>
        <p className="text-sm">
          Add locations to your trip to see weather information
        </p>
      </div>
    )
  }

  const { current, forecast, error: weatherError } = weather || {}

  if (weatherError) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p className="text-lg mb-2">{weatherError}</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Current Weather Section */}
      {current && (
        <div className="bg-slate-100 p-6 rounded-xl shadow-md">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            {current.location}
          </h3>
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              {getWeatherIcon(current.condition)}
              <div>
                <p className="text-5xl font-bold text-gray-900">
                  {current.temperature_c}°C
                </p>
                <p className="text-gray-600">{current.condition}</p>
              </div>
            </div>
            <div className="text-right text-gray-700 space-y-2">
              <div className="flex items-center justify-end">
                <WiHumidity size={24} className="mr-2" /> Humidity:{" "}
                {current.humidity}
              </div>
              <div className="flex items-center justify-end">
                <WiStrongWind size={24} className="mr-2" /> Wind: {current.wind}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Forecast Section */}
      {forecast && forecast.length > 0 && (
        <div>
          <h4 className="text-xl font-semibold mb-4 text-gray-700">
            5-Day Forecast
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {forecast.map((day, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-lg border text-center space-y-2"
              >
                <p className="font-bold text-gray-800">{day.day}</p>
                {getWeatherIcon(day.condition)}
                <p className="text-sm text-gray-600">{day.condition}</p>
                <div className="flex justify-center items-baseline space-x-2">
                  <span className="text-lg font-semibold">{day.high_f}°</span>
                  <span className="text-gray-500">{day.low_f}°</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TripWeather
