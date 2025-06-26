"use client"

import { Location } from "@/app/generated/prisma"
import React from "react"
import { GoogleMap, Marker, useLoadScript } from "@react-google-maps/api"

interface MapProps {
  itineraries: Location[]
}

const Map = ({ itineraries }: MapProps) => {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
  })

  if (loadError) {
    return <div>Error loading maps. Please try again later.</div>
  }

  const center = itineraries.length > 0 ? itineraries[0] : { lat: 0, lng: 0 }

  if (!isLoaded) {
    return <div>Loading maps...</div>
  }
  return (
    <GoogleMap
      mapContainerStyle={{ width: "100%", height: "100%" }}
      zoom={8}
      center={center}
    >
      {itineraries.map((location, key) => (
        <Marker
          key={key}
          position={{ lat: location.lat, lng: location.lng }}
          title={location.locationTitle}
        />
      ))}
    </GoogleMap>
  )
}

export default Map
