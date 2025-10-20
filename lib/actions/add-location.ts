"use server"

import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { redirect } from "next/navigation"

async function geocodeAddress(address: string) {
  const apiKey = process.env.GOOGLE_MAPS_API_KEY!
  const response = await fetch(
    `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
      address
    )}&key=${apiKey}`
  )

  const data = await response.json()
  const result = data.results[0]
  const { lat, lng } = result.geometry.location

  // Extract city/locality for better weather searches
  const cityComponent = result.address_components.find(
    (component: any) =>
      component.types.includes("locality") ||
      component.types.includes("administrative_area_level_1")
  )
  const countryComponent = result.address_components.find((component: any) =>
    component.types.includes("country")
  )

  // Create a clean location name (e.g., "Paris, France" instead of "4 rue tourat")
  const locationName =
    cityComponent && countryComponent
      ? `${cityComponent.long_name}, ${countryComponent.long_name}`
      : result.formatted_address

  return { lat, lng, locationName }
}

export async function addLocation(formData: FormData, tripId: string) {
  const session = await auth()
  if (!session) {
    throw new Error("Not authenticated")
  }

  const address = formData.get("address")?.toString()
  if (!address) {
    throw new Error("Missing address")
  }

  const { lat, lng, locationName } = await geocodeAddress(address)

  const count = await prisma.location.count({
    where: { tripId },
  })

  await prisma.location.create({
    data: {
      locationTitle: locationName, // Use clean city name instead of street address
      lat,
      lng,
      tripId,
      order: count,
    },
  })

  redirect(`/trips/${tripId}`)
}
